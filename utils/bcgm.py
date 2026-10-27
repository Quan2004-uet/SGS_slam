"""CPU-testable admission policy for Phase 7 bounded Gaussian insertion."""

from dataclasses import dataclass

import torch


@dataclass(frozen=True)
class BCGMBudget:
    max_new_gaussians_per_event: int
    max_gaussians: int


def parse_bcgm_config(config):
    """Return None for the unchanged Phase 4 path; validate supplied controls."""
    if config is None:
        return None
    if not isinstance(config, dict):
        raise ValueError("bcgm must be a dictionary")
    unknown = set(config) - {"enabled", "max_new_gaussians_per_event", "max_gaussians"}
    if unknown:
        raise ValueError(f"Unknown bcgm keys: {sorted(unknown)}")
    enabled = config.get("enabled", False)
    if type(enabled) is not bool:
        raise ValueError("bcgm.enabled must be a boolean")
    limits = {}
    for name in ("max_new_gaussians_per_event", "max_gaussians"):
        if name not in config:
            if enabled:
                raise ValueError(f"bcgm.{name} is required when enabled")
            continue
        value = config[name]
        if type(value) is not int or value < 0:
            raise ValueError(f"bcgm.{name} must be a nonnegative integer")
        limits[name] = value
    if not enabled:
        return None
    return BCGMBudget(**limits)


def validate_bcgm_config(config):
    """Validate the optional policy against the online mapping configuration."""
    budget = parse_bcgm_config(config.get("bcgm"))
    if budget is not None and config.get("mapping", {}).get(
            "use_gaussian_splatting_densification", False):
        raise ValueError("BCGM admission cap requires gradient densification to remain disabled")
    return budget


def select_bounded_candidates(candidate_mask, depth_priority, depth_error, silhouette,
                              current_count, budget):
    """Select valid flattened pixels, ranking depth evidence then silhouette.

    Equal scores retain ascending flattened pixel index. Inputs already include
    the baseline candidate test and positive-ground-truth-depth filter.
    """
    if candidate_mask.dtype != torch.bool or candidate_mask.ndim != 1:
        raise ValueError("candidate_mask must be a flattened boolean tensor")
    if not all(value.numel() == candidate_mask.numel()
               for value in (depth_priority, depth_error, silhouette)):
        raise ValueError("candidate evidence must align with candidate_mask")
    if current_count > budget.max_gaussians:
        raise ValueError("current Gaussian count already exceeds bcgm.max_gaussians")

    candidate_indices = torch.nonzero(candidate_mask, as_tuple=False).flatten()
    candidate_count = candidate_indices.numel()
    global_available = budget.max_gaussians - current_count
    allowed = min(candidate_count, budget.max_new_gaussians_per_event, global_available)

    if allowed == candidate_count:
        selected_mask = candidate_mask
    else:
        selected_mask = torch.zeros_like(candidate_mask)
        if allowed:
            priority = depth_priority.reshape(-1)[candidate_indices].bool()
            depth_scores = depth_error.reshape(-1)[candidate_indices]
            silhouette_scores = 1.0 - silhouette.reshape(-1)[candidate_indices]
            scores = torch.where(priority, depth_scores, silhouette_scores)
            scores = torch.nan_to_num(scores, nan=float("-inf"),
                                      posinf=float("inf"), neginf=float("-inf"))
            # nonzero() supplies ascending indices; stable sorts preserve that
            # index order for equal evidence values.
            order = torch.argsort(scores, descending=True, stable=True)
            order = order[torch.argsort(priority[order].to(torch.int8),
                                        descending=True, stable=True)]
            selected_mask[candidate_indices[order[:allowed]]] = True

    if candidate_count == 0:
        reason = "no_valid_candidates"
    elif allowed == 0 and global_available == 0:
        reason = "global_cap_reached"
    elif allowed == 0:
        reason = "event_cap_zero"
    elif allowed < candidate_count:
        reason = "budget_limited"
    else:
        reason = "all_candidates_admitted"

    record = {
        "before": current_count,
        "valid_candidates": candidate_count,
        "admitted": allowed,
        "rejected": candidate_count - allowed,
        "global_cap": budget.max_gaussians,
        "event_cap": budget.max_new_gaussians_per_event,
        "global_saturated": current_count + allowed >= budget.max_gaussians,
        "event_saturated": candidate_count > allowed and allowed == budget.max_new_gaussians_per_event,
        "reason": reason,
    }
    return selected_mask, record
