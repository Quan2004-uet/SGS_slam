"""Phase 7 source with BCGM disabled; load with the Phase 7 source root first."""
from copy import deepcopy

from configs.replica.slam import config as phase4_config

config = deepcopy(phase4_config)
config["workdir"] = "/home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica"
config["run_name"] = "p7_bcgm_g1b_room0_off_0_99_r01"
config["use_wandb"] = False
config["data"]["basedir"] = "/home/robot/research/SGS_slam/data/Replica"
config["data"]["gradslam_data_cfg"] = "/home/robot/research/SGS_slam_phase4_multiscene/configs/data/replica.yaml"
config["data"]["sequence"] = "room0"
config["data"]["start"] = 0
config["data"]["end"] = 100
config["data"]["stride"] = 1
config["data"]["num_frames"] = 100
config["bcgm"] = {"enabled": False}
