"""P6 V-A2: conservative quality-constrained adaptive mapping candidate."""

import os
from importlib.machinery import SourceFileLoader

_BASE = SourceFileLoader(
    "phase6_bam_common_va2",
    os.path.join(os.path.dirname(__file__), "phase6_bam_base.py"),
).load_module()

config = _BASE.make_config("V-A2", {
    "enabled": True,
    "mode": "adaptive",
    "budgets": {"low": 45, "mid": 60, "full": 60},
    "fraction_thresholds": {"low_max": 0.01, "mid_max": 0.05},
})
