"""P6 V0: current Phase 6 code with the 60-iteration controller disabled."""

import os
from importlib.machinery import SourceFileLoader

_BASE = SourceFileLoader("phase6_bam_common_v0", os.path.join(os.path.dirname(__file__), "phase6_bam_base.py")).load_module()
config = _BASE.make_config("V0", {"enabled": False})
