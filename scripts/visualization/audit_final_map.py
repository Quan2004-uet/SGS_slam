#!/usr/bin/env python3
"""Read-only diagnostics for a saved SGS-SLAM map and its visualization cameras."""

from __future__ import annotations

import argparse
import csv
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image


PERCENTILES = [0, 0.1, 1, 5, 25, 50, 75, 95, 99, 99.9, 100]
REPRESENTATIVE_FRAMES = [0, 499, 999, 1499, 1999]


def distribution(values: np.ndarray) -> dict[str, object]:
    finite = np.isfinite(values)
    selected = values[finite]
    return {
        "count": int(values.size),
        "finite_count": int(finite.sum()),
        "nonfinite_count": int((~finite).sum()),
        "mean": float(selected.mean(dtype=np.float64)),
        "std": float(selected.std(dtype=np.float64)),
        "percentiles": {
            str(value): float(result)
            for value, result in zip(PERCENTILES, np.percentile(selected, PERCENTILES))
        },
    }


def load_palette(dataset_root: Path) -> tuple[dict[int, tuple[int, int, int]], dict[int, int]]:
    palette: dict[int, tuple[int, int, int]] = {}
    observed_pixels: dict[int, int] = {}
    for frame_id in REPRESENTATIVE_FRAMES:
        ids = np.asarray(Image.open(dataset_root / "semantic_ids" / f"semantic_id{frame_id:06d}.png"))
        colors = np.asarray(
            Image.open(dataset_root / "semantic_colors" / f"semantic_color{frame_id:06d}.png").convert("RGB")
        )
        for value in np.unique(ids):
            class_id = int(value)
            unique_colors = np.unique(colors[ids == value].reshape(-1, 3), axis=0)
            if len(unique_colors) != 1:
                raise ValueError(f"Class {class_id} has multiple colors in frame {frame_id}")
            rgb = tuple(int(channel) for channel in unique_colors[0])
            if class_id in palette and palette[class_id] != rgb:
                raise ValueError(f"Class {class_id} palette conflict: {palette[class_id]} versus {rgb}")
            palette[class_id] = rgb
            observed_pixels[class_id] = observed_pixels.get(class_id, 0) + int((ids == value).sum())
    return palette, observed_pixels


def quaternion_to_rotation(wxyz: np.ndarray) -> np.ndarray:
    quaternions = wxyz.astype(np.float64, copy=True)
    norms = np.linalg.norm(quaternions, axis=1, keepdims=True)
    quaternions /= norms
    w, x, y, z = quaternions.T
    rotations = np.empty((len(quaternions), 3, 3), dtype=np.float64)
    rotations[:, 0, 0] = 1 - 2 * (y * y + z * z)
    rotations[:, 0, 1] = 2 * (x * y - z * w)
    rotations[:, 0, 2] = 2 * (x * z + y * w)
    rotations[:, 1, 0] = 2 * (x * y + z * w)
    rotations[:, 1, 1] = 1 - 2 * (x * x + z * z)
    rotations[:, 1, 2] = 2 * (y * z - x * w)
    rotations[:, 2, 0] = 2 * (x * z - y * w)
    rotations[:, 2, 1] = 2 * (y * z + x * w)
    rotations[:, 2, 2] = 1 - 2 * (x * x + y * y)
    return rotations


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--params", required=True, type=Path)
    parser.add_argument("--visualization", required=True, type=Path)
    parser.add_argument("--dataset-root", required=True, type=Path)
    parser.add_argument("--class-mapping", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)

    with np.load(args.params, allow_pickle=False) as archive:
        params = {key: np.asarray(archive[key]) for key in archive.files}

    means = params["means3D"]
    log_scales = params["log_scales"].reshape(-1)
    scales = np.exp(log_scales.astype(np.float64))
    opacity_logits = params["logit_opacities"].reshape(-1).astype(np.float64)
    opacities = 1.0 / (1.0 + np.exp(-opacity_logits))
    rotations = params["unnorm_rotations"]
    rotation_norms = np.linalg.norm(rotations.astype(np.float64), axis=1)
    rgb = params["rgb_colors"]
    semantic_rgb = params["semantic_colors"]
    semantic_ids = params["semantic_ids"].reshape(-1).astype(np.int64)
    center = means.mean(axis=0, dtype=np.float64)
    radii = np.linalg.norm(means.astype(np.float64) - center, axis=1)

    palette, observed_pixels = load_palette(args.dataset_root)
    present_ids, primitive_counts = np.unique(semantic_ids, return_counts=True)
    missing_palette = sorted(set(int(value) for value in present_ids) - set(palette))
    if missing_palette:
        raise ValueError(f"No verified GT palette for saved semantic IDs: {missing_palette}")

    mapping_json = json.loads(args.class_mapping.read_text(encoding="utf-8"))
    class_names = {int(item["id"]): item["name"] for item in mapping_json["classes"]}
    class_names[0] = "unknown/background"
    palette_ids = sorted(palette)
    palette_array = np.asarray([palette[value] for value in palette_ids], dtype=np.float64) / 255.0
    palette_id_array = np.asarray(palette_ids, dtype=np.int64)

    agreement_count = 0
    own_errors = np.empty(len(semantic_ids), dtype=np.float32)
    chunk_size = 100_000
    for start in range(0, len(semantic_ids), chunk_size):
        stop = min(start + chunk_size, len(semantic_ids))
        chunk = semantic_rgb[start:stop].astype(np.float64)
        distances = np.sum((chunk[:, None, :] - palette_array[None, :, :]) ** 2, axis=2)
        nearest_ids = palette_id_array[np.argmin(distances, axis=1)]
        agreement_count += int((nearest_ids == semantic_ids[start:stop]).sum())
        own = np.asarray([palette[int(value)] for value in semantic_ids[start:stop]], dtype=np.float64) / 255.0
        own_errors[start:stop] = np.linalg.norm(chunk - own, axis=1)

    semantic_table: list[dict[str, object]] = []
    for class_id, count in zip(present_ids, primitive_counts):
        class_id_int = int(class_id)
        mask = semantic_ids == class_id_int
        class_colors = semantic_rgb[mask].astype(np.float64)
        canonical = palette[class_id_int]
        canonical_normalized = np.asarray(canonical, dtype=np.float64) / 255.0
        nearest_own = np.linalg.norm(class_colors - canonical_normalized, axis=1)
        semantic_table.append({
            "class_id": class_id_int,
            "class_name": class_names.get(class_id_int, "unresolved"),
            "rgb_palette": list(canonical),
            "primitive_count": int(count),
            "primitive_fraction": float(count / len(semantic_ids)),
            "mean_learned_rgb": class_colors.mean(axis=0).tolist(),
            "median_learned_rgb": np.median(class_colors, axis=0).tolist(),
            "mean_l2_to_own_palette": float(nearest_own.mean()),
            "median_l2_to_own_palette": float(np.median(nearest_own)),
            "gt_palette_pixels_in_representative_frames": observed_pixels[class_id_int],
            "interpretation": (
                "ignore/background in released mIoU" if class_id_int == 0
                else "Replica class name verified from info_semantic.json; RGB verified from aligned GT semantic ID/color PNGs"
            ),
        })

    projected: dict[str, object] = {}
    for camera_path in sorted((args.visualization / "cameras").glob("*.json")):
        camera = json.loads(camera_path.read_text(encoding="utf-8"))
        extrinsic = np.asarray(camera["world_to_camera_extrinsic"], dtype=np.float64)
        intrinsic = np.asarray(camera["intrinsic_matrix"], dtype=np.float64)
        depth = means.astype(np.float64) @ extrinsic[2, :3] + extrinsic[2, 3]
        approximate_sigma_px = intrinsic[0, 0] * scales / depth
        visible = depth > camera["near_clip"]
        values = approximate_sigma_px[visible]
        high_opacity = opacities[visible] >= 0.5
        projected[camera["viewpoint"]] = {
            "camera_distance": camera["camera_distance"],
            "near_clip": camera["near_clip"],
            "far_clip": camera["far_clip"],
            "visible_center_count": int(visible.sum()),
            "approx_projected_sigma_pixels": distribution(values),
            "count_sigma_gt_5px": int((values > 5).sum()),
            "count_sigma_gt_10px": int((values > 10).sum()),
            "count_sigma_gt_20px": int((values > 20).sum()),
            "count_sigma_gt_50px": int((values > 50).sum()),
            "count_sigma_gt_100px": int((values > 100).sum()),
            "count_opacity_ge_0_5_and_sigma_gt_20px": int((high_opacity & (values > 20)).sum()),
            "caveat": "focal*isotropic_scale/depth is a diagnostic 1-sigma approximation, not the rasterizer's exact EWA footprint",
        }

    camera_quaternions = params["cam_unnorm_rots"][0].T
    camera_translations = params["cam_trans"][0].T
    camera_rotations = quaternion_to_rotation(camera_quaternions)
    estimated_w2c = np.repeat(np.eye(4)[None], len(camera_quaternions), axis=0)
    estimated_w2c[:, :3, :3] = camera_rotations
    estimated_w2c[:, :3, 3] = camera_translations
    estimated_centers = np.linalg.inv(estimated_w2c)[:, :3, 3]

    diagnostics = {
        "params_path": str(args.params.resolve()),
        "params_file_size_bytes": args.params.stat().st_size,
        "gaussian_count": int(len(means)),
        "array_schema": {
            key: {"shape": list(value.shape), "dtype": str(value.dtype), "nbytes": int(value.nbytes)}
            for key, value in params.items()
        },
        "nonfinite_counts": {
            key: int((~np.isfinite(value)).sum())
            for key, value in params.items()
            if np.issubdtype(value.dtype, np.number)
        },
        "position": {
            "min_xyz": means.min(axis=0).astype(float).tolist(),
            "max_xyz": means.max(axis=0).astype(float).tolist(),
            "centroid_xyz": center.tolist(),
            "extent_xyz": (means.max(axis=0) - means.min(axis=0)).astype(float).tolist(),
            "radius_from_centroid": distribution(radii),
            "count_beyond_radius_p99_9": int((radii > np.percentile(radii, 99.9)).sum()),
            "spatial_outlier_definition": "diagnostic only: center radius greater than its 99.9th percentile; not classified invalid",
        },
        "log_scale": distribution(log_scales.astype(np.float64)),
        "scale_meters": distribution(scales),
        "scale_counts": {
            "gt_0_01m": int((scales > 0.01).sum()),
            "gt_0_02m": int((scales > 0.02).sum()),
            "gt_0_05m": int((scales > 0.05).sum()),
            "gt_0_10m": int((scales > 0.10).sum()),
            "gt_0_15m": int((scales > 0.15).sum()),
        },
        "opacity_logit": distribution(opacity_logits),
        "opacity": distribution(opacities),
        "opacity_counts": {
            "lt_0_01": int((opacities < 0.01).sum()),
            "lt_0_05": int((opacities < 0.05).sum()),
            "ge_0_5": int((opacities >= 0.5).sum()),
            "ge_0_9": int((opacities >= 0.9).sum()),
        },
        "rotation_norm": distribution(rotation_norms),
        "rgb_colors": {
            "per_channel": [distribution(rgb[:, index].astype(np.float64)) for index in range(3)],
            "values_below_0": int((rgb < 0).sum()),
            "values_above_1": int((rgb > 1).sum()),
            "primitive_count_with_any_channel_outside_0_1": int(((rgb < 0) | (rgb > 1)).any(axis=1).sum()),
        },
        "semantic_colors": {
            "per_channel": [distribution(semantic_rgb[:, index].astype(np.float64)) for index in range(3)],
            "values_below_0": int((semantic_rgb < 0).sum()),
            "values_above_1": int((semantic_rgb > 1).sum()),
            "primitive_count_with_any_channel_outside_0_1": int(((semantic_rgb < 0) | (semantic_rgb > 1)).any(axis=1).sum()),
            "nearest_verified_palette_agreement_with_fixed_semantic_id": float(agreement_count / len(semantic_ids)),
            "l2_distance_to_own_verified_palette": distribution(own_errors.astype(np.float64)),
            "verified_palette_frames": REPRESENTATIVE_FRAMES,
            "verified_palette_class_count": len(palette),
        },
        "semantic_mapping": semantic_table,
        "projected_footprint_diagnostics": projected,
        "camera_state": {
            "intrinsics": params["intrinsics"].astype(float).tolist(),
            "first_frame_w2c": params["w2c"].astype(float).tolist(),
            "estimated_pose_count": int(camera_quaternions.shape[0]),
            "gt_pose_count": int(params["gt_w2c_all_frames"].shape[0]),
            "all_estimated_camera_parameters_finite": bool(np.isfinite(camera_quaternions).all() and np.isfinite(camera_translations).all()),
            "all_gt_poses_finite": bool(np.isfinite(params["gt_w2c_all_frames"]).all()),
            "estimated_camera_center_min_xyz": estimated_centers.min(axis=0).tolist(),
            "estimated_camera_center_max_xyz": estimated_centers.max(axis=0).tolist(),
            "representative_frames": REPRESENTATIVE_FRAMES,
        },
    }

    diagnostics_path = args.output / "gaussian_diagnostics.json"
    diagnostics_path.write_text(json.dumps(diagnostics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (args.output / "semantic_mapping.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(semantic_table[0].keys()))
        writer.writeheader()
        writer.writerows(semantic_table)
    print(json.dumps({
        "diagnostics": str(diagnostics_path),
        "gaussian_count": len(means),
        "semantic_classes": len(semantic_table),
        "palette_agreement": agreement_count / len(semantic_ids),
    }, indent=2))


if __name__ == "__main__":
    main()
