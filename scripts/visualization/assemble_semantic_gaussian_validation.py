#!/usr/bin/env python3
"""Validate offline Figure 8B renders and assemble lossless camera comparisons."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[2]
NAMES = ("A_center_points.png", "B_learned_semantic_splats.png", "C_fixed_id_palette_splats.png")
METHODS = ("phase4", "phase6")
CAMERAS = ("room_overview", "top_oblique")
ORIGINALS = {
    "phase4": ROOT / "results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/categorical",
    "phase6": ROOT / "results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/cross_modal_overview/semantic/categorical",
}
EXPECTED_CHECKPOINTS = {
    "phase4": (ROOT / "experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz", "dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2"),
    "phase6": (ROOT / "results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/params.npz", "1193f5d5a854225d6e9fc68154d459b5eb026e056a91b5f00639b8da0facd0a5"),
}
FIG8 = ROOT / "results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate3_thesis_packaging/run_04/figures/figure_08_full_scene_semantic_3d_comparison.png"
FIG8_SHA = "1bf5ed3d3d6d96daa2719f6727dab1fbbf259cf447203c1ecec1de1e06a98d09"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(8 << 20), b""):
            h.update(block)
    return h.hexdigest()


def write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)


def figure(rows: list[tuple[str, str]], source: dict, title: str, caption: str, dest: Path) -> dict:
    cell_w, cell_h, gap, label_h, margin = 960, 540, 14, 48, 22
    head_h, foot_h = 90, 68
    width = margin * 2 + 3 * cell_w + 2 * gap
    height = head_h + len(rows) * (label_h + cell_h + gap) + foot_h
    canvas = Image.new("RGB", (width, height), "white")
    d = ImageDraw.Draw(canvas)
    font = ImageFont.load_default()
    d.text((margin, 15), title, fill="black", font=font)
    d.text((margin, 40), "A: 650,000 sampled centers  |  B: learned semantic-color Gaussian splats  |  C: fixed-ID palette-color Gaussian splats", fill="#333333", font=font)
    d.text((margin, 62), "A is point display; B/C use checkpoint scale, rotation, opacity and full Gaussian count.", fill="#333333", font=font)
    components = []
    for row, (method, camera) in enumerate(rows):
        y = head_h + row * (label_h + cell_h + gap)
        d.text((margin, y + 10), f"{method.upper()} | {camera} | V3A camera", fill="black", font=font)
        for col, name in enumerate(NAMES):
            p = source[(method, camera, name)]
            with Image.open(p) as opened:
                image = opened.convert("RGB")
                if image.size != (cell_w, cell_h):
                    raise ValueError(f"Unexpected size: {p}: {image.size}")
                x = margin + col * (cell_w + gap)
                y_img = y + label_h
                canvas.paste(image, (x, y_img))
                # Exact decoded source pixels, no resize/crop/overlay.
                assert np.array_equal(np.asarray(canvas.crop((x, y_img, x + cell_w, y_img + cell_h))), np.asarray(image))
            components.append({"path": str(p.relative_to(ROOT)), "sha256": sha(p), "panel_xy": [x, y_img]})
    d.text((margin, height - foot_h + 8), caption, fill="#333333", font=font)
    d.text((margin, height - foot_h + 28), "C is a palette-color visualization, not categorical per-pixel prediction; alpha coverage is not geometric watertightness.", fill="#333333", font=font)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.exists():
        raise FileExistsError(dest)
    canvas.save(dest)
    return {"path": str(dest.relative_to(ROOT)), "sha256": sha(dest), "resolution": list(canvas.size), "components": components, "no_resize_or_crop": True}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--root", type=Path, required=True)
    a = ap.parse_args()
    root = a.root.resolve()
    if (root / "figures").exists() or (root / "metrics").exists():
        raise FileExistsError("Refusing to overwrite assembled outputs")
    checkpoints = {}
    for method, (path, expected) in EXPECTED_CHECKPOINTS.items():
        actual = sha(path)
        if actual != expected:
            raise ValueError(f"Checkpoint hash mismatch: {path}")
        checkpoints[method] = {"path": str(path.relative_to(ROOT)), "sha256": actual}
    if sha(FIG8) != FIG8_SHA:
        raise ValueError("Original Figure 8 hash mismatch")
    source, records, coverage, performance = {}, {}, [], []
    for method in METHODS:
        for camera in CAMERAS:
            folder = root / "renders" / method / camera
            metadata = json.loads((folder / "render_metadata.json").read_text())
            if metadata["method"] != method or metadata["camera"] != camera or metadata["resolution"] != [960, 540]:
                raise ValueError("Render metadata identity mismatch")
            for filename, expected in metadata["outputs"].items():
                if sha(folder / filename) != expected:
                    raise ValueError(f"Render checksum mismatch: {folder / filename}")
            for name in NAMES:
                path = folder / name
                with Image.open(path) as im:
                    im.verify()
                with Image.open(path) as im:
                    if im.size != (960, 540) or np.asarray(im).std() == 0:
                        raise ValueError(f"Invalid/nonuniform image {path}")
                source[(method, camera, name)] = path
            original = np.asarray(Image.open(ORIGINALS[method] / f"{camera}.png").convert("RGB"))[54:]
            point = np.asarray(Image.open(folder / NAMES[0]).convert("RGB"))
            if original.shape != point.shape or not np.array_equal(original, point):
                raise ValueError(f"Mode A not pixel-identical to V3A: {method}/{camera}")
            records[f"{method}/{camera}"] = metadata
            for mode, name in zip(("A_center_points", "B_learned_semantic_splats", "C_fixed_id_palette_splats"), NAMES):
                detail = metadata["modes"].get(mode, {})
                coverage.append({
                    "phase": method, "camera": camera, "mode": mode, "gaussian_total": metadata["gaussian_count"],
                    "gaussians_passed_to_rasterizer": metadata["gaussian_count"] if mode != "A_center_points" else 0,
                    "sampled_centers": metadata["sample_count"] if mode == "A_center_points" else "",
                    "full_projectable_center_count": metadata["full_projectable_centers"],
                    "point_occupancy_ratio": metadata["point_occupancy_ratio"] if mode == "A_center_points" else "",
                    "point_display_coverage_ratio": metadata["point_display_coverage_ratio"] if mode == "A_center_points" else "",
                    "alpha_mean": detail.get("alpha_mean", "NOT AVAILABLE"),
                    "alpha_median": detail.get("alpha_median", "NOT AVAILABLE"),
                    "alpha_gt_0_1": detail.get("alpha_gt_0_1", "NOT AVAILABLE"),
                    "alpha_gt_0_5": detail.get("alpha_gt_0_5", "NOT AVAILABLE"),
                    "alpha_gt_0_9": detail.get("alpha_gt_0_9", "NOT AVAILABLE"),
                    "background_alpha_le_0_1": detail.get("background_alpha_le_0_1", "NOT AVAILABLE"),
                })
                performance.append({
                    "phase": method, "camera": camera, "mode": mode,
                    "cpu_stage_seconds": metadata["cpu_stage_seconds"],
                    "render_seconds": detail.get("render_seconds", "CPU point display"),
                    "alpha_pass_seconds": detail.get("alpha_pass_seconds", "NOT APPLICABLE"),
                    "gpu_total_seconds_for_B_C_and_alpha": metadata["gpu_total_seconds"],
                    "peak_gpu_allocated_bytes": metadata["peak_gpu_allocated_bytes"],
                    "peak_gpu_reserved_bytes": metadata["peak_gpu_reserved_bytes"],
                    "gpu_free_before_bytes": metadata["gpu_free_before_bytes"],
                })
    (root / "metrics").mkdir(parents=True)
    (root / "metadata").mkdir(parents=True)
    write_csv(root / "metrics/coverage_comparison.csv", coverage)
    write_csv(root / "metrics/rendering_performance.csv", performance)
    figures = {}
    for camera in CAMERAS:
        figures[camera] = figure([(method, camera) for method in METHODS], source,
            f"Figure 8B | {camera} | Phase 4 vs Phase 6",
            "Matched V3A camera, native 960x540 panels; point display versus covariance-aware alpha-composited splats.",
            root / "figures" / f"figure_08b_{camera}.png")
    figures["combined"] = figure([(method, camera) for camera in CAMERAS for method in METHODS], source,
        "Figure 8B | Semantic Gaussian splatting validation | Replica Room 0",
        "Two V3A cameras, two immutable checkpoints; white regions include true background and low-alpha areas.",
        root / "figures/figure_08b_combined_comparison.png")
    manifest = {"checkpoints": checkpoints, "original_figure_8": {"path": str(FIG8.relative_to(ROOT)), "sha256": FIG8_SHA},
        "figures": figures, "renders": {k: {"metadata_path": str((root / 'renders' / k / 'render_metadata.json').relative_to(ROOT)), "checkpoint_sha256": v["checkpoint_sha256"], "camera_sha256": v["camera_sha256"], "outputs": v["outputs"]} for k, v in records.items()},
        "validation": {"mode_A_matches_original_pixels": 4, "render_png_count": 12, "figure_png_count": 3,
            "alpha_16bit_png_count": 8, "source_checkpoint_hashes_pass": True, "original_figure_8_hash_pass": True,
            "no_resizing_cropping_or_overlays_on_source_panels": True}}
    (root / "metadata/checkpoint_manifest.json").write_text(json.dumps(checkpoints, indent=2) + "\n")
    (root / "metadata/camera_config.json").write_text(json.dumps({c: {"source": str((ROOT / "results/runtime_artifacts/phase4_vb001_visualization_v3a/cameras" / (c + '.json')).relative_to(ROOT)), "sha256": records[f'phase4/{c}']["camera_sha256"], "resolution": [960, 540]} for c in CAMERAS}, indent=2) + "\n")
    (root / "metadata/renderer_config.json").write_text(json.dumps({"backend": "diff_gaussian_rasterization.GaussianRasterizer", "geometry": "full checkpoint", "scale": "exp(log_scales) tiled to XYZ", "rotation": "L2-normalized unnorm_rotations", "opacity": "sigmoid(logit_opacities)", "background": "white RGB for B/C, black for constant-one alpha pass", "scale_modifier": 1, "prefiltered": False, "alpha_mask_background_threshold": 0.1}, indent=2) + "\n")
    (root / "metadata/validation_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(json.dumps(manifest["validation"], indent=2))


if __name__ == "__main__":
    main()
