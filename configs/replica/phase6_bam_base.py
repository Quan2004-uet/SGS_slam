"""Shared isolated Replica configuration for P6-BAM experiments.

Set P6_BAM_RUN_ID to a new ``p6_bam_*`` identifier before loading a variant.
The guard runs while the experiment config is loaded, before SLAM starts.
"""

import copy
import os
import re
from importlib.machinery import SourceFileLoader


_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(os.path.dirname(_HERE))
_BASE = SourceFileLoader("phase6_replica_base_config", os.path.join(_HERE, "slam.py")).load_module()
_OUTPUT_ROOT = os.path.join(_REPO, "results", "runtime_artifacts", "phase6_bam")


def make_config(variant, budget_control):
    run_id = os.environ.get("P6_BAM_RUN_ID", "")
    if not re.fullmatch(r"p6_bam_[a-z0-9][a-z0-9_-]*", run_id):
        raise ValueError("Set P6_BAM_RUN_ID to a unique p6_bam_* identifier")
    output_dir = os.path.join(_OUTPUT_ROOT, run_id)
    if os.path.exists(output_dir):
        raise FileExistsError(f"Phase 6 output directory already exists: {output_dir}")
    telemetry_dir = os.path.join(_OUTPUT_ROOT, "telemetry", run_id)
    if os.path.exists(telemetry_dir):
        raise FileExistsError(f"Phase 6 telemetry directory already exists: {telemetry_dir}")

    result = copy.deepcopy(_BASE.config)
    result["workdir"] = _OUTPUT_ROOT
    result["run_name"] = run_id
    result["mapping"]["budget_control"] = copy.deepcopy(budget_control)
    result["profiling"] = {
        "mode": "off",  # Use a frozen LIGHT config for the separately approved GPU gate.
        "run_id": run_id,
        "output_dir": os.path.join(_OUTPUT_ROOT, "telemetry"),
    }
    result["phase6_variant"] = variant
    return result
