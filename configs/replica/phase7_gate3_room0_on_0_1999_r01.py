"""Phase 7 Gate 3: full-scene BCGM-on Replica room0 configuration."""
from copy import deepcopy

from configs.replica.phase7_gate2_room0_on_0_499_r01 import config as gate2_config

config = deepcopy(gate2_config)
config["run_name"] = "p7_bcgm_g3_room0_on_0_1999_r01"
config["data"]["end"] = 2000
config["data"]["num_frames"] = 2000
