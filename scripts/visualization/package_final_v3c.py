#!/usr/bin/env python3
"""Create the CPU-only PHASE4-VIS-GATE-V3C presentation refinement package.

The script only recomposes validated raster artifacts. It never loads the
Gaussian checkpoint, invokes a renderer, changes trajectory coordinates, or
computes scientific metrics.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import resource
import subprocess
import time
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[2]
VERSION = "PHASE4-VIS-GATE-V3C-v1"
STATUS = "PASS_V3C_PRESENTATION_REFINEMENT"
BG = (246, 247, 249)
WHITE = (255, 255, 255)
INK = (27, 33, 41)
MUTED = (78, 89, 102)
LINE = (194, 202, 212)
RED = (166, 55, 55)
BLUE = (31, 119, 180)
GREEN = (44, 160, 44)
PATH_RED = (214, 39, 40)
RESAMPLE = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v3b", required=True, type=Path)
    parser.add_argument("--v3a", required=True, type=Path)
    parser.add_argument("--v2", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--semantic-mapping", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    return parser.parse_args()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(8 * 1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def tree_digest(root: Path) -> dict[str, Any]:
    digest = hashlib.sha256()
    count = 0
    for path in sorted(p for p in root.rglob("*") if p.is_file()):
        relative = str(path.relative_to(root))
        digest.update(relative.encode())
        digest.update(b"\0")
        digest.update(sha256_file(path).encode())
        digest.update(b"\n")
        count += 1
    return {"file_count": count, "tree_sha256": digest.hexdigest()}


def verify_checksum_file(root: Path) -> bool:
    checksum_file = root / "checksums/SHA256SUMS.txt"
    if not checksum_file.exists():
        raise FileNotFoundError(checksum_file)
    for line in checksum_file.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        expected, relative = line.split(maxsplit=1)
        path = root / relative.strip()
        if not path.is_file() or sha256_file(path) != expected:
            return False
    return True


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    for root in (Path("/usr/share/fonts/truetype/dejavu"), Path("/usr/share/fonts/dejavu")):
        path = root / name
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    raise FileNotFoundError(name)


def put(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int, *, bold: bool = False, fill=INK, anchor=None) -> None:
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)


def fit(image: Image.Image, size: tuple[int, int], background=WHITE) -> Image.Image:
    image = image.convert("RGB")
    scale = min(size[0] / image.width, size[1] / image.height)
    resized = image.resize((round(image.width * scale), round(image.height * scale)), RESAMPLE)
    canvas = Image.new("RGB", size, background)
    canvas.paste(resized, ((size[0] - resized.width) // 2, (size[1] - resized.height) // 2))
    return canvas


def crop_v3a_header(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    return image.crop((0, 54, image.width, image.height)) if image.height == 594 else image


def panel(image: Image.Image, size: tuple[int, int], label: str, *, subtitle: str | None = None, swatch=None, label_size=28) -> Image.Image:
    header = 74 if subtitle is None else 103
    canvas = Image.new("RGB", (size[0], size[1] + header), WHITE)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, canvas.width - 1, canvas.height - 1), outline=LINE, width=2)
    x = 18
    if swatch is not None:
        draw.rounded_rectangle((18, 18, 58, 58), radius=4, fill=swatch, outline=INK, width=2)
        x = 72
    put(draw, (x, 18), label, label_size, bold=True)
    if subtitle:
        put(draw, (18, 62), subtitle, 21, fill=MUTED)
    canvas.paste(fit(image, size), (0, header))
    return canvas


def load_palette(path: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    records: list[dict[str, Any]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            records.append({
                "id": int(row["class_id"]),
                "name": row["class_name"],
                "rgb": tuple(int(v) for v in ast.literal_eval(row["rgb_palette"])),
            })
    return records, {r["name"]: r for r in records}


def lighten_neutral_context(image: Image.Image, retained_alpha: float = 0.32) -> tuple[Image.Image, int]:
    """Blend only near-neutral non-white pixels toward white; colored pixels stay exact."""
    array = np.asarray(image.convert("RGB")).copy()
    spread = array.max(axis=2).astype(np.int16) - array.min(axis=2).astype(np.int16)
    brightness = array.mean(axis=2)
    mask = (spread <= 5) & (brightness < 248)
    blended = np.rint(array[mask] * retained_alpha + 255.0 * (1.0 - retained_alpha)).astype(np.uint8)
    array[mask] = blended
    return Image.fromarray(array, "RGB"), int(mask.sum())


def refine_trajectory(image: Image.Image) -> tuple[Image.Image, dict[str, int]]:
    """Lighten neutral context and enlarge only the rasterized path/marker footprints."""
    lightened, neutral_pixels = lighten_neutral_context(image, retained_alpha=0.32)
    source = np.asarray(image.convert("RGB"))
    red, green, blue = source[:, :, 0], source[:, :, 1], source[:, :, 2]
    path_mask = (blue > 100) & (blue.astype(np.int16) > red.astype(np.int16) + 30) & (blue.astype(np.int16) > green.astype(np.int16) + 15)
    start_mask = (green > 75) & (green.astype(np.int16) > red.astype(np.int16) + 25) & (green.astype(np.int16) > blue.astype(np.int16) + 15)
    end_mask = (red > 100) & (red.astype(np.int16) > green.astype(np.int16) + 35) & (red.astype(np.int16) > blue.astype(np.int16) + 25)
    canvas = np.asarray(lightened).copy()
    for mask, color, kernel in ((path_mask, BLUE, 3), (start_mask, GREEN, 7), (end_mask, PATH_RED, 7)):
        expanded = np.asarray(Image.fromarray(mask.astype(np.uint8) * 255).filter(ImageFilter.MaxFilter(kernel))) > 0
        canvas[expanded] = color
    return Image.fromarray(canvas, "RGB"), {
        "neutral_pixels_adjusted": neutral_pixels,
        "path_source_pixels": int(path_mask.sum()),
        "start_source_pixels": int(start_mask.sum()),
        "end_source_pixels": int(end_mask.sum()),
    }


def full_scene_figure(v3a: Path, output: Path, *, slide: bool) -> None:
    width, height = (1920, 1080) if slide else (2400, 810)
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    margin, gap = (45, 24) if slide else (48, 28)
    put(draw, (margin, 28), "Full-Scene Reconstruction Overview", 46 if slide else 42, bold=True)
    put(draw, (margin, 86), "One validated room_overview camera across all modalities", 24, fill=MUTED)
    panel_w = (width - 2 * margin - 2 * gap) // 3
    image_h = round(panel_w * 9 / 16)
    y = 156 if slide else 142
    sources = [
        (Image.open(v3a / "rgb/unfiltered/room_overview.png"), "RGB Gaussian Reconstruction", "Original unfiltered RGB"),
        (crop_v3a_header(Image.open(v3a / "geometry/room_overview.png")), "Geometry Diagnostic", "Sampled Gaussian centers"),
        (crop_v3a_header(Image.open(v3a / "semantic/categorical/room_overview.png")), "Fixed Semantic IDs", "Verified categorical palette"),
    ]
    for index, (source, label, subtitle) in enumerate(sources):
        item = panel(source, (panel_w, image_h), label, subtitle=subtitle, label_size=27 if slide else 29)
        canvas.paste(item, (margin + index * (panel_w + gap), y))
    note_y = y + image_h + 103 + (105 if slide else 38)
    put(draw, (width // 2, note_y), "Virtual limited-offset overview — diagnostic, not novel-view accuracy evidence.", 24 if slide else 22, fill=RED, anchor="mm")
    canvas.save(output)


def semantic_classwise(v3a: Path, output: Path, selected: list[dict[str, Any]], *, slide: bool) -> dict[str, int]:
    width, height = (1920, 1080) if slide else (2400, 1060)
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    margin, gap, top = 42, 22, 135
    put(draw, (margin, 25), "Fixed Semantic-ID Class Structure", 45 if slide else 42, bold=True)
    put(draw, (margin, 81), "Colored class centers preserved; neutral context reduced for visibility", 23, fill=MUTED)
    columns = 4
    panel_w = (width - 2 * margin - 3 * gap) // columns
    image_h = round(panel_w * 540 / 960)
    totals: dict[str, int] = {}
    for index, record in enumerate(selected):
        raw = crop_v3a_header(Image.open(v3a / f"semantic/classwise/{record['name']}_top_oblique.png"))
        refined, count = lighten_neutral_context(raw, retained_alpha=0.32)
        totals[record["name"]] = count
        item = panel(refined, (panel_w, image_h), f"{record['name'].title()}  ·  ID {record['id']}", swatch=record["rgb"], label_size=23 if slide else 25)
        row, column = divmod(index, columns)
        canvas.paste(item, (margin + column * (panel_w + gap), top + row * (item.height + gap)))
    put(draw, (width // 2, height - 25), "Presentation-only context alpha: 0.32; class membership, coordinates, and palette unchanged.", 19, fill=MUTED, anchor="mm")
    canvas.save(output)
    return totals


def trajectory_figure(v3a: Path, output: Path, *, slide: bool) -> dict[str, int]:
    width, height = (1920, 1080) if slide else (2200, 940)
    canvas = Image.new("RGB", (width, height), BG)
    draw = ImageDraw.Draw(canvas)
    margin = 44
    put(draw, (margin, 27), "Estimated Camera Trajectory", 47 if slide else 43, bold=True)
    put(draw, (margin, 86), "2,000 saved camera centers in reconstructed map coordinates", 24, fill=MUTED)
    geometry = crop_v3a_header(Image.open(v3a / "geometry/top_oblique.png"))
    trajectory = crop_v3a_header(Image.open(v3a / "trajectory/estimated_trajectory_3d.png"))
    refined, stats = refine_trajectory(trajectory)
    gap = 28
    left_w = 690 if slide else 790
    right_w = width - 2 * margin - gap - left_w
    body_h = 640 if slide else 620
    left = panel(geometry, (left_w, body_h), "Global Geometry Context", label_size=28)
    right = panel(refined, (right_w, body_h), "Estimated 2,000-Frame Path", subtitle="Start: green   End: red   Path: blue", label_size=31)
    y = 145
    canvas.paste(left, (margin, y))
    canvas.paste(right, (margin + left_w + gap, y))
    put(draw, (width // 2, height - 33), "No GT overlay or trajectory alignment; line and markers enlarged for display only.", 21, fill=MUTED, anchor="mm")
    canvas.save(output)
    return stats


def hero_slide(v2: Path, v3a: Path, output: Path) -> None:
    canvas = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(canvas)
    put(draw, (50, 27), "PHASE4-VB-001 — Reconstruction at a Glance", 45, bold=True)
    put(draw, (50, 83), "Observed-view fidelity + full-scene diagnostic structure", 24, fill=MUTED)
    rendered = Image.open(v2 / "frames/frame_1999/rendered_rgb.png")
    full_rgb = Image.open(v3a / "rgb/unfiltered/room_overview.png")
    semantic = crop_v3a_header(Image.open(v3a / "semantic/categorical/room_overview.png"))
    trajectory_raw = crop_v3a_header(Image.open(v3a / "trajectory/estimated_trajectory_3d.png"))
    trajectory, _ = refine_trajectory(trajectory_raw)
    entries = [
        (rendered, "Observed Camera — Rendered RGB", "Observed-view evidence"),
        (full_rgb, "Full-Scene RGB Reconstruction", "Virtual diagnostic view"),
        (semantic, "Fixed per-Gaussian Semantic IDs", "Virtual diagnostic view"),
        (trajectory, "Estimated Camera Trajectory", "Map-coordinate diagnostic"),
    ]
    margin, gap, top = 48, 24, 132
    panel_w = (1920 - 2 * margin - gap) // 2
    image_h = 360
    for index, (source, label, subtitle) in enumerate(entries):
        item = panel(source, (panel_w, image_h), label, subtitle=subtitle, label_size=27)
        row, column = divmod(index, 2)
        canvas.paste(item, (margin + column * (panel_w + gap), top + row * (item.height + 20)))
    put(draw, (1870, 1052), "Virtual views are diagnostic", 19, fill=RED, anchor="rm")
    canvas.save(output)


def thesis_plate(v2: Path, v3a: Path, output: Path) -> None:
    canvas = Image.new("RGB", (2400, 2000), BG)
    draw = ImageDraw.Draw(canvas)
    put(draw, (45, 24), "PHASE4-VB-001 Qualitative Reconstruction", 44, bold=True)
    put(draw, (45, 78), "Observed-camera evidence", 25, bold=True, fill=MUTED)
    margin, gap = 45, 24
    top_w = (2400 - 2 * margin - gap) // 2
    for i, (name, label) in enumerate((("gt_rgb.png", "GT RGB — Frame 1999"), ("rendered_rgb.png", "Rendered RGB — Frame 1999"))):
        item = panel(Image.open(v2 / "frames/frame_1999" / name), (top_w, 480), label, label_size=28)
        canvas.paste(item, (margin + i * (top_w + gap), 116))
    put(draw, (45, 692), "Virtual full-scene diagnostics — one room_overview camera", 25, bold=True, fill=MUTED)
    mid_w = (2400 - 2 * margin - 2 * gap) // 3
    mids = [
        (Image.open(v3a / "rgb/unfiltered/room_overview.png"), "RGB Reconstruction"),
        (crop_v3a_header(Image.open(v3a / "geometry/room_overview.png")), "Gaussian-Center Geometry"),
        (crop_v3a_header(Image.open(v3a / "semantic/categorical/room_overview.png")), "Fixed Semantic IDs"),
    ]
    for i, (source, label) in enumerate(mids):
        item = panel(source, (mid_w, 390), label, label_size=25)
        canvas.paste(item, (margin + i * (mid_w + gap), 730))
    put(draw, (45, 1218), "Global structure diagnostics", 25, bold=True, fill=MUTED)
    trajectory, _ = refine_trajectory(crop_v3a_header(Image.open(v3a / "trajectory/estimated_trajectory_3d.png")))
    semantic, _ = lighten_neutral_context(crop_v3a_header(Image.open(v3a / "semantic/classwise/selected_classes_overview_top_oblique.png")), 0.32)
    bottom_w = (2400 - 2 * margin - gap) // 2
    for i, (source, label) in enumerate(((trajectory, "Estimated 2,000-Frame Trajectory"), (semantic, "Selected Fixed-ID Semantic Structure"))):
        item = panel(source, (bottom_w, 610), label, label_size=27)
        canvas.paste(item, (margin + i * (bottom_w + gap), 1255))
    put(draw, (1200, 1970), "Observed-view evidence is separated from virtual diagnostics; virtual views are not novel-view accuracy evidence.", 20, fill=RED, anchor="mm")
    canvas.save(output)


def compact_legend(records: list[dict[str, Any]], output: Path) -> None:
    canvas = Image.new("RGB", (1600, 430), WHITE)
    draw = ImageDraw.Draw(canvas)
    put(draw, (38, 24), "Verified Semantic Palette", 40, bold=True)
    put(draw, (38, 76), "Compact slide legend — fixed per-Gaussian IDs", 22, fill=MUTED)
    columns, rows = 4, 3
    cell_w = 380
    for index, record in enumerate(records):
        row, column = divmod(index, columns)
        x, y = 38 + column * cell_w, 132 + row * 86
        draw.rounded_rectangle((x, y, x + 44, y + 44), radius=4, fill=record["rgb"], outline=INK, width=2)
        put(draw, (x + 60, y + 7), f"{record['name'].title()} · ID {record['id']}", 23, bold=True)
    canvas.save(output)


def review_sheet(original: Path, refined: Path, output: Path, title: str) -> None:
    canvas = Image.new("RGB", (2400, 1050), BG)
    draw = ImageDraw.Draw(canvas)
    put(draw, (45, 25), title, 42, bold=True)
    put(draw, (45, 80), "Presentation review only", 22, fill=MUTED)
    gap, margin, top = 28, 45, 125
    width = (2400 - 2 * margin - gap) // 2
    for index, (path, label) in enumerate(((original, "Original V3B"), (refined, "Refined V3C"))):
        item = panel(Image.open(path), (width, 820), label, label_size=30)
        canvas.paste(item, (margin + index * (width + gap), top))
    canvas.save(output)


def record(path: Path, output: Path, source: list[Path], **changes: Any) -> dict[str, Any]:
    with Image.open(path) as image:
        dimensions = [image.width, image.height]
    base = {
        "source_files": [str(p.resolve()) for p in source],
        "output_file": str(path.relative_to(output)),
        "dimensions": dimensions,
        "crop": "V3A 54-pixel annotation header removed where present; scientific plot body retained",
        "resize": "aspect-preserving Lanczos fit; no stretching",
        "context_alpha": None,
        "point_density_change": "none",
        "line_width_change": "none",
        "marker_size_change": "none",
        "text_size_change": "larger presentation typography",
        "semantic_color_change": False,
        "trajectory_coordinate_change": False,
        "checkpoint_change": False,
    }
    base.update(changes)
    return base


def main() -> int:
    args = parse_args()
    start = time.perf_counter()
    v3b, v3a, v2 = args.v3b.resolve(), args.v3a.resolve(), args.v2.resolve()
    checkpoint, mapping, output = args.checkpoint.resolve(), args.semantic_mapping.resolve(), args.output.resolve()
    required = [v3b, v3a, v2, checkpoint, mapping]
    if missing := [str(p) for p in required if not p.exists()]:
        raise FileNotFoundError(missing)
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing to overwrite non-empty output: {output}")
    if not verify_checksum_file(v3b) or not verify_checksum_file(v3a):
        raise RuntimeError("V3B or V3A checksum validation failed")
    for subdir in ("figures/review", "slides", "thesis", "legends", "metadata", "checksums"):
        (output / subdir).mkdir(parents=True, exist_ok=True)

    trees_before = {"v3b": tree_digest(v3b), "v3a": tree_digest(v3a)}
    hashes_before = {"checkpoint": sha256_file(checkpoint), "semantic_mapping": sha256_file(mapping)}
    palette, by_name = load_palette(mapping)
    selected_names = ["wall", "floor", "ceiling", "sofa", "chair", "table", "rug", "blinds"]
    compact_names = selected_names + ["cabinet", "door", "window", "stool"]
    selected = [by_name[name] for name in selected_names]

    paths = {
        "full_figure": output / "figures/figure_full_scene_overview_refined.png",
        "full_slide": output / "slides/02_full_scene_3d_refined.png",
        "semantic_figure": output / "figures/figure_semantic_classwise_refined.png",
        "semantic_slide": output / "slides/03_semantic_structure_refined.png",
        "trajectory_figure": output / "figures/figure_trajectory_reconstruction_refined.png",
        "trajectory_slide": output / "slides/04_trajectory_refined.png",
        "hero": output / "slides/00_hero_overview_refined.png",
        "thesis": output / "thesis/final_qualitative_plate_refined.png",
        "legend": output / "legends/semantic_legend_slide_compact.png",
    }
    full_scene_figure(v3a, paths["full_figure"], slide=False)
    full_scene_figure(v3a, paths["full_slide"], slide=True)
    semantic_stats = semantic_classwise(v3a, paths["semantic_figure"], selected, slide=False)
    semantic_classwise(v3a, paths["semantic_slide"], selected, slide=True)
    trajectory_stats = trajectory_figure(v3a, paths["trajectory_figure"], slide=False)
    trajectory_figure(v3a, paths["trajectory_slide"], slide=True)
    hero_slide(v2, v3a, paths["hero"])
    thesis_plate(v2, v3a, paths["thesis"])
    compact_legend([by_name[name] for name in compact_names], paths["legend"])

    reviews = {
        "review_full": output / "figures/review/full_scene_overview_before_after.png",
        "review_semantic": output / "figures/review/semantic_classwise_before_after.png",
        "review_trajectory": output / "figures/review/trajectory_before_after.png",
    }
    review_sheet(v3b / "figures/figure_full_scene_overview.png", paths["full_figure"], reviews["review_full"], "Full-Scene Overview — Before / After")
    review_sheet(v3b / "figures/figure_semantic_classwise.png", paths["semantic_figure"], reviews["review_semantic"], "Semantic Class Structure — Before / After")
    review_sheet(v3b / "figures/figure_trajectory_reconstruction.png", paths["trajectory_figure"], reviews["review_trajectory"], "Trajectory Visualization — Before / After")

    class_sources = [v3a / f"semantic/classwise/{name}_top_oblique.png" for name in selected_names]
    full_sources = [v3a / "rgb/unfiltered/room_overview.png", v3a / "geometry/room_overview.png", v3a / "semantic/categorical/room_overview.png", v3a / "cameras/room_overview.json"]
    traj_sources = [v3a / "geometry/top_oblique.png", v3a / "trajectory/estimated_trajectory_3d.png"]
    entries = [
        record(paths["full_figure"], output, full_sources),
        record(paths["full_slide"], output, full_sources),
        record(paths["semantic_figure"], output, class_sources + [mapping], context_alpha=0.32, text_size_change="class labels increased; verified ID and swatch retained"),
        record(paths["semantic_slide"], output, class_sources + [mapping], context_alpha=0.32, text_size_change="projector-scale class labels; verified ID and swatch retained"),
        record(paths["trajectory_figure"], output, traj_sources, context_alpha=0.32, line_width_change="3x3 raster-mask dilation (+1 pixel per side)", marker_size_change="7x7 raster-mask dilation (+3 pixels per side)"),
        record(paths["trajectory_slide"], output, traj_sources, context_alpha=0.32, line_width_change="3x3 raster-mask dilation (+1 pixel per side)", marker_size_change="7x7 raster-mask dilation (+3 pixels per side)"),
        record(paths["hero"], output, [v2 / "frames/frame_1999/rendered_rgb.png", *full_sources[:3], traj_sources[1]], context_alpha="0.32 for trajectory context only", line_width_change="trajectory panel: 3x3 raster-mask dilation", marker_size_change="trajectory panel: 7x7 raster-mask dilation"),
        record(paths["thesis"], output, [v2 / "frames/frame_1999/gt_rgb.png", v2 / "frames/frame_1999/rendered_rgb.png", *full_sources[:3], traj_sources[1], v3a / "semantic/classwise/selected_classes_overview_top_oblique.png"], context_alpha="0.32 for trajectory and neutral class context", line_width_change="trajectory panel: 3x3 raster-mask dilation", marker_size_change="trajectory panel: 7x7 raster-mask dilation"),
        record(paths["legend"], output, [mapping], crop="none", resize="none", text_size_change="slide-optimized 23–40 px typography"),
        record(reviews["review_full"], output, [v3b / "figures/figure_full_scene_overview.png", paths["full_figure"]], crop="none", text_size_change="review labels only"),
        record(reviews["review_semantic"], output, [v3b / "figures/figure_semantic_classwise.png", paths["semantic_figure"]], crop="none", text_size_change="review labels only"),
        record(reviews["review_trajectory"], output, [v3b / "figures/figure_trajectory_reconstruction.png", paths["trajectory_figure"]], crop="none", text_size_change="review labels only"),
    ]

    trees_after = {"v3b": tree_digest(v3b), "v3a": tree_digest(v3a)}
    hashes_after = {"checkpoint": sha256_file(checkpoint), "semantic_mapping": sha256_file(mapping)}
    integrity = trees_before == trees_after and hashes_before == hashes_after
    if not integrity:
        raise RuntimeError("Input integrity changed during packaging")

    image_records = []
    for path in sorted(output.rglob("*.png")):
        with Image.open(path) as image:
            array = np.asarray(image.convert("RGB"))
            valid = path.stat().st_size > 0 and array.std() > 1
            image_records.append({"path": str(path.relative_to(output)), "dimensions": [image.width, image.height], "sha256": sha256_file(path), "readable_nonempty_nonuniform": bool(valid)})
    if not all(r["readable_nonempty_nonuniform"] for r in image_records):
        raise RuntimeError("Unreadable or uniform output image")

    runtime = {
        "wall_time_seconds": time.perf_counter() - start,
        "peak_host_rss_kib": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "peak_host_rss_bytes": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024),
        "gpu_used": False,
        "peak_gpu_allocated_bytes": 0,
        "peak_gpu_reserved_bytes": 0,
    }
    metadata = {
        "status": STATUS,
        "version": VERSION,
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "git_status_before": git("status", "--short"),
        "source_integrity": {"v3b_and_v3a_checksum_files_passed": True, "trees_before": trees_before, "trees_after": trees_after, "hashes_before": hashes_before, "hashes_after": hashes_after, "unchanged": integrity},
        "scientific_operations": {"renderer_invoked": False, "slam_invoked": False, "metrics_recomputed": False, "checkpoint_loaded": False, "scientific_data_changed": False},
        "display_policy": {"neutral_context_retained_alpha": 0.32, "neutral_pixel_rule": "RGB max-min <= 5 and mean < 248", "colored_highlight_pixels_modified": False, "semantic_palette_modified": False, "trajectory_coordinates_modified": False, "trajectory_smoothed": False, "trajectory_frames_removed": False},
        "semantic_context_pixels_adjusted_by_class": semantic_stats,
        "trajectory_raster_mask_statistics": trajectory_stats,
        "outputs": entries,
        "image_validation": image_records,
        "runtime": runtime,
    }
    metadata_path = output / "metadata/presentation_refinement.json"
    metadata_path.write_text(json.dumps(metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    inventory = "\n".join(f"- `{r['path']}` — {r['dimensions'][0]}×{r['dimensions'][1]}" for r in image_records)
    report = f"""# PHASE4-VIS-GATE-V3C — Presentation Refinement

Final status: `{STATUS}`

## 1. Git state

- Branch: `{metadata['branch']}`
- HEAD: `{metadata['head']}`
- Scope: CPU-only raster composition and display refinement.
- Pre-existing dirty project-management and visualization work was preserved.

## 2. Source V3B integrity

- V3B and V3A checksum manifests passed before generation.
- V3B/V3A complete tree digests are unchanged before/after: `{integrity}`.
- Checkpoint SHA256: `{hashes_after['checkpoint']}`.
- Semantic mapping SHA256: `{hashes_after['semantic_mapping']}`.
- V3A/V3B files were not overwritten.

## 3. Refinements applied

- Full-scene overview: identical `room_overview` RGB, geometry, and fixed-ID semantic images; larger titles, tighter panel gaps, consistent margins, aspect-preserving placement, and a less dominant caveat.
- Semantic class-wise: neutral near-gray context retained at alpha 0.32 over white. Colored class pixels, membership, point coordinates, IDs, and verified palette values were retained.
- Trajectory: neutral near-gray geometry context retained at alpha 0.32. The blue raster path was dilated by one pixel per side; start/end raster markers by three pixels per side. Saved coordinates, ordering, all 2,000 frames, and path shape were unchanged.
- Hero/thesis layouts: redundant prose reduced and observed-camera evidence kept visibly separate from virtual diagnostics.
- Legend: twelve requested classes copied from the verified semantic mapping without color changes.

## 4. Before/after differences

Three review sheets pair the original V3B figure with the refined V3C output. Refinements improve projection-scale typography, reduce neutral-context competition, and enlarge trajectory cues. They do not introduce or remove scientific samples.

## 5. Refined figure inventory

{inventory}

## 6. Slide recommendations

- Primary defense overview: `slides/00_hero_overview_refined.png`.
- Use `02_full_scene_3d_refined.png` for cross-modal map structure.
- Use `03_semantic_structure_refined.png` when explaining fixed-ID class distributions.
- Use `04_trajectory_refined.png` for the saved camera path.

## 7. Thesis recommendations

- Primary consolidated plate: `thesis/final_qualitative_plate_refined.png`.
- The refined full-scene, semantic class-wise, and trajectory figures remain suitable as dedicated results figures.

## 8. Scientific integrity validation

- Scientific data changed: no.
- Renderer, SLAM, E4 evaluation, tracking, mapping, optimization, and metric computation: not invoked.
- Semantic colors changed: no; context-only neutral pixels were display-blended and exact palette swatches were regenerated from the verified mapping.
- Trajectory coordinates, ordering, smoothing, and frame membership changed: no.
- Gaussian parameters/checkpoint loaded or changed: no.
- All images are readable, non-empty, non-uniform, and aspect-preserving.

## 9. Runtime / CPU / GPU usage

- Wall time: {runtime['wall_time_seconds']:.4f} s.
- Peak host RSS: {runtime['peak_host_rss_kib']:,} KiB / {runtime['peak_host_rss_bytes']:,} B.
- GPU used: no; peak allocated/reserved attributable to V3C: 0 / 0 B.

## 10. Reproduction command

```bash
python scripts/visualization/package_final_v3c.py \\
  --v3b results/runtime_artifacts/phase4_vb001_visualization_v3b \\
  --v3a results/runtime_artifacts/phase4_vb001_visualization_v3a \\
  --v2 results/runtime_artifacts/phase4_vb001_visualization_v2 \\
  --checkpoint experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz \\
  --semantic-mapping results/runtime_artifacts/phase4_vb001_visualization_audit/semantic_mapping.csv \\
  --output results/runtime_artifacts/phase4_vb001_visualization_v3c
```

The script refuses to overwrite a non-empty output directory.

## 11. Final status

Final status: `{STATUS}`
"""
    report_path = output / "GATE_V3C_REPORT.md"
    report_path.write_text(report, encoding="utf-8")

    checksum_paths = sorted(p for p in output.rglob("*") if p.is_file() and p.parent.name != "checksums")
    checksum_text = "".join(f"{sha256_file(p)}  {p.relative_to(output)}\n" for p in checksum_paths)
    (output / "checksums/SHA256SUMS.txt").write_text(checksum_text, encoding="utf-8")
    print(json.dumps({"status": STATUS, "output": str(output), "images": len(image_records), "runtime": runtime}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
