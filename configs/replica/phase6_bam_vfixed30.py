"""P6 fixed 30-step mapping control, with full budget on frame 0."""

import os
from importlib.machinery import SourceFileLoader

_BASE = SourceFileLoader("phase6_bam_common_fixed30", os.path.join(os.path.dirname(__file__), "phase6_bam_base.py")).load_module()
config = _BASE.make_config("V-FIXED30", {"enabled": True, "mode": "fixed", "fixed_iters": 30})
