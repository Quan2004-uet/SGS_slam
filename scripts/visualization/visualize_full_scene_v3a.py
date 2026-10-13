#!/usr/bin/env python3
"""Bounded, deterministic Gate V3A visualization of the final SGS-SLAM map.

This utility is visualization-only. It reads the immutable final params.npz,
uses the repository-native renderer for original RGB/raw semantic splats, and
uses a deterministic sampled Gaussian-center projection for geometry,
categorical semantic-ID, class-wise, and trajectory diagnostics. It never
writes Gaussian parameters or evaluation metrics.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import os
import platform
import resource
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

VIEW_NAMES = ("trajectory_observed", "room_overview", "top_oblique")
CLASS_NAMES = ("wall", "floor", "ceiling", "sofa", "chair", "table", "rug", "blinds")
SAMPLE_SEED = 20261013
SAMPLE_COUNT = 650_000


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--rgb-ply", required=True, type=Path)
    parser.add_argument("--semantic-ply", required=True, type=Path)
    parser.add_argument("--semantic-mapping", required=True, type=Path)
    parser.add_argument("--v1-root", required=True, type=Path)
    parser.add_argument("--v2-root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--width", type=int, default=960)
    parser.add_argument("--height", type=int, default=540)
    parser.add_argument("--device", default="cuda:0")
    parser.add_argument("--skip-native-render", action="store_true")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def hash_array(array: np.ndarray) -> str:
    digest = hashlib.sha256()
    digest.update(np.ascontiguousarray(array).view(np.uint8))
    return digest.hexdigest()


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()


def sigmoid(x: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-x))


def quaternion_to_rotation(q: np.ndarray) -> np.ndarray:
    q = q.astype(np.float64, copy=True)
    q /= np.linalg.norm(q, axis=1, keepdims=True)
    w, x, y, z = q.T
    rotation = np.empty((len(q), 3, 3), dtype=np.float64)
    rotation[:, 0, 0] = 1 - 2 * (y * y + z * z)
    rotation[:, 0, 1] = 2 * (x * y - w * z)
    rotation[:, 0, 2] = 2 * (x * z + w * y)
    rotation[:, 1, 0] = 2 * (x * y + w * z)
    rotation[:, 1, 1] = 1 - 2 * (x * x + z * z)
    rotation[:, 1, 2] = 2 * (y * z - w * x)
    rotation[:, 2, 0] = 2 * (x * z - w * y)
    rotation[:, 2, 1] = 2 * (y * z + w * x)
    rotation[:, 2, 2] = 1 - 2 * (x * x + y * y)
    return rotation


def trajectory_from_params(q_saved: np.ndarray, t_saved: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    q = np.asarray(q_saved)[0].T
    translation = np.asarray(t_saved)[0].T.astype(np.float64)
    rotations = quaternion_to_rotation(q)
    w2cs = np.repeat(np.eye(4, dtype=np.float64)[None], len(q), axis=0)
    w2cs[:, :3, :3] = rotations
    w2cs[:, :3, 3] = translation
    c2w_rotations = np.transpose(rotations, (0, 2, 1))
    centers = -np.einsum("nij,nj->ni", c2w_rotations, translation)
    forward = c2w_rotations[:, :, 2]
    camera_down = c2w_rotations[:, :, 1]
    return w2cs, centers, forward, camera_down


def load_palette(path: Path) -> tuple[dict[int, tuple[int, int, int]], dict[int, str], dict[str, int]]:
    palette: dict[int, tuple[int, int, int]] = {}
    names: dict[int, str] = {}
    reverse: dict[str, int] = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            class_id = int(row["class_id"])
            rgb = tuple(int(value) for value in ast.literal_eval(row["rgb_palette"]))
            if len(rgb) != 3:
                raise ValueError(f"Invalid palette row for ID {class_id}")
            palette[class_id] = rgb
            names[class_id] = row["class_name"]
            reverse[row["class_name"]] = class_id
    return palette, names, reverse


def look_at_w2c(eye: np.ndarray, target: np.ndarray, gravity_up: np.ndarray) -> np.ndarray:
    forward = target - eye
    forward /= np.linalg.norm(forward)
    right = np.cross(forward, gravity_up)
    right /= np.linalg.norm(right)
    true_up = np.cross(right, forward)
    true_up /= np.linalg.norm(true_up)
    down = -true_up
    rotation = np.stack([right, down, forward])
    result = np.eye(4, dtype=np.float64)
    result[:3, :3] = rotation
    result[:3, 3] = -rotation @ eye
    return result


def intrinsic_for_fov(width: int, height: int, fov_y: float) -> np.ndarray:
    fy = height / (2 * math.tan(math.radians(fov_y) / 2))
    return np.array([[fy, 0, width / 2], [0, fy, height / 2], [0, 0, 1]], dtype=np.float64)


def camera_record(
    name: str,
    w2c: np.ndarray,
    intrinsic: np.ndarray,
    width: int,
    height: int,
    means_probe: np.ndarray,
    rationale: str,
    selection: dict[str, Any],
) -> dict[str, Any]:
    c2w = np.linalg.inv(w2c)
    cam = (w2c[:3, :3] @ means_probe.T).T + w2c[:3, 3]
    positive = cam[:, 2] > 0.01
    positive_depth = cam[positive, 2]
    if len(positive_depth) == 0:
        raise ValueError(f"Camera {name} sees no probe centers")
    near = max(0.01, float(np.quantile(positive_depth, 0.001)) * 0.25)
    far = max(near + 1.0, float(np.quantile(positive_depth, 0.999)) * 1.35)
    projected = np.zeros(len(cam), dtype=bool)
    indices = np.flatnonzero(positive)
    u = intrinsic[0, 0] * cam[positive, 0] / positive_depth + intrinsic[0, 2]
    v = intrinsic[1, 1] * cam[positive, 1] / positive_depth + intrinsic[1, 2]
    projected[indices] = (u >= 0) & (u < width) & (v >= 0) & (v < height) & (positive_depth <= far)
    fov_x = math.degrees(2 * math.atan(width / (2 * intrinsic[0, 0])))
    fov_y = math.degrees(2 * math.atan(height / (2 * intrinsic[1, 1])))
    return {
        "view_name": name,
        "camera_position": c2w[:3, 3].tolist(),
        "camera_target": (c2w[:3, 3] + c2w[:3, 2]).tolist(),
        "world_to_camera_w2c": w2c.tolist(),
        "camera_to_world_c2w": c2w.tolist(),
        "intrinsics": intrinsic.tolist(),
        "fov_x_degrees": fov_x,
        "fov_y_degrees": fov_y,
        "near_plane_m": near,
        "far_plane_m": far,
        "resolution": [width, height],
        "coordinate_convention": "First-frame-relative map coordinates; OpenCV camera axes +x right, +y down, +z forward; w2c maps world to camera.",
        "selection_rationale": rationale,
        "selection_evidence": selection,
        "probe_center_count": int(len(means_probe)),
        "probe_center_visible_fraction": float(projected.mean()),
        "warning": "A virtual camera is not photometrically validated merely because projected centers are visible.",
    }


def build_cameras(
    means: np.ndarray,
    semantic_ids: np.ndarray,
    saved_intrinsic: np.ndarray,
    original_size: tuple[int, int],
    w2cs: np.ndarray,
    trajectory_centers: np.ndarray,
    forwards: np.ndarray,
    camera_down: np.ndarray,
    width: int,
    height: int,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    floor_median = np.median(means[semantic_ids == 40], axis=0).astype(np.float64)
    ceiling_median = np.median(means[semantic_ids == 31], axis=0).astype(np.float64)
    gravity_down = camera_down.mean(axis=0)
    gravity_down /= np.linalg.norm(gravity_down)
    if np.dot(floor_median - ceiling_median, gravity_down) < 0:
        gravity_down *= -1
    gravity_up = -gravity_down
    concentration = float(np.mean(camera_down @ gravity_down))
    separation = float(np.dot(floor_median - ceiling_median, gravity_down))

    probe = means[::20].astype(np.float64)
    target = np.median(probe, axis=0)
    to_target = target - trajectory_centers
    distances = np.linalg.norm(to_target, axis=1)
    alignment = np.einsum("ij,ij->i", to_target / np.maximum(distances[:, None], 1e-9), forwards)
    score = alignment - 0.03 * distances
    observed_frame = int(np.argmax(score))

    original_width, original_height = original_size
    observed_intrinsic = saved_intrinsic.astype(np.float64).copy()
    observed_intrinsic[0, :] *= width / original_width
    observed_intrinsic[1, :] *= height / original_height

    observed_w2c = w2cs[observed_frame]
    observed_eye = trajectory_centers[observed_frame]
    observed_forward = forwards[observed_frame]
    overview_eye = observed_eye - 0.85 * observed_forward + 0.35 * gravity_up
    overview_target = target + 0.10 * gravity_up
    overview_w2c = look_at_w2c(overview_eye, overview_target, gravity_up)

    centered = probe - target
    horizontal = centered - np.outer(centered @ gravity_down, gravity_down)
    covariance = horizontal.T @ horizontal / len(horizontal)
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    major = eigenvectors[:, -1]
    major -= gravity_down * np.dot(major, gravity_down)
    major /= np.linalg.norm(major)
    if np.dot(major, observed_eye - target) < 0:
        major *= -1
    top_eye = target + 3.2 * gravity_up + 3.8 * major
    top_w2c = look_at_w2c(top_eye, target, gravity_up)

    gravity = {
        "method": "Mean estimated c2w camera-down direction, sign validated by fixed semantic-ID floor minus ceiling medians.",
        "gravity_down_world": gravity_down.tolist(),
        "gravity_up_world": gravity_up.tolist(),
        "mean_camera_down_directional_concentration": concentration,
        "floor_semantic_id": 40,
        "ceiling_semantic_id": 31,
        "floor_median_world": floor_median.tolist(),
        "ceiling_median_world": ceiling_median.tolist(),
        "floor_to_ceiling_signed_separation_along_gravity_m": separation,
        "validation_pass": bool(concentration > 0.9 and separation > 1.0),
        "not_bbox_axis_inference": True,
    }
    common = {
        "observed_frame": observed_frame,
        "observed_alignment_to_robust_map_center": float(alignment[observed_frame]),
        "observed_distance_to_robust_map_center_m": float(distances[observed_frame]),
        "robust_map_target_world": target.tolist(),
        "gravity_evidence": gravity,
    }
    camera_inputs = {
        "trajectory_observed": (
            observed_w2c,
            observed_intrinsic,
            "Exact saved estimated pose selected deterministically for strongest forward alignment to the robust map center; no pose offset.",
            {**common, "pose_offset_m": 0.0, "fov_source": "saved intrinsics scaled to pilot resolution"},
        ),
        "room_overview": (
            overview_w2c,
            intrinsic_for_fov(width, height, 75.0),
            "Limited offset from the selected observed pose: 0.85 m backward along observed forward and 0.35 m upward along validated gravity; looks at robust center.",
            {**common, "backward_offset_m": 0.85, "upward_offset_m": 0.35, "virtual_view": True},
        ),
        "top_oblique": (
            top_w2c,
            intrinsic_for_fov(width, height, 70.0),
            "Gravity-validated elevated oblique view, with horizontal direction from the dominant gravity-orthogonal PCA axis of occupied centers.",
            {**common, "upward_offset_m": 3.2, "horizontal_offset_m": 3.8, "horizontal_pca_eigenvalues": eigenvalues.tolist(), "virtual_view": True},
        ),
    }
    cameras = {
        name: camera_record(name, *camera_inputs[name][:2], width, height, probe, camera_inputs[name][2], camera_inputs[name][3])
        for name in VIEW_NAMES
    }
    return cameras, gravity


def project_points(points: np.ndarray, camera: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    w2c = np.asarray(camera["world_to_camera_w2c"], dtype=np.float64)
    intrinsic = np.asarray(camera["intrinsics"], dtype=np.float64)
    cam = (w2c[:3, :3] @ points.astype(np.float64).T).T + w2c[:3, 3]
    z = cam[:, 2]
    valid = (z > camera["near_plane_m"]) & (z < camera["far_plane_m"])
    u = np.rint(intrinsic[0, 0] * cam[:, 0] / np.maximum(z, 1e-12) + intrinsic[0, 2]).astype(np.int64)
    v = np.rint(intrinsic[1, 1] * cam[:, 1] / np.maximum(z, 1e-12) + intrinsic[1, 2]).astype(np.int64)
    width, height = camera["resolution"]
    valid &= (u >= 0) & (u < width) & (v >= 0) & (v < height)
    return u, v, z, valid


def nearest_pixels(points: np.ndarray, camera: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, dict[str, Any]]:
    u, v, z, valid = project_points(points, camera)
    width, height = camera["resolution"]
    source = np.flatnonzero(valid)
    pixel = v[valid] * width + u[valid]
    order = np.lexsort((z[valid], pixel))
    ordered_pixels = pixel[order]
    keep = np.r_[True, ordered_pixels[1:] != ordered_pixels[:-1]]
    chosen = source[order[keep]]
    chosen_pixels = ordered_pixels[keep]
    return chosen, chosen_pixels, {
        "input_point_count": int(len(points)),
        "projectable_point_count": int(valid.sum()),
        "occupied_pixel_count": int(len(chosen_pixels)),
        "occupied_pixel_fraction": float(len(chosen_pixels) / (width * height)),
    }


def paint_points(colors: np.ndarray, chosen: np.ndarray, pixels: np.ndarray, size: tuple[int, int], background=(248, 248, 248)) -> np.ndarray:
    width, height = size
    image = np.empty((height * width, 3), dtype=np.uint8)
    image[:] = np.asarray(background, dtype=np.uint8)
    image[pixels] = colors[chosen]
    occupied = np.zeros(height * width, dtype=bool)
    occupied[pixels] = True
    image2 = image.reshape(height, width, 3)
    occupied2 = occupied.reshape(height, width)
    # Deterministic one-pixel gap fill; it changes only point-display size, not geometry.
    for dy, dx in ((0, 1), (1, 0), (0, -1), (-1, 0)):
        shifted_colors = np.roll(image2, (dy, dx), axis=(0, 1))
        shifted_mask = np.roll(occupied2, (dy, dx), axis=(0, 1))
        fill = shifted_mask & ~occupied2
        image2[fill] = shifted_colors[fill]
    return image2


def add_title(image: np.ndarray, title: str, subtitle: str) -> Image.Image:
    source = Image.fromarray(image, mode="RGB")
    header = 54
    canvas = Image.new("RGB", (source.width, source.height + header), "white")
    canvas.paste(source, (0, header))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    draw.text((12, 8), title, fill="black", font=font)
    draw.text((12, 28), subtitle, fill=(70, 70, 70), font=font)
    return canvas


def depth_colors(depth: np.ndarray) -> np.ndarray:
    lo, hi = np.quantile(depth, [0.02, 0.98])
    norm = np.clip((depth - lo) / max(hi - lo, 1e-9), 0, 1)
    # Fixed analytic blue-cyan-yellow depth palette; near blue, far yellow.
    return np.stack([
        np.rint(255 * norm),
        np.rint(255 * (1 - np.abs(2 * norm - 1))),
        np.rint(255 * (1 - norm)),
    ], axis=1).astype(np.uint8)


def save_legend(path: Path, palette: dict[int, tuple[int, int, int]], names: dict[int, str]) -> None:
    rows = math.ceil(len(palette) / 3)
    image = Image.new("RGB", (900, 42 + rows * 32), "white")
    draw = ImageDraw.Draw(image)
    draw.text((12, 10), "Fixed per-Gaussian Semantic-ID Visualization - verified Replica palette", fill="black")
    for index, class_id in enumerate(sorted(palette)):
        column, row = divmod(index, rows)
        x, y = 12 + column * 296, 42 + row * 32
        draw.rectangle((x, y, x + 22, y + 22), fill=palette[class_id], outline="black")
        draw.text((x + 30, y + 4), f"{class_id}: {names[class_id]}", fill="black")
    image.save(path)


def render_native(
    params: dict[str, np.ndarray],
    cameras: dict[str, dict[str, Any]],
    output: Path,
    device: str,
) -> dict[str, Any]:
    import torch
    import torch.nn.functional as functional
    from diff_gaussian_rasterization import GaussianRasterizer
    from utils.recon_helpers import setup_camera

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable for repository-native Gaussian rendering")
    torch.cuda.set_device(torch.device(device))
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()
    means = torch.from_numpy(params["means3D"]).to(device)
    rotations = functional.normalize(torch.from_numpy(params["unnorm_rotations"]).to(device))
    opacities = torch.sigmoid(torch.from_numpy(params["logit_opacities"]).to(device))
    scales = torch.exp(torch.from_numpy(np.tile(params["log_scales"], (1, 3))).to(device))
    means2d = torch.zeros_like(means)
    modalities = {
        "rgb/unfiltered": torch.from_numpy(params["rgb_colors"]).to(device),
        "semantic/raw": torch.from_numpy(params["semantic_colors"]).to(device),
    }
    results: dict[str, Any] = {}
    with torch.no_grad():
        for modality, colors in modalities.items():
            destination = output / modality
            destination.mkdir(parents=True, exist_ok=True)
            results[modality] = {}
            render_variables = {
                "means3D": means,
                "colors_precomp": colors,
                "rotations": rotations,
                "opacities": opacities,
                "scales": scales,
                "means2D": means2d,
            }
            for name in VIEW_NAMES:
                camera = cameras[name]
                settings = setup_camera(
                    camera["resolution"][0], camera["resolution"][1],
                    np.asarray(camera["intrinsics"]), np.asarray(camera["world_to_camera_w2c"]),
                    camera["near_plane_m"], camera["far_plane_m"], device=device,
                )
                settings = settings._replace(bg=torch.ones(3, dtype=torch.float32, device=device))
                rendered, _, _ = GaussianRasterizer(raster_settings=settings)(**render_variables)
                torch.cuda.synchronize()
                raw = rendered.permute(1, 2, 0).cpu().numpy()
                displayed = np.rint(np.clip(raw, 0, 1) * 255).astype(np.uint8)
                path = destination / f"{name}.png"
                Image.fromarray(displayed, mode="RGB").save(path)
                results[modality][name] = {
                    "path": str(path),
                    "raw_min": float(raw.min()),
                    "raw_max": float(raw.max()),
                    "display_clamped_to_0_1": True,
                    "nonwhite_pixel_fraction": float(np.any(displayed != 255, axis=2).mean()),
                    "pixel_std": float(displayed.std()),
                }
    memory = {
        "peak_gpu_allocated_bytes": int(torch.cuda.max_memory_allocated()),
        "peak_gpu_reserved_bytes": int(torch.cuda.max_memory_reserved()),
        "device": device,
        "device_name": torch.cuda.get_device_name(torch.device(device)),
    }
    return {"render_results": results, "gpu_memory": memory}


def make_comparison(rgb: Path, geometry: Path, semantic: Path, destination: Path, view: str) -> None:
    items = [Image.open(path).convert("RGB") for path in (rgb, geometry, semantic)]
    height = max(item.height for item in items)
    canvas = Image.new("RGB", (sum(item.width for item in items), height + 40), "white")
    draw = ImageDraw.Draw(canvas)
    x = 0
    labels = ("Original unfiltered RGB Gaussian render", "Geometry-only sampled centers", "Fixed per-Gaussian Semantic-ID centers")
    for item, label in zip(items, labels):
        canvas.paste(item, (x, 40))
        draw.text((x + 8, 12), label, fill="black")
        x += item.width
    draw.text((8, 0), f"Gate V3A coordinate-consistent comparison: {view}", fill="black")
    canvas.save(destination)


def main() -> int:
    args = parse_args()
    started = time.perf_counter()
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing to overwrite non-empty output: {output}")
    for relative in (
        "rgb/unfiltered", "rgb/diagnostic", "geometry", "semantic/categorical",
        "semantic/raw", "semantic/classwise", "trajectory", "comparisons",
        "cameras", "metadata", "checksums",
    ):
        (output / relative).mkdir(parents=True, exist_ok=True)

    sources = {
        "checkpoint": args.checkpoint.resolve(),
        "rgb_ply": args.rgb_ply.resolve(),
        "semantic_ply": args.semantic_ply.resolve(),
        "semantic_mapping": args.semantic_mapping.resolve(),
    }
    for path in sources.values():
        if not path.is_file():
            raise FileNotFoundError(path)
    hashes_before = {name: sha256_file(path) for name, path in sources.items()}
    git_before = git("status", "--short")

    with np.load(sources["checkpoint"], allow_pickle=False) as archive:
        required = (
            "means3D", "rgb_colors", "unnorm_rotations", "logit_opacities", "log_scales",
            "semantic_ids", "semantic_colors", "cam_unnorm_rots", "cam_trans", "intrinsics",
            "org_width", "org_height",
        )
        params = {key: np.asarray(archive[key]).copy() for key in required}
    count = len(params["means3D"])
    if not all(len(params[key]) == count for key in ("rgb_colors", "semantic_ids", "semantic_colors", "log_scales")):
        raise ValueError("Per-Gaussian checkpoint arrays are not aligned")
    if not all(np.isfinite(params[key]).all() for key in required if np.issubdtype(params[key].dtype, np.number)):
        raise ValueError("Non-finite checkpoint input")

    palette, class_names, reverse_names = load_palette(sources["semantic_mapping"])
    missing_ids = sorted(set(int(v) for v in np.unique(params["semantic_ids"])) - set(palette))
    if missing_ids:
        raise ValueError(f"Palette misses semantic IDs: {missing_ids}")
    w2cs, centers, forwards, camera_down = trajectory_from_params(params["cam_unnorm_rots"], params["cam_trans"])
    cameras, gravity = build_cameras(
        params["means3D"], params["semantic_ids"], params["intrinsics"],
        (int(params["org_width"]), int(params["org_height"])),
        w2cs, centers, forwards, camera_down, args.width, args.height,
    )
    for name, camera in cameras.items():
        dump_json(output / "cameras" / f"{name}.json", camera)

    rng = np.random.default_rng(SAMPLE_SEED)
    sample_count = min(SAMPLE_COUNT, count)
    sample_indices = np.sort(rng.choice(count, size=sample_count, replace=False).astype(np.int64))
    np.save(output / "metadata" / "gaussian_center_sample_indices.npy", sample_indices)
    sample_points = params["means3D"][sample_indices]
    sample_ids = params["semantic_ids"][sample_indices]
    semantic_colors = np.asarray([palette[int(value)] for value in sample_ids], dtype=np.uint8)

    point_stats: dict[str, Any] = {}
    nearest_by_view: dict[str, tuple[np.ndarray, np.ndarray]] = {}
    for name in VIEW_NAMES:
        camera = cameras[name]
        chosen, pixels, stats = nearest_pixels(sample_points, camera)
        nearest_by_view[name] = (chosen, pixels)
        point_stats[name] = stats
        _, _, sampled_depth, _ = project_points(sample_points, camera)
        geometry_rgb = depth_colors(sampled_depth)
        geometry_image = paint_points(geometry_rgb, chosen, pixels, tuple(camera["resolution"]))
        add_title(
            geometry_image,
            f"Geometry-only Gaussian-center diagnostic - {name}",
            f"{sample_count:,} deterministic centers; color = camera depth; centers are not a continuous surface.",
        ).save(output / "geometry" / f"{name}.png")
        categorical = paint_points(semantic_colors, chosen, pixels, tuple(camera["resolution"]))
        add_title(
            categorical,
            f"Fixed per-Gaussian Semantic-ID Visualization - {name}",
            "Categorical center metadata with verified Replica palette; not a per-pixel released predictor.",
        ).save(output / "semantic/categorical" / f"{name}.png")

    save_legend(output / "semantic/categorical/legend_29_classes.png", palette, class_names)

    best_view = "top_oblique"
    chosen, pixels = nearest_by_view[best_view]
    context = np.full((sample_count, 3), 188, dtype=np.uint8)
    selected_class_records: list[dict[str, Any]] = []
    for class_name in CLASS_NAMES:
        if class_name not in reverse_names:
            continue
        class_id = reverse_names[class_name]
        class_mask = params["semantic_ids"] == class_id
        class_count = int(class_mask.sum())
        colors = context.copy()
        colors[sample_ids == class_id] = palette[class_id]
        image = paint_points(colors, chosen, pixels, tuple(cameras[best_view]["resolution"]))
        add_title(
            image,
            f"Class-wise fixed semantic ID: {class_name} (ID {class_id})",
            f"{class_count:,} authoritative primitives; sampled class centers highlighted over neutral context.",
        ).save(output / "semantic/classwise" / f"{class_name}_{best_view}.png")
        selected_class_records.append({
            "class_name": class_name,
            "class_id": class_id,
            "palette_rgb": palette[class_id],
            "authoritative_primitive_count": class_count,
            "sampled_primitive_count": int(np.sum(sample_ids == class_id)),
            "view": best_view,
        })

    combined_ids = {reverse_names[name] for name in CLASS_NAMES if name in reverse_names}
    combined_colors = np.full((sample_count, 3), 205, dtype=np.uint8)
    for class_id in combined_ids:
        combined_colors[sample_ids == class_id] = palette[class_id]
    combined = paint_points(combined_colors, chosen, pixels, tuple(cameras[best_view]["resolution"]))
    add_title(
        combined,
        "Selected fixed semantic-ID classes with neutral context",
        ", ".join(CLASS_NAMES),
    ).save(output / "semantic/classwise/selected_classes_overview_top_oblique.png")

    # Trajectory overlay uses the same sampled-center projection and camera.
    geometry_context = paint_points(np.full((sample_count, 3), 210, dtype=np.uint8), chosen, pixels, tuple(cameras[best_view]["resolution"]))
    trajectory_image = Image.fromarray(geometry_context, mode="RGB")
    draw = ImageDraw.Draw(trajectory_image)
    u, v, _, valid = project_points(centers, cameras[best_view])
    segments = []
    current = []
    for x, y, is_valid in zip(u, v, valid):
        if is_valid:
            current.append((int(x), int(y)))
        elif current:
            if len(current) > 1:
                segments.append(current)
            current = []
    if len(current) > 1:
        segments.append(current)
    for segment in segments:
        draw.line(segment, fill=(0, 110, 230), width=3)
    valid_indices = np.flatnonzero(valid)
    if len(valid_indices):
        start = valid_indices[0]
        end = valid_indices[-1]
        draw.ellipse((u[start] - 6, v[start] - 6, u[start] + 6, v[start] + 6), fill=(0, 180, 0), outline="black")
        draw.ellipse((u[end] - 6, v[end] - 6, u[end] + 6, v[end] + 6), fill=(220, 30, 30), outline="black")
    trajectory_array = np.asarray(trajectory_image)
    add_title(
        trajectory_array,
        "Estimated camera trajectory over Gaussian-center geometry",
        f"{len(centers):,} ordered estimated poses; green=start, red=end, blue=path; no GT alignment applied.",
    ).save(output / "trajectory/estimated_trajectory_3d.png")

    native = {"skipped": True, "reason": "--skip-native-render"}
    if not args.skip_native_render:
        native = render_native(params, cameras, output, args.device)
        for name in VIEW_NAMES:
            make_comparison(
                output / "rgb/unfiltered" / f"{name}.png",
                output / "geometry" / f"{name}.png",
                output / "semantic/categorical" / f"{name}.png",
                output / "comparisons" / f"{name}_rgb_geometry_semantic.png",
                name,
            )

    hashes_after = {name: sha256_file(path) for name, path in sources.items()}
    integrity = hashes_before == hashes_after
    elapsed = time.perf_counter() - started
    runtime = {
        "total_wall_time_seconds": elapsed,
        "peak_host_rss_kib": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "peak_host_rss_bytes_linux": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024),
        "gpu": native.get("gpu_memory", {"peak_gpu_allocated_bytes": 0, "peak_gpu_reserved_bytes": 0, "note": "native render skipped"}),
    }
    metadata = {
        "gate": "PHASE4-VIS-GATE-V3A",
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "git_status_before": git_before,
        "git_status_after": git("status", "--short"),
        "source_paths": {name: str(path) for name, path in sources.items()},
        "source_hashes_before": hashes_before,
        "source_hashes_after": hashes_after,
        "source_integrity_pass": integrity,
        "v1_reference_root": str(args.v1_root.resolve()),
        "v2_primary_fidelity_evidence_root": str(args.v2_root.resolve()),
        "gaussian_count": count,
        "trajectory_pose_count": int(len(centers)),
        "gravity_validation": gravity,
        "camera_names": list(VIEW_NAMES),
        "camera_files": [f"cameras/{name}.json" for name in VIEW_NAMES],
        "center_diagnostic": {
            "representation": "Projected Gaussian centers with a z-buffer; no mesh or continuous surface invented.",
            "sample_method": "NumPy Generator(PCG64) choice without replacement, indices sorted",
            "seed": SAMPLE_SEED,
            "sample_count": sample_count,
            "population_count": count,
            "sample_indices_path": "metadata/gaussian_center_sample_indices.npy",
            "sample_indices_sha256": sha256_file(output / "metadata/gaussian_center_sample_indices.npy"),
            "point_display_rule": "Nearest center per pixel plus deterministic one-pixel gap fill; fixed display-only point size.",
            "projection_stats": point_stats,
        },
        "semantic_categorical": {
            "label": "Fixed per-Gaussian Semantic-ID Visualization",
            "source_field": "semantic_ids",
            "palette_source": str(sources["semantic_mapping"]),
            "palette_entry_count": len(palette),
            "not_released_per_pixel_predictor": True,
            "not_gt_assisted_per_frame_recoloring": True,
        },
        "selected_classes": selected_class_records,
        "native_renderer": native,
        "optional_filtering": {
            "applied": False,
            "reason": "The required unfiltered RGB and independent center diagnostics were sufficient for the bounded proof; no threshold was introduced merely for presentation.",
        },
        "runtime": runtime,
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "numpy": np.__version__,
        },
        "scope": {
            "slam_rerun": False,
            "evaluation_rerun": False,
            "optimization_or_training": False,
            "checkpoint_or_ply_write": False,
            "visualization_only": True,
        },
    }
    dump_json(output / "metadata/run_metadata.json", metadata)
    dump_json(output / "metadata/classwise_counts.json", selected_class_records)

    artifacts = []
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name not in ("SHA256SUMS.txt", "artifact_manifest.json"):
            artifacts.append({
                "relative_path": str(path.relative_to(output)),
                "size_bytes": path.stat().st_size,
                "sha256": sha256_file(path),
            })
    dump_json(output / "metadata/artifact_manifest.json", {"artifact_count_excluding_manifest_and_checksum_file": len(artifacts), "artifacts": artifacts})
    checksum_lines = [f"{item['sha256']}  {item['relative_path']}" for item in artifacts]
    checksum_lines.append(f"{sha256_file(output / 'metadata/artifact_manifest.json')}  metadata/artifact_manifest.json")
    (output / "checksums/SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")

    summary = {
        "technical_completion": bool(integrity and gravity["validation_pass"] and not args.skip_native_render),
        "source_integrity": integrity,
        "cameras": list(VIEW_NAMES),
        "best_diagnostic_view": best_view,
        "runtime": runtime,
        "output": str(output),
    }
    print(json.dumps(summary, indent=2))
    return 0 if summary["technical_completion"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
