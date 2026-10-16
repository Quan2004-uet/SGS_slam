"""CPU-only mapping iteration budget selection for P6-BAM-001.

Counts are Python integers obtained from ``means3D.shape[0]``. No tensor values
or device operations belong in this module.
"""

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class MappingBudgetDecision:
    enabled: bool
    signal_valid: bool
    added_count: int | None
    added_fraction: float | None
    tier: str
    configured_iters: int
    effective_iters: int
    fallback_reason: str | None


def _positive_int(value):
    return type(value) is int and value > 0


def _required_prune_iterations(pruning_config, configured_iters):
    if pruning_config is None:
        return 0
    try:
        start = pruning_config["start_after"]
        stop = pruning_config["stop_after"]
        every = pruning_config["prune_every"]
        if any(type(value) is not int or value < 0 for value in (start, stop)) or not _positive_int(every):
            return None
        if pruning_config.get("reset_opacities", False):
            return None  # Preserve reset scheduling when it is active.
    except (KeyError, TypeError):
        return None
    last_due = min(stop, configured_iters - 1)
    due = [index for index in range(start, last_due + 1) if index % every == 0]
    return due[-1] + 1 if due else 0


def select_mapping_budget(config, configured_iters, pre_gaussians, post_gaussians,
                          frame_id, pruning_config):
    """Choose a mapping budget; invalid active inputs fall back to V0."""
    control = config.get("mapping", {}).get("budget_control")
    enabled = isinstance(control, dict) and control.get("enabled") is True

    def full(reason, valid=False, added=None, fraction=None):
        return MappingBudgetDecision(enabled, valid, added, fraction, "FULL",
                                     configured_iters, configured_iters, reason)

    if control is not None and not isinstance(control, dict):
        return full("invalid_control")
    if isinstance(control, dict) and "enabled" in control and type(control["enabled"]) is not bool:
        return full("invalid_control")
    if not enabled:
        return full("disabled")
    if not _positive_int(configured_iters):
        return full("invalid_configured_iters")
    if type(frame_id) is not int or frame_id < 0:
        return full("invalid_frame_id")
    if frame_id == 0:
        return full("initial_frame")
    if (type(pre_gaussians) is not int or type(post_gaussians) is not int
            or pre_gaussians <= 0 or post_gaussians < pre_gaussians):
        return full("missing_or_invalid_signal")

    added = post_gaussians - pre_gaussians
    fraction = added / pre_gaussians
    if config.get("mapping", {}).get("use_gaussian_splatting_densification", False):
        return full("densification_enabled", True, added, fraction)
    required = _required_prune_iterations(pruning_config, configured_iters)
    if required is None:
        return full("invalid_or_reset_pruning_schedule", True, added, fraction)

    mode = control.get("mode")
    if mode == "fixed":
        budget = control.get("fixed_iters")
        tier = "FIXED"
    elif mode == "adaptive":
        budgets = control.get("budgets")
        thresholds = control.get("fraction_thresholds")
        if (not isinstance(budgets, dict) or not isinstance(thresholds, dict)
                or set(budgets) != {"low", "mid", "full"}
                or set(thresholds) != {"low_max", "mid_max"}):
            return full("invalid_tier_config", True, added, fraction)
        low, mid, high = (budgets[key] for key in ("low", "mid", "full"))
        low_max, mid_max = thresholds["low_max"], thresholds["mid_max"]
        if (not all(_positive_int(value) for value in (low, mid, high))
                or not (low <= mid <= high == configured_iters)
                or any(type(value) not in (int, float) or not isfinite(value)
                       for value in (low_max, mid_max))
                or not (0 <= low_max < mid_max)):
            return full("invalid_tier_config", True, added, fraction)
        if low < required:
            return full("pruning_iteration_floor", True, added, fraction)
        if fraction <= low_max:
            budget, tier = low, "LOW"
        elif fraction <= mid_max:
            budget, tier = mid, "MID"
        else:
            budget, tier = high, "FULL"
    else:
        return full("invalid_mode", True, added, fraction)

    if not _positive_int(budget) or budget > configured_iters:
        return full("invalid_budget", True, added, fraction)
    if budget < required:
        return full("pruning_iteration_floor", True, added, fraction)
    return MappingBudgetDecision(True, True, added, fraction, tier,
                                 configured_iters, budget, None)


TIER_CODES = {"FULL": 0, "MID": 1, "LOW": 2, "FIXED": 3}
FALLBACK_CODES = {
    None: 0, "disabled": 1, "initial_frame": 2, "invalid_frame_id": 3,
    "missing_or_invalid_signal": 4, "densification_enabled": 5,
    "invalid_or_reset_pruning_schedule": 6, "invalid_tier_config": 7,
    "invalid_mode": 8, "invalid_budget": 9, "pruning_iteration_floor": 10,
    "invalid_control": 11, "invalid_configured_iters": 12,
}


def record_mapping_budget(profiler, decision, frame_id, pre_gaussians,
                          post_gaussians, executed_iters, pruning_config):
    """Write one event's scalar metadata to the existing LIGHT telemetry."""
    values = {
        "event_id": frame_id,  # One mapping event at most per frame.
        "enabled": int(decision.enabled),
        "signal_valid": int(decision.signal_valid),
        "pre_gaussians": pre_gaussians if pre_gaussians is not None else -1,
        "post_gaussians": post_gaussians if post_gaussians is not None else -1,
        "added_count": decision.added_count if decision.added_count is not None else -1,
        "added_fraction": decision.added_fraction if decision.added_fraction is not None else -1.0,
        "tier_code": TIER_CODES[decision.tier],
        "configured_iters": decision.configured_iters,
        "effective_iters": decision.effective_iters,
        "executed_iters": executed_iters,
        "fallback_code": FALLBACK_CODES[decision.fallback_reason],
        "pruning_enabled": int(pruning_config is not None),
        "prune_required_iters": _required_prune_iterations(pruning_config, decision.configured_iters) or 0,
    }
    for name, value in values.items():
        profiler.record("mapping.budget", name, value,
                        "fraction" if name == "added_fraction" else "count", frame_id)
    return values
