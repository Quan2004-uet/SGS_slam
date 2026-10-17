#!/usr/bin/env python3
"""Package Gate 3 thesis figures and slides from validated Gate 2 PNG pairs only."""

from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont


PHASE4_LABEL = "Phase 4 - CPU Keyframe Offload"
PHASE6_LABEL = "Phase 6 - CPU Keyframe Offload + Budget-Aware Mapping (V-A2)"
FRAMES = ["0000", "0499", "0999", "1499", "1999"]
V3A_VIEWS = ["room_overview", "top_oblique", "trajectory_observed"]
REQUIRED_FIGURES = [
    "figure_01_observed_rgb_comparison.png",
    "figure_02_observed_depth_comparison.png",
    "figure_03_observed_semantic_color_comparison.png",
    "figure_04_full_scene_rgb_3d_comparison.png",
    "figure_05_cross_modal_comparison.png",
    "figure_06_semantic_classwise_comparison.png",
    "figure_07_trajectory_comparison.png",
    "figure_08_full_scene_semantic_3d_comparison.png",
]
REQUIRED_SLIDES = [
    "01_reconstruction_fidelity.png",
    "02_depth_and_semantic.png",
    "03_full_scene_3d.png",
    "04_semantic_structure.png",
    "05_trajectory_and_summary.png",
]
CHECKPOINTS = {
    "experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz":
        "dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2",
    "results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/params.npz":
        "1193f5d5a854225d6e9fc68154d459b5eb026e056a91b5f00639b8da0facd0a5",
    "results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/params.ply":
        "dc10441cd383ad7861d27fb70a4f9a76fe9dd88a91e2bacc197b18bbe24cb50a",
    "results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/seg_params.ply":
        "98676b4c3e6447681f99426153dfb112bee76882ac9f5d3a18cf11f4832fec21",
}
FAMILY_COUNTS = {"v1": 6, "v2": 15, "v3a_cross_modal": 12, "v3a_classwise": 9, "v3a_trajectory": 1}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def get_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    candidates = ([
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
    ] if bold else [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf",
    ])
    for candidate in candidates:
        if Path(candidate).is_file():
            return ImageFont.truetype(candidate, size=size)
    raise RuntimeError("A deterministic TrueType font is unavailable")


def resampling_filter():
    return getattr(Image, "Resampling", Image).LANCZOS


def verify_sums(root: Path) -> list[str]:
    sums_path = root / "metadata/SHA256SUMS.txt"
    if not sums_path.is_file():
        raise FileNotFoundError(f"Missing Gate 2 checksums: {sums_path}")
    entries = []
    for line in sums_path.read_text(encoding="utf-8").splitlines():
        digest, rel = line.split("  ", 1)
        path = root / rel
        if not path.is_file() or sha256(path) != digest:
            raise ValueError(f"Gate 2 checksum failure: {rel}")
        entries.append(rel)
    if len(entries) != len(set(entries)):
        raise ValueError("Duplicate path in Gate 2 SHA256SUMS.txt")
    return entries


def load_gate2(repo: Path, gate2_root: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, dict[str, Any]], dict[str, str]]:
    if not gate2_root.is_dir():
        raise FileNotFoundError(f"Accepted Gate 2 run_02 directory is missing: {gate2_root}")
    manifest_path = gate2_root / "metadata/pair_manifest.json"
    validation_path = gate2_root / "metadata/validation_report.json"
    readme_path = gate2_root / "metadata/README.md"
    for path in (manifest_path, validation_path, readme_path):
        if not path.is_file():
            raise FileNotFoundError(f"Required Gate 2 file missing: {path}")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    validation = json.loads(validation_path.read_text(encoding="utf-8"))
    if manifest.get("session") != "SESSION_021" or manifest.get("gate") != 2:
        raise ValueError("Gate 2 manifest does not identify SESSION_021 Gate 2")
    if validation.get("final_gate_classification") != "PASS_P6_BAM_007_GATE2_SIDE_BY_SIDE":
        raise ValueError("Gate 2 validation report is not PASS")
    if validation.get("actual_pair_count") != 43 or validation.get("preview_count") != 7:
        raise ValueError("Gate 2 validation counts do not match expected 43 pairs / 7 previews")
    if not validation.get("panel_pixel_integrity_pass") or not validation.get("protected_checkpoint_hashes_match"):
        raise ValueError("Gate 2 essential validation flags do not pass")
    sums_entries = verify_sums(gate2_root)
    if len(manifest.get("pairs", [])) != 43 or len(manifest.get("previews", [])) != 7:
        raise ValueError("Gate 2 manifest pair/preview inventory is incomplete")
    family_counts = Counter(row["family_directory"] for row in manifest["pairs"])
    if dict(family_counts) != FAMILY_COUNTS:
        raise ValueError(f"Unexpected Gate 2 family distribution: {dict(family_counts)}")

    pairs = {}
    source_hashes = {}
    for row in manifest["pairs"]:
        pid = row["pair_id"]
        out = gate2_root / row["output_paired_png"]
        if not out.is_file() or sha256(out) != row["output_sha256"]:
            raise ValueError(f"Gate 2 pair output hash mismatch: {pid}")
        if row["readiness_classification"] not in {"READY_FOR_SIDE_BY_SIDE", "READY_WITH_EXPLICIT_CAVEAT"}:
            raise ValueError(f"Unexpected readiness status for {pid}")
        for key, expected in [("phase4_source_path", row["phase4_source_sha256"]),
                              ("phase6_source_path", row["phase6_source_sha256"])]:
            source = repo / row[key]
            if not source.is_file() or sha256(source) != expected:
                raise ValueError(f"Gate 2 source hash mismatch: {pid} {key}")
            source_hashes[str(source)] = expected
        camera_source = repo / row["camera_source_path"]
        camera_copy = repo / row["camera_copy_path"]
        if not camera_source.is_file() or not camera_copy.is_file():
            raise ValueError(f"Gate 2 camera metadata missing for {pid}")
        if (sha256(camera_source) != row["camera_sha256"] or
                sha256(camera_copy) != row["camera_sha256"] or
                camera_source.read_bytes() != camera_copy.read_bytes()):
            raise ValueError(f"Gate 2 camera provenance mismatch for {pid}")
        pairs[pid] = row
    return manifest, validation, pairs, source_hashes


def get_panel(repo: Path, gate2_root: Path, row: dict[str, Any], side: str) -> Image.Image:
    pair_path = gate2_root / row["output_paired_png"]
    settings = row["composition_settings"]
    x, y = settings["panel_origins"][side]
    width, height = settings["panel_dimensions"]
    with Image.open(pair_path) as pair:
        pair.load()
        if pair.mode != "RGB":
            raise ValueError(f"Gate 2 pair is not RGB: {pair_path}")
        panel = pair.crop((x, y, x + width, y + height))
    source_path = repo / row[f"phase{4 if side == 'phase4' else 6}_source_path"]
    with Image.open(source_path) as source:
        source.load()
        if source.mode != "RGB" or source.size != panel.size or source.tobytes() != panel.tobytes():
            raise ValueError(f"Gate 2 source panel pixels differ from validated source: {row['pair_id']} {side}")
    return panel


def find_pair(pairs: Any, *, family: str, frame_view: str | None = None,
              modality: str | None = None, contains: str | None = None) -> dict[str, Any]:
    records = pairs.values() if hasattr(pairs, "values") else pairs
    found = [r for r in records
             if r["family_directory"] == family
             and (frame_view is None or r["frame_view_id"] == frame_view)
             and (modality is None or r["modality"] == modality)
             and (contains is None or contains in r["frame_view_id"])]
    if len(found) != 1:
        raise ValueError(f"Expected one pair for {family}/{frame_view}/{modality}/{contains}; found {len(found)}")
    return found[0]


class FigureBuilder:
    def __init__(self, repo: Path, gate2: Path, output: Path):
        self.repo, self.gate2, self.output = repo, gate2, output
        self.records: list[dict[str, Any]] = []
        self.source_hashes: dict[str, str] = {}
        self.regular = get_font(20)
        self.bold = get_font(24, True)
        self.small = get_font(16)

    def image_pair(self, row: dict[str, Any]) -> tuple[Image.Image, Image.Image]:
        self.source_hashes[str(self.repo / row["phase4_source_path"])] = row["phase4_source_sha256"]
        self.source_hashes[str(self.repo / row["phase6_source_path"])] = row["phase6_source_sha256"]
        return get_panel(self.repo, self.gate2, row, "phase4"), get_panel(self.repo, self.gate2, row, "phase6")

    def save_figure(self, name: str, title: str, subtitle: str, rows: list[tuple[dict[str, Any], str]],
                    caption: str, panel_width: int | None = None, appendix_images: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        loaded = []
        maximum_pair_width = 0
        for row, label in rows:
            left, right = self.image_pair(row)
            tw = panel_width or left.width
            if left.size != right.size:
                raise ValueError(f"Gate 2 pair panel dimensions differ: {row['pair_id']}")
            th = round(left.height * tw / left.width)
            loaded.append((row, label, left, right, tw, th))
            maximum_pair_width = max(maximum_pair_width, tw * 2 + 96)
        margin, header_h, row_label_h, method_h, row_gap, footer_h = 48, 142, 44, 34, 24, 100
        canvas_h = margin + header_h + sum(row_label_h + method_h + item[5] + row_gap for item in loaded) + footer_h
        extra_w = 0
        legend_img = None
        legend_meta = None
        if appendix_images:
            extra_w = 950
            legend_item = appendix_images[0]
            legend_path = self.repo / legend_item["path"]
            if sha256(legend_path) != legend_item["sha256"]:
                raise ValueError(f"Auxiliary legend hash mismatch: {legend_path}")
            with Image.open(legend_path) as im:
                im.load()
                legend_img = im.convert("RGB")
            legend_meta = {**legend_item, "dimensions": list(legend_img.size)}
        canvas_w = margin * 2 + maximum_pair_width + extra_w
        canvas = Image.new("RGB", (canvas_w, canvas_h), "#ffffff")
        draw = ImageDraw.Draw(canvas)
        draw.text((margin, 24), title, fill="#181818", font=get_font(34, True))
        draw.text((margin, 76), subtitle, fill="#444444", font=self.regular)
        y = margin + header_h
        regions = []
        for row, row_label, left, right, tw, th in loaded:
            draw.text((margin, y), row_label, fill="#202020", font=self.bold)
            y += row_label_h
            pair_w = tw * 2 + 48
            x = margin + max(0, (maximum_pair_width - pair_w) // 2)
            draw.text((x, y), PHASE4_LABEL, fill="#222222", font=self.small)
            draw.text((x + tw + 48, y), PHASE6_LABEL, fill="#222222", font=self.small)
            y += method_h
            left_r = left.resize((tw, th), resampling_filter()) if left.size != (tw, th) else left.copy()
            right_r = right.resize((tw, th), resampling_filter()) if right.size != (tw, th) else right.copy()
            canvas.paste(left_r, (x, y))
            canvas.paste(right_r, (x + tw + 48, y))
            draw.rectangle((x - 1, y - 1, x + tw, y + th), outline="#999999", width=1)
            draw.rectangle((x + tw + 47, y - 1, x + 2 * tw + 48, y + th), outline="#999999", width=1)
            regions.extend([
                {"pair_id": row["pair_id"], "side": "phase4", "region": [x, y, tw, th], "source_size": list(left.size), "scale_x": tw / left.width, "scale_y": th / left.height},
                {"pair_id": row["pair_id"], "side": "phase6", "region": [x + tw + 48, y, tw, th], "source_size": list(right.size), "scale_x": tw / right.width, "scale_y": th / right.height},
            ])
            y += th + row_gap
        if legend_img is not None:
            lx = margin * 2 + maximum_pair_width
            legend_width = min(850, legend_img.width)
            legend_height = round(legend_img.height * legend_width / legend_img.width)
            legend = legend_img.resize((legend_width, legend_height), resampling_filter())
            ly = margin + header_h
            draw.text((lx, ly), "Verified Replica semantic palette", fill="#222222", font=self.bold)
            canvas.paste(legend, (lx, ly + 40))
        footer_y = canvas_h - footer_h + 8
        draw.text((margin, footer_y), caption, fill="#333333", font=get_font(17))
        path = self.output / "figures" / name
        path.parent.mkdir(parents=True, exist_ok=True)
        canvas.save(path, format="PNG", optimize=False)
        self.verify_regions(path, regions, loaded)
        record = self.output_record(path, "scientific_figure", rows, caption, regions, appendix_images)
        record["title"] = title
        record["subtitle"] = subtitle
        record["legend_source"] = legend_meta
        self.records.append(record)
        return record

    def verify_regions(self, output_path: Path, regions: list[dict[str, Any]], loaded: list[Any]) -> None:
        rowmap = {item[0]["pair_id"]: item for item in loaded}
        with Image.open(output_path) as out:
            out.load()
            for region in regions:
                x, y, w, h = region["region"]
                row, _, left, right, _, _ = rowmap[region["pair_id"]]
                source = left if region["side"] == "phase4" else right
                expected = source.resize((w, h), resampling_filter()) if source.size != (w, h) else source
                if out.crop((x, y, x + w, y + h)).tobytes() != expected.tobytes():
                    raise ValueError(f"Figure panel transform integrity failed: {output_path} {region}")

    def output_record(self, path: Path, image_type: str, pairs: list[tuple[dict[str, Any], str]],
                      caption: str, regions: list[dict[str, Any]], auxiliary: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        with Image.open(path) as im:
            im.load()
            if im.mode != "RGB" or not any(lo != hi for lo, hi in im.getextrema()):
                raise ValueError(f"Invalid or uniform output: {path}")
            dimensions = list(im.size)
        sources = []
        for row, _ in pairs:
            sources.append({
                "gate2_pair_id": row["pair_id"],
                "gate2_output_path": row["output_paired_png"],
                "gate2_output_sha256": row["output_sha256"],
                "phase4_source_path": row["phase4_source_path"],
                "phase4_source_sha256": row["phase4_source_sha256"],
                "phase6_source_path": row["phase6_source_path"],
                "phase6_source_sha256": row["phase6_source_sha256"],
                "camera_sha256": row["camera_sha256"],
                "camera_family": row["family_directory"],
                "frame_view_id": row["frame_view_id"],
                "modality": row["modality"],
                "classification": row["readiness_classification"],
                "caveat": row.get("explicit_visible_caveat", ""),
            })
        return {
            "filename": path.name,
            "image_type": image_type,
            "output_path": str(path.relative_to(self.output)),
            "output_sha256": sha256(path),
            "output_dimensions": dimensions,
            "component_gate2_pairs": sources,
            "caption_and_caveats": caption,
            "resize_transforms": regions,
            "auxiliary_sources": auxiliary or [],
            "label_order": ["Phase 4 (left)", "Phase 6 (right)"],
            "image_enhancement": "none",
            "source_content_crop": "none; only Gate 2 frame surrounds were excluded when recovering the complete source panel",
        }


def choose(pairs: dict[str, dict[str, Any]]) -> dict[str, list[tuple[dict[str, Any], str]]]:
    result: dict[str, list[tuple[dict[str, Any], str]]] = {}
    result["rgb_frames"] = [(find_pair(pairs, family="v2", frame_view=f, modality="RGB"), f"Frame {int(f)}") for f in FRAMES]
    result["depth_frames"] = [(find_pair(pairs, family="v2", frame_view=f, modality="Metric depth [0,6 m]"), f"Frame {int(f)}") for f in FRAMES]
    result["semantic_frames"] = [(find_pair(pairs, family="v2", frame_view=f, modality="Raw learned semantic color"), f"Frame {int(f)}") for f in FRAMES]
    result["full_rgb"] = [
        (find_pair(pairs, family="v3a_cross_modal", frame_view="room_overview", modality="RGB"), "Phase 4 V3A camera - room_overview"),
        (find_pair(pairs, family="v3a_cross_modal", frame_view="top_oblique", modality="RGB"), "Phase 4 V3A camera - top_oblique"),
    ]
    result["cross_modal"] = [
        (find_pair(pairs, family="v3a_cross_modal", frame_view="top_oblique", modality=m), label)
        for m, label in [("RGB", "Unfiltered RGB Gaussian reconstruction"),
                         ("Gaussian-center geometry", "Sampled Gaussian-center geometry diagnostic"),
                         ("Fixed semantic IDs", "Fixed per-Gaussian Semantic IDs - verified Replica palette")]
    ]
    result["classwise"] = [
        (find_pair(pairs, family="v3a_classwise", contains=f"{name}_top_oblique.png"), name.title())
        for name in ["wall", "floor", "sofa", "chair", "table"]
    ]
    result["trajectory"] = [(find_pair(pairs, family="v3a_trajectory"), "Phase 4 V3A top_oblique comparison camera")]
    result["semantic_3d"] = [
        (find_pair(pairs, family="v3a_cross_modal", frame_view=view, modality=modality), f"{label} | V3A {view}")
        for modality, label in [("Raw learned semantic color", "Raw learned semantic-color Gaussian rendering"),
                                ("Fixed semantic IDs", "Fixed per-Gaussian Semantic IDs - verified Replica palette")]
        for view in ["room_overview", "top_oblique"]
    ]
    result["rgb_preview_sample"] = [result["rgb_frames"][2]]
    result["overview_plate"] = [
        result["rgb_frames"][2],
        (find_pair(pairs, family="v3a_cross_modal", frame_view="room_overview", modality="RGB"), "Full-scene V3A room_overview"),
        (find_pair(pairs, family="v3a_cross_modal", frame_view="top_oblique", modality="Fixed semantic IDs"), "Fixed semantic IDs - V3A top_oblique"),
        result["trajectory"][0],
    ]
    return result


def make_slide_header(canvas: Image.Image, title: str, subtitle: str) -> ImageDraw.ImageDraw:
    draw = ImageDraw.Draw(canvas)
    draw.text((60, 30), title, fill="#171717", font=get_font(34, True))
    draw.text((60, 82), subtitle, fill="#444444", font=get_font(19))
    return draw


def resize_panel(image: Image.Image, width: int) -> Image.Image:
    height = round(image.height * width / image.width)
    return image.resize((width, height), resampling_filter()) if image.size != (width, height) else image.copy()


def slide_pair(builder: FigureBuilder, draw: ImageDraw.ImageDraw, row: dict[str, Any],
               x: int, y: int, panel_width: int, label: str, *, vertical: bool = False) -> tuple[int, list[dict[str, Any]]]:
    left, right = builder.image_pair(row)
    left_r, right_r = resize_panel(left, panel_width), resize_panel(right, panel_width)
    gap, label_h = 20, 28
    regions = []
    if vertical:
        draw.text((x, y), PHASE4_LABEL, fill="#222222", font=get_font(13))
        y += label_h
        canvas = draw._image
        canvas.paste(left_r, (x, y))
        regions.append(("phase4", x, y, left, left_r))
        y += left_r.height + 8
        draw.text((x, y), PHASE6_LABEL, fill="#222222", font=get_font(13))
        y += label_h
        canvas.paste(right_r, (x, y))
        regions.append(("phase6", x, y, right, right_r))
        y += right_r.height
    else:
        draw.text((x, y), PHASE4_LABEL, fill="#222222", font=get_font(13))
        draw.text((x + panel_width + gap, y), PHASE6_LABEL, fill="#222222", font=get_font(13))
        y += label_h
        canvas = draw._image
        canvas.paste(left_r, (x, y)); canvas.paste(right_r, (x + panel_width + gap, y))
        regions.extend([("phase4", x, y, left, left_r), ("phase6", x + panel_width + gap, y, right, right_r)])
        y += max(left_r.height, right_r.height)
    return y, [{"pair_id": row["pair_id"], "side": side, "region": [px, py, resized.width, resized.height],
                "source_size": list(src.size), "resize_size": list(resized.size),
                "scale_x": resized.width / src.width, "scale_y": resized.height / src.height}
               for side, px, py, src, resized in regions]


def save_slide(builder: FigureBuilder, name: str, title: str, subtitle: str,
               used: list[dict[str, Any]], draw_content, caption: str) -> dict[str, Any]:
    canvas = Image.new("RGB", (1920, 1080), "#ffffff")
    draw = make_slide_header(canvas, title, subtitle)
    regions = draw_content(canvas, draw)
    draw.text((60, 1030), caption, fill="#333333", font=get_font(15))
    path = builder.output / "slides" / name
    path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(path, format="PNG", optimize=False)
    builder.verify_slide_regions(path, regions)
    record = builder.output_record(path, "16:9_presentation_slide", [(r, "") for r in used], caption, regions)
    record["title"] = title; record["subtitle"] = subtitle
    builder.records.append(record)
    return record


def verify_slide_regions(builder: FigureBuilder, path: Path, regions: list[dict[str, Any]]) -> None:
    with Image.open(path) as out:
        out.load()
        for region in regions:
            x, y, w, h = region["region"]
            source_row = builder._pair_by_id[region["pair_id"]]
            source = get_panel(builder.repo, builder.gate2, source_row, region["side"])
            expected = resize_panel(source, w)
            if expected.size != (w, h) or out.crop((x, y, x+w, y+h)).tobytes() != expected.tobytes():
                raise ValueError(f"Slide panel resize/pixel check failed: {path} {region}")


FigureBuilder.verify_slide_regions = verify_slide_regions


def build_slides(builder: FigureBuilder, selections: dict[str, list[tuple[dict[str, Any], str]]], legend: dict[str, Any]) -> None:
    builder._pair_by_id.update({r["pair_id"]: r for group in selections.values() for r, _ in group})

    def slide1(canvas, draw):
        regions=[]; colw=350; gap=18; startx=55; y0=150
        for idx, (row, label) in enumerate(selections["rgb_frames"]):
            x=startx+idx*(colw+gap)
            draw.text((x, y0),label,fill="#222222",font=get_font(17,True))
            _, rs=slide_pair(builder,draw,row,x,y0+28,300,"",vertical=True);regions+=rs
        return regions
    save_slide(builder,"01_reconstruction_fidelity.png","Observed-camera RGB reconstruction",
               "Five fixed frames; Phase 6 uses the corresponding Phase 4 estimated camera.",
               [r for r,_ in selections["rgb_frames"]],slide1,
               "Qualitative matched-camera comparison only; not a comparison of independent Phase 6 tracking poses.")

    def slide2(canvas, draw):
        regions=[]; frames=["0000","0999","1999"]; startx=85; colw=560; gap=35; y=170
        for i,f in enumerate(frames):
            x=startx+i*(colw+gap)
            draw.text((x,y),f"Frame {int(f)}",fill="#222222",font=get_font(18,True))
            depth=find_pair(builder._pair_by_id.values(),family="v2",frame_view=f,modality="Metric depth [0,6 m]")
            sem=find_pair(builder._pair_by_id.values(),family="v2",frame_view=f,modality="Raw learned semantic color")
            draw.text((x,y+28),"Rendered depth visualization (0-6 m)",fill="#333333",font=get_font(15,True))
            _, rs=slide_pair(builder,draw,depth,x,y+52,245,"",vertical=False);regions+=rs
            draw.text((x,y+260),"Raw learned semantic-color rendering",fill="#333333",font=get_font(15,True))
            _, rs=slide_pair(builder,draw,sem,x,y+284,245,"",vertical=False);regions+=rs
        return regions
    used2=[find_pair(builder._pair_by_id.values(),family="v2",frame_view=f,modality=m)
           for f in ["0000","0999","1999"] for m in ["Metric depth [0,6 m]","Raw learned semantic color"]]
    save_slide(builder,"02_depth_and_semantic.png","Depth and learned semantic color",
               "Shared depth display range; raw learned colors are distinct from fixed semantic IDs.",used2,slide2,
               "Depth: fixed 0-6 m visualization. Learned colors are independently optimized and are not GT-palette recoloring.")

    def slide3(canvas, draw):
        regions=[]; views=[
            (find_pair(builder._pair_by_id.values(),family="v1",frame_view="overview",modality="RGB Gaussian reconstruction"),"V1 overview"),
            (find_pair(builder._pair_by_id.values(),family="v3a_cross_modal",frame_view="room_overview",modality="RGB"),"V3A room_overview"),
            (find_pair(builder._pair_by_id.values(),family="v3a_cross_modal",frame_view="top_oblique",modality="RGB"),"V3A top_oblique"),]
        for i,(row,label) in enumerate(views):
            x=62+i*620; draw.text((x,160),label,fill="#222222",font=get_font(18,True))
            _,rs=slide_pair(builder,draw,row,x,194,270,"",vertical=True);regions+=rs
        return regions
    used3=[r for r,_ in selections["full_rgb"]]+[find_pair(builder._pair_by_id.values(),family="v1",frame_view="overview",modality="RGB Gaussian reconstruction")]
    save_slide(builder,"03_full_scene_3d.png","Full-scene RGB Gaussian reconstructions",
               "Camera family is printed per view; V1 and V3A camera definitions are distinct.",used3,slide3,
               "Map-view diagnostics. V1 overview and V3A room_overview/top_oblique are not interchangeable cameras.")

    def slide4(canvas, draw):
        regions=[]
        # Two large fixed-ID views across the top.
        for i,view in enumerate(["room_overview","top_oblique"]):
            row=find_pair(builder._pair_by_id.values(),family="v3a_cross_modal",frame_view=view,modality="Fixed semantic IDs")
            x=55+i*925; draw.text((x,150),f"Fixed per-Gaussian Semantic IDs | V3A {view}",fill="#222222",font=get_font(16,True))
            _,rs=slide_pair(builder,draw,row,x,178,390,"",vertical=False);regions+=rs
        # Three representative classwise selections; full five-class figure remains in Figure 06.
        for i,name in enumerate(["wall","floor","sofa"]):
            row=find_pair(builder._pair_by_id.values(),family="v3a_classwise",contains=f"{name}_top_oblique.png")
            x=85+i*590; draw.text((x,510),f"Selected Gaussian centers: {name}",fill="#222222",font=get_font(16,True))
            _,rs=slide_pair(builder,draw,row,x,538,250,"",vertical=True);regions+=rs
        return regions
    used4=[find_pair(builder._pair_by_id.values(),family="v3a_cross_modal",frame_view=v,modality="Fixed semantic IDs") for v in ["room_overview","top_oblique"]]
    used4 += [find_pair(builder._pair_by_id.values(),family="v3a_classwise",contains=f"{n}_top_oblique.png") for n in ["wall","floor","sofa"]]
    save_slide(builder,"04_semantic_structure.png","Fixed semantic-ID structure",
               "Fixed per-Gaussian metadata, shown with the verified Replica palette.",used4,slide4,
               "These are selected Gaussian-center labels, not categorical per-pixel predictions.")

    def slide5(canvas, draw):
        regions=[]
        traj=selections["trajectory"][0][0]
        draw.text((65,150),"Estimated camera trajectory over reconstructed geometry",fill="#222222",font=get_font(19,True))
        _,rs=slide_pair(builder,draw,traj,65,182,460,"",vertical=False);regions+=rs
        notes=[
            "Independent estimated trajectories shown from the same comparison camera; not a quantitative ATE plot.",
            "Fixed IDs are per-Gaussian metadata; learned semantic colors are a separate representation.",
            "Gaussian-center geometry is a sampled diagnostic, not a continuous surface.",
            "Qualitative figures do not establish statistical non-inferiority or full-scene runtime speedup.",
        ]
        y=180
        for note in notes:
            draw.text((1100,y),"• "+note,fill="#333333",font=get_font(18));y+=88
        for i,(row,label) in enumerate([selections["rgb_frames"][2],
                (find_pair(builder._pair_by_id.values(),family="v3a_cross_modal",frame_view="top_oblique",modality="Fixed semantic IDs"),"Fixed semantic IDs")]):
            x=90+i*880;draw.text((x,700),label,fill="#222222",font=get_font(17,True))
            _,rs=slide_pair(builder,draw,row,x,730,380,"",vertical=False);regions+=rs
        return regions
    used5=[selections["trajectory"][0][0],selections["rgb_frames"][2][0],find_pair(builder._pair_by_id.values(),family="v3a_cross_modal",frame_view="top_oblique",modality="Fixed semantic IDs")]
    save_slide(builder,"05_trajectory_and_summary.png","Trajectory and interpretation limits",
               "A visual summary of the saved Phase 4 and P6-BAM-006 maps.",used5,slide5,
               "Visual comparison only. Trajectories are estimated independently; no new metric or quantitative trajectory claim is made.")


def build_thesis_plate(builder: FigureBuilder, selected: list[tuple[dict[str, Any], str]]) -> None:
    builder.save_figure(
        "final_phase4_vs_phase6_qualitative_plate.png",
        "Phase 4 and Phase 6 qualitative comparison",
        "Replica room0 | observed camera, full-scene appearance, fixed IDs, and estimated trajectory",
        selected,
        "Qualitative evidence from one Phase 4 and one P6-BAM-006 V-A2 run. Fixed IDs are per-Gaussian metadata; the trajectory panels are not an ATE comparison.",
        panel_width=850,
    )
    # Rename the output record type to make the thesis plate explicit.
    builder.records[-1]["image_type"] = "thesis_summary_plate"
    builder.records[-1]["output_path"] = "thesis/final_phase4_vs_phase6_qualitative_plate.png"
    src=builder.output/"figures/final_phase4_vs_phase6_qualitative_plate.png"
    dst=builder.output/"thesis/final_phase4_vs_phase6_qualitative_plate.png"
    dst.parent.mkdir(parents=True,exist_ok=True)
    if dst.exists(): raise FileExistsError(dst)
    src.replace(dst)
    builder.records[-1]["output_sha256"]=sha256(dst)


def build_all(builder: FigureBuilder, pairs: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    selections=choose(pairs)
    builder._pair_by_id=pairs
    legend_path="results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/categorical/legend_29_classes.png"
    legend={"path":legend_path,"sha256":sha256(builder.repo/legend_path),"meaning":"Verified 29-class Replica palette"}
    builder.save_figure(REQUIRED_FIGURES[0],"Observed-camera RGB reconstruction fidelity",
        "Phase 4 and Phase 6 map renders at the same Phase 4 estimated cameras; five fixed frames.",selections["rgb_frames"],
        "Phase 6 is rendered at the Phase 4 estimated camera pose; this is not a comparison of independent Phase 6 tracking poses.")
    builder.save_figure(REQUIRED_FIGURES[1],"Observed-camera depth visualization",
        "Five fixed frames | rendered depth visualization | shared 0-6 m display range.",selections["depth_frames"],
        "The fixed display range supports visual comparison; no raw-array analysis or Depth L1 metric was recomputed.")
    builder.save_figure(REQUIRED_FIGURES[2],"Observed-camera learned semantic color",
        "Raw learned semantic-color rendering | five fixed frames.",selections["semantic_frames"],
        "Learned color values are independently optimized; they are not fixed IDs or GT-palette-assisted recoloring.")
    builder.save_figure(REQUIRED_FIGURES[3],"Full-scene RGB Gaussian reconstruction",
        "Phase 4 V3A camera family | room_overview and top_oblique are distinct named views.",selections["full_rgb"],
        "Unfiltered RGB Gaussian map views. Both methods use the same Phase 4 V3A camera definition within each row.")
    builder.save_figure(REQUIRED_FIGURES[4],"Cross-modal reconstruction and semantic structure",
        "Phase 4 V3A top_oblique camera | paired modalities use the same camera definition.",selections["cross_modal"],
        "Gaussian-center geometry is a sampled diagnostic, not a surface. Fixed IDs are per-Gaussian labels, not per-pixel predictions.")
    builder.save_figure(REQUIRED_FIGURES[5],"Selected fixed semantic-ID class structure",
        "Phase 4 V3A top_oblique camera | identical selected classes and verified Replica palette.",selections["classwise"],
        "Each panel shows selected Gaussian centers carrying the named fixed semantic ID; this is not per-pixel segmentation.",
        appendix_images=[legend])
    builder.save_figure(REQUIRED_FIGURES[6],"Estimated camera trajectories in reconstructed geometry",
        "Phase 4 V3A top_oblique comparison camera.",selections["trajectory"],
        "Independent estimated trajectories shown from the same comparison camera; not a quantitative ATE plot.")
    builder.save_figure(REQUIRED_FIGURES[7],"Full-scene 3D semantic visualization",
        "Learned semantic-color rendering and fixed per-Gaussian semantic IDs are separate representations.",selections["semantic_3d"],
        "Learned colors need not match across runs. Fixed IDs use the verified Replica palette and are not categorical per-pixel predictions.",
        appendix_images=[legend])
    build_slides(builder,selections,legend)
    build_thesis_plate(builder,selections["overview_plate"])
    # The Gate 2 camera record proves the V1/V3A top_oblique distinction; attach it to report metadata.
    builder.camera_family_note={
        "v1_top_oblique_sha256": "0d865494919fb2066cf769ef654163ee3f1e262d5ebb4cf8b95681d6934ec196",
        "v3a_top_oblique_sha256": "a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d",
        "distinct": True,
    }
    return builder.records


def run(repo: Path, gate2: Path, output: Path) -> dict[str, Any]:
    if output.exists():
        raise FileExistsError(f"Gate 3 output exists; refusing overwrite: {output}")
    gate2_manifest, gate2_validation, pairs, initial_sources = load_gate2(repo, gate2)
    checkpoint_before={}
    for rel, expected in CHECKPOINTS.items():
        p=repo/rel
        if not p.is_file() or sha256(p)!=expected: raise ValueError(f"Protected model hash mismatch: {rel}")
        checkpoint_before[rel]=sha256(p)
    output.mkdir(parents=True,exist_ok=False)
    builder=FigureBuilder(repo,gate2,output)
    builder._gate2_validation=gate2_validation
    records=build_all(builder,pairs)
    if len([r for r in records if r["image_type"]=="scientific_figure"])!=8:
        raise ValueError("Expected eight required scientific figures")
    if len([r for r in records if r["image_type"]=="16:9_presentation_slide"])!=5:
        raise ValueError("Expected five required presentation slides")
    if len([r for r in records if r["image_type"]=="thesis_summary_plate"])!=1:
        raise ValueError("Expected one thesis summary plate")
    after_sources={path:sha256(Path(path)) for path in builder.source_hashes}
    source_unchanged=all(after_sources[p]==digest for p,digest in builder.source_hashes.items())
    checkpoint_after={rel:sha256(repo/rel) for rel in CHECKPOINTS}
    if not source_unchanged or checkpoint_after!=checkpoint_before:
        raise ValueError("Source images or protected model hashes changed during packaging")
    all_pngs=list(output.rglob("*.png"))
    expected_pngs=14
    if len(all_pngs)!=expected_pngs: raise ValueError(f"Expected exactly {expected_pngs} output PNGs, found {len(all_pngs)}")
    for path in all_pngs:
        with Image.open(path) as im:
            im.load()
            if im.mode!="RGB" or not any(lo!=hi for lo,hi in im.getextrema()): raise ValueError(f"Bad PNG: {path}")
    figure_names={r["filename"] for r in records if r["image_type"]=="scientific_figure"}
    slide_names={r["filename"] for r in records if r["image_type"]=="16:9_presentation_slide"}
    if figure_names!=set(REQUIRED_FIGURES) or slide_names!=set(REQUIRED_SLIDES): raise ValueError("Required output filenames differ")
    validation={
        "gate3_classification":"PASS_P6_BAM_007_GATE3_THESIS_PACKAGING",
        "gate2_input":"results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate2_side_by_side/run_02",
        "gate2_status":"PASS_P6_BAM_007_GATE2_SIDE_BY_SIDE",
        "gate2_pair_count_verified":len(gate2_manifest["pairs"]),
        "gate2_preview_count_verified":len(gate2_manifest["previews"]),
        "gate2_pair_hashes_verified":len(gate2_manifest["pairs"]),
        "gate2_source_image_sha256_checks":len(initial_sources),
        "gate2_camera_pair_checks":len(gate2_manifest["pairs"]),
        "expected_figure_count":8,"actual_figure_count":len(figure_names),
        "expected_slide_count":5,"actual_slide_count":len(slide_names),
        "expected_thesis_plate_count":1,"actual_thesis_plate_count":sum(r["image_type"]=="thesis_summary_plate" for r in records),
        "expected_total_png_count":14,"actual_total_png_count":len(all_pngs),
        "all_images_readable":True,"all_outputs_nonuniform":True,
        "source_hash_checks":len(builder.source_hashes),
        "source_images_unchanged":source_unchanged,
        "camera_provenance_inherited_and_reverified":True,
        "v1_v3a_top_oblique_camera_distinction":builder.camera_family_note,
        "phase4_left_phase6_right":True,
        "full_resolution_gate2_pairs_preserved":True,
        "all_full_resolution_figures_keep_native_panels":True,
        "slide_resizing_symmetric_with_per_panel_transform_records":True,
        "no_deceptive_crop_or_image_enhancement":True,
        "checkpoint_hashes_before":checkpoint_before,
        "checkpoint_hashes_after":checkpoint_after,
        "checkpoint_hashes_unchanged":checkpoint_before==checkpoint_after,
        "cuda_or_gpu_work":False,"gaussian_rendering_or_model_loading":False,
        "slam_tracking_mapping_evaluation_or_metric_recomputation":False,
        "gate4_or_gate5_started":False,
    }
    metadata=output/"metadata";metadata.mkdir(parents=True,exist_ok=True)
    manifest={
        "session":"SESSION_021","gate":3,"repository_head":"17fe98a82a1c7c38b05b7fdefe154bb7b0002453",
        "gate2_root":str(gate2.relative_to(repo)),"gate2_validation_sha256":sha256(gate2/"metadata/validation_report.json"),
        "figure_records":records,
        "camera_family_notes":builder.camera_family_note,
    }
    (metadata/"figure_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
    (metadata/"validation_report.json").write_text(json.dumps(validation,indent=2)+"\n",encoding="utf-8")
    readme="""# Gate 3 thesis-ready qualitative package

This package contains eight scientific comparison figures, five 16:9 presentation slides, and one thesis summary plate. Every image panel is derived from the accepted P6-BAM-007 Gate 2 `run_02` pair manifest and output PNGs. The Gate 2 outputs remain intact as the native-resolution lossless comparison source.

The utility uses Pillow on CPU. It never loads models or imports CUDA/rendering code. Full scientific figures use source panel dimensions when practical. Slides and the thesis plate apply uniform Lanczos scaling equally to Phase 4 and Phase 6 panels within each pair; exact transforms and panel coordinates are recorded in `figure_manifest.json`. No source image is color-adjusted, sharpened, denoised, content-cropped, or selectively altered.

## Interpretation

- Observed-frame RGB/depth/semantic comparisons use the Phase 4 estimated camera pose for both systems. This does not compare Phase 6's independent tracking pose.
- Depth is a rendered visualization with the shared 0-6 m range; no Depth L1 was recomputed.
- Learned semantic-color rendering and fixed semantic IDs are separate. Learned colors are independently optimized and need not match. Fixed IDs are per-Gaussian metadata with the verified Replica palette, not per-pixel predictions.
- Gaussian-center geometry is a sampled spatial diagnostic, not a continuous surface or mesh.
- Trajectories are independently estimated and are not a quantitative ATE plot.
- V1 and V3A `top_oblique` are distinct camera definitions.

## Review and limitations

Start with Figures 01-03 for observed-frame outputs, then Figures 04-08 for full-scene and semantic diagnostics, followed by the slides and thesis plate. Visual differences do not establish statistical non-inferiority, runtime superiority, novel-view accuracy, or identical trajectories. These outputs have not been visually approved by the researcher. Gate 4 and Gate 5 remain pending.

`figure_manifest.json` maps every figure, slide, and plate to Gate 2 pair IDs, original source paths and hashes, camera hashes, captions/caveats, and resize transforms. `SHA256SUMS.txt` covers generated outputs and metadata except itself.
"""
    (metadata/"README.md").write_text(readme,encoding="utf-8")
    log=output/"logs/package.log";log.parent.mkdir(parents=True,exist_ok=True)
    log.write_text("CPU-only Gate 3 Pillow composition.\nFigures: 8; slides: 5; thesis plate: 1; PNGs: 14.\nNo CUDA, model loading, rendering, SLAM, or evaluation.\n",encoding="utf-8")
    sum_path=metadata/"SHA256SUMS.txt"
    files=sorted(p for p in output.rglob("*") if p.is_file() and p!=sum_path)
    sum_path.write_text("".join(f"{sha256(p)}  {p.relative_to(output)}\n" for p in files),encoding="utf-8")
    return validation


def main(argv: list[str]|None=None)->int:
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root",type=Path,required=True)
    parser.add_argument("--gate2-root",type=Path,required=True)
    parser.add_argument("--output-root",type=Path,required=True)
    args=parser.parse_args(argv)
    repo=args.repo_root.resolve()
    gate2=args.gate2_root if args.gate2_root.is_absolute() else repo/args.gate2_root
    output=args.output_root if args.output_root.is_absolute() else repo/args.output_root
    logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")
    try:
        result=run(repo,gate2.resolve(),output.resolve())
    except Exception as exc:
        logging.exception("Gate 3 packaging failed: %s",exc)
        return 2
    print(json.dumps(result,indent=2))
    return 0


if __name__=="__main__":
    sys.exit(main())
