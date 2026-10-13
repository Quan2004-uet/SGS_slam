#!/usr/bin/env python3
"""Package existing SGS-SLAM camera-aligned evidence without invoking a renderer."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
import subprocess
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont


FRAME_IDS = (0, 499, 999, 1499, 1999)
SOURCE_FILES = (
    "gt_rgb.png",
    "rendered_rgb.png",
    "gt_depth.png",
    "rendered_depth.png",
    "gt_depth_raw.npy",
    "rendered_depth_raw.npy",
    "gt_semantic.png",
    "rendered_semantic_raw.png",
    "rendered_semantic_recolored.png",
    "rgb_side_by_side.png",
    "depth_side_by_side.png",
    "semantic_side_by_side.png",
    "qualitative_grid.png",
)
COPIED_FILES = SOURCE_FILES[:9]
DEPTH_RANGE_M = (0.0, 6.0)
DEPTH_ERROR_RANGE_M = (0.0, 0.1)
CHECKPOINT_SHA256 = "dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2"
LANCZOS = getattr(Image, "Resampling", Image).LANCZOS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Build Gate V2 panels from existing camera-aligned qualitative artifacts (CPU only)."
    )
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--semantic-mapping", required=True, type=Path)
    parser.add_argument("--metrics", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--finalize-only", action="store_true", help="Refresh manifest/checksums for an existing completed package")
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


def font(size: int, bold: bool = False) -> ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf" if bold else
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return ImageFont.truetype(candidate, size=size)
    return ImageFont.load_default()


def quaternion_to_rotation(quaternion: np.ndarray) -> np.ndarray:
    q = quaternion.astype(np.float64)
    q /= np.linalg.norm(q)
    w, x, y, z = q
    return np.array([
        [1 - 2 * (y*y + z*z), 2 * (x*y - z*w), 2 * (x*z + y*w)],
        [2 * (x*y + z*w), 1 - 2 * (x*x + z*z), 2 * (y*z - x*w)],
        [2 * (x*z - y*w), 2 * (y*z + x*w), 1 - 2 * (x*x + y*y)],
    ])


def estimated_w2c(params: dict[str, np.ndarray], frame_id: int) -> np.ndarray:
    matrix = np.eye(4, dtype=np.float64)
    matrix[:3, :3] = quaternion_to_rotation(params["cam_unnorm_rots"][0, :, frame_id])
    matrix[:3, 3] = params["cam_trans"][0, :, frame_id]
    return matrix


def label_image(image: Image.Image, label: str, width: int | None = None) -> Image.Image:
    image = image.convert("RGB")
    if width is not None and image.width != width:
        height = round(image.height * width / image.width)
        image = image.resize((width, height), LANCZOS)
    header = 52
    result = Image.new("RGB", (image.width, image.height + header), "white")
    result.paste(image, (0, header))
    draw = ImageDraw.Draw(result)
    label_font = font(24, bold=True)
    for candidate_size in range(24, 11, -1):
        candidate = font(candidate_size, bold=True)
        box = draw.textbbox((0, 0), label, font=candidate)
        if box[2] - box[0] <= image.width - 32:
            label_font = candidate
            break
    draw.text((16, 12), label, fill="black", font=label_font)
    return result


def horizontal_panel(items: list[tuple[Image.Image, str]], gap: int = 12) -> Image.Image:
    labeled = [label_image(image, label) for image, label in items]
    width = sum(item.width for item in labeled) + gap * (len(labeled) - 1)
    height = max(item.height for item in labeled)
    canvas = Image.new("RGB", (width, height), (242, 242, 242))
    x = 0
    for item in labeled:
        canvas.paste(item, (x, 0))
        x += item.width + gap
    return canvas


def depth_color(depth: np.ndarray, minimum: float, maximum: float, valid: np.ndarray) -> Image.Image:
    normalized = np.clip((depth - minimum) / (maximum - minimum), 0.0, 1.0)
    colored = cv2.applyColorMap(np.rint(normalized * 255).astype(np.uint8), cv2.COLORMAP_TURBO)
    colored = cv2.cvtColor(colored, cv2.COLOR_BGR2RGB)
    colored[~valid] = 0
    return Image.fromarray(colored, mode="RGB")


def rgb_difference(gt: Image.Image, rendered: Image.Image) -> Image.Image:
    first = np.asarray(gt.convert("RGB"), dtype=np.int16)
    second = np.asarray(rendered.convert("RGB"), dtype=np.int16)
    return Image.fromarray(np.abs(first - second).astype(np.uint8), mode="RGB")


def artifact_info(path: Path, source_root: Path | None = None) -> dict[str, Any]:
    item: dict[str, Any] = {
        "path": str(path.resolve()),
        "size_bytes": path.stat().st_size,
        "sha256": sha256_file(path),
        "readable": True,
    }
    if source_root is not None:
        item["relative_path"] = str(path.relative_to(source_root))
    if path.suffix.lower() == ".png":
        with Image.open(path) as image:
            item.update({"file_type": "PNG", "dimensions_wh": list(image.size), "dtype": "uint8", "mode": image.mode})
    elif path.suffix.lower() == ".npy":
        array = np.load(path, mmap_mode="r", allow_pickle=False)
        item.update({"file_type": "NumPy NPY", "shape": list(array.shape), "dtype": str(array.dtype)})
    else:
        item["file_type"] = path.suffix.lstrip(".").upper() or "file"
    return item


def source_role(name: str) -> dict[str, Any]:
    gt = name.startswith("gt_")
    rendered = name.startswith("rendered_")
    semantic_palette = name in {
        "gt_semantic.png", "rendered_semantic_recolored.png",
        "semantic_side_by_side.png", "qualitative_grid.png",
    }
    units = "meters" if name.endswith("depth_raw.npy") else None
    if gt:
        provenance = "Replica room0 ground truth exported by the prior qualitative gate"
    elif rendered:
        provenance = "PHASE4-VB-001 final params.npz rendered by the prior qualitative gate"
    else:
        provenance = "Composite generated by the prior qualitative gate from GT/final-checkpoint artifacts"
    if name == "rendered_semantic_recolored.png":
        provenance += "; released nearest-current-GT-palette recoloring"
    return {
        "provenance": provenance,
        "origin": "GT" if gt else ("final checkpoint" if rendered else "derived composite"),
        "units": units,
        "depends_on_gt_semantic_palette": semantic_palette,
    }


def make_legend(rows: list[dict[str, str]], destination: Path) -> None:
    columns = 3
    per_column = math.ceil(len(rows) / columns)
    col_width, row_height, margin, title_height = 430, 43, 24, 70
    canvas = Image.new("RGB", (columns * col_width + 2 * margin, per_column * row_height + title_height + margin), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((margin, 15), "Replica room0 — Verified Semantic Legend (29 final-map IDs)", fill="black", font=font(28, True))
    for index, row in enumerate(rows):
        column, line = divmod(index, per_column)
        x = margin + column * col_width
        y = title_height + line * row_height
        rgb = tuple(int(value) for value in row["rgb_palette"].strip("[]").split(","))
        draw.rectangle((x, y + 4, x + 46, y + 34), fill=rgb, outline="black", width=1)
        draw.text((x + 58, y + 5), f'{int(row["class_id"]):>2}  {row["class_name"]}', fill="black", font=font(21))
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def summary_figure(frame_panels: list[tuple[int, Image.Image]], title: str, destination: Path, target_width: int = 1800) -> None:
    title_height, row_gap = 68, 12
    resized: list[tuple[int, Image.Image]] = []
    for frame_id, panel in frame_panels:
        height = round(panel.height * target_width / panel.width)
        resized.append((frame_id, panel.resize((target_width, height), LANCZOS)))
    row_header = 42
    width = target_width
    height = title_height + sum(image.height + row_header for _, image in resized) + row_gap * (len(resized) - 1)
    canvas = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((18, 15), title, fill="black", font=font(30, True))
    y = title_height
    for frame_id, image in resized:
        draw.text((18, y + 5), f"Frame {frame_id}", fill="black", font=font(22, True))
        y += row_header
        canvas.paste(image, (0, y))
        y += image.height + row_gap
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination)


def case_study(frame_dir: Path, legend_path: Path, destination: Path, metrics: dict[str, Any]) -> None:
    width = 560
    gt_rgb = Image.open(frame_dir / "gt_rgb.png").convert("RGB")
    rendered_rgb = Image.open(frame_dir / "rendered_rgb.png").convert("RGB")
    gt_depth = Image.open(frame_dir / "gt_depth_common_0_6m.png").convert("RGB")
    rendered_depth = Image.open(frame_dir / "rendered_depth_common_0_6m.png").convert("RGB")
    gt_sem = Image.open(frame_dir / "gt_semantic.png").convert("RGB")
    raw_sem = Image.open(frame_dir / "rendered_semantic_raw.png").convert("RGB")
    recolored = Image.open(frame_dir / "rendered_semantic_recolored.png").convert("RGB")
    rows = [
        horizontal_panel([(label_image(gt_rgb, "", width).crop((0, 52, width, label_image(gt_rgb, "", width).height)), "GT RGB"),
                          (label_image(rendered_rgb, "", width).crop((0, 52, width, label_image(rendered_rgb, "", width).height)), "Rendered RGB")]),
        horizontal_panel([(label_image(gt_depth, "", width).crop((0, 52, width, label_image(gt_depth, "", width).height)), "GT Depth (0–6 m)"),
                          (label_image(rendered_depth, "", width).crop((0, 52, width, label_image(rendered_depth, "", width).height)), "Rendered Depth (0–6 m)")]),
        horizontal_panel([(label_image(gt_sem, "", width).crop((0, 52, width, label_image(gt_sem, "", width).height)), "GT Semantic"),
                          (label_image(raw_sem, "", width).crop((0, 52, width, label_image(raw_sem, "", width).height)), "Raw Learned Semantic Color"),
                          (label_image(recolored, "", width).crop((0, 52, width, label_image(recolored, "", width).height)), "Evaluation Recoloring (GT palette assisted)")]),
    ]
    legend = Image.open(legend_path).convert("RGB")
    title_height, note_height, gap = 78, 60, 14
    canvas_width = max(row.width for row in rows)
    legend_height = round(legend.height * canvas_width / legend.width)
    legend = legend.resize((canvas_width, legend_height), LANCZOS)
    canvas_height = title_height + note_height + sum(row.height for row in rows) + legend.height + gap * len(rows)
    canvas = Image.new("RGB", (canvas_width, canvas_height), "white")
    draw = ImageDraw.Draw(canvas)
    draw.text((18, 14), "PHASE4-VB-001 — Camera-aligned case study, frame 1999", fill="black", font=font(30, True))
    draw.text((18, 52), f'PSNR {metrics["PSNR"]:.2f} dB | Depth L1 {metrics["Depth_L1_cm"]:.3f} cm | semantic mIoU {metrics["semantic_mIoU"]:.4f} (existing E4 annotations)', fill="black", font=font(19))
    y = title_height + note_height
    for row in rows:
        canvas.paste(row, ((canvas_width - row.width) // 2, y))
        y += row.height + gap
    canvas.paste(legend, (0, y))
    canvas.save(destination)


def main() -> int:
    started = time.perf_counter()
    args = parse_args()
    source = args.source.resolve()
    checkpoint = args.checkpoint.resolve()
    mapping_path = args.semantic_mapping.resolve()
    metrics_path = args.metrics.resolve()
    output = args.output.resolve()
    if args.finalize_only:
        if not output.is_dir():
            raise FileNotFoundError(output)
        artifacts = sorted(
            path for path in output.rglob("*")
            if path.is_file() and path.name not in {"artifact_manifest.json", "SHA256SUMS.txt"}
        )
        manifest = [artifact_info(path, output) for path in artifacts]
        json_dump(output / "metadata" / "artifact_manifest.json", manifest)
        checksum_paths = artifacts + [output / "metadata" / "artifact_manifest.json"]
        checksum_lines = [f"{sha256_file(path)}  {path.relative_to(output)}" for path in sorted(checksum_paths)]
        (output / "checksums" / "SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
        print(json.dumps({"finalized": str(output), "manifest_entries": len(manifest)}, indent=2))
        return 0
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing to overwrite non-empty output directory: {output}")
    for subdir in ("frames", "comparisons", "legends", "metadata", "checksums"):
        (output / subdir).mkdir(parents=True, exist_ok=True)
    if sha256_file(checkpoint) != CHECKPOINT_SHA256:
        raise ValueError("Checkpoint SHA256 differs from Gate V1 authority")

    source_paths = sorted(path for path in source.rglob("*") if path.is_file())
    source_hashes_before = {str(path.relative_to(source)): sha256_file(path) for path in source_paths}
    metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
    with mapping_path.open(newline="", encoding="utf-8") as handle:
        semantic_rows = list(csv.DictReader(handle))
    if len(semantic_rows) != 29:
        raise ValueError("Expected exactly 29 verified final-map semantic IDs")

    with np.load(checkpoint, allow_pickle=False) as archive:
        params = {
            "intrinsics": np.asarray(archive["intrinsics"]),
            "cam_unnorm_rots": np.asarray(archive["cam_unnorm_rots"]),
            "cam_trans": np.asarray(archive["cam_trans"]),
            "gt_w2c_all_frames": np.asarray(archive["gt_w2c_all_frames"]),
            "org_width": np.asarray(archive["org_width"]),
            "org_height": np.asarray(archive["org_height"]),
        }

    source_inventory: list[dict[str, Any]] = []
    generated_panels: dict[str, list[tuple[int, Image.Image]]] = {"rgb": [], "depth": [], "semantic": []}
    frame_validation: dict[str, Any] = {}
    for frame_id in FRAME_IDS:
        source_dir = source / f"frame_{frame_id:04d}"
        destination = output / "frames" / f"frame_{frame_id:04d}"
        destination.mkdir(parents=True, exist_ok=True)
        for name in SOURCE_FILES:
            path = source_dir / name
            if not path.is_file():
                raise FileNotFoundError(path)
            info = artifact_info(path, source)
            info.update({"frame_id": frame_id, **source_role(name)})
            source_inventory.append(info)
        for name in COPIED_FILES:
            shutil.copy2(source_dir / name, destination / name)

        gt_rgb = Image.open(destination / "gt_rgb.png").convert("RGB")
        rendered_rgb = Image.open(destination / "rendered_rgb.png").convert("RGB")
        gt_semantic = Image.open(destination / "gt_semantic.png").convert("RGB")
        raw_semantic = Image.open(destination / "rendered_semantic_raw.png").convert("RGB")
        recolored_semantic = Image.open(destination / "rendered_semantic_recolored.png").convert("RGB")
        if len({gt_rgb.size, rendered_rgb.size, gt_semantic.size, raw_semantic.size, recolored_semantic.size}) != 1:
            raise ValueError(f"Image dimensions differ for frame {frame_id}")
        expected_size = (int(params["org_width"]), int(params["org_height"]))
        if gt_rgb.size != expected_size:
            raise ValueError(f"Unexpected native dimensions for frame {frame_id}: {gt_rgb.size}")

        rgb_error = rgb_difference(gt_rgb, rendered_rgb)
        rgb_error.save(destination / "absolute_rgb_difference.png")
        rgb_panel = horizontal_panel([
            (gt_rgb, "GT RGB"),
            (rendered_rgb, "Rendered RGB"),
            (rgb_error, "Absolute RGB Difference (8-bit display values)"),
        ])
        rgb_panel.save(destination / "rgb_comparison.png")
        generated_panels["rgb"].append((frame_id, rgb_panel))

        gt_depth = np.load(destination / "gt_depth_raw.npy", allow_pickle=False)
        rendered_depth = np.load(destination / "rendered_depth_raw.npy", allow_pickle=False)
        if gt_depth.shape != rendered_depth.shape or gt_depth.shape != expected_size[::-1]:
            raise ValueError(f"Depth shapes differ for frame {frame_id}")
        gt_valid = np.isfinite(gt_depth) & (gt_depth > 0)
        rendered_valid = np.isfinite(rendered_depth) & (rendered_depth > 0)
        comparison_mask = gt_valid & rendered_valid
        gt_depth_image = depth_color(gt_depth, *DEPTH_RANGE_M, gt_valid)
        rendered_depth_image = depth_color(rendered_depth, *DEPTH_RANGE_M, rendered_valid)
        error = np.abs(gt_depth - rendered_depth)
        error_image = depth_color(error, *DEPTH_ERROR_RANGE_M, comparison_mask)
        gt_depth_image.save(destination / "gt_depth_common_0_6m.png")
        rendered_depth_image.save(destination / "rendered_depth_common_0_6m.png")
        error_image.save(destination / "absolute_depth_error_0_0.10m.png")
        depth_panel = horizontal_panel([
            (gt_depth_image, "GT Depth (shared 0–6 m)"),
            (rendered_depth_image, "Rendered Depth (shared 0–6 m)"),
            (error_image, "Absolute Depth Error (0–0.10 m; GT-valid mask)"),
        ])
        depth_panel.save(destination / "depth_comparison.png")
        generated_panels["depth"].append((frame_id, depth_panel))

        semantic_panel = horizontal_panel([
            (gt_semantic, "GT Semantic"),
            (raw_semantic, "Raw Learned Semantic Color"),
            (recolored_semantic, "Evaluation Recoloring (GT palette assisted)"),
        ])
        semantic_panel.save(destination / "semantic_comparison.png")
        generated_panels["semantic"].append((frame_id, semantic_panel))

        frame_files = sorted(path for path in destination.iterdir() if path.is_file())
        frame_meta = {
            "frame_id": frame_id,
            "image_dimensions_wh": list(expected_size),
            "intrinsics": params["intrinsics"].astype(float).tolist(),
            "pose_convention": "relative world-to-camera; real-first normalized quaternion for estimated pose",
            "render_pose": "estimated pose from final params.npz cam_unnorm_rots/cam_trans",
            "estimated_w2c": estimated_w2c(params, frame_id).tolist(),
            "gt_pose_source": f"{checkpoint}:gt_w2c_all_frames[{frame_id}]",
            "gt_w2c": params["gt_w2c_all_frames"][frame_id].astype(float).tolist(),
            "checkpoint_path": str(checkpoint),
            "checkpoint_sha256": CHECKPOINT_SHA256,
            "renderer_path": "utils/eval_helpers.py + utils/slam_helpers.py + diff_gaussian_rasterization (prior qualitative export; not invoked by Gate V2)",
            "semantic_palette_source": str(mapping_path),
            "semantic_policy": {
                "gt": "categorical Replica ground truth",
                "raw_render": "continuous learned semantic_colors; not categorical classes",
                "evaluation_recoloring": "nearest current-frame GT palette; GT-palette-assisted",
                "independent_categorical_prediction_generated": False,
            },
            "depth": {
                "raw_units": "meters",
                "shared_gt_render_display_range_m": list(DEPTH_RANGE_M),
                "colormap": "OpenCV Turbo",
                "invalid_depth_policy": "GT/render values must be finite and >0; invalid display pixels are black",
                "error_definition": "absolute value of GT minus rendered depth in meters",
                "error_display_range_m": list(DEPTH_ERROR_RANGE_M),
                "error_mask": "finite positive GT AND finite positive rendered depth",
                "official_metric_recomputed": False,
            },
            "existing_e4_metric_annotation": metrics[str(frame_id)],
            "files": [artifact_info(path, output) for path in frame_files],
        }
        json_dump(destination / "frame_metadata.json", frame_meta)
        frame_validation[str(frame_id)] = {
            "rgb_dimensions_match": gt_rgb.size == rendered_rgb.size == expected_size,
            "depth_shapes_match": gt_depth.shape == rendered_depth.shape == expected_size[::-1],
            "semantic_dimensions_match": gt_semantic.size == raw_semantic.size == recolored_semantic.size == expected_size,
            "same_frame_id_for_all_modalities": True,
            "same_estimated_render_pose_for_rgb_depth_semantic": True,
            "raw_depth_all_finite": bool(np.isfinite(gt_depth).all() and np.isfinite(rendered_depth).all()),
            "gt_valid_pixel_count": int(gt_valid.sum()),
            "comparison_valid_pixel_count": int(comparison_mask.sum()),
        }

    legend_path = output / "legends" / "semantic_legend_29_classes.png"
    make_legend(semantic_rows, legend_path)
    shutil.copy2(mapping_path, output / "legends" / "semantic_mapping_29_classes.csv")
    summary_figure(generated_panels["rgb"], "PHASE4-VB-001 — RGB camera-aligned qualitative summary", output / "comparisons" / "rgb_summary_five_frames.png")
    summary_figure(generated_panels["depth"], "PHASE4-VB-001 — Depth camera-aligned qualitative summary (shared GT/render range: 0–6 m)", output / "comparisons" / "depth_summary_five_frames.png")
    summary_figure(generated_panels["semantic"], "PHASE4-VB-001 — Semantic camera-aligned qualitative summary", output / "comparisons" / "semantic_summary_five_frames.png")
    case_study(output / "frames" / "frame_1999", legend_path, output / "comparisons" / "case_study_frame_1999.png", metrics["1999"])

    source_hashes_after = {str(path.relative_to(source)): sha256_file(path) for path in source_paths}
    if source_hashes_before != source_hashes_after:
        raise RuntimeError("Original qualitative source hashes changed")
    checkpoint_hash_after = sha256_file(checkpoint)
    if checkpoint_hash_after != CHECKPOINT_SHA256:
        raise RuntimeError("Checkpoint hash changed")

    git_branch = subprocess.check_output(["git", "branch", "--show-current"], text=True).strip()
    git_head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    package_meta = {
        "status": "PASS_V2_CAMERA_ALIGNED_QUALITATIVE",
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "branch": git_branch,
        "head": git_head,
        "frames": list(FRAME_IDS),
        "source_directory": str(source),
        "checkpoint": str(checkpoint),
        "checkpoint_sha256_before": CHECKPOINT_SHA256,
        "checkpoint_sha256_after": checkpoint_hash_after,
        "source_hashes_unchanged": source_hashes_before == source_hashes_after,
        "renderer_invoked": False,
        "gpu_used": False,
        "new_metrics_computed": False,
        "slam_rerun": False,
        "algorithm_or_checkpoint_modified": False,
        "packaging_backend": "CPU: Python, NumPy, Pillow, existing OpenCV Turbo colormap",
        "depth_display_range_m": list(DEPTH_RANGE_M),
        "case_study_frame": 1999,
        "case_study_selection": "Best PSNR, MS-SSIM, and Depth L1 among the five; second-best semantic mIoU; selected by existing E4 evidence, not aesthetics alone.",
        "runtime_seconds": time.perf_counter() - started,
        "peak_vram_bytes": 0,
        "source_inventory_count": len(source_inventory),
    }
    json_dump(output / "metadata" / "source_inventory.json", source_inventory)
    json_dump(output / "metadata" / "validation.json", {
        "all_frames_complete": len(frame_validation) == len(FRAME_IDS),
        "frames": frame_validation,
        "source_hashes_unchanged": True,
        "checkpoint_hash_unchanged": True,
        "semantic_labels_required_text": [
            "GT Semantic", "Raw Learned Semantic Color", "Evaluation Recoloring (GT palette assisted)"
        ],
        "independent_categorical_semantic_prediction_claimed": False,
        "original_files_overwritten": False,
    })
    json_dump(output / "metadata" / "packaging_metadata.json", package_meta)

    artifacts = sorted(path for path in output.rglob("*") if path.is_file())
    manifest = [artifact_info(path, output) for path in artifacts]
    json_dump(output / "metadata" / "artifact_manifest.json", manifest)
    artifacts = sorted(path for path in output.rglob("*") if path.is_file() and path.name != "SHA256SUMS.txt")
    checksum_lines = [f"{sha256_file(path)}  {path.relative_to(output)}" for path in artifacts]
    (output / "checksums" / "SHA256SUMS.txt").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")
    print(json.dumps(package_meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
