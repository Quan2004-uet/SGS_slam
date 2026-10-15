"""Phase 5 profiling wrapper for the unchanged Replica SGS-SLAM config.

The default mode is deliberately ``off``.  P5-G3 must use an immutable copy
with a unique run_id/output directory and explicit authorization before any
CUDA workload is started.
"""

import copy
import os
from importlib.machinery import SourceFileLoader


_HERE = os.path.dirname(os.path.abspath(__file__))
_BASE = SourceFileLoader("phase5_replica_base_config", os.path.join(_HERE, "slam.py")).load_module()
config = copy.deepcopy(_BASE.config)

config["profiling"] = {
    "mode": "off",  # off | light | detailed
    "run_id": "P5G3_UNSET",
    "output_dir": "./results/runtime_artifacts/phase5_profiling",
    "cpu_timing_interval": 1,
    "memory_interval": 5,
    "cuda_event_interval": 10,
    "cuda_resolve_interval": 10,
    "flush_every": 128,
    "max_buffered_records": 512,
    "max_pending_cuda_events": 512,
    "max_summary_samples": 2048,
}
