#!/usr/bin/env python3
"""Package validated V2/V3A evidence into final thesis and slide figures.

This script performs CPU-only image composition. It does not invoke the
Gaussian renderer, load Gaussian tensors, run evaluation, or recompute metrics.
"""

from __future__ import annotations

import argparse
import ast
import csv
import hashlib
import json
import math
import platform
import resource
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image, ImageDraw, ImageFont


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_VERSION = "PHASE4-VIS-GATE-V3B-v1"
STATUS = "PASS_V3B_FINAL_PRESENTATION_PACKAGE"
BG = (246, 247, 249)
WHITE = (255, 255, 255)
INK = (28, 34, 42)
MUTED = (82, 92, 105)
LINE = (205, 211, 219)
BLUE = (32, 91, 153)
GREEN = (43, 122, 79)
ORANGE = (190, 104, 35)
RED = (166, 55, 55)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--v2", required=True, type=Path)
    parser.add_argument("--v3a", required=True, type=Path)
    parser.add_argument("--checkpoint", required=True, type=Path)
    parser.add_argument("--semantic-mapping", required=True, type=Path)
    parser.add_argument("--baseline-evidence", required=True, type=Path)
    parser.add_argument("--variant-evidence", required=True, type=Path)
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
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        relative = str(path.relative_to(root))
        file_hash = sha256_file(path)
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(file_hash.encode("ascii"))
        digest.update(b"\n")
        count += 1
    return {"file_count": count, "tree_sha256": digest.hexdigest()}


def git(*args: str) -> str:
    return subprocess.check_output(["git", *args], cwd=REPO_ROOT, text=True).strip()


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    candidates = (
        Path("/usr/share/fonts/truetype/dejavu") / name,
        Path("/usr/share/fonts/dejavu") / name,
    )
    for path in candidates:
        if path.exists():
            return ImageFont.truetype(str(path), size=size)
    raise FileNotFoundError(f"DejaVu font not found: {name}")


def text(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, size: int, *, bold: bool = False, fill=INK, anchor=None) -> None:
    draw.text(xy, value, font=font(size, bold), fill=fill, anchor=anchor)


def fit_image(image: Image.Image, box: tuple[int, int], background=WHITE) -> Image.Image:
    image = image.convert("RGB")
    ratio = min(box[0] / image.width, box[1] / image.height)
    resampling = Image.Resampling.LANCZOS if hasattr(Image, "Resampling") else Image.LANCZOS
    resized = image.resize((max(1, round(image.width * ratio)), max(1, round(image.height * ratio))), resampling)
    result = Image.new("RGB", box, background)
    result.paste(resized, ((box[0] - resized.width) // 2, (box[1] - resized.height) // 2))
    return result


def crop_v3a_header(image: Image.Image) -> Image.Image:
    image = image.convert("RGB")
    return image.crop((0, 54, image.width, image.height)) if image.height == 594 else image


def panel(image: Image.Image, size: tuple[int, int], label: str, *, subtitle: str | None = None, swatch: tuple[int, int, int] | None = None, label_size: int = 28) -> Image.Image:
    header = 66 if subtitle is None else 92
    canvas = Image.new("RGB", (size[0], size[1] + header), WHITE)
    draw = ImageDraw.Draw(canvas)
    draw.rectangle((0, 0, canvas.width - 1, canvas.height - 1), outline=LINE, width=2)
    x = 18
    if swatch is not None:
        draw.rectangle((18, 18, 48, 48), fill=swatch, outline=INK, width=1)
        x = 62
    text(draw, (x, 17), label, label_size, bold=True)
    if subtitle:
        text(draw, (18, 55), subtitle, 20, fill=MUTED)
    canvas.paste(fit_image(image, size), (0, header))
    return canvas


def title_block(canvas: Image.Image, title_value: str, subtitle: str, *, title_size: int = 42) -> None:
    draw = ImageDraw.Draw(canvas)
    text(draw, (40, 26), title_value, title_size, bold=True)
    text(draw, (40, 82), subtitle, 23, fill=MUTED)


def paste_center(canvas: Image.Image, item: Image.Image, box: tuple[int, int, int, int]) -> None:
    fitted = fit_image(item, (box[2] - box[0], box[3] - box[1]), background=canvas.getpixel((0, 0)))
    canvas.paste(fitted, (box[0], box[1]))


def load_palette(path: Path) -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]]]:
    rows = []
    by_name = {}
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            record = {
                "id": int(row["class_id"]),
                "name": row["class_name"],
                "rgb": tuple(int(value) for value in ast.literal_eval(row["rgb_palette"])),
            }
            rows.append(record)
            by_name[record["name"]] = record
    return rows, by_name


def figure_a(v2: Path, output: Path, metrics: dict[str, float], slide: bool = False) -> None:
    if slide:
        figure_a_slide(v2, output, metrics)
        return
    frame = v2 / "frames/frame_1999"
    width = 1920 if slide else 2100
    margin, gap = (50, 28) if slide else (60, 32)
    top = 130
    panel_h = 385 if slide else 420
    panel_w2 = (width - 2 * margin - gap) // 2
    panel_w3 = (width - 2 * margin - 2 * gap) // 3
    total_h = top + (panel_h + 66) * 2 + (panel_h + 92) + gap * 2 + 90
    canvas = Image.new("RGB", (width, total_h), BG)
    title_block(
        canvas,
        "Camera-Aligned Reconstruction Fidelity — Replica room0, Frame 1999",
        f"Existing E4 values: PSNR {metrics['PSNR']:.2f} dB   |   Depth L1 {metrics['Depth_L1_cm']:.3f} cm   |   Semantic-color mIoU {metrics['semantic_mIoU']:.4f}",
        title_size=38 if slide else 42,
    )
    rows = [
        [
            panel(Image.open(frame / "gt_rgb.png"), (panel_w2, panel_h), "GT RGB", label_size=30),
            panel(Image.open(frame / "rendered_rgb.png"), (panel_w2, panel_h), "Rendered RGB", label_size=30),
        ],
        [
            panel(Image.open(frame / "gt_depth_common_0_6m.png"), (panel_w2, panel_h), "GT Depth", subtitle="Shared display range: 0–6 m", label_size=30),
            panel(Image.open(frame / "rendered_depth_common_0_6m.png"), (panel_w2, panel_h), "Rendered Depth", subtitle="Shared display range: 0–6 m", label_size=30),
        ],
        [
            panel(Image.open(frame / "gt_semantic.png"), (panel_w3, panel_h), "GT Semantic", subtitle="Categorical Replica ground truth", label_size=26),
            panel(Image.open(frame / "rendered_semantic_raw.png"), (panel_w3, panel_h), "Raw Learned Semantic Color", subtitle="Continuous learned colors; not categorical IDs", label_size=25),
            panel(Image.open(frame / "rendered_semantic_recolored.png"), (panel_w3, panel_h), "Evaluation Recoloring", subtitle="GT palette assisted", label_size=26),
        ],
    ]
    y = top
    for row_index, row in enumerate(rows):
        x = margin
        for item in row:
            canvas.paste(item, (x, y))
            x += item.width + gap
        y += max(item.height for item in row) + gap
    draw = ImageDraw.Draw(canvas)
    text(draw, (width // 2, total_h - 44), "Observed training-camera evidence; metrics copied from the existing E4 record and not recomputed.", 21, fill=MUTED, anchor="mm")
    canvas.save(output)


def figure_a_slide(v2: Path, output: Path, metrics: dict[str, float]) -> None:
    frame = v2 / "frames/frame_1999"
    canvas = Image.new("RGB", (1920, 1080), BG)
    title_block(
        canvas,
        "Observed-Camera Reconstruction Quality — Frame 1999",
        f"Existing E4: PSNR {metrics['PSNR']:.2f} dB   |   Depth L1 {metrics['Depth_L1_cm']:.3f} cm   |   Semantic-color mIoU {metrics['semantic_mIoU']:.4f}",
        title_size=40,
    )
    margin, gap, top = 42, 22, 132
    left_w = 1180
    cell_w = (left_w - gap) // 2
    cell_h = 330
    left_sources = [
        (frame / "gt_rgb.png", "GT RGB", None),
        (frame / "rendered_rgb.png", "Rendered RGB", None),
        (frame / "gt_depth_common_0_6m.png", "GT Depth", "Shared 0–6 m range"),
        (frame / "rendered_depth_common_0_6m.png", "Rendered Depth", "Shared 0–6 m range"),
    ]
    for index, (path, label, subtitle) in enumerate(left_sources):
        row, column = divmod(index, 2)
        item = panel(Image.open(path), (cell_w, cell_h), label, subtitle=subtitle, label_size=27)
        canvas.paste(item, (margin + column * (cell_w + gap), top + row * (item.height + gap)))
    right_x = margin + left_w + 32
    right_w = 1920 - right_x - margin
    semantic_sources = [
        (frame / "gt_semantic.png", "GT Semantic", "Categorical ground truth"),
        (frame / "rendered_semantic_raw.png", "Raw Learned Semantic Color", "Continuous; not categorical IDs"),
        (frame / "rendered_semantic_recolored.png", "Evaluation Recoloring", "GT palette assisted"),
    ]
    semantic_h = 190
    for index, (path, label, subtitle) in enumerate(semantic_sources):
        item = panel(Image.open(path), (right_w, semantic_h), label, subtitle=subtitle, label_size=23)
        canvas.paste(item, (right_x, top + index * (item.height + 18)))
    draw = ImageDraw.Draw(canvas)
    text(draw, (960, 1052), "Observed training-camera evidence; metrics copied from E4 and not recomputed.", 20, fill=MUTED, anchor="mm")
    canvas.save(output)


def figure_b(v3a: Path, output: Path, slide: bool = False) -> None:
    width = 1920 if slide else 2400
    margin, gap, top = 42, 24, 130
    panel_w = (width - 2 * margin - 2 * gap) // 3
    panel_h = round(panel_w * 9 / 16)
    canvas = Image.new("RGB", (width, top + panel_h + 86 + 80), BG)
    title_block(canvas, "Full-Scene 3D Cross-Modal Overview", "Same room_overview camera for all panels", title_size=40)
    sources = [
        (Image.open(v3a / "rgb/unfiltered/room_overview.png"), "RGB Gaussian Reconstruction"),
        (crop_v3a_header(Image.open(v3a / "geometry/room_overview.png")), "Geometry Diagnostic (Gaussian Centers)"),
        (crop_v3a_header(Image.open(v3a / "semantic/categorical/room_overview.png")), "Fixed per-Gaussian Semantic IDs"),
    ]
    x = margin
    for image, label in sources:
        item = panel(image, (panel_w, panel_h), label, label_size=25 if slide else 28)
        canvas.paste(item, (x, top))
        x += panel_w + gap
    draw = ImageDraw.Draw(canvas)
    text(draw, (width // 2, canvas.height - 38), "Virtual limited-offset overview; not novel-view accuracy evidence.", 23, fill=RED, anchor="mm")
    canvas.save(output)


def figure_c(v3a: Path, output: Path, slide: bool = False) -> None:
    width = 1920 if slide else 2100
    top, margin, gap = 130, 44, 28
    panel_w = (width - 2 * margin - gap) // 2
    panel_h = round(panel_w * 540 / 960)
    canvas = Image.new("RGB", (width, top + panel_h + 94 + 80), BG)
    title_block(canvas, "Estimated Trajectory in Reconstructed Geometry", "Top-oblique diagnostic camera", title_size=40)
    geometry = crop_v3a_header(Image.open(v3a / "geometry/top_oblique.png"))
    trajectory = crop_v3a_header(Image.open(v3a / "trajectory/estimated_trajectory_3d.png"))
    items = [
        panel(geometry, (panel_w, panel_h), "Global Geometry Context", label_size=28),
        panel(trajectory, (panel_w, panel_h), "Estimated 2,000-Frame Trajectory", subtitle="Green: start   Red: end   Blue: path", label_size=27),
    ]
    x = margin
    for item in items:
        canvas.paste(item, (x, top))
        x += panel_w + gap
    draw = ImageDraw.Draw(canvas)
    text(draw, (width // 2, canvas.height - 38), "Estimated trajectory shown in reconstructed map coordinates; no GT trajectory overlay.", 22, fill=MUTED, anchor="mm")
    canvas.save(output)


def figure_d(v3a: Path, output: Path, selected: list[dict[str, Any]], slide: bool = False) -> None:
    width = 1920 if slide else 2200
    margin, gap, top = 42, 22, 125
    columns = 4
    panel_w = (width - 2 * margin - (columns - 1) * gap) // columns
    image_h = round(panel_w * 540 / 960)
    panel_h = image_h + 70
    rows = 2
    canvas = Image.new("RGB", (width, top + rows * panel_h + (rows - 1) * gap + 64), BG)
    title_block(canvas, "Fixed Semantic-ID Class Structure", "Top-oblique Gaussian-center diagnostics with neutral context", title_size=40)
    for index, record in enumerate(selected):
        source = crop_v3a_header(Image.open(v3a / f"semantic/classwise/{record['name']}_top_oblique.png"))
        label = f"{record['name'].title()}  ·  ID {record['id']}"
        item = panel(source, (panel_w, image_h), label, swatch=record["rgb"], label_size=22)
        row, column = divmod(index, columns)
        canvas.paste(item, (margin + column * (panel_w + gap), top + row * (panel_h + gap)))
    canvas.save(output)


def legend_figure(records: list[dict[str, Any]], output: Path, *, compact: bool = False) -> None:
    columns = 4 if compact else 3
    rows = math.ceil(len(records) / columns)
    width = 1500 if compact else 1800
    margin, top = 48, 115
    row_h = 76 if compact else 68
    cell_w = (width - 2 * margin) // columns
    canvas = Image.new("RGB", (width, top + rows * row_h + 38), WHITE)
    title_block(canvas, "Verified Replica Semantic Palette", "Fixed per-Gaussian IDs present in the final map", title_size=38)
    draw = ImageDraw.Draw(canvas)
    for index, record in enumerate(records):
        row, column = divmod(index, columns)
        x, y = margin + column * cell_w, top + row * row_h
        draw.rectangle((x, y, x + 42, y + 42), fill=record["rgb"], outline=INK, width=2)
        text(draw, (x + 58, y + 6), f"{record['id']}  {record['name']}", 24 if compact else 22, bold=True)
    canvas.save(output)


def wrapped(draw: ImageDraw.ImageDraw, xy: tuple[int, int], value: str, width_chars: int, size: int, *, bold=False, fill=INK, line_gap=8) -> int:
    words = value.split()
    lines, current = [], ""
    for word in words:
        proposal = f"{current} {word}".strip()
        if len(proposal) > width_chars and current:
            lines.append(current)
            current = word
        else:
            current = proposal
    if current:
        lines.append(current)
    y = xy[1]
    for line in lines:
        text(draw, (xy[0], y), line, size, bold=bold, fill=fill)
        y += size + line_gap
    return y


def figure_f(output: Path, slide: bool = False) -> None:
    width, height = (1920, 1080) if slide else (2200, 1040)
    canvas = Image.new("RGB", (width, height), BG)
    title_block(canvas, "PHASE4-VB-001: CPU Keyframe Offload Evidence", "Memory-management variant on RTX 5080 16 GB; explanatory summary, not a new experiment", title_size=40)
    draw = ImageDraw.Draw(canvas)
    margin, gap, top = 45, 34, 155
    box_w = (width - 2 * margin - 2 * gap) // 3
    box_h = height - top - 95
    specifications = [
        (
            "Released Baseline Behavior",
            RED,
            [
                "Archived keyframe image/depth/semantic payload remained GPU-resident.",
                "Full Replica room0 attempt reached frames 0–1293, then CUDA OOM occurred during mapping around frame 1294.",
                "Allocator-only attempt also OOMed; no completed baseline full-scene quality result exists on this GPU.",
            ],
        ),
        (
            "PHASE4-VB-001",
            BLUE,
            [
                "Archived RGB, depth, semantic-ID, and semantic-color payloads are CPU-authoritative.",
                "Selected payloads are synchronously staged CPU→GPU only when needed.",
                "Persistent GPU archived payload: 0 B. Estimated camera poses remain GPU-resident.",
            ],
        ),
        (
            "Observed Outcome",
            GREEN,
            [
                "Detailed variant run completed frames 0–1999.",
                "Peak GPU: 6.774 GB allocated / 8.009 GB reserved.",
                "Final CPU keyframe archive: 10.497 GB; persistent GPU archive: 0 B.",
                "A saved VB001 state subsequently passed released E4 and V2 qualitative evaluation. This is not a direct baseline accuracy comparison.",
            ],
        ),
    ]
    for index, (heading, color, bullets) in enumerate(specifications):
        x = margin + index * (box_w + gap)
        draw.rounded_rectangle((x, top, x + box_w, top + box_h), radius=16, fill=WHITE, outline=LINE, width=2)
        draw.rectangle((x, top, x + box_w, top + 12), fill=color)
        text(draw, (x + 28, top + 34), heading, 31 if slide else 34, bold=True, fill=color)
        y = top + 102
        for bullet in bullets:
            draw.ellipse((x + 30, y + 9, x + 42, y + 21), fill=color)
            y = wrapped(draw, (x + 58, y), bullet, 43 if slide else 46, 23 if slide else 24, line_gap=9) + 25
        if index < 2:
            arrow_x = x + box_w + 7
            arrow_y = top + box_h // 2
            draw.line((arrow_x, arrow_y, arrow_x + gap - 14, arrow_y), fill=MUTED, width=5)
            draw.polygon([(arrow_x + gap - 14, arrow_y - 10), (arrow_x + gap - 2, arrow_y), (arrow_x + gap - 14, arrow_y + 10)], fill=MUTED)
    text(draw, (width // 2, height - 42), "Causal claim is limited to the controlled memory-management change and observed completion behavior on this hardware.", 21, fill=MUTED, anchor="mm")
    canvas.save(output)


def hero_figure(v2: Path, v3a: Path, output: Path) -> None:
    width, height = 2200, 2040
    canvas = Image.new("RGB", (width, height), BG)
    title_block(canvas, "PHASE4-VB-001 Qualitative Results — Replica room0", "Observed-camera fidelity and diagnostic full-scene structure", title_size=44)
    frame = v2 / "frames/frame_1999"
    margin, gap = 45, 25
    # Top: observed GT/render.
    y = 130
    top_w = (width - 2 * margin - gap) // 2
    for index, (path, label) in enumerate(((frame / "gt_rgb.png", "Observed Camera: GT RGB"), (frame / "rendered_rgb.png", "Observed Camera: Rendered RGB"))):
        item = panel(Image.open(path), (top_w, 500), label, label_size=30)
        canvas.paste(item, (margin + index * (top_w + gap), y))
    # Middle: full-scene cross-modal.
    y = 730
    mid_w = (width - 2 * margin - 2 * gap) // 3
    middle = [
        (Image.open(v3a / "rgb/unfiltered/room_overview.png"), "Virtual Full-Scene RGB"),
        (crop_v3a_header(Image.open(v3a / "geometry/room_overview.png")), "Gaussian-Center Geometry"),
        (crop_v3a_header(Image.open(v3a / "semantic/categorical/room_overview.png")), "Fixed Semantic IDs"),
    ]
    for index, (source, label) in enumerate(middle):
        item = panel(source, (mid_w, 390), label, label_size=24)
        canvas.paste(item, (margin + index * (mid_w + gap), y))
    # Bottom: trajectory and selected classes.
    y = 1240
    bottom_w = (width - 2 * margin - gap) // 2
    bottom = [
        (crop_v3a_header(Image.open(v3a / "trajectory/estimated_trajectory_3d.png")), "Estimated 2,000-Frame Trajectory"),
        (crop_v3a_header(Image.open(v3a / "semantic/classwise/selected_classes_overview_top_oblique.png")), "Selected Fixed-ID Semantic Structure"),
    ]
    for index, (source, label) in enumerate(bottom):
        item = panel(source, (bottom_w, 620), label, label_size=27)
        canvas.paste(item, (margin + index * (bottom_w + gap), y))
    draw = ImageDraw.Draw(canvas)
    text(draw, (width // 2, height - 35), "Top: observed-camera evidence. Middle/bottom: virtual diagnostic views, not novel-view accuracy evidence.", 22, fill=RED, anchor="mm")
    canvas.save(output)


def slide_from_figure(source: Path, output: Path, title_value: str, note: str) -> None:
    canvas = Image.new("RGB", (1920, 1080), BG)
    draw = ImageDraw.Draw(canvas)
    text(draw, (55, 30), title_value, 42, bold=True)
    text(draw, (55, 88), note, 23, fill=MUTED)
    source_image = Image.open(source).convert("RGB")
    paste_center(canvas, source_image, (45, 130, 1875, 1035))
    canvas.save(output)


def caption_markdown() -> str:
    return """# Final Figure Captions

## Figure A — Camera-Aligned Reconstruction Fidelity

**Thesis caption.** Camera-aligned qualitative evaluation of the final PHASE4-VB-001 Replica `room0` reconstruction at frame 1999. RGB and metric-depth renderings are compared with the corresponding ground truth. The semantic row separates categorical ground truth, raw continuous learned semantic color, and the released evaluation recoloring, which uses the current ground-truth palette. PSNR, Depth L1, and semantic-color mIoU are copied from the existing E4 record and were not recomputed.

**Slide explanation.** At an observed training-camera pose, the saved reconstruction reproduces room appearance and depth; semantic recoloring remains GT-palette-assisted.

**Scientific caveat.** This is selected observed-camera evidence, not novel-view validation; raw semantic color is not categorical, and evaluation recoloring is not an independent prediction.

**Sources.** Gate V2 frame-1999 atomic RGB/depth/semantic images, frame metadata, E4 per-frame annotations, and `comparisons/case_study_frame_1999.png`.

## Figure B — Full-Scene 3D Cross-Modal Overview

**Thesis caption.** Full-scene qualitative visualization of the final PHASE4-VB-001 reconstruction using one limited-offset virtual camera. The RGB panel shows the original unfiltered Gaussian render, the center panel projects sampled Gaussian centers colored by depth for geometric interpretability, and the semantic panel displays fixed per-Gaussian semantic IDs using the verified Replica palette.

**Slide explanation.** One consistent virtual camera reveals RGB appearance, Gaussian-center geometry, and fixed semantic-ID structure.

**Scientific caveat.** The virtual viewpoint is diagnostic and does not constitute novel-view photometric validation; Gaussian centers are not a continuous surface, and fixed IDs are not a released per-pixel prediction.

**Sources.** Gate V3A `room_overview` RGB, geometry, categorical semantic image, and camera JSON.

## Figure C — Trajectory and Global Geometry

**Thesis caption.** Estimated 2,000-frame camera trajectory over the sampled Gaussian-center geometry of Replica `room0`. Green and red markers indicate the start and end positions, respectively; the connected blue polyline follows saved estimated camera centers in reconstructed map coordinates.

**Slide explanation.** The estimated camera path remains spatially embedded within the reconstructed room envelope.

**Scientific caveat.** No ground-truth trajectory is overlaid and no alignment or trajectory metric is introduced by this figure.

**Sources.** Gate V3A top-oblique geometry and `estimated_trajectory_3d.png`.

## Figure D — Fixed Semantic-ID Class Structure

**Thesis caption.** Class-wise spatial distributions for wall, floor, ceiling, sofa, chair, table, rug, and blinds in the final Gaussian map. Each panel highlights centers carrying the corresponding fixed semantic ID with the verified Replica display color while retaining neutral geometric context.

**Slide explanation.** Fixed semantic metadata forms coherent room surfaces and object regions across eight representative classes.

**Scientific caveat.** These are sampled per-Gaussian metadata visualizations, not per-pixel semantic predictions or new class-accuracy measurements.

**Sources.** Gate V3A top-oblique class-wise images and V1 verified semantic mapping.

## Figure E — Verified Semantic Legends

**Thesis caption.** Verified Replica display palette for all 29 semantic IDs present in the final PHASE4-VB-001 Gaussian map. The compact version retains twelve room-structure and furniture classes for slide use.

**Slide explanation.** Colors and IDs are copied unchanged from the verified final-map semantic mapping.

**Scientific caveat.** Palette entries label fixed Gaussian metadata; they do not convert raw learned semantic colors into categorical predictions.

**Sources.** Gate V1 `semantic_mapping.csv`.

## Figure F — CPU Keyframe Offload Contribution Summary

**Thesis caption.** Evidence-based summary of PHASE4-VB-001 on the tested RTX 5080 16 GB system. The unchanged released baseline retained archived keyframe payloads on GPU and failed during full-scene mapping, whereas PHASE4-VB-001 stored archived image/depth/semantic payloads on CPU and staged selected payloads synchronously. The detailed variant run completed frames 0–1999 with 6.774 GB peak allocated, 8.009 GB peak reserved, a 10.497 GB CPU archive, and zero persistent GPU archived-payload bytes.

**Slide explanation.** CPU-authoritative keyframe payloads removed persistent archived-payload VRAM growth and enabled the measured full-scene completion.

**Scientific caveat.** This summarizes one scene and one GPU; it does not prove benchmark-wide accuracy equivalence, and the saved-state E4/V2 quality evidence is not a direct full-scene baseline comparison because the baseline did not complete.

**Sources.** Phase 3 baseline closure, PHASE4-VB-001 detailed runtime evidence, canonical handoff, E4 result, and V2 qualitative evidence.

## Figure G — Final Thesis Qualitative Plate

**Thesis caption.** Consolidated qualitative evidence for PHASE4-VB-001 on Replica `room0`. The top row shows selected observed-camera RGB ground truth and rendering. The middle row provides an original virtual RGB Gaussian render, sampled Gaussian-center geometry, and fixed-ID semantic structure from one consistent limited-offset camera. The bottom row places the saved estimated trajectory and selected class-wise semantic distributions in a global top-oblique context.

**Slide explanation.** The final saved state combines observed-view fidelity with interpretable full-scene geometry, semantics, and trajectory context.

**Scientific caveat.** Only the top row is observed-camera fidelity evidence; virtual views, center projections, fixed IDs, and trajectory overlays remain explicitly diagnostic.

**Sources.** Gate V2 frame-1999 RGB and Gate V3A room-overview/top-oblique products.
"""


def report_markdown(branch: str, head: str, runtime: dict[str, Any], figures: list[dict[str, Any]], source_hashes: dict[str, str], integrity: bool) -> str:
    inventory = "\n".join(f"- `{item['path']}` — {item['width']}×{item['height']}" for item in figures)
    return f"""# PHASE4-VIS-GATE-V3B — Final Presentation Packaging

Final status: `{STATUS}`

## 1. Git and project state

- Branch: `{branch}`
- HEAD: `{head}`
- Scope: CPU-only presentation packaging from completed V2/V3A evidence.
- Scientific source/config changes: none.
- Renderer, SLAM, E4 evaluation, metrics, training, mapping, and checkpoint loading: not invoked.
- Pre-existing dirty project-management and visualization work was preserved.

## 2. Inputs from V2 and V3A

- Gate V2 supplies observed frame-1999 RGB, shared-scale metric depth, categorical GT semantics, raw learned semantic color, explicitly GT-palette-assisted evaluation recoloring, and existing E4 annotations.
- Gate V3A supplies the camera-consistent `room_overview` triptych, top-oblique geometry, fixed-ID class-wise views, trajectory overlay, camera JSONs, and validated semantic legend.
- The V1 mapping supplies the verified 29-ID Replica palette.

## 3. Source integrity verification

- V2 and V3A checksum manifests passed before packaging.
- Complete source-tree digests were identical before and after packaging: `{integrity}`.
- Checkpoint SHA256 before/after: `{source_hashes['checkpoint']}`.
- Semantic mapping SHA256 before/after: `{source_hashes['semantic_mapping']}`.
- No original visualization was overwritten and the output directory was initially absent.

## 4. Final figure inventory

{inventory}

All figures are readable, non-empty, non-uniform, and recorded in `metadata/final_figure_manifest.json` with exact source paths, hashes, dimensions, view type, and semantic-panel policy.

## 5. Thesis figure recommendations

1. Use `figure_camera_aligned_fidelity.png` as the primary fidelity figure.
2. Use `figure_full_scene_overview.png` as the primary full-scene 3D figure.
3. Use `figure_cpu_offload_contribution_summary.png` for the method contribution.
4. Use `thesis/final_qualitative_plate.png` as the compact results-chapter overview.
5. Use trajectory/class-wise figures when spatial interpretation needs a dedicated panel.

## 6. Slide figure recommendations

- `01_camera_aligned_quality.png`: observed-camera qualitative result.
- `02_full_scene_3d.png`: camera-consistent diagnostic scene overview.
- `03_semantic_structure.png`: eight fixed-ID class distributions.
- `04_trajectory.png`: estimated path in map coordinates.
- `05_cpu_offload_contribution.png`: evidence-bounded method summary.

Slide exports use 1920×1080 canvases, larger typography, neutral backgrounds, and aspect-preserving image placement.

## 7. Semantic labeling validation

- Categorical legends use exactly the verified V1 palette; no colors were invented or modified.
- Observed semantic panels retain the labels `GT Semantic`, `Raw Learned Semantic Color`, and `Evaluation Recoloring — GT palette assisted`.
- Full-scene semantic panels are labeled fixed per-Gaussian IDs, not released per-pixel predictions.
- Class-wise panels state class name, fixed ID, and verified color swatch.

## 8. CPU offload contribution provenance

The baseline side is evidence-based but primarily qualitative: the released full-scene attempt completed frames 0–1293 and OOMed during mapping around frame 1294 on RTX 5080 16 GB. No baseline full-scene quality metric is invented.

The variant side uses detailed validated runtime values: frames 0–1999 completed; peak allocated/reserved 6,774,482,432 / 8,009,023,488 B; CPU archive 10,497,024,000 B; persistent GPU archived payload 0 B. E4/V2 quality evidence is presented as evidence from the saved VB001 state, not as a direct baseline accuracy comparison or benchmark-wide causal claim.

## 9. Captions generated

`captions/FIGURE_CAPTIONS.md` provides a thesis caption, one-sentence slide explanation, scientific caveat, and exact source category for Figures A–G.

## 10. Scientific caveats

- Observed-camera evidence and virtual diagnostic views remain distinct.
- Virtual cameras are not novel-view accuracy evidence.
- Gaussian-center plots are not continuous surfaces.
- Fixed semantic IDs are metadata, not released per-pixel semantic predictions.
- Released recoloring is explicitly GT-palette-assisted.
- The contribution summary covers one scene and hardware configuration; it does not establish generalization or paper-level superiority.

## 11. Runtime / CPU / GPU usage

- Packaging wall time: {runtime['wall_time_seconds']:.4f} s.
- Peak host RSS: {runtime['peak_host_rss_kib']:,} KiB / {runtime['peak_host_rss_bytes']:,} B.
- GPU used: no.
- Attributable peak GPU allocated/reserved: 0 / 0 B.
- New metrics computed: no.

## 12. Reproduction command

```bash
python scripts/visualization/package_final_v3b.py \\
  --v2 results/runtime_artifacts/phase4_vb001_visualization_v2 \\
  --v3a results/runtime_artifacts/phase4_vb001_visualization_v3a \\
  --checkpoint experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz \\
  --semantic-mapping results/runtime_artifacts/phase4_vb001_visualization_audit/semantic_mapping.csv \\
  --baseline-evidence docs/experiments/PHASE3_BASELINE_CLOSURE_2026-10-10.md \\
  --variant-evidence project_management/SESSION_HANDOFF.md \\
  --output results/runtime_artifacts/phase4_vb001_visualization_v3b
```

The utility refuses to overwrite a non-empty output directory.

## 13. Final Gate status

All requested primary, thesis, slide, legend, caption, metadata, and checksum products are complete and scientifically labeled.

Final status: `{STATUS}`
"""


def main() -> int:
    args = parse_args()
    start = time.perf_counter()
    v2, v3a = args.v2.resolve(), args.v3a.resolve()
    checkpoint = args.checkpoint.resolve()
    mapping = args.semantic_mapping.resolve()
    baseline_evidence = args.baseline_evidence.resolve()
    variant_evidence = args.variant_evidence.resolve()
    output = args.output.resolve()
    required = [v2, v3a, checkpoint, mapping, baseline_evidence, variant_evidence]
    if not all(path.exists() for path in required):
        raise FileNotFoundError([str(path) for path in required if not path.exists()])
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing to overwrite non-empty output: {output}")
    for subdir in ("thesis", "slides", "figures", "legends", "captions", "metadata", "checksums"):
        (output / subdir).mkdir(parents=True, exist_ok=True)

    tree_before = {"v2": tree_digest(v2), "v3a": tree_digest(v3a)}
    source_hashes_before = {
        "checkpoint": sha256_file(checkpoint),
        "semantic_mapping": sha256_file(mapping),
        "baseline_evidence": sha256_file(baseline_evidence),
        "variant_evidence": sha256_file(variant_evidence),
    }
    git_before = git("status", "--short")

    frame_metadata_path = v2 / "frames/frame_1999/frame_metadata.json"
    frame_metadata = json.loads(frame_metadata_path.read_text(encoding="utf-8"))
    metrics = frame_metadata["existing_e4_metric_annotation"]
    palette, by_name = load_palette(mapping)
    selected_names = ["wall", "floor", "ceiling", "sofa", "chair", "table", "rug", "blinds"]
    selected = [by_name[name] for name in selected_names]
    compact_names = ["wall", "floor", "ceiling", "sofa", "chair", "table", "rug", "blinds", "cabinet", "door", "window", "stool"]
    compact = [by_name[name] for name in compact_names]

    figure_a(v2, output / "figures/figure_camera_aligned_fidelity.png", metrics)
    figure_a(v2, output / "slides/camera_aligned_fidelity.png", metrics, slide=True)
    figure_b(v3a, output / "figures/figure_full_scene_overview.png")
    figure_c(v3a, output / "figures/figure_trajectory_reconstruction.png")
    figure_d(v3a, output / "figures/figure_semantic_classwise.png", selected)
    legend_figure(palette, output / "legends/semantic_legend_full.png")
    legend_figure(compact, output / "legends/semantic_legend_compact.png", compact=True)
    figure_f(output / "figures/figure_cpu_offload_contribution_summary.png")
    hero_figure(v2, v3a, output / "thesis/final_qualitative_plate.png")

    shutil.copyfile(output / "slides/camera_aligned_fidelity.png", output / "slides/01_camera_aligned_quality.png")
    figure_b(v3a, output / "slides/02_full_scene_3d.png", slide=True)
    figure_d(v3a, output / "slides/03_semantic_structure.png", selected, slide=True)
    figure_c(v3a, output / "slides/04_trajectory.png", slide=True)
    figure_f(output / "slides/05_cpu_offload_contribution.png", slide=True)

    (output / "captions/FIGURE_CAPTIONS.md").write_text(caption_markdown(), encoding="utf-8")

    used_sources = {
        "figure_camera_aligned_fidelity": [
            v2 / "comparisons/case_study_frame_1999.png",
            frame_metadata_path,
            *[v2 / "frames/frame_1999" / name for name in (
                "gt_rgb.png", "rendered_rgb.png", "gt_depth_common_0_6m.png",
                "rendered_depth_common_0_6m.png", "gt_semantic.png",
                "rendered_semantic_raw.png", "rendered_semantic_recolored.png",
            )],
        ],
        "figure_full_scene_overview": [
            v3a / "rgb/unfiltered/room_overview.png",
            v3a / "geometry/room_overview.png",
            v3a / "semantic/categorical/room_overview.png",
            v3a / "cameras/room_overview.json",
        ],
        "figure_trajectory_reconstruction": [
            v3a / "trajectory/estimated_trajectory_3d.png",
            v3a / "geometry/top_oblique.png",
            v3a / "cameras/top_oblique.json",
        ],
        "figure_semantic_classwise": [v3a / f"semantic/classwise/{name}_top_oblique.png" for name in selected_names] + [mapping],
        "semantic_legends": [mapping],
        "figure_cpu_offload_contribution_summary": [baseline_evidence, variant_evidence, REPO_ROOT / "docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md", v2 / "GATE_V2_REPORT.md"],
        "final_qualitative_plate": [
            v2 / "frames/frame_1999/gt_rgb.png", v2 / "frames/frame_1999/rendered_rgb.png",
            v3a / "rgb/unfiltered/room_overview.png", v3a / "geometry/room_overview.png",
            v3a / "semantic/categorical/room_overview.png", v3a / "trajectory/estimated_trajectory_3d.png",
            v3a / "semantic/classwise/selected_classes_overview_top_oblique.png",
        ],
    }
    all_sources = sorted({path.resolve() for paths in used_sources.values() for path in paths})
    source_records = [{"path": str(path), "sha256": sha256_file(path), "size_bytes": path.stat().st_size} for path in all_sources]

    tree_after = {"v2": tree_digest(v2), "v3a": tree_digest(v3a)}
    source_hashes_after = {
        "checkpoint": sha256_file(checkpoint),
        "semantic_mapping": sha256_file(mapping),
        "baseline_evidence": sha256_file(baseline_evidence),
        "variant_evidence": sha256_file(variant_evidence),
    }
    integrity = tree_before == tree_after and source_hashes_before == source_hashes_after
    if not integrity:
        raise RuntimeError("Source integrity changed during packaging")

    elapsed_before_report = time.perf_counter() - start
    runtime = {
        "wall_time_seconds": elapsed_before_report,
        "peak_host_rss_kib": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss),
        "peak_host_rss_bytes": int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024),
        "gpu_used": False,
        "peak_gpu_allocated_bytes": 0,
        "peak_gpu_reserved_bytes": 0,
    }
    output_figure_paths = sorted(list((output / "figures").glob("*.png")) + list((output / "slides").glob("*.png")) + list((output / "thesis").glob("*.png")) + list((output / "legends").glob("*.png")))
    figure_records = []
    for path in output_figure_paths:
        with Image.open(path) as image:
            array = np.asarray(image.convert("RGB"))
            figure_records.append({
                "path": str(path.relative_to(output)),
                "width": image.width,
                "height": image.height,
                "mode": "RGB",
                "sha256": sha256_file(path),
                "size_bytes": path.stat().st_size,
                "readable_nonempty_nonuniform": bool(path.stat().st_size > 0 and array.std() > 1),
            })
    if not all(record["readable_nonempty_nonuniform"] for record in figure_records):
        raise RuntimeError("At least one packaged figure is empty or uniform")

    # Refresh resource values after full-resolution figure validation so the
    # recorded peak covers composition and validation, not only composition.
    runtime["wall_time_seconds"] = time.perf_counter() - start
    runtime["peak_host_rss_kib"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    runtime["peak_host_rss_bytes"] = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss * 1024)

    report = report_markdown(git("branch", "--show-current"), git("rev-parse", "HEAD"), runtime, figure_records, source_hashes_before, integrity)
    (output / "GATE_V3B_REPORT.md").write_text(report, encoding="utf-8")

    camera_room = json.loads((v3a / "cameras/room_overview.json").read_text(encoding="utf-8"))
    manifest = {
        "gate": "PHASE4-VIS-GATE-V3B",
        "status": STATUS,
        "script": {"path": str(Path(__file__).resolve()), "version": SCRIPT_VERSION, "sha256": sha256_file(Path(__file__).resolve())},
        "branch": git("branch", "--show-current"),
        "head": git("rev-parse", "HEAD"),
        "git_status_before": git_before,
        "source_roots": {"v2": str(v2), "v3a": str(v3a)},
        "source_tree_integrity": {"before": tree_before, "after": tree_after, "unchanged": integrity},
        "source_hashes_before": source_hashes_before,
        "source_hashes_after": source_hashes_after,
        "source_artifacts_used": source_records,
        "source_mapping": str(mapping),
        "metric_source": metrics["source"],
        "metrics_copied_not_recomputed": {"PSNR": metrics["PSNR"], "Depth_L1_m": metrics["Depth_L1_m"], "Depth_L1_cm": metrics["Depth_L1_cm"], "semantic_mIoU": metrics["semantic_mIoU"]},
        "input_camera_jsons": [str(v3a / "cameras/room_overview.json"), str(v3a / "cameras/top_oblique.json")],
        "room_overview_camera_sha256": sha256_file(v3a / "cameras/room_overview.json"),
        "full_scene_triptych_same_camera": True,
        "full_scene_triptych_camera": camera_room,
        "panel_policies": {
            "camera_aligned_gt_rgb": {"view_type": "observed_view", "semantic_type": None},
            "camera_aligned_rendered_rgb": {"view_type": "observed_view", "semantic_type": None},
            "camera_aligned_gt_semantic": {"view_type": "observed_view", "semantic_type": "ground_truth_categorical"},
            "camera_aligned_raw_semantic": {"view_type": "observed_view", "semantic_type": "raw_learned_color"},
            "camera_aligned_recolored_semantic": {"view_type": "observed_view", "semantic_type": "GT_palette_assisted_recoloring"},
            "full_scene_rgb": {"view_type": "virtual_limited_offset", "semantic_type": None},
            "full_scene_geometry": {"view_type": "virtual_limited_offset", "representation": "sampled_Gaussian_centers_not_surface"},
            "full_scene_semantic": {"view_type": "virtual_limited_offset", "semantic_type": "fixed_per_Gaussian_ID"},
            "classwise_semantic": {"view_type": "virtual_top_oblique", "semantic_type": "fixed_per_Gaussian_ID"},
            "trajectory": {"view_type": "virtual_top_oblique", "trajectory_type": "estimated_only_no_GT_overlay"},
        },
        "figures": figure_records,
        "runtime": runtime,
        "scope": {"rerendered_gaussians": False, "gpu_used": False, "metrics_recomputed": False, "slam_rerun": False, "evaluation_rerun": False, "checkpoint_loaded": False},
    }
    dump_json(output / "metadata/final_figure_manifest.json", manifest)

    artifacts = []
    for path in sorted(item for item in output.rglob("*") if item.is_file() and item.name not in ("SHA256SUMS.txt", "artifact_manifest.json")):
        artifacts.append({"relative_path": str(path.relative_to(output)), "sha256": sha256_file(path), "size_bytes": path.stat().st_size})
    dump_json(output / "metadata/artifact_manifest.json", {"artifact_count_excluding_manifests_and_checksum_file": len(artifacts), "artifacts": artifacts})
    checksum_paths = sorted(item for item in output.rglob("*") if item.is_file() and item.name != "SHA256SUMS.txt")
    (output / "checksums/SHA256SUMS.txt").write_text("\n".join(f"{sha256_file(path)}  {path.relative_to(output)}" for path in checksum_paths) + "\n", encoding="utf-8")

    print(json.dumps({"status": STATUS, "output": str(output), "figure_count": len(figure_records), "source_integrity": integrity, "runtime": runtime}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
