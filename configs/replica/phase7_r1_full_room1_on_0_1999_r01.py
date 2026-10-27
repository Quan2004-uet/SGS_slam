"""Phase 7 R1 fast-track: full-scene BCGM-on Replica room1."""
from copy import deepcopy
from configs.replica.phase7_gate3_room0_on_0_1999_r01 import config as room0_gate3

config = deepcopy(room0_gate3)
config["run_name"] = "p7_bcgm_r1_full_room1_on_0_1999_r01"
config["data"]["sequence"] = "room1"
config["viz"]["scene_name"] = "room1"
# Wandb is disabled; retain a scene/run-correct label in saved provenance.
config["wandb"]["name"] = "p7_bcgm_r1_full_room1_on_0_1999_r01"
