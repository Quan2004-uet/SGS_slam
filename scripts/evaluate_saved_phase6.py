"""Evaluate a completed Phase 6 Replica checkpoint without rerunning SLAM.

The evaluator deliberately imports the renderer/evaluation stack only inside
``main``. Importing this module for CPU/static validation does not initialize
CUDA. Use a fresh, non-existing ``--output-dir`` for each evaluation attempt.
"""

import argparse
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
PHASE6_ROOT = (ROOT / "results/runtime_artifacts/phase6_bam").resolve()
EXPECTED_FRAMES = tuple([0] + list(range(4, 2000, 5)))
GAUSSIAN_TENSOR_KEYS = (
    "means3D", "rgb_colors", "unnorm_rotations", "logit_opacities",
    "log_scales", "semantic_colors", "cam_unnorm_rots", "cam_trans",
)


def validate_evaluation_paths(checkpoint, output_dir, phase6_root=PHASE6_ROOT):
    checkpoint = Path(checkpoint).resolve(strict=True)
    output_dir = Path(output_dir).resolve(strict=False)
    phase6_root = Path(phase6_root).resolve(strict=True)
    if checkpoint.name != "params.npz" or checkpoint.parent.parent != phase6_root:
        raise ValueError("Checkpoint must be params.npz directly inside one Phase 6 run directory")
    if not checkpoint.is_file():
        raise FileNotFoundError(checkpoint)
    if output_dir == checkpoint.parent or checkpoint.parent in output_dir.parents:
        raise ValueError("Evaluation output must not be inside the immutable SLAM run directory")
    if phase6_root not in output_dir.parents:
        raise ValueError("Evaluation output must remain below the Phase 6 artifact root")
    if output_dir.exists():
        raise FileExistsError(f"Refusing to reuse evaluation output: {output_dir}")
    return checkpoint, output_dir


def expected_eval_frame_ids(num_frames=2000, eval_every=5):
    if num_frames != 2000 or eval_every != 5:
        raise ValueError("This saved-state evaluator is frozen to the Phase 4 E4 2000/5 protocol")
    return tuple([0] + list(range(eval_every - 1, num_frames, eval_every)))


def validate_evaluation_outputs(output_dir):
    import numpy as np

    output_dir = Path(output_dir)
    values_by_file = {}
    for filename in ("psnr.txt", "ssim.txt", "lpips.txt", "l1.txt", "rmse.txt", "miou.txt"):
        values = np.atleast_1d(np.loadtxt(output_dir / filename))
        if values.size != 401 or not np.isfinite(values).all():
            raise ValueError(f"Invalid E4 metric output {filename}: expected 401 finite values")
        values_by_file[filename] = values
    for subdir in ("rendered_rgb", "rendered_depth", "rendered_seg"):
        image_ids = sorted(
            int(path.stem.split("_")[-1])
            for path in (output_dir / subdir).glob("gs_*.png")
        )
        if image_ids != list(EXPECTED_FRAMES):
            raise ValueError(f"Saved-state {subdir} frame IDs do not match E4 schedule")
    return {
        "evaluated_image_frame_count": 401,
        "evaluated_frame_ids": list(EXPECTED_FRAMES),
        "mean_PSNR_dB": float(values_by_file["psnr.txt"].mean()),
        "mean_MS_SSIM": float(values_by_file["ssim.txt"].mean()),
        "mean_LPIPS_Alex": float(values_by_file["lpips.txt"].mean()),
        "mean_depth_RMSE_m": float(values_by_file["rmse.txt"].mean()),
        "mean_depth_L1_m": float(values_by_file["l1.txt"].mean()),
        "mean_semantic_color_mIoU": float(values_by_file["miou.txt"].mean()),
        "aggregation": "unweighted mean of released per-view metric values",
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path,
                        help="effective_config.json saved beside params.npz")
    parser.add_argument("--output-dir", required=True, type=Path)
    args = parser.parse_args(argv)

    checkpoint, output_dir = validate_evaluation_paths(args.checkpoint, args.output_dir)
    config_path = args.config.resolve(strict=True)
    if config_path.parent != checkpoint.parent or config_path.name != "effective_config.json":
        raise ValueError("Config snapshot must be effective_config.json beside the saved checkpoint")
    config = json.loads(config_path.read_text(encoding="utf-8"))
    expected_run_dir = (Path(config["workdir"]) / config["run_name"]).resolve()
    if checkpoint.parent != expected_run_dir:
        raise ValueError("Checkpoint does not correspond to the supplied frozen run configuration")
    if config.get("phase6_variant") != "V-A2-FULL-0-1999":
        raise ValueError("Saved-state evaluator only accepts the frozen full-scene V-A2 configuration")
    if config["data"].get("start") != 0 or config["data"].get("end") != 2000 or config["data"].get("num_frames") != 2000:
        raise ValueError("Saved config is not bounded to exactly 2000 frames")
    if config["eval_every"] != 5:
        raise ValueError("Saved config does not use the frozen E4 evaluation cadence")
    if expected_eval_frame_ids() != EXPECTED_FRAMES:
        raise AssertionError("Internal E4 sampling definition mismatch")

    # Everything below is intentionally the existing released GPU evaluator;
    # it consumes only saved params.npz and dataset observations, never SLAM.
    import numpy as np
    import torch
    import torch.nn.functional as F
    from datasets.gradslam_datasets import load_dataset_config
    from scripts.slam import eval, get_dataset
    from utils.eval_helpers import align
    from utils.slam_external import build_rotation

    device = torch.device(config["primary_device"])
    if device.type != "cuda" or not torch.cuda.is_available():
        raise RuntimeError("Saved-state E4 evaluation requires the configured CUDA device")
    dataset_cfg = load_dataset_config(config["data"]["gradslam_data_cfg"])
    data = config["data"]
    dataset = get_dataset(
        config_dict=dataset_cfg,
        basedir=data["basedir"], sequence=data["sequence"],
        start=0, end=2000, stride=1,
        desired_height=data["desired_image_height"], desired_width=data["desired_image_width"],
        device=device, relative_pose=True, load_semantics=True,
        num_semantic_classes=data["num_semantic_classes"],
    )
    if len(dataset) != 2000:
        raise ValueError(f"Expected 2000 Replica room0 frames, got {len(dataset)}")

    with np.load(checkpoint, allow_pickle=False) as archive:
        required = set(GAUSSIAN_TENSOR_KEYS) | {
            "w2c", "gt_w2c_all_frames", "intrinsics", "keyframe_time_indices",
            "semantic_ids", "semantic_colors",
        }
        missing = sorted(required.difference(archive.files))
        if missing:
            raise ValueError(f"Saved checkpoint is missing E4 fields: {missing}")
        params = {
            key: torch.from_numpy(np.ascontiguousarray(archive[key])).to(device)
            for key in GAUSSIAN_TENSOR_KEYS
        }
        first_w2c = np.array(archive["w2c"], copy=True)
        gt_w2c = np.array(archive["gt_w2c_all_frames"], copy=True)
        keyframes = np.array(archive["keyframe_time_indices"], copy=True)
        semantic_ids = np.array(archive["semantic_ids"], copy=True)
        if (gt_w2c.shape != (2000, 4, 4)
                or params["cam_trans"].shape != (1, 3, 2000)
                or params["cam_unnorm_rots"].shape != (1, 4, 2000)):
            raise ValueError("Saved trajectory schema is not a 2000-frame checkpoint")
        if (params["means3D"].ndim != 2 or params["means3D"].shape[1] != 3
                or params["semantic_colors"].shape != params["means3D"].shape
                or semantic_ids.ndim != 1 or semantic_ids.shape[0] != params["means3D"].shape[0]):
            raise ValueError("Saved semantic model arrays do not align with Gaussian geometry")
        if keyframes.ndim != 1 or keyframes.size == 0 or keyframes[-1] != 1999:
            raise ValueError("Saved keyframe history does not terminate at frame 1999")
        if not np.isfinite(gt_w2c).all() or not np.isfinite(first_w2c).all():
            raise ValueError("Saved camera metadata contains non-finite values")

    output_dir.mkdir(parents=True, exist_ok=False)
    (output_dir / "evaluated_frame_ids.json").write_text(json.dumps({
        "sampling_rule": "{0} union {5k-1 | k=1..400}",
        "count": 401,
        "frame_ids": list(EXPECTED_FRAMES),
        "metric_implementation": "utils.eval_helpers.eval from the frozen source checkout",
    }, indent=2) + "\n", encoding="utf-8")

    with torch.no_grad():
        eval(
            dataset, params, 2000, str(output_dir),
            sil_thres=config["mapping"]["sil_thres"],
            mapping_iters=config["mapping"]["num_iters"],
            add_new_gaussians=config["mapping"]["add_new_gaussians"],
            device=device, load_semantics=True, eval_every=5, save_frames=True,
        )
    aggregate = validate_evaluation_outputs(output_dir)

    normalized = F.normalize(params["cam_unnorm_rots"][0].T, dim=1)
    estimated = torch.eye(4, device=device).repeat(2000, 1, 1)
    estimated[0] = torch.as_tensor(first_w2c, device=device, dtype=torch.float32)
    estimated[1:, :3, :3] = build_rotation(normalized[1:], device=device)
    estimated[1:, :3, 3] = params["cam_trans"][0, :, 1:].T
    gt_points = gt_w2c[:, :3, 3].T
    est_points = estimated[:, :3, 3].detach().cpu().numpy().T
    _, _, errors = align(gt_points, est_points)
    trajectory = {
        "frame_count": 2000,
        "alignment": "Horn rigid rotation+translation, no scale; saved relative w2c",
        "released_ate_mean_m": float(np.mean(errors)),
        "supplementary_true_ate_rmse_m": float(np.sqrt(np.mean(np.square(errors)))),
    }
    (output_dir / "trajectory_metrics.json").write_text(
        json.dumps(trajectory, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    aggregate.update(trajectory)
    (output_dir / "aggregate_metrics.json").write_text(
        json.dumps(aggregate, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
