#!/usr/bin/env python3
"""Render a saved Phase 6 map from the exact five Phase 4 V2 camera poses.

This is a visualization-only saved-checkpoint path. It does not load a dataset,
compute metrics, or execute any online SLAM operation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.visualization.visualize_full_scene_v3a import render_native


FRAME_IDS = (0, 499, 999, 1499, 1999)
PARAM_KEYS = (
    "means3D", "rgb_colors", "unnorm_rotations", "logit_opacities",
    "log_scales", "semantic_colors",
)
REFERENCE_FILES = (
    "gt_rgb.png", "rendered_rgb.png", "rgb_comparison.png",
    "gt_depth.png", "rendered_depth.png", "depth_comparison.png",
    "gt_semantic.png", "rendered_semantic_raw.png",
    "rendered_semantic_recolored.png", "semantic_comparison.png",
)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(4 * 1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def render_depth_only(params: dict[str, np.ndarray], cameras: dict[str, dict[str, Any]], output: Path, device: str) -> dict[str, Any]:
    import cv2
    import torch
    import torch.nn.functional as functional
    from diff_gaussian_rasterization import GaussianRasterizer
    from utils.recon_helpers import setup_camera
    from utils.slam_helpers import get_depth_and_silhouette

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable for saved-map depth visualization")
    torch.cuda.set_device(torch.device(device))
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    means = torch.from_numpy(params["means3D"]).to(device)
    rotations = functional.normalize(torch.from_numpy(params["unnorm_rotations"]).to(device))
    opacities = torch.sigmoid(torch.from_numpy(params["logit_opacities"]).to(device))
    scales = torch.exp(torch.tile(torch.from_numpy(params["log_scales"]).to(device), (1, 3)))
    means2d = torch.zeros_like(means)
    records: dict[str, Any] = {}
    with torch.no_grad():
        for name, camera in cameras.items():
            w2c = torch.as_tensor(camera["world_to_camera_w2c"], dtype=torch.float32, device=device)
            settings = setup_camera(
                camera["resolution"][0], camera["resolution"][1],
                np.asarray(camera["intrinsics"]), np.asarray(camera["world_to_camera_w2c"]),
                camera["near_plane_m"], camera["far_plane_m"], device=device,
            )
            depth_colors = get_depth_and_silhouette(means, w2c, device=device)
            depth_render_vars = {
                "means3D": means,
                "colors_precomp": depth_colors,
                "rotations": rotations,
                "opacities": opacities,
                "scales": scales,
                "means2D": means2d,
            }
            rendered, _, _ = GaussianRasterizer(raster_settings=settings)(**depth_render_vars)
            torch.cuda.synchronize()
            raw = rendered[0].detach().cpu().numpy().astype(np.float32, copy=False)
            stem = output / name
            stem.parent.mkdir(parents=True, exist_ok=True)
            np.save(stem.with_suffix(".npy"), raw)
            normalized = np.clip(raw / 6.0, 0.0, 1.0)
            bgr = cv2.applyColorMap(np.rint(normalized * 255).astype(np.uint8), cv2.COLORMAP_JET)
            cv2.imwrite(str(stem.with_name(stem.name + "_common_0_6m.png")), bgr)
            records[name] = {
                "raw_depth_path": str(stem.with_suffix(".npy")),
                "display_path": str(stem.with_name(stem.name + "_common_0_6m.png")),
                "resolution_wh": camera["resolution"],
                "display_protocol": "OpenCV JET with fixed shared depth range [0,6] m, matching Phase 4 V2 convention.",
                "raw_min": float(np.nanmin(raw)),
                "raw_max": float(np.nanmax(raw)),
                "pixel_std": float(raw.std()),
            }
    return {
        "frames": records,
        "device_name": torch.cuda.get_device_name(torch.device(device)),
        "peak_gpu_allocated_bytes": int(torch.cuda.max_memory_allocated()),
        "peak_gpu_reserved_bytes": int(torch.cuda.max_memory_reserved()),
        "method": "Phase 4 eval_helpers depth/silhouette color pass; no GT, metrics, or dataset access.",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", type=Path, required=True)
    parser.add_argument("--phase4-v2-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--depth-only", action="store_true", help="Add Phase 4-compatible depth visualization without touching existing RGB/semantic output.")
    args = parser.parse_args()

    checkpoint = args.checkpoint.resolve()
    reference_root = args.phase4_v2_root.resolve()
    output = args.output.resolve()
    depth_output = output / "phase6_rendered" / "depth"
    if args.depth_only:
        if not output.is_dir():
            raise FileNotFoundError(f"Existing camera-matched output is required for depth-only mode: {output}")
        if depth_output.exists():
            raise FileExistsError(f"Refusing to overwrite depth output: {depth_output}")
    elif output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing to overwrite populated output: {output}")
    for frame_id in FRAME_IDS:
        source = reference_root / "frames" / f"frame_{frame_id:04d}"
        for filename in (*REFERENCE_FILES, "frame_metadata.json"):
            if not (source / filename).is_file():
                raise FileNotFoundError(source / filename)
    if not args.depth_only:
        output.mkdir(parents=True, exist_ok=True)
    camera_dir = output / "cameras" / "phase4_v2"
    reference_dir = output / "phase4_reference"
    if not args.depth_only:
        camera_dir.mkdir(parents=True, exist_ok=False)
        reference_dir.mkdir(parents=True, exist_ok=False)

    cameras: dict[str, dict[str, Any]] = {}
    camera_source_hashes: dict[str, str] = {}
    reference_hashes: dict[str, str] = {}
    for frame_id in FRAME_IDS:
        source_dir = reference_root / "frames" / f"frame_{frame_id:04d}"
        metadata_path = source_dir / "frame_metadata.json"
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        name = f"frame_{frame_id:04d}"
        size = metadata["image_dimensions_wh"]
        if size != [1200, 680]:
            raise ValueError(f"Unexpected Phase 4 V2 image size for {name}: {size}")
        w2c = np.asarray(metadata["estimated_w2c"], dtype=np.float64)
        intrinsics = np.asarray(metadata["intrinsics"], dtype=np.float64)
        if w2c.shape != (4, 4) or intrinsics.shape != (3, 3):
            raise ValueError(f"Malformed Phase 4 camera metadata for {name}")
        if not np.isfinite(w2c).all() or not np.isfinite(intrinsics).all():
            raise ValueError(f"Non-finite Phase 4 camera metadata for {name}")
        camera_file = camera_dir / f"{name}.json"
        if args.depth_only:
            if not camera_file.is_file() or sha256(camera_file) != sha256(metadata_path):
                raise RuntimeError(f"Stored exact Phase 4 V2 camera metadata missing/different: {camera_file}")
            camera_source_hashes[name] = sha256(camera_file)
        else:
            shutil.copyfile(metadata_path, camera_file)
            camera_source_hashes[name] = sha256(camera_file)
        cameras[name] = {
            "view_name": name,
            "resolution": size,
            "world_to_camera_w2c": w2c.tolist(),
            "camera_to_world_c2w": np.linalg.inv(w2c).tolist(),
            "intrinsics": intrinsics.tolist(),
            "near_plane_m": 0.01,
            "far_plane_m": 100.0,
            "camera_source": str(metadata_path),
            "camera_source_sha256": camera_source_hashes[name],
        }
        if not args.depth_only:
            frame_output = reference_dir / name
            frame_output.mkdir(parents=True, exist_ok=False)
            for filename in REFERENCE_FILES:
                src = source_dir / filename
                dst = frame_output / filename
                shutil.copyfile(src, dst)
                reference_hashes[f"{name}/{filename}"] = sha256(dst)

    with np.load(checkpoint, allow_pickle=False) as archive:
        missing = sorted(set(PARAM_KEYS) - set(archive.files))
        if missing:
            raise KeyError(f"Checkpoint missing required Gaussian arrays: {missing}")
        params = {key: np.asarray(archive[key]).copy() for key in PARAM_KEYS}
    before = sha256(checkpoint)
    if args.depth_only:
        depth_result = render_depth_only(params, cameras, depth_output, args.device)
        if sha256(checkpoint) != before:
            raise RuntimeError("Saved Phase 6 checkpoint hash changed during depth visualization")
        output_manifest = {
            "source_checkpoint": str(checkpoint),
            "source_checkpoint_sha256_before_after": before,
            "camera_source_sha256": camera_source_hashes,
            "depth_result": depth_result,
            "evaluation_or_metric_computation": False,
            "slam_tracking_mapping_optimization": False,
        }
        depth_output.mkdir(parents=True, exist_ok=True)
        (depth_output / "render_metadata.json").write_text(json.dumps(output_manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(output_manifest, indent=2, sort_keys=True))
        return 0

    renderer_result = render_native(
        params, cameras, output / "phase6_rendered", args.device,
        view_names=tuple(cameras),
    )
    after = sha256(checkpoint)
    if before != after:
        raise RuntimeError("Saved Phase 6 checkpoint hash changed during visualization")

    records = {
        "source_checkpoint": str(checkpoint),
        "source_checkpoint_sha256_before": before,
        "source_checkpoint_sha256_after": after,
        "phase4_v2_source_root": str(reference_root),
        "frame_ids": list(FRAME_IDS),
        "camera_source_sha256": camera_source_hashes,
        "copied_phase4_reference_sha256": reference_hashes,
        "camera_convention": "Exact per-frame estimated relative-w2c matrices and intrinsics copied from the validated Phase 4 V2 frame metadata; native setup_camera defaults near=0.01, far=100.",
        "rendered_modalities": ["saved Phase 6 RGB Gaussian color", "saved Phase 6 learned semantic colors"],
        "evaluation_or_metric_computation": False,
        "slam_tracking_mapping_optimization": False,
        "renderer_result": renderer_result,
    }
    (output / "render_metadata.json").write_text(
        json.dumps(records, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(records, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
