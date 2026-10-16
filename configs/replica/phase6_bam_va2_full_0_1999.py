"""Explicitly bounded P6 V-A2 full-scene experiment wrapper."""

import os
from importlib.machinery import SourceFileLoader
from pathlib import Path

_HERE = os.path.dirname(os.path.abspath(__file__))
_BASE = SourceFileLoader(
    "phase6_bam_full_va2_base",
    os.path.join(_HERE, "phase6_bam_base.py"),
).load_module()

config = _BASE.make_config("V-A2-FULL-0-1999", {
    "enabled": True,
    "mode": "adaptive",
    "budgets": {"low": 45, "mid": 60, "full": 60},
    "fraction_thresholds": {"low_max": 0.01, "mid_max": 0.05},
})

_PHASE6_ROOT = Path(_BASE._OUTPUT_ROOT).resolve(strict=True)
_RUN_OUTPUT = _PHASE6_ROOT / config["run_name"]
_RUN_TELEMETRY = _PHASE6_ROOT / "telemetry" / config["run_name"]
if _RUN_OUTPUT.is_symlink() or _RUN_TELEMETRY.is_symlink():
    raise ValueError("Refusing Phase 6 run/telemetry symlink targets")
if _RUN_OUTPUT.resolve() != _PHASE6_ROOT / config["run_name"]:
    raise ValueError("Run output path escapes the canonical Phase 6 root")
if _RUN_TELEMETRY.resolve() != _PHASE6_ROOT / "telemetry" / config["run_name"]:
    raise ValueError("Telemetry path escapes the canonical Phase 6 root")

config["data"].update({
    "sequence": "room0",
    "start": 0,
    "end": 2000,
    "stride": 1,
    "num_frames": 2000,
    "load_semantics": True,
    "num_semantic_classes": 101,
})
config["seed"] = 0
config["tracking"]["num_iters"] = 40
config["mapping"]["num_iters"] = 60
config["eval_every"] = 5
config["save_checkpoints"] = True
config["checkpoint_interval"] = 1999
config["checkpoint_first_finalization"] = True
config["use_wandb"] = False
config["profiling"] = {
    "mode": "light",
    "run_id": config["run_name"],
    "output_dir": os.path.join(_BASE._OUTPUT_ROOT, "telemetry"),
    "cpu_timing_interval": 1,
    "cuda_event_interval": 10,
    "cuda_resolve_interval": 10,
    "flush_every": 128,
    "max_buffered_records": 512,
    "max_pending_cuda_events": 512,
    "max_summary_samples": 2048,
    "memory_interval": 5,
}
