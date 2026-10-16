"""P6 V-A: experimental novelty thresholds, not runtime validated."""

import os
from importlib.machinery import SourceFileLoader

_BASE = SourceFileLoader("phase6_bam_common_va", os.path.join(os.path.dirname(__file__), "phase6_bam_base.py")).load_module()
config = _BASE.make_config("V-A", {
    "enabled": True,
    "mode": "adaptive",
    "budgets": {"low": 30, "mid": 45, "full": 60},
    "fraction_thresholds": {"low_max": 0.01, "mid_max": 0.05},
})
