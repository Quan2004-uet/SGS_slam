"""Phase 7 Gate 2 single-arm bounded BCGM-on experiment."""
from copy import deepcopy

from configs.replica.slam import config as phase4_cpu_offload_config

config = deepcopy(phase4_cpu_offload_config)
config["workdir"] = "/home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica"
config["run_name"] = "p7_bcgm_g2_room0_on_0_499_r01"
config["use_wandb"] = False
config["data"]["basedir"] = "/home/robot/research/SGS_slam/data/Replica"
config["data"]["gradslam_data_cfg"] = "/home/robot/research/SGS_slam_phase4_multiscene/configs/data/replica.yaml"
config["data"]["sequence"] = "room0"
config["data"]["start"] = 0
config["data"]["end"] = 500
config["data"]["stride"] = 1
config["data"]["num_frames"] = 500
config["bcgm"] = {
    "enabled": True,
    "max_new_gaussians_per_event": 9000,
    "max_gaussians": 4500000,
}
