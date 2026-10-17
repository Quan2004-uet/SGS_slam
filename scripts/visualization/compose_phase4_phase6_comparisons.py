#!/usr/bin/env python3
"""Compose audited Phase 4/Phase 6 PNG pairs without loading models or CUDA."""

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

from PIL import Image, ImageChops, ImageDraw, ImageFont


EXPECTED_FAMILY_COUNTS = {
    "v1": 6,
    "v2": 15,
    "v3a_cross_modal": 12,
    "v3a_classwise": 9,
    "v3a_trajectory": 1,
}
EXPECTED_READY_COUNTS = {
    "READY_FOR_SIDE_BY_SIDE": 12,
    "READY_WITH_EXPLICIT_CAVEAT": 31,
}
PHASE4_LABEL = "Phase 4 - CPU Keyframe Offload"
PHASE6_LABEL = "Phase 6 - CPU Keyframe Offload + Budget-Aware Mapping (V-A2)"
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
FAMILY_DIRS = {
    "V1": "v1",
    "V2": "v2",
    "V3A": "v3a_cross_modal",  # modality-specific override below
}
MODALITY_LABELS = {
    "RGB Gaussian reconstruction": "Unfiltered RGB Gaussian reconstruction",
    "RGB": "Unfiltered RGB Gaussian reconstruction",
    "Metric depth [0,6 m]": "Rendered depth visualization; fixed shared 0-6 m display range",
    "Raw learned semantic color": "Learned semantic-color rendering",
    "Learned semantic color": "Learned semantic-color rendering",
    "Gaussian-center geometry": "Sampled Gaussian-center geometry diagnostic",
    "Fixed semantic IDs": "Fixed per-Gaussian Semantic IDs with verified Replica palette",
    "Fixed semantic-ID class selection": "Fixed per-Gaussian Semantic IDs with verified Replica palette",
    "Estimated trajectory in geometry": "Estimated camera trajectory over reconstructed geometry",
}
EXPLICIT_CAVEATS = {
    ("V1", "RGB Gaussian reconstruction"): "The maps were independently estimated; this matched view is qualitative, not evidence of equal trajectories or novel-view accuracy.",
    ("V1", "Learned semantic color"): "Learned color values are independent between runs and are not directly comparable as class labels.",
    ("V2", "RGB"): "Phase 6 is rendered using the Phase 4 estimated camera; this does not compare each system at its own estimated pose.",
    ("V2", "Metric depth [0,6 m]"): "A shared display scale aids visual comparison but is not a recomputed depth-accuracy metric.",
    ("V2", "Raw learned semantic color"): "Learned color values are independent between runs; no GT-palette-assisted recoloring is shown.",
    ("V3A", "RGB"): "These are map-view diagnostics and do not establish novel-view accuracy or identical estimated poses.",
    ("V3A", "Raw learned semantic color"): "Learned color values are independent between runs and should not be interpreted as class identity.",
    ("V3A", "Gaussian-center geometry"): "Gaussian centers are sampled diagnostics, not a continuous surface or mesh.",
    ("V3A", "Estimated trajectory in geometry"): "The paths are independently estimated; this matched view is not a quantitative ATE comparison.",
}


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def parse_appendix(plan_path: Path) -> list[dict[str, str]]:
    lines = plan_path.read_text(encoding="utf-8").splitlines()
    start = next((i for i, line in enumerate(lines)
                  if line.startswith("| Family | Frame/view | Modality |")), None)
    if start is None:
        raise ValueError("Plan is missing Appendix A per-pair source audit table")
    rows: list[dict[str, str]] = []
    headers = [cell.strip() for cell in lines[start].strip("|").split("|")]
    expected_headers = [
        "Family", "Frame/view", "Modality", "Phase 4 PNG", "Phase 6 PNG",
        "Camera SHA256", "P4/P6 size", "P4 image SHA256", "P6 image SHA256",
        "Interpretation", "Classification",
    ]
    if headers != expected_headers:
        raise ValueError(f"Unexpected Appendix A headers: {headers!r}")
    for line in lines[start + 2:]:
        if not line.startswith("|"):
            break
        cells = [cell.strip() for cell in line.strip("|").split("|")]
        if len(cells) != len(headers):
            raise ValueError(f"Malformed Appendix A row with {len(cells)} cells")
        rows.append(dict(zip(headers, cells)))
    if len(rows) != 43:
        raise ValueError(f"Expected exactly 43 Appendix A rows, found {len(rows)}")
    return rows


def uncode(value: str) -> str:
    return value.strip().strip("`")


def family_dir(row: dict[str, str]) -> str:
    family, modality = row["Family"], row["Modality"]
    if family == "V1":
        return "v1"
    if family == "V2":
        return "v2"
    if family == "V3A" and modality == "Fixed semantic-ID class selection":
        return "v3a_classwise"
    if family == "V3A" and modality == "Estimated trajectory in geometry":
        return "v3a_trajectory"
    if family == "V3A":
        return "v3a_cross_modal"
    raise ValueError(f"Unknown family {family!r}")


def camera_paths(repo: Path, row: dict[str, str]) -> tuple[Path, Path]:
    family, ident = row["Family"], row["Frame/view"]
    if family == "V1":
        source = repo / "results/runtime_artifacts/phase4_vb001_visualization/cameras" / f"{ident}.json"
        copy = repo / "results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/cameras" / f"{ident}.json"
    elif family == "V2":
        source = repo / "results/runtime_artifacts/phase4_vb001_visualization_v2/frames" / f"frame_{ident}/frame_metadata.json"
        copy = repo / "results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/cameras/phase4_v2" / f"frame_{ident}.json"
    else:
        view = "top_oblique" if ident.endswith("top_oblique.png") or ident == "estimated_trajectory_3d" else ident
        source = repo / "results/runtime_artifacts/phase4_vb001_visualization_v3a/cameras" / f"{view}.json"
        copy = repo / "results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/cameras/v3a" / f"{view}.json"
    return source, copy


def pair_id(row: dict[str, str]) -> str:
    components = [row["Family"], row["Frame/view"], row["Modality"]]
    slug = "_".join(components).lower()
    slug = re.sub(r"[^a-z0-9]+", "_", slug).strip("_")
    return slug


def explicit_caveat(row: dict[str, str]) -> str:
    if row["Classification"] != "READY_WITH_EXPLICIT_CAVEAT":
        return ""
    family, modality = row["Family"], row["Modality"]
    key = (family, modality)
    if key not in EXPLICIT_CAVEATS:
        raise ValueError(f"No explicit visible caveat defined for {key}")
    return EXPLICIT_CAVEATS[key]


def load_rgb(path: Path) -> Image.Image:
    with Image.open(path) as source:
        source.load()
        if source.mode != "RGB":
            raise ValueError(f"Expected RGB PNG, got {source.mode}: {path}")
        return source.copy()


def font_paths() -> tuple[str, str]:
    regular_candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Regular.ttf"),
    ]
    bold_candidates = [
        Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
        Path("/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"),
    ]
    regular = next((p for p in regular_candidates if p.is_file()), None)
    bold = next((p for p in bold_candidates if p.is_file()), None)
    return (str(regular) if regular else "Pillow-default", str(bold) if bold else "Pillow-default")


def get_font(path: str, size: int) -> ImageFont.ImageFont:
    return ImageFont.load_default() if path == "Pillow-default" else ImageFont.truetype(path, size=size)


def wrap_text(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = f"{current} {word}".strip()
        if current and draw.textbbox((0, 0), candidate, font=font)[2] > width:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


def compose_pair(row: dict[str, str], left: Image.Image, right: Image.Image,
                 output_path: Path, regular_font: str, bold_font: str) -> dict[str, Any]:
    if left.size != right.size:
        raise ValueError(f"Panel dimensions differ: {left.size} vs {right.size}")
    width, height = left.size
    margin, gap = 24, 24
    header_h, label_h, footer_h = 84, 34, 72
    canvas_w = margin * 2 + width * 2 + gap
    canvas_h = margin + header_h + label_h + height + footer_h + margin
    canvas = Image.new("RGB", (canvas_w, canvas_h), "#f7f7f7")
    draw = ImageDraw.Draw(canvas)
    title_font = get_font(bold_font, 22)
    body_font = get_font(regular_font, 17)
    small_font = get_font(regular_font, 14)

    title = f"{row['Family']} | {row['Frame/view']} | {row['Modality']}"
    draw.text((margin, margin), title, fill="#202020", font=title_font)
    scientific_label = MODALITY_LABELS.get(row["Modality"], row["Modality"])
    draw.text((margin, margin + 34), scientific_label, fill="#404040", font=body_font)

    top = margin + header_h
    left_x = margin
    right_x = margin + width + gap
    draw.text((left_x, top), PHASE4_LABEL, fill="#202020", font=body_font)
    draw.text((right_x, top), PHASE6_LABEL, fill="#202020", font=body_font)
    panel_y = top + label_h
    canvas.paste(left, (left_x, panel_y))
    canvas.paste(right, (right_x, panel_y))
    draw.rectangle((left_x - 1, panel_y - 1, left_x + width, panel_y + height), outline="#888888", width=1)
    draw.rectangle((right_x - 1, panel_y - 1, right_x + width, panel_y + height), outline="#888888", width=1)
    draw.line((margin + width, panel_y, margin + width, panel_y + height), fill="#c0c0c0", width=1)

    footer_y = panel_y + height + 10
    if row["Classification"] == "READY_WITH_EXPLICIT_CAVEAT":
        note = f"{row['Classification']} | Meaning: {row['Interpretation']} | Caveat: {explicit_caveat(row)}"
    else:
        note = f"{row['Classification']} | Meaning: {row['Interpretation']}"
    lines = wrap_text(draw, note, small_font, canvas_w - margin * 2)
    if len(lines) > 3:
        lines = lines[:3]
        lines[-1] = lines[-1].rstrip(" .") + "…"
    for i, line in enumerate(lines):
        draw.text((margin, footer_y + i * 18), line, fill="#404040", font=small_font)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path, format="PNG", optimize=False)
    # Verify the exact decoded source pixels were pasted without resampling.
    with Image.open(output_path) as check:
        check.load()
        if check.crop((left_x, panel_y, left_x + width, panel_y + height)).tobytes() != left.tobytes():
            raise ValueError(f"Phase 4 panel pixel integrity failed: {output_path}")
        if check.crop((right_x, panel_y, right_x + width, panel_y + height)).tobytes() != right.tobytes():
            raise ValueError(f"Phase 6 panel pixel integrity failed: {output_path}")
        if check.size != canvas.size:
            raise ValueError(f"Output dimensions changed unexpectedly: {output_path}")
    return {
        "output_dimensions": list(canvas.size),
        "panel_dimensions": [width, height],
        "panel_origins": {"phase4": [left_x, panel_y], "phase6": [right_x, panel_y]},
        "padding_px": margin,
        "gap_px": gap,
        "resampling": "none",
        "font_files": {"regular": regular_font, "bold": bold_font},
    }


def verify_existing_pair(path: Path, left: Image.Image, right: Image.Image) -> dict[str, Any]:
    if left.size != right.size:
        raise ValueError(f"Panel dimensions differ: {left.size} vs {right.size}")
    width, height = left.size
    margin, gap = 24, 24
    header_h, label_h, footer_h = 84, 34, 72
    canvas_w = margin * 2 + width * 2 + gap
    canvas_h = margin + header_h + label_h + height + footer_h + margin
    left_x, right_x = margin, margin + width + gap
    panel_y = margin + header_h + label_h
    with Image.open(path) as image:
        image.load()
        if image.mode != "RGB" or image.size != (canvas_w, canvas_h):
            raise ValueError(f"Existing pair layout does not match expected geometry: {path}")
        if image.crop((left_x, panel_y, left_x + width, panel_y + height)).tobytes() != left.tobytes():
            raise ValueError(f"Existing Phase 4 panel pixels do not match current source: {path}")
        if image.crop((right_x, panel_y, right_x + width, panel_y + height)).tobytes() != right.tobytes():
            raise ValueError(f"Existing Phase 6 panel pixels do not match current source: {path}")
        if not any(low != high for low, high in image.getextrema()):
            raise ValueError(f"Existing pair is uniform/blank: {path}")
    regular, bold = font_paths()
    return {
        "output_dimensions": [canvas_w, canvas_h],
        "panel_dimensions": [width, height],
        "panel_origins": {"phase4": [left_x, panel_y], "phase6": [right_x, panel_y]},
        "padding_px": margin,
        "gap_px": gap,
        "resampling": "none",
        "font_files": {"regular": regular, "bold": bold},
    }


def preview_sheet(paths: list[tuple[str, Path]], destination: Path, title: str,
                  columns: int = 2, max_width: int = 1500) -> None:
    tile_w = max(1, min(max_width // columns, 800))
    pad, label_h, gap = 18, 28, 18
    tiles: list[tuple[str, Image.Image]] = []
    for figure_id, path in paths:
        with Image.open(path) as im:
            im.load()
            thumb_h = max(1, round(im.height * tile_w / im.width))
            resampling = getattr(Image, "Resampling", Image)
            thumb = im.resize((tile_w, thumb_h), resampling.LANCZOS)
        tiles.append((figure_id, thumb))
    rows = (len(tiles) + columns - 1) // columns
    max_tile_h = max(im.height for _, im in tiles)
    title_h = 46
    canvas = Image.new("RGB", (pad * 2 + columns * tile_w + gap * (columns - 1),
                               title_h + pad * 2 + rows * (label_h + max_tile_h) + gap * (rows - 1)), "#f4f4f4")
    draw = ImageDraw.Draw(canvas)
    regular, bold = font_paths()
    draw.text((pad, 10), f"PREVIEW CONTACT SHEET - {title}", fill="#202020", font=get_font(bold, 18))
    draw.text((pad, 29), "Reduced preview only; paired PNGs retain native source panel pixels.", fill="#555555", font=get_font(regular, 12))
    for i, (figure_id, image) in enumerate(tiles):
        row, col = divmod(i, columns)
        x = pad + col * (tile_w + gap)
        y = title_h + pad + row * (label_h + max_tile_h + gap)
        draw.text((x, y), figure_id, fill="#222222", font=get_font(bold, 13))
        canvas.paste(image, (x, y + label_h))
    destination.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(destination, format="PNG", optimize=False)


def validate_and_compose(repo: Path, plan_path: Path, output_root: Path,
                         resume_incomplete: bool = False) -> dict[str, Any]:
    if output_root.exists() and not resume_incomplete:
        raise FileExistsError(f"Output root already exists; refusing to overwrite: {output_root}")
    rows = parse_appendix(plan_path)
    counts = Counter(family_dir(row) for row in rows)
    readiness = Counter(uncode(row["Classification"]) for row in rows)
    if dict(counts) != EXPECTED_FAMILY_COUNTS:
        raise ValueError(f"Unexpected family distribution: {dict(counts)}")
    if dict(readiness) != EXPECTED_READY_COUNTS:
        raise ValueError(f"Unexpected readiness distribution: {dict(readiness)}")

    logging.info("Preflighting %d planned pairs", len(rows))
    prepared: list[dict[str, Any]] = []
    source_hashes: dict[str, str] = {}
    protected_before: dict[str, str] = {}
    issues: dict[str, list[str]] = {k: [] for k in ["missing", "invalid_images", "source_hash_mismatches", "camera_mismatches"]}
    for relative, expected in CHECKPOINTS.items():
        path = repo / relative
        if not path.is_file() or sha256(path) != expected:
            raise ValueError(f"Protected model hash mismatch: {relative}")
        protected_before[relative] = sha256(path)

    for index, row in enumerate(rows, start=1):
        row = {k: uncode(v) for k, v in row.items()}
        p4 = repo / row["Phase 4 PNG"]
        p6 = repo / row["Phase 6 PNG"]
        camera_expected = row["Camera SHA256"]
        expected_p4 = row["P4 image SHA256"]
        expected_p6 = row["P6 image SHA256"]
        if not p4.is_file() or not p6.is_file():
            issues["missing"].append(f"{row['Family']} {row['Frame/view']}: {p4} | {p6}")
            continue
        actual_p4, actual_p6 = sha256(p4), sha256(p6)
        source_hashes[str(p4)] = actual_p4
        source_hashes[str(p6)] = actual_p6
        if actual_p4 != expected_p4 or actual_p6 != expected_p6:
            issues["source_hash_mismatches"].append(f"{p4}={actual_p4}; {p6}={actual_p6}")
            continue
        try:
            im4, im6 = load_rgb(p4), load_rgb(p6)
        except Exception as exc:
            issues["invalid_images"].append(f"{p4} | {p6}: {exc}")
            continue
        declared_sizes = row["P4/P6 size"].split("/")
        actual_sizes = [f"{im4.width}×{im4.height}", f"{im6.width}×{im6.height}"]
        if len(declared_sizes) != 2 or [x.strip() for x in declared_sizes] != actual_sizes or im4.size != im6.size:
            issues["invalid_images"].append(f"Dimension mismatch for {p4} | {p6}: {actual_sizes}")
            continue
        camera_source, camera_copy = camera_paths(repo, row)
        if not camera_source.is_file() or not camera_copy.is_file():
            issues["camera_mismatches"].append(f"Missing camera evidence: {camera_source} | {camera_copy}")
            continue
        source_camera_hash = sha256(camera_source)
        copy_camera_hash = sha256(camera_copy)
        if source_camera_hash != camera_expected or copy_camera_hash != camera_expected or camera_source.read_bytes() != camera_copy.read_bytes():
            issues["camera_mismatches"].append(
                f"{row['Family']} {row['Frame/view']}: expected {camera_expected}; source {source_camera_hash}; copy {copy_camera_hash}"
            )
            continue
        dirname = family_dir(row)
        pid = f"{index:02d}_{pair_id(row)}"
        output_rel = Path("pairs") / dirname / f"{pid}.png"
        prepared.append({
            "row": row, "pair_id": pid, "family_dir": dirname,
            "phase4_path": p4, "phase6_path": p6,
            "phase4_image": im4, "phase6_image": im6,
            "camera_source": camera_source, "camera_copy": camera_copy,
            "camera_sha256": camera_expected,
            "output_rel": output_rel,
            "dimensions": actual_sizes,
        })
    if any(issues.values()):
        raise ValueError("Preflight failed; no output was created: " + json.dumps(issues, indent=2))
    if len(prepared) != 43:
        raise ValueError(f"Preflight assembled {len(prepared)} pairs, expected 43")

    # Resume only the exact partial tree created by this utility: existing files
    # must all be expected pair PNGs, and each decoded panel must match source.
    expected_relpaths = {item["output_rel"] for item in prepared}
    if output_root.exists():
        existing_files = {p.relative_to(output_root) for p in output_root.rglob("*") if p.is_file()}
        unexpected = existing_files - expected_relpaths
        if unexpected:
            raise FileExistsError(f"Refusing to resume tree with unexpected files: {sorted(map(str, unexpected))}")
        for item in prepared:
            existing = output_root / item["output_rel"]
            if existing.is_file():
                verify_existing_pair(existing, item["phase4_image"], item["phase6_image"])
    else:
        output_root.mkdir(parents=True, exist_ok=False)
    log_path = output_root / "logs/composition.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    regular_font, bold_font = font_paths()
    pair_records: list[dict[str, Any]] = []
    for item in prepared:
        record = item["row"]
        output_path = output_root / item["output_rel"]
        if output_path.exists():
            if not resume_incomplete:
                raise FileExistsError(f"Refusing to overwrite pair: {output_path}")
            settings = verify_existing_pair(output_path, item["phase4_image"], item["phase6_image"])
        else:
            settings = compose_pair(record, item["phase4_image"], item["phase6_image"],
                                    output_path, regular_font, bold_font)
        with Image.open(output_path) as output_image:
            output_image.load()
            extrema = output_image.getextrema()
            nonuniform = any(low != high for low, high in extrema)
        if not nonuniform:
            raise ValueError(f"Uniform/blank output: {output_path}")
        pair_records.append({
            "pair_id": item["pair_id"],
            "family": record["Family"],
            "family_directory": item["family_dir"],
            "frame_view_id": record["Frame/view"],
            "modality": record["Modality"],
            "phase4_source_path": record["Phase 4 PNG"],
            "phase6_source_path": record["Phase 6 PNG"],
            "phase4_source_sha256": sha256(item["phase4_path"]),
            "phase6_source_sha256": sha256(item["phase6_path"]),
            "camera_source_path": str(item["camera_source"].relative_to(repo)),
            "camera_copy_path": str(item["camera_copy"].relative_to(repo)),
            "camera_sha256": item["camera_sha256"],
            "phase4_input_dimensions": item["phase4_image"].size,
            "phase6_input_dimensions": item["phase6_image"].size,
            "output_paired_png": str(item["output_rel"]),
            "output_sha256": sha256(output_path),
            "output_dimensions": settings["output_dimensions"],
            "readiness_classification": record["Classification"],
            "scientific_interpretation": record["Interpretation"],
            "explicit_visible_caveat": explicit_caveat(record),
            "visible_modality_label": MODALITY_LABELS[record["Modality"]],
            "composition_settings": settings,
            "output_nonuniform": nonuniform,
        })
        logging.info("Composed %s", item["pair_id"])

    record_by_key = {(r["family"], r["frame_view_id"], r["modality"]): r for r in pair_records}
    preview_defs: list[tuple[str, str, list[dict[str, Any]], int]] = []
    preview_defs.append(("v1_overview.png", "V1 overview / oblique / top_oblique", [r for r in pair_records if r["family"] == "V1"], 2))
    for modality_key, name in [("RGB", "v2_rgb_five_frames.png"),
                               ("Metric depth [0,6 m]", "v2_depth_five_frames.png"),
                               ("Raw learned semantic color", "v2_semantic_five_frames.png")]:
        preview_defs.append((name, name.replace("_", " "), [r for r in pair_records if r["family"] == "V2" and r["modality"] == modality_key], 2))
    preview_defs.append(("v3a_rgb_geometry_semantic.png", "V3A RGB / geometry / learned semantic color", [r for r in pair_records if r["family"] == "V3A" and r["modality"] in {"RGB", "Gaussian-center geometry", "Raw learned semantic color"}], 2))
    preview_defs.append(("v3a_semantic_id_classwise.png", "V3A fixed semantic IDs / selected classes", [r for r in pair_records if r["family"] == "V3A" and r["modality"] in {"Fixed semantic IDs", "Fixed semantic-ID class selection"}], 2))
    preview_defs.append(("v3a_trajectory.png", "V3A estimated trajectory in geometry", [r for r in pair_records if r["modality"] == "Estimated trajectory in geometry"], 1))
    previews: list[dict[str, Any]] = []
    for name, title, records, cols in preview_defs:
        preview_path = output_root / "previews" / name
        sheet_sources = [(r["pair_id"], output_root / r["output_paired_png"]) for r in records]
        preview_sheet(sheet_sources, preview_path, title, columns=cols)
        previews.append({"path": str(preview_path.relative_to(output_root)), "sha256": sha256(preview_path),
                         "source_pair_ids": [r["pair_id"] for r in records], "reduced_preview": True})

    # Verify originals and model checkpoints remained intact after composition.
    source_after = {path: sha256(Path(path)) for path in source_hashes}
    changed_sources = [path for path, value in source_hashes.items() if source_after[path] != value]
    protected_after = {relative: sha256(repo / relative) for relative in CHECKPOINTS}
    protected_ok = protected_after == protected_before
    pair_counts = Counter(r["family_directory"] for r in pair_records)
    readiness_counts = Counter(r["readiness_classification"] for r in pair_records)
    validation = {
        "expected_pair_count": 43,
        "actual_pair_count": len(pair_records),
        "expected_family_counts": EXPECTED_FAMILY_COUNTS,
        "actual_family_counts": dict(pair_counts),
        "expected_readiness_counts": EXPECTED_READY_COUNTS,
        "actual_readiness_counts": dict(readiness_counts),
        "preview_expected_count": 7,
        "preview_actual_count": len(previews),
        "preview_count": len(previews),
        "missing_or_blocked_pair_count": 0,
        "missing_pairs": issues["missing"],
        "invalid_images": issues["invalid_images"],
        "source_image_checksum_mismatches": issues["source_hash_mismatches"],
        "camera_mismatches": issues["camera_mismatches"],
        "camera_pair_checks": 43,
        "source_sha_checks": 86,
        "all_outputs_readable": True,
        "all_outputs_nonuniform": all(r["output_nonuniform"] for r in pair_records),
        "panel_pixel_integrity_checks": 86,
        "panel_pixel_integrity_pass": True,
        "source_unchanged_after_composition": not changed_sources,
        "changed_source_images": changed_sources,
        "protected_checkpoint_hashes_before": protected_before,
        "protected_checkpoint_hashes_after": protected_after,
        "protected_checkpoint_hashes_match": protected_ok,
        "source_image_content_cropped": False,
        "resampling_of_full_resolution_pairs": False,
        "new_gpu_rendering_or_cuda": False,
        "algorithm_or_config_changes": False,
        "final_gate_classification": "PASS_P6_BAM_007_GATE2_SIDE_BY_SIDE",
    }
    manifest = {
        "session": "SESSION_021",
        "gate": 2,
        "source_plan": str(plan_path.relative_to(repo)) if plan_path.is_relative_to(repo) else str(plan_path),
        "repository_head": "17fe98a82a1c7c38b05b7fdefe154bb7b0002453",
        "pairs": pair_records,
        "previews": previews,
    }
    metadata = output_root / "metadata"
    metadata.mkdir(parents=True, exist_ok=True)
    (metadata / "pair_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (metadata / "validation_report.json").write_text(json.dumps(validation, indent=2) + "\n", encoding="utf-8")
    readme = """# Gate 2 side-by-side comparison outputs

This package composes the 43 Phase 4/Phase 6 pairs listed in the P6-BAM-007 Gate 1 Appendix A. It uses Pillow on CPU to place the original decoded RGB PNGs into labeled panels. The full-resolution panels are copied pixel-for-pixel without resize, crop, warp, color adjustment, sharpening, denoising, or filtering. Title, system labels, separators, and the interpretation note occupy new surrounding bands only.

No Gaussian model was loaded; no CUDA operation, renderer, SLAM, tracking, mapping, optimization, evaluation, or metric recomputation was run. `pairs/` contains the full-resolution comparisons. `previews/` contains labeled, reduced contact-sheet previews; each identifies its source pair IDs in `metadata/pair_manifest.json`.

## Interpretation

- RGB is an unfiltered RGB Gaussian reconstruction.
- Depth is rendered metric depth shown with the shared fixed 0–6 m display range.
- Raw semantic images are learned semantic-color renderings; they are neither fixed class IDs nor GT-palette-assisted recoloring.
- Fixed-ID panels show per-Gaussian metadata with the verified Replica palette. They are not categorical per-pixel predictions.
- Geometry panels sample Gaussian centers and are diagnostics, not meshes or continuous surfaces.
- Trajectory panels show two independently estimated camera trajectories over each reconstruction. They are not a direct quantitative ATE comparison, and matched views do not imply identical trajectories.
- V1 and V3A `top_oblique` refer to distinct camera JSONs; the pair manifest records the camera hash for every comparison.

`READY_WITH_EXPLICIT_CAVEAT` explanations are printed on the associated pair panels and stored in the pair manifest. Phase 4 and Phase 6 source files remain separately preserved and unchanged.

## Attribution and limits

Phase 4 is `PHASE4-VB-001 — CPU Keyframe Offload`; Phase 6 is P6-BAM-006 V-A2 (Budget-Aware Mapping with CPU Keyframe Offload). This visual package adds no metric evidence and must not be used to claim statistical non-inferiority, full-scene runtime speedup, adaptive superiority over fixed-45, novel-view accuracy, or identical trajectories. Learned semantic-color values are independently learned, so visual color equality is not guaranteed to represent class equivalence.

## Suggested review order

1. V2 fixed-frame RGB and depth comparisons.
2. V1 camera views.
3. V3A RGB/geometry/learned-color views.
4. Fixed semantic-ID and selected classwise views.
5. Independently estimated trajectories.

See `pair_manifest.json`, `validation_report.json`, and `SHA256SUMS.txt` for exact provenance and integrity checks.
"""
    (metadata / "README.md").write_text(readme, encoding="utf-8")
    log_path = output_root / "logs/composition.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if not log_path.exists():
        log_path.write_text(
            "CPU-only Pillow composition completed.\n"
            f"Pairs: {len(pair_records)}; previews: {len(previews)}.\n"
            "Source PNG panels were retained at native resolution and verified pixel-for-pixel.\n"
            "No CUDA, model loading, rendering, SLAM, or evaluation was used.\n",
            encoding="utf-8",
        )
    # Include all generated deliverables except the self-referential sum file.
    sum_file = metadata / "SHA256SUMS.txt"
    generated = sorted(p for p in output_root.rglob("*") if p.is_file() and p != sum_file)
    sum_file.write_text("".join(f"{sha256(path)}  {path.relative_to(output_root)}\n" for path in generated), encoding="utf-8")
    if len(pair_records) != 43 or len(previews) != 7 or not protected_ok or changed_sources:
        raise ValueError("Post-composition validation failed")
    return validation


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, required=True)
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--output-root", type=Path, required=True)
    parser.add_argument("--resume-incomplete", action="store_true",
                        help="Resume only when the output contains expected pair PNGs and no other files")
    args = parser.parse_args(argv)
    repo = args.repo_root.resolve()
    plan = args.plan if args.plan.is_absolute() else repo / args.plan
    output = args.output_root if args.output_root.is_absolute() else repo / args.output_root
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    try:
        result = validate_and_compose(repo, plan.resolve(), output.resolve(), args.resume_incomplete)
    except Exception as exc:
        logging.error("Gate 2 composition failed safely: %s", exc)
        return 2
    logging.info("Gate 2 output complete: %s", output)
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
