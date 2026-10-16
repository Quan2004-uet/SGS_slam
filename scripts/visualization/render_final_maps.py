#!/usr/bin/env python3
"""Deterministically render paired RGB/semantic views of saved SGS-SLAM PLY maps.

This is an offline visualization utility. It reads Gaussian-splat PLY exports,
does not load a dataset, and does not execute tracking, mapping, optimization,
or evaluation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from plyfile import PlyData


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


C0 = 0.28209479177387814
REQUIRED_PROPERTIES = [
    "x", "y", "z", "nx", "ny", "nz", "f_dc_0", "f_dc_1", "f_dc_2",
    "opacity", "scale_0", "scale_1", "scale_2", "rot_0", "rot_1",
    "rot_2", "rot_3",
]
VIEW_NAMES = ("overview", "oblique", "top_oblique")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Render deterministic full-map RGB and semantic Gaussian views."
    )
    parser.add_argument("--reconstruction", required=True, type=Path)
    parser.add_argument("--semantic", required=True, type=Path)
    parser.add_argument("--params-npz", type=Path, default=None)
    parser.add_argument("--class-mapping", type=Path, default=None)
    parser.add_argument(
        "--camera-dir", type=Path, default=None,
        help="Reuse overview/oblique/top_oblique camera JSON files from this directory.",
    )
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--width", type=int, default=1600)
    parser.add_argument("--height", type=int, default=900)
    parser.add_argument("--fov-y-deg", type=float, default=55.0)
    parser.add_argument("--fit-margin", type=float, default=0.88)
    parser.add_argument(
        "--background", choices=("white", "black"), default="white"
    )
    parser.add_argument("--device", default="cuda:0")
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def json_dump(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def git_value(repo_root: Path, *args: str) -> str:
    return subprocess.check_output(
        ["git", *args], cwd=repo_root, text=True
    ).strip()


def read_ply_header(path: Path) -> dict[str, Any]:
    lines: list[str] = []
    with path.open("rb") as handle:
        while True:
            line = handle.readline()
            if not line:
                raise ValueError(f"PLY header has no end_header: {path}")
            decoded = line.decode("ascii").rstrip("\r\n")
            lines.append(decoded)
            if decoded == "end_header":
                break
    fmt = next(line.split(maxsplit=1)[1] for line in lines if line.startswith("format "))
    vertex_line = next(line for line in lines if line.startswith("element vertex "))
    properties = [line.split()[-1] for line in lines if line.startswith("property ")]
    return {
        "format": fmt,
        "vertex_count": int(vertex_line.split()[-1]),
        "properties": properties,
        "header_lines": lines,
    }


def load_vertex_data(path: Path) -> tuple[dict[str, Any], np.ndarray]:
    header = read_ply_header(path)
    missing = [name for name in REQUIRED_PROPERTIES if name not in header["properties"]]
    if missing:
        raise ValueError(f"Missing required Gaussian properties in {path}: {missing}")
    ply = PlyData.read(str(path), mmap="r")
    vertex = ply["vertex"].data
    if len(vertex) != header["vertex_count"]:
        raise ValueError(f"Header/data vertex-count mismatch in {path}")
    return header, vertex


def stack_fields(vertex: np.ndarray, names: list[str]) -> np.ndarray:
    return np.column_stack([vertex[name] for name in names]).astype(np.float32, copy=False)


def map_statistics(path: Path, header: dict[str, Any], vertex: np.ndarray) -> dict[str, Any]:
    xyz = stack_fields(vertex, ["x", "y", "z"])
    minimum = xyz.min(axis=0).astype(np.float64)
    maximum = xyz.max(axis=0).astype(np.float64)
    centroid = xyz.mean(axis=0, dtype=np.float64)
    extent = maximum - minimum
    f_dc_ranges = {
        name: [float(vertex[name].min()), float(vertex[name].max())]
        for name in ("f_dc_0", "f_dc_1", "f_dc_2")
    }
    return {
        "source_ply_path": str(path),
        "source_ply_sha256": sha256_file(path),
        "source_ply_file_size_bytes": path.stat().st_size,
        "ply_format": header["format"],
        "number_of_vertices_points_gaussians": int(header["vertex_count"]),
        "property_names": header["properties"],
        "position_fields": ["x", "y", "z"],
        "color_fields": ["f_dc_0", "f_dc_1", "f_dc_2"],
        "bounding_box": {
            "min_x": float(minimum[0]), "min_y": float(minimum[1]), "min_z": float(minimum[2]),
            "max_x": float(maximum[0]), "max_y": float(maximum[1]), "max_z": float(maximum[2]),
        },
        "centroid": centroid.tolist(),
        "spatial_extent_xyz": extent.tolist(),
        "all_positions_finite": bool(np.isfinite(xyz).all()),
        "detected_color_representation": (
            "3DGS degree-0 spherical-harmonic coefficients; decoded as RGB = "
            "f_dc * 0.28209479177387814 + 0.5"
        ),
        "f_dc_ranges": f_dc_ranges,
        "opacity_information": {
            "field": "opacity", "representation": "logit", "renderer_transform": "sigmoid",
            "min": float(vertex["opacity"].min()), "max": float(vertex["opacity"].max()),
        },
        "scale_information": {
            "fields": ["scale_0", "scale_1", "scale_2"],
            "representation": "log scale", "renderer_transform": "exp",
            "min": [float(vertex[f"scale_{i}"].min()) for i in range(3)],
            "max": [float(vertex[f"scale_{i}"].max()) for i in range(3)],
        },
        "rotation_information": {
            "fields": ["rot_0", "rot_1", "rot_2", "rot_3"],
            "representation": "unnormalized quaternion, real-first",
            "renderer_transform": "L2 normalize",
            "all_finite": bool(all(np.isfinite(vertex[f"rot_{i}"]).all() for i in range(4))),
        },
    }


def bbox_corners(stats: dict[str, Any]) -> np.ndarray:
    box = stats["bounding_box"]
    lo = np.array([box["min_x"], box["min_y"], box["min_z"]], dtype=np.float64)
    hi = np.array([box["max_x"], box["max_y"], box["max_z"]], dtype=np.float64)
    return np.array(
        [[x, y, z] for x in (lo[0], hi[0]) for y in (lo[1], hi[1]) for z in (lo[2], hi[2])],
        dtype=np.float64,
    )


def make_camera(
    name: str,
    direction_components: np.ndarray,
    vertical_axis: int,
    stats: dict[str, Any],
    fit_points: np.ndarray,
    width: int,
    height: int,
    fov_y_deg: float,
    fit_margin: float,
) -> dict[str, Any]:
    target = np.array(stats["centroid"], dtype=np.float64)
    forward_from_target = direction_components / np.linalg.norm(direction_components)
    eye_direction = forward_from_target
    viewing_forward = -eye_direction
    up_hint = np.zeros(3, dtype=np.float64)
    up_hint[vertical_axis] = 1.0
    right = np.cross(viewing_forward, up_hint)
    right /= np.linalg.norm(right)
    true_up = np.cross(right, viewing_forward)
    true_up /= np.linalg.norm(true_up)
    down = -true_up

    corners = bbox_corners(stats)
    rel = fit_points - target
    tan_y = math.tan(math.radians(fov_y_deg) / 2.0)
    tan_x = tan_y * width / height
    forward_offsets = rel @ viewing_forward
    right_offsets = rel @ right
    down_offsets = rel @ down
    required = np.maximum(
        np.abs(right_offsets) / (tan_x * fit_margin) - forward_offsets,
        np.abs(down_offsets) / (tan_y * fit_margin) - forward_offsets,
    )
    distance = float(max(required.max(), -forward_offsets.min() + 0.1) * 1.02)
    eye = target + eye_direction * distance

    rotation = np.stack([right, down, viewing_forward], axis=0)
    translation = -rotation @ eye
    w2c = np.eye(4, dtype=np.float64)
    w2c[:3, :3] = rotation
    w2c[:3, 3] = translation

    points_cam = (rotation @ fit_points.T).T + translation
    corners_cam = (rotation @ corners.T).T + translation
    near = max(0.01, float(points_cam[:, 2].min()) * 0.25)
    far = float(points_cam[:, 2].max()) * 1.5
    fy = height / (2.0 * tan_y)
    fx = fy
    cx = width / 2.0
    cy = height / 2.0
    intrinsic = np.array([[fx, 0.0, cx], [0.0, fy, cy], [0.0, 0.0, 1.0]])
    point_u = fx * points_cam[:, 0] / points_cam[:, 2] + cx
    point_v = fy * points_cam[:, 1] / points_cam[:, 2] + cy
    corner_u = fx * corners_cam[:, 0] / corners_cam[:, 2] + cx
    corner_v = fy * corners_cam[:, 1] / corners_cam[:, 2] + cy
    points_inside = bool(
        np.all(points_cam[:, 2] > near)
        and np.all(point_u >= 0) and np.all(point_u <= width - 1)
        and np.all(point_v >= 0) and np.all(point_v <= height - 1)
    )
    projection = np.array(
        [
            [2 * fx / width, 0, -(width - 2 * cx) / width, 0],
            [0, 2 * fy / height, -(height - 2 * cy) / height, 0],
            [0, 0, far / (far - near), -(far * near) / (far - near)],
            [0, 0, 1, 0],
        ],
        dtype=np.float64,
    )
    return {
        "viewpoint": name,
        "camera_position": eye.tolist(),
        "look_at_target": target.tolist(),
        "up_vector": true_up.tolist(),
        "right_vector": right.tolist(),
        "forward_vector": viewing_forward.tolist(),
        "world_to_camera_extrinsic": w2c.tolist(),
        "intrinsic_matrix": intrinsic.tolist(),
        "projection_matrix": projection.tolist(),
        "fov_y_degrees": fov_y_deg,
        "fov_x_degrees": math.degrees(2.0 * math.atan(tan_x)),
        "zoom": None,
        "near_clip": near,
        "far_clip": far,
        "image_width": width,
        "image_height": height,
        "fit_margin": fit_margin,
        "camera_distance": distance,
        "full_map_point_projection": {
            "point_count": int(fit_points.shape[0]),
            "min_u": float(point_u.min()), "max_u": float(point_u.max()),
            "min_v": float(point_v.min()), "max_v": float(point_v.max()),
            "min_depth": float(points_cam[:, 2].min()),
            "max_depth": float(points_cam[:, 2].max()),
            "all_map_points_inside_image": points_inside,
        },
        "full_bbox_corner_projection": {
            "min_u": float(corner_u.min()), "max_u": float(corner_u.max()),
            "min_v": float(corner_v.min()), "max_v": float(corner_v.max()),
            "min_depth": float(corners_cam[:, 2].min()),
            "max_depth": float(corners_cam[:, 2].max()),
            "note": "Axis-aligned box corners need not contain map elements; full-map fit is validated on every Gaussian center.",
        },
        "backend_convention": "OpenCV-style w2c with +x right, +y down, +z forward",
    }


def camera_set(stats: dict[str, Any], fit_points: np.ndarray, width: int, height: int, fov_y: float, margin: float) -> dict[str, dict[str, Any]]:
    extent = np.array(stats["spatial_extent_xyz"], dtype=np.float64)
    vertical_axis = int(np.argmin(extent))
    horizontal = [axis for axis in range(3) if axis != vertical_axis]

    def vec(h0: float, h1: float, vertical: float) -> np.ndarray:
        result = np.zeros(3, dtype=np.float64)
        result[horizontal[0]] = h0
        result[horizontal[1]] = h1
        result[vertical_axis] = vertical
        return result

    definitions = {
        "overview": vec(-1.35, -1.15, 0.55),
        "oblique": vec(1.30, -1.10, 0.72),
        "top_oblique": vec(-0.75, 0.55, 2.20),
    }
    cameras = {
        name: make_camera(name, direction, vertical_axis, stats, fit_points, width, height, fov_y, margin)
        for name, direction in definitions.items()
    }
    for camera in cameras.values():
        camera["inferred_vertical_axis"] = ["x", "y", "z"][vertical_axis]
        camera["vertical_axis_inference"] = "smallest full-map bounding-box extent"
    return cameras


def render_gaussian_map(
    vertex: np.ndarray,
    cameras: dict[str, dict[str, Any]],
    output_dir: Path,
    device: str,
    background: str,
) -> tuple[dict[str, dict[str, Any]], dict[str, Any]]:
    import torch
    import torch.nn.functional as functional
    from diff_gaussian_rasterization import GaussianRasterizer
    from utils.recon_helpers import setup_camera

    if not torch.cuda.is_available():
        raise RuntimeError("CUDA is unavailable; native Gaussian rasterizer cannot run")
    torch.cuda.set_device(torch.device(device))
    torch.cuda.empty_cache()
    torch.cuda.reset_peak_memory_stats()

    means = torch.from_numpy(stack_fields(vertex, ["x", "y", "z"])).to(device)
    colors = torch.from_numpy(stack_fields(vertex, ["f_dc_0", "f_dc_1", "f_dc_2"])).to(device)
    colors = colors * C0 + 0.5
    opacities = torch.from_numpy(stack_fields(vertex, ["opacity"])).to(device).sigmoid()
    scales = torch.from_numpy(stack_fields(vertex, ["scale_0", "scale_1", "scale_2"])).to(device).exp()
    rotations = torch.from_numpy(stack_fields(vertex, ["rot_0", "rot_1", "rot_2", "rot_3"])).to(device)
    rotations = functional.normalize(rotations)
    means2d = torch.zeros_like(means)

    render_variable = {
        "means3D": means,
        "colors_precomp": colors,
        "rotations": rotations,
        "opacities": opacities,
        "scales": scales,
        "means2D": means2d,
    }
    bg_rgb = np.array([1.0, 1.0, 1.0] if background == "white" else [0.0, 0.0, 0.0])
    results: dict[str, dict[str, Any]] = {}
    output_dir.mkdir(parents=True, exist_ok=True)
    with torch.no_grad():
        for name in VIEW_NAMES:
            camera = cameras[name]
            intrinsic = np.asarray(camera["intrinsic_matrix"], dtype=np.float64)
            extrinsic = np.asarray(camera["world_to_camera_extrinsic"], dtype=np.float64)
            settings = setup_camera(
                camera["image_width"], camera["image_height"], intrinsic, extrinsic,
                camera["near_clip"], camera["far_clip"], device=device,
            )
            settings = settings._replace(
                bg=torch.tensor(bg_rgb, dtype=torch.float32, device=device)
            )
            image_tensor, _, _ = GaussianRasterizer(raster_settings=settings)(**render_variable)
            torch.cuda.synchronize()
            image_float = image_tensor.permute(1, 2, 0).detach().cpu().numpy()
            image_clamped = np.clip(image_float, 0.0, 1.0)
            image_u8 = np.rint(image_clamped * 255.0).astype(np.uint8)
            image_path = output_dir / f"{name}.png"
            Image.fromarray(image_u8, mode="RGB").save(image_path)
            background_u8 = np.rint(bg_rgb * 255.0).astype(np.uint8)
            non_background = np.any(image_u8 != background_u8[None, None, :], axis=2)
            results[name] = {
                "path": str(image_path),
                "mean_rgb_0_255": image_u8.mean(axis=(0, 1), dtype=np.float64).tolist(),
                "std_rgb_0_255": image_u8.std(axis=(0, 1), dtype=np.float64).tolist(),
                "non_background_pixel_ratio": float(non_background.mean()),
                "raw_render_min": float(image_float.min()),
                "raw_render_max": float(image_float.max()),
                "display_clamped_to_0_1": True,
                "empty_or_uniform": bool(image_u8.std() < 1.0 or non_background.mean() < 0.005),
            }
    memory = {
        "peak_gpu_allocated_bytes": int(torch.cuda.max_memory_allocated()),
        "peak_gpu_reserved_bytes": int(torch.cuda.max_memory_reserved()),
        "device": device,
        "device_name": torch.cuda.get_device_name(torch.device(device)),
    }
    del render_variable, means, colors, opacities, scales, rotations, means2d
    torch.cuda.empty_cache()
    return results, memory


def map_points_fit_camera(fit_points: np.ndarray, camera: dict[str, Any]) -> bool:
    extrinsic = np.asarray(camera["world_to_camera_extrinsic"], dtype=np.float64)
    intrinsic = np.asarray(camera["intrinsic_matrix"], dtype=np.float64)
    points_camera = (extrinsic[:3, :3] @ fit_points.T).T + extrinsic[:3, 3]
    z = points_camera[:, 2]
    u = intrinsic[0, 0] * points_camera[:, 0] / z + intrinsic[0, 2]
    v = intrinsic[1, 1] * points_camera[:, 1] / z + intrinsic[1, 2]
    return bool(
        np.isfinite(points_camera).all()
        and np.all(z >= float(camera["near_clip"]))
        and np.all(z <= float(camera["far_clip"]))
        and np.all(u >= 0) and np.all(u <= int(camera["image_width"]) - 1)
        and np.all(v >= 0) and np.all(v <= int(camera["image_height"]) - 1)
    )


def semantic_statistics(vertex: np.ndarray, params_npz: Path | None, class_mapping: Path | None) -> dict[str, Any]:
    decoded = stack_fields(vertex, ["f_dc_0", "f_dc_1", "f_dc_2"]) * C0 + 0.5
    quantized = np.rint(np.clip(decoded, 0.0, 1.0) * 255.0).astype(np.uint8)
    packed = (
        quantized[:, 0].astype(np.uint32) << 16
        | quantized[:, 1].astype(np.uint32) << 8
        | quantized[:, 2].astype(np.uint32)
    )
    unique_color_count = int(np.unique(packed).size)
    result: dict[str, Any] = {
        "semantic_color_fields": ["f_dc_0", "f_dc_1", "f_dc_2"],
        "semantic_color_decode": "RGB = f_dc * 0.28209479177387814 + 0.5",
        "semantic_colors_are_finite": bool(np.isfinite(decoded).all()),
        "unique_semantic_colors_after_uint8_display_quantization": unique_color_count,
        "semantic_palette_source": (
            "Saved trainable semantic_colors exported by utils/convert_ply.py; initialized "
            "from Replica semantic-color images. No recoloring is applied."
        ),
        "semantic_ids_present_in_ply": False,
        "legend_generated": False,
        "legend_note": "No canonical color dictionary is present; learned colors are preserved without inventing a legend.",
    }
    if params_npz is not None and params_npz.exists():
        with np.load(params_npz, allow_pickle=False) as params:
            ids = np.asarray(params["semantic_ids"]).reshape(-1)
        result["aligned_saved_state_semantic_ids_path"] = str(params_npz)
        result["unique_semantic_label_ids"] = [int(value) for value in np.unique(ids)]
        result["number_of_unique_semantic_label_ids"] = int(np.unique(ids).size)
        result["semantic_id_alignment_note"] = "IDs are metadata from aligned params.npz; IDs are not fields in seg_params.ply."
    if class_mapping is not None and class_mapping.exists():
        mapping = json.loads(class_mapping.read_text(encoding="utf-8"))
        result["class_mapping_source"] = str(class_mapping)
        result["class_mapping_entry_count"] = len(mapping.get("classes", []))
        result["class_mapping_note"] = "Replica class names only; this file does not define the saved learned RGB palette."
    return result


def make_pair(left_path: Path, right_path: Path, destination: Path) -> None:
    left = Image.open(left_path).convert("RGB")
    right = Image.open(right_path).convert("RGB")
    if left.size != right.size:
        raise ValueError("Paired reconstruction/semantic images have different sizes")
    label_height = 56
    canvas = Image.new("RGB", (left.width * 2, left.height + label_height), "white")
    canvas.paste(left, (0, label_height))
    canvas.paste(right, (left.width, label_height))
    draw = ImageDraw.Draw(canvas)
    font = ImageFont.load_default(size=28)
    for x, text in ((left.width // 2, "Reconstruction"), (left.width + right.width // 2, "Semantic Segmentation")):
        box = draw.textbbox((0, 0), text, font=font)
        draw.text((x - (box[2] - box[0]) // 2, 12), text, fill="black", font=font)
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def image_record(path: Path, root: Path, artifact_type: str, source_map: str | None, viewpoint: str | None) -> dict[str, Any]:
    width = height = None
    if path.suffix.lower() == ".png":
        with Image.open(path) as image:
            width, height = image.size
    return {
        "relative_path": str(path.relative_to(root)),
        "artifact_type": artifact_type,
        "source_map": source_map,
        "viewpoint": viewpoint,
        "width": width,
        "height": height,
        "file_size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
    }


def main() -> int:
    args = parse_args()
    if args.width < 1600:
        raise ValueError("Width must be at least 1600 pixels")
    if args.height <= 0 or not 0.5 < args.fit_margin < 1.0:
        raise ValueError("Invalid height or fit margin")

    repo_root = REPO_ROOT
    reconstruction = args.reconstruction.resolve()
    semantic = args.semantic.resolve()
    params_npz = args.params_npz.resolve() if args.params_npz else None
    class_mapping = args.class_mapping.resolve() if args.class_mapping else None
    camera_dir = args.camera_dir.resolve() if args.camera_dir else None
    output = args.output.resolve()
    expected_subdirs = {"reconstruction", "semantic", "paired", "cameras", "metadata", "logs"}
    if output.exists():
        existing_files = [path for path in output.rglob("*") if path.is_file()]
        existing_dirs = {
            path.relative_to(output).parts[0]
            for path in output.rglob("*") if path.is_dir()
        }
        unexpected_files = []
        for path in existing_files:
            relative = path.relative_to(output).as_posix()
            is_log = relative.startswith("logs/renderer_")
            is_identical_camera = (
                relative.startswith("cameras/") and camera_dir is not None
                and (camera_dir / path.name).is_file()
                and path.read_bytes() == (camera_dir / path.name).read_bytes()
            )
            if not (is_log or is_identical_camera):
                unexpected_files.append(relative)
        if unexpected_files or not existing_dirs.issubset(expected_subdirs):
            raise FileExistsError(f"Refusing to overwrite populated visualization output: {output}")
    for subdir in expected_subdirs:
        (output / subdir).mkdir(parents=True, exist_ok=True)

    log_lines: list[str] = []
    def log(message: str) -> None:
        timestamped = f"[{datetime.now(timezone.utc).isoformat()}] {message}"
        log_lines.append(timestamped)
        print(timestamped, flush=True)

    started = datetime.now(timezone.utc)
    branch = git_value(repo_root, "branch", "--show-current")
    commit = git_value(repo_root, "rev-parse", "HEAD")
    git_status_before = git_value(repo_root, "status", "--short")
    source_hashes_before = {str(path): sha256_file(path) for path in (reconstruction, semantic)}
    log(f"branch={branch} commit={commit}")
    log("Loading and auditing reconstruction PLY")
    reconstruction_header, reconstruction_vertex = load_vertex_data(reconstruction)
    reconstruction_meta = map_statistics(reconstruction, reconstruction_header, reconstruction_vertex)
    log("Loading and auditing semantic PLY")
    semantic_header, semantic_vertex = load_vertex_data(semantic)
    semantic_meta = map_statistics(semantic, semantic_header, semantic_vertex)

    same_geometry = bool(
        len(reconstruction_vertex) == len(semantic_vertex)
        and all(np.array_equal(reconstruction_vertex[name], semantic_vertex[name]) for name in ("x", "y", "z"))
    )
    if not same_geometry:
        raise ValueError("Reconstruction and semantic PLY geometry differs")
    if reconstruction_header["properties"] != semantic_header["properties"]:
        raise ValueError("Reconstruction and semantic PLY schemas differ")

    fit_points = stack_fields(reconstruction_vertex, ["x", "y", "z"])
    camera_sources: dict[str, Path] = {}
    if camera_dir is not None:
        cameras = {}
        for name in VIEW_NAMES:
            source_path = camera_dir / f"{name}.json"
            if not source_path.is_file():
                raise FileNotFoundError(f"Missing required camera definition: {source_path}")
            camera = json.loads(source_path.read_text(encoding="utf-8"))
            if camera.get("viewpoint") != name:
                raise ValueError(f"Camera name mismatch in {source_path}")
            if (camera.get("image_width"), camera.get("image_height")) != (args.width, args.height):
                raise ValueError(f"Requested image size differs from source camera: {source_path}")
            cameras[name] = camera
            camera_sources[name] = source_path
        map_fit_by_view = {name: map_points_fit_camera(fit_points, camera) for name, camera in cameras.items()}
    else:
        cameras = camera_set(
            reconstruction_meta, fit_points, args.width, args.height, args.fov_y_deg, args.fit_margin
        )
        map_fit_by_view = {
            name: camera["full_map_point_projection"]["all_map_points_inside_image"]
            for name, camera in cameras.items()
        }
    if camera_dir is None and not all(map_fit_by_view.values()):
        raise ValueError("At least one deterministic camera does not contain every map Gaussian center")
    for name, camera in cameras.items():
        if name in camera_sources:
            camera_destination = output / "cameras" / f"{name}.json"
            if not camera_destination.exists():
                import shutil
                shutil.copyfile(camera_sources[name], camera_destination)
            elif camera_destination.read_bytes() != camera_sources[name].read_bytes():
                raise FileExistsError(f"Refusing to replace a different camera file: {camera_destination}")
        else:
            json_dump(output / "cameras" / f"{name}.json", camera)

    log("Rendering reconstruction map with native Gaussian rasterizer")
    reconstruction_render, reconstruction_memory = render_gaussian_map(
        reconstruction_vertex, cameras, output / "reconstruction", args.device, args.background
    )
    log("Rendering semantic map with the exact V1 cameras")
    semantic_render, semantic_memory = render_gaussian_map(
        semantic_vertex, cameras, output / "semantic", args.device, args.background
    )

    for name in VIEW_NAMES:
        make_pair(
            output / "reconstruction" / f"{name}.png",
            output / "semantic" / f"{name}.png",
            output / "paired" / f"{name}_reconstruction_vs_semantic.png",
        )

    common_viz = {
        "visualization_backend": "repository-native diff_gaussian_rasterization CUDA extension",
        "rendering_mode": "native anisotropic Gaussian splatting from saved PLY parameters",
        "image_resolution": [args.width, args.height],
        "point_or_gaussian_size": "saved exp(scale_0..2), renderer scale_modifier=1.0",
        "background_configuration": args.background,
        "camera_files": [f"cameras/{name}.json" for name in VIEW_NAMES],
        "camera_source_directory": str(camera_dir) if camera_dir else None,
        "camera_source_sha256": {
            name: sha256_file(path) for name, path in camera_sources.items()
        },
        "repo_commit_sha": commit,
        "branch": branch,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "coordinate_transform": "No geometry transform; PLY xyz used directly in saved first-frame-relative world coordinates.",
    }
    reconstruction_meta.update(common_viz)
    reconstruction_meta["render_results"] = reconstruction_render
    reconstruction_meta["renderer_memory"] = reconstruction_memory
    semantic_meta.update(common_viz)
    semantic_meta.update(semantic_statistics(semantic_vertex, params_npz, class_mapping))
    semantic_meta["render_results"] = semantic_render
    semantic_meta["renderer_memory"] = semantic_memory
    semantic_meta["camera_correspondence"] = "Exact same camera JSON files used for reconstruction and semantic rendering."
    semantic_meta["geometry_exactly_matches_reconstruction_ply"] = same_geometry
    json_dump(output / "metadata" / "reconstruction_map.json", reconstruction_meta)
    json_dump(output / "metadata" / "semantic_map.json", semantic_meta)

    source_hashes_after = {str(path): sha256_file(path) for path in (reconstruction, semantic)}
    sources_unchanged = source_hashes_before == source_hashes_after
    images_nonempty = all(
        not result["empty_or_uniform"]
        for result in list(reconstruction_render.values()) + list(semantic_render.values())
    )
    camera_finite = all(
        np.isfinite(np.asarray(cam["world_to_camera_extrinsic"])).all()
        and np.isfinite(np.asarray(cam["intrinsic_matrix"])).all()
        for cam in cameras.values()
    )
    camera_correspondence = True
    v1_pass = sources_unchanged and images_nonempty and camera_finite
    v2_pass = v1_pass and same_geometry and camera_correspondence
    v1_status = "PASS_V1_FINAL_RECONSTRUCTION_VISUALIZATION" if v1_pass else "FAIL_V1_VALIDATION"
    v2_status = "PASS_V2_FINAL_SEMANTIC_VISUALIZATION" if v2_pass else "FAIL_V2_VALIDATION"
    finished = datetime.now(timezone.utc)
    validation = {
        "v1_status": v1_status,
        "v2_status": v2_status,
        "all_required_images_exist_and_nonzero": all(
            (output / kind / f"{name}.png").stat().st_size > 0
            for kind in ("reconstruction", "semantic") for name in VIEW_NAMES
        ),
        "resolution_correct": all(
            Image.open(output / kind / f"{name}.png").size == (args.width, args.height)
            for kind in ("reconstruction", "semantic") for name in VIEW_NAMES
        ),
        "same_camera_parameters_for_v1_and_v2": camera_correspondence,
        "all_map_gaussian_centers_inside_each_view": all(
            map_fit_by_view.values()
        ),
        "map_gaussian_centers_inside_by_view": map_fit_by_view,
        "images_nonempty_and_nonuniform": images_nonempty,
        "camera_parameters_finite": camera_finite,
        "source_ply_hashes_unchanged": sources_unchanged,
        "source_hashes_before": source_hashes_before,
        "source_hashes_after": source_hashes_after,
        "reconstruction_semantic_geometry_exact_match": same_geometry,
        "slam_rerun": False,
        "optimization_training_tracking_mapping_run": False,
        "offline_visualization_only": True,
    }

    summary = f"""# PHASE4-VB-001 Final Map Visualization Summary

- V1 status: `{v1_status}`
- V2 status: `{v2_status}`
- Reconstruction source: `{reconstruction}`
- Semantic source: `{semantic}`
- Gaussian count: `{reconstruction_header['vertex_count']}`
- Backend: repository-native `diff_gaussian_rasterization` CUDA extension
- Rendering mode: native anisotropic Gaussian splatting from saved PLY parameters
- Viewpoints: `{list(VIEW_NAMES)}`
- Resolution: `{args.width}x{args.height}` per map image
- Background: `{args.background}`
- All map Gaussian centers fit inside every camera: `{validation['all_map_gaussian_centers_inside_each_view']}`
- Exact V1/V2 camera correspondence: `{camera_correspondence}`
- Reconstruction/semantic geometry exact match: `{same_geometry}`
- Source PLY hashes unchanged: `{sources_unchanged}`
- SLAM rerun: `False`
- Training/mapping/tracking/optimization: `False`
- Started UTC: `{started.isoformat()}`
- Finished UTC: `{finished.isoformat()}`

## Validation

```json
{json.dumps(validation, indent=2, sort_keys=True)}
```

## Interpretation

These images are deterministic free-view renders of the complete saved Gaussian map.
They are not dataset camera-frame renders and do not recompute evaluation metrics.
The semantic render preserves the saved learned semantic colors without palette recoloring.
"""
    (output / "metadata" / "visualization_summary.md").write_text(summary, encoding="utf-8")
    json_dump(output / "metadata" / "validation_report.json", validation)
    log(f"V1 status={v1_status}")
    log(f"V2 status={v2_status}")
    log("No SLAM, optimization, training, tracking, mapping, or evaluation executed")
    (output / "logs" / "visualization.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")

    artifact_specs: list[tuple[Path, str, str | None, str | None]] = []
    for kind, source_map in (("reconstruction", "params.ply"), ("semantic", "seg_params.ply")):
        for name in VIEW_NAMES:
            artifact_specs.append((output / kind / f"{name}.png", f"{kind}_image", source_map, name))
    for name in VIEW_NAMES:
        artifact_specs.append((output / "paired" / f"{name}_reconstruction_vs_semantic.png", "paired_preview", "both", name))
        artifact_specs.append((output / "cameras" / f"{name}.json", "camera_parameters", "both", name))
    for filename, artifact_type in (
        ("reconstruction_map.json", "map_metadata"),
        ("semantic_map.json", "map_metadata"),
        ("validation_report.json", "validation_report"),
        ("visualization_summary.md", "summary"),
    ):
        artifact_specs.append((output / "metadata" / filename, artifact_type, None, None))
    artifact_specs.append((output / "logs" / "visualization.log", "log", None, None))
    manifest = {
        "status": {"v1": v1_status, "v2": v2_status},
        "generated_artifacts": [
            image_record(path, output, artifact_type, source_map, viewpoint)
            for path, artifact_type, source_map, viewpoint in artifact_specs
        ],
        "manifest_self_entry_note": "The manifest does not hash itself because that would be self-referential.",
        "generated_artifact_count_excluding_manifest": len(artifact_specs),
        "repo_commit_sha": commit,
        "branch": branch,
    }
    json_dump(output / "metadata" / "visualization_manifest.json", manifest)

    git_status_after = git_value(repo_root, "status", "--short")
    print(json.dumps({
        "v1_status": v1_status,
        "v2_status": v2_status,
        "output": str(output),
        "git_status_before": git_status_before,
        "git_status_after": git_status_after,
    }, indent=2))
    return 0 if v1_pass and v2_pass else 2


if __name__ == "__main__":
    sys.exit(main())
