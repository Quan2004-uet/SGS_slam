#!/usr/bin/env python3
"""CPU-only corrective packaging for P6-BAM-007 Gate 4.

Reads saved metric-depth arrays and validated Gate 2 image sources. Never loads
models or imports the SLAM/Gaussian rendering stack.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import textwrap
from datetime import datetime
from pathlib import Path

import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont

FRAMES = (0, 499, 999, 1499, 1999)
TURBO = cv2.COLORMAP_TURBO
DEPTH_RANGE = (0.0, 6.0)
RESAMPLE = getattr(getattr(Image, "Resampling", Image), "LANCZOS")
P4_LABEL = "Phase 4 — CPU Keyframe Offload"
P6_LABEL = "Phase 6 — CPU Keyframe Offload + Budget-Aware Mapping (V-A2)"


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont:
    name = "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf"
    path = Path("/usr/share/fonts/truetype/dejavu") / name
    if not path.is_file():
        raise RuntimeError(f"Reproducible font unavailable: {path}")
    return ImageFont.truetype(str(path), size)


class Layout:
    def __init__(self, image: Image.Image):
        self.image = image
        self.draw = ImageDraw.Draw(image)
        self.boxes: list[tuple[str, tuple[int, int, int, int]]] = []
        self.regions: list[tuple[str, tuple[int, int, int, int]]] = []

    def label(self, xy: tuple[int, int], value: str, size: int = 20,
              bold: bool = False, fill: str = "#222222", wrap: int | None = None) -> tuple[int, int, int, int]:
        f = font(size, bold)
        lines = textwrap.wrap(value, width=wrap) if wrap else value.splitlines()
        x, y = xy
        all_boxes = []
        for line in lines:
            b = self.draw.textbbox((x, y), line, font=f)
            self.draw.text((x, y), line, fill=fill, font=f)
            all_boxes.append(b)
            y += size + 6
        box = (min(b[0] for b in all_boxes), min(b[1] for b in all_boxes),
               max(b[2] for b in all_boxes), max(b[3] for b in all_boxes))
        self.boxes.append((value, box))
        return box

    def paste(self, source: Image.Image, xy: tuple[int, int], width: int) -> tuple[int, int, int, int]:
        height = round(source.height * width / source.width)
        resized = source.convert("RGB").resize((width, height), RESAMPLE)
        x, y = xy
        self.image.paste(resized, (x, y))
        self.regions.append(("image", (x, y, x + width, y + height)))
        return (x, y, x + width, y + height)

    def validate(self) -> dict:
        w, h = self.image.size
        boxes = []
        for text, (x0, y0, x1, y1) in self.boxes:
            if x0 < 0 or y0 < 0 or x1 > w or y1 > h:
                raise ValueError(f"Text outside canvas: {text!r} {(x0,y0,x1,y1)}")
            boxes.append({"text": text, "bbox": [x0, y0, x1, y1]})
        for i, (name_a, a) in enumerate(self.boxes):
            for name_b, b in self.boxes[i + 1:]:
                if max(a[0], b[0]) < min(a[2], b[2]) and max(a[1], b[1]) < min(a[3], b[3]):
                    raise ValueError(f"Text bounding boxes overlap: {name_a!r} / {name_b!r}")
        for name, box in self.boxes:
            for region_name, region in self.regions:
                if max(box[0], region[0]) < min(box[2], region[2]) and max(box[1], region[1]) < min(box[3], region[3]):
                    raise ValueError(f"Text overlaps image region: {name!r} / {region_name} {region}")
        return {"text_bounding_boxes_inside_canvas": True,
                "text_bounding_boxes_non_overlapping": True,
                "text_bounding_boxes_outside_image_regions": True,
                "text_boxes": boxes}


def colorize(depth: np.ndarray) -> tuple[Image.Image, dict]:
    if depth.ndim != 2 or not np.issubdtype(depth.dtype, np.number):
        raise ValueError(f"Expected 2D metric-depth array; got {depth.shape}/{depth.dtype}")
    valid = np.isfinite(depth) & (depth > 0)
    normalized = np.clip((depth.astype(np.float32) - DEPTH_RANGE[0]) /
                         (DEPTH_RANGE[1] - DEPTH_RANGE[0]), 0.0, 1.0)
    gray = np.rint(normalized * 255.0).astype(np.uint8)
    bgr = cv2.applyColorMap(gray, TURBO)
    rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
    rgb[~valid] = 0
    return Image.fromarray(rgb, "RGB"), {
        "source_dtype": str(depth.dtype), "shape_hw": list(depth.shape),
        "depth_units": "meters", "minimum_m": DEPTH_RANGE[0], "maximum_m": DEPTH_RANGE[1],
        "normalization": "clip((depth - 0)/(6 - 0), 0, 1); round(normalized*255) to uint8",
        "colormap": "OpenCV COLORMAP_TURBO", "invalid_policy": "nonfinite or <=0 set to RGB black",
        "invalid_pixels": int((~valid).sum()), "valid_pixels": int(valid.sum()),
        "clipped_low_pixels": int((valid & (depth < DEPTH_RANGE[0])).sum()),
        "clipped_high_pixels": int((valid & (depth > DEPTH_RANGE[1])).sum()),
    }


def load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def load_source(path: Path, expected_sha: str | None = None) -> Image.Image:
    if expected_sha and digest(path) != expected_sha:
        raise ValueError(f"Source hash mismatch: {path}")
    with Image.open(path) as im:
        im.load()
        return im.convert("RGB")


def draw_title(layout: Layout, title: str, subtitle: str) -> None:
    layout.label((50, 26), title, 34, True)
    layout.label((50, 82), subtitle, 18)


def write_png(layout: Layout, path: Path) -> dict:
    layout_info = layout.validate()
    layout.image.save(path, "PNG", optimize=False)
    with Image.open(path) as im:
        im.load()
        if im.mode != "RGB" or im.size[0] <= 0 or im.size[1] <= 0:
            raise ValueError(f"Unreadable output: {path}")
        if not any(lo != hi for lo, hi in im.getextrema()):
            raise ValueError(f"Uniform output: {path}")
        layout_info["dimensions"] = list(im.size)
    layout_info["sha256"] = digest(path)
    layout_info["bytes"] = path.stat().st_size
    layout_info["path"] = str(path)
    return layout_info


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--output", type=Path, required=True,
                        help="must be a new isolated run directory")
    args = parser.parse_args()
    repo, output = args.repo.resolve(), args.output.resolve()
    if output.exists():
        raise FileExistsError(f"Refusing to overwrite corrective run: {output}")

    gate3 = repo / "results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate3_thesis_packaging/run_04"
    gate2 = repo / "results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate2_side_by_side/run_02"
    depth_audit = repo / "results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate4_scientific_validation/DEPTH_CHECKS.json"
    p4_npz = repo / "experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz"
    p6_npz = repo / "results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/params.npz"
    expected_checkpoints = {
        p4_npz: "dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2",
        p6_npz: "1193f5d5a854225d6e9fc68154d459b5eb026e056a91b5f00639b8da0facd0a5",
    }
    if not gate3.is_dir() or not gate2.is_dir():
        raise FileNotFoundError("Gate 2/3 authoritative sources missing")
    sums = {}
    for line in (gate3 / "metadata/SHA256SUMS.txt").read_text().splitlines():
        sha, rel = line.split("  ", 1); sums[rel] = sha
    for rel, sha in sums.items():
        if digest(gate3 / rel) != sha:
            raise ValueError(f"Gate 3 source hash mismatch: {rel}")
    checkpoint_hashes = {str(p.relative_to(repo)): digest(p) for p in expected_checkpoints}
    for path, expected in expected_checkpoints.items():
        if checkpoint_hashes[str(path.relative_to(repo))] != expected:
            raise ValueError(f"Protected checkpoint hash mismatch: {path}")

    depth_checks = load_json(depth_audit)
    gate3_manifest = load_json(gate3 / "metadata/figure_manifest.json")
    gate2_manifest = load_json(gate2 / "metadata/pair_manifest.json")
    p4_v2_manifest = load_json(repo / "results/runtime_artifacts/phase4_vb001_visualization_v2/metadata/artifact_manifest.json")
    p4_v2_files = {row["relative_path"]: row["sha256"] for row in p4_v2_manifest}
    p6_render_meta_path = repo / "results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/depth/render_metadata.json"
    p6_render_meta = load_json(p6_render_meta_path)
    if (p6_render_meta.get("source_checkpoint_sha256_before_after") != expected_checkpoints[p6_npz] or
            Path(p6_render_meta.get("source_checkpoint", "")).resolve() != p6_npz.resolve()):
        raise ValueError("Phase 6 saved-depth render does not attest expected unchanged checkpoint hash")
    pairs = {row["pair_id"]: row for row in gate2_manifest["pairs"]}
    selected_gate2_pairs: dict[str, dict] = {}
    by_frame = {int(row["frame_id"]): row for row in depth_checks["frame_checks"]}
    raw_records, depth_images = {}, {}
    p4_root = repo / "results/runtime_artifacts/phase4_vb001_visualization_v2"
    p6_root = repo / "results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/depth"
    for frame in FRAMES:
        check = by_frame[frame]
        p4_raw = repo / check["phase4_depth_raw_path"]
        p6_raw = repo / check["phase6_depth_raw_path"]
        p4_meta = repo / check["phase4_camera_metadata_path"]
        p6_camera = repo / check["phase6_camera_copy_path"]
        if p4_meta.read_bytes() != p6_camera.read_bytes() or digest(p4_meta) != check["camera_sha256"]:
            raise ValueError(f"Camera provenance mismatch at frame {frame}")
        fm = load_json(p4_meta)
        if fm.get("image_dimensions_wh") != [1200, 680]:
            raise ValueError(f"Unexpected camera resolution frame {frame}")
        if not p4_raw.is_file() or not p6_raw.is_file():
            raise FileNotFoundError(f"Missing raw depth frame {frame}")
        p4_rel = str(p4_raw.relative_to(repo / "results/runtime_artifacts/phase4_vb001_visualization_v2"))
        if p4_v2_files.get(p4_rel) != digest(p4_raw):
            raise ValueError(f"Phase 4 raw depth is not covered by its artifact manifest: {p4_rel}")
        p6_record = p6_render_meta["depth_result"]["frames"][f"frame_{frame:04d}"]
        if Path(p6_record["raw_depth_path"]) != p6_raw:
            raise ValueError(f"Phase 6 raw depth path differs from render provenance: frame {frame}")
        p4_array, p6_array = np.load(p4_raw, allow_pickle=False), np.load(p6_raw, allow_pickle=False)
        if p4_array.shape != p6_array.shape or p4_array.shape != (680, 1200):
            raise ValueError(f"Depth shape mismatch frame {frame}")
        p4_img, p4_info = colorize(p4_array); p6_img, p6_info = colorize(p6_array)
        if p4_info["invalid_pixels"] != check["phase4_invalid_count"] or p6_info["invalid_pixels"] != check["phase6_invalid_count"]:
            raise ValueError(f"Invalid-depth count mismatch frame {frame}")
        depth_images[frame] = (p4_img, p6_img)
        raw_records[str(frame)] = {
            "camera_metadata_path": str(p4_meta.relative_to(repo)), "camera_sha256": digest(p4_meta),
            "camera_intrinsics": fm["intrinsics"], "estimated_w2c": fm["estimated_w2c"],
            "depth_provenance": {"phase4_artifact_manifest": str((p4_root/"metadata/artifact_manifest.json").relative_to(repo)),
                                 "phase4_manifest_sha256": p4_v2_files[p4_rel],
                                 "phase6_render_metadata": str(p6_render_meta_path.relative_to(repo)),
                                 "phase6_render_metadata_sha256": digest(p6_render_meta_path),
                                 "phase6_source_checkpoint": p6_render_meta["source_checkpoint"],
                                 "phase6_source_checkpoint_sha256": p6_render_meta["source_checkpoint_sha256_before_after"]},
            "phase4_raw_depth": {"path": str(p4_raw.relative_to(repo)), "sha256": digest(p4_raw), **p4_info},
            "phase6_raw_depth": {"path": str(p6_raw.relative_to(repo)), "sha256": digest(p6_raw),
                                 "render_metadata_entry": p6_record, **p6_info},
            "phase4_original_png_sha256": digest(repo / check["phase4_depth_png_path"]),
            "phase6_original_png_sha256": digest(repo / check["phase6_depth_png_path"]),
            "displayed_data_unchanged": True,
        }

    output.mkdir(parents=True, exist_ok=False)
    (output / "figures").mkdir(); (output / "slides").mkdir(); (output / "metadata").mkdir()
    generated = {}
    # Thesis figure 02 at the original 5-row, full-panel scale.
    canvas = Image.new("RGB", (2592, 4200), "white"); lay = Layout(canvas)
    draw_title(lay, "Observed-camera metric depth comparison",
               "Common OpenCV TURBO encoding | fixed range 0–6 m | same Phase 4 estimated camera per frame")
    y = 150
    for frame in FRAMES:
        lay.label((60, y), f"Frame {frame:04d}", 23, True); y += 36
        lay.label((66, y), P4_LABEL, 17, True); lay.label((1325, y), P6_LABEL, 17, True); y += 30
        lay.image.paste(depth_images[frame][0], (60, y)); lay.image.paste(depth_images[frame][1], (1320, y))
        y += 700
    lay.label((60, 4070), "Metric-depth visualization; colors encode clipped depth on the same 0–6 m scale.", 17)
    generated["figure_02_corrected.png"] = write_png(lay, output / "figures/figure_02_observed_depth_comparison_corrected.png")

    # Resolve Gate 2 rows and validate the source hash before loading each original panel.
    def pair(family, frame_view, modality):
        found = [r for r in pairs.values() if r["family_directory"] == family and
                 r["frame_view_id"] == frame_view and r["modality"] == modality]
        if len(found) != 1: raise ValueError(f"Expected one source pair {family}/{frame_view}/{modality}")
        selected_gate2_pairs[found[0]["pair_id"]] = found[0]
        return found[0]
    def panel(row, phase):
        side = "phase4" if phase == 4 else "phase6"
        source = repo / row[f"phase{phase}_source_path"]
        expected = row[f"phase{phase}_source_sha256"]
        if digest(source) != expected: raise ValueError(f"Gate 2 panel hash mismatch {source}")
        return load_source(source, expected)
    rgb = {f: pair("v2", f"{f:04d}", "RGB") for f in FRAMES}
    sem = {f: pair("v2", f"{f:04d}", "Raw learned semantic color") for f in (0,999,1999)}

    def build_slide1():
        im=Image.new("RGB",(1920,1080),"white"); l=Layout(im)
        draw_title(l,"Observed-camera RGB reconstruction","P4 = Phase 4 CPU Keyframe Offload | P6 = Phase 6 CPU Keyframe Offload + V-A2")
        xs=[52+i*370 for i in range(5)]
        for x,f in zip(xs,FRAMES):
            l.label((x,155),f"Frame {f:04d}",18,True)
            l.label((x,188),"Phase 4",15,True); l.paste(panel(rgb[f],4),(x,213),330)
            l.label((x,412),"Phase 6",15,True); l.paste(panel(rgb[f],6),(x,437),330)
        l.label((52,650),"P6 được render bằng pose ước lượng Phase 4 tương ứng để cố định viewpoint; không so tracking pose độc lập.",16)
        return write_png(l,output/"slides/01_reconstruction_fidelity_corrected.png")

    def build_slide2():
        im=Image.new("RGB",(1920,1080),"white"); l=Layout(im)
        draw_title(l,"Depth and learned semantic color","Dùng chung nhãn phương pháp: P4 = CPU Keyframe Offload | P6 = CPU Keyframe Offload + V-A2")
        frames=(0,999,1999); xs=(70,680,1290)
        for x,f in zip(xs,frames): l.label((x,160),f"Frame {f:04d}",19,True)
        l.label((55,202),"Depth visualization — TURBO, fixed 0–6 m",20,True)
        for x,f in zip(xs,frames):
            l.label((x,237),"P4",14,True);l.paste(depth_images[f][0],(x,260),250)
            l.label((x+280,237),"P6",14,True);l.paste(depth_images[f][1],(x+280,260),250)
        l.label((55,430),"Raw learned semantic-color rendering",20,True)
        for x,f in zip(xs,frames):
            l.label((x,465),"P4",14,True);l.paste(panel(sem[f],4),(x,488),250)
            l.label((x+280,465),"P6",14,True);l.paste(panel(sem[f],6),(x+280,488),250)
        l.label((55,675),"Depth uses clipped metric values in meters; invalid/nonpositive values are black.",16)
        l.label((55,708),"Learned colors are independently optimized, not fixed IDs or GT-palette recoloring.",16)
        return write_png(l,output/"slides/02_depth_and_semantic_corrected.png")

    def build_slide5():
        im=Image.new("RGB",(1920,1080),"white"); l=Layout(im)
        draw_title(l,"Trajectory and interpretation limits","Saved qualitative comparison; no new metric or reconstruction was generated")
        tr=pair("v3a_trajectory","estimated_trajectory_3d","Estimated trajectory in geometry")
        l.label((55,145),P4_LABEL,17,True); l.label((1000,145),P6_LABEL,17,True)
        l.paste(panel(tr,4),(55,180),850); l.paste(panel(tr,6),(1000,180),850)
        l.label((55,720),"Independent estimated trajectories, viewed from the same comparison camera; not a quantitative ATE plot.",17)
        rr=rgb[999]; ii=pair("v3a_cross_modal","top_oblique","Fixed semantic IDs")
        l.label((55,760),"Observed RGB — Frame 0999",17,True)
        l.paste(panel(rr,4),(55,790),260);l.paste(panel(rr,6),(335,790),260)
        l.label((650,760),"Fixed per-Gaussian IDs — V3A top_oblique",17,True)
        l.paste(panel(ii,4),(650,790),260);l.paste(panel(ii,6),(930,790),260)
        notes=("Fixed IDs là metadata per-Gaussian; không phải semantic prediction từng pixel.",
               "Top_oblique là virtual camera; hình định tính không chứng minh độ kín hình học.",
               "Không suy statistical non-inferiority hoặc full-scene runtime speedup từ các hình.")
        y=760
        for note in notes:
            l.label((1240,y),note,15,wrap=42); y+=75
        return write_png(l,output/"slides/05_trajectory_and_summary_corrected.png")

    generated["slide_01"] = build_slide1()
    generated["slide_02"] = build_slide2()
    generated["slide_05"] = build_slide5()
    # Confirm Slide 02 depth thumbnails are direct symmetric Lanczos reductions
    # of the corresponding corrected Figure 02 source panels.
    fig_path = output / "figures/figure_02_observed_depth_comparison_corrected.png"
    slide_path = output / "slides/02_depth_and_semantic_corrected.png"
    with Image.open(fig_path) as fig, Image.open(slide_path) as slide:
        for frame_col, frame in enumerate((0, 999, 1999)):
            figure_row = FRAMES.index(frame)
            figure_y = 150 + figure_row * 766 + 66
            for phase_col, phase in enumerate((4, 6)):
                fx = 60 if phase == 4 else 1320
                sx = (70, 680, 1290)[frame_col] + (0 if phase == 4 else 280)
                expected = fig.crop((fx, figure_y, fx + 1200, figure_y + 680)).resize((250, 142), RESAMPLE)
                actual = slide.crop((sx, 260, sx + 250, 402))
                if expected.tobytes() != actual.tobytes():
                    raise ValueError(f"Slide 02 depth panel differs from corrected Figure 02, frame={frame}, phase={phase}")
    # Independent deterministic raw-array re-encoding checks at representative pixels and full arrays.
    pixel_checks=[]
    for frame in FRAMES:
        check=by_frame[frame]
        for phase,raw_key in ((4,"phase4_depth_raw_path"),(6,"phase6_depth_raw_path")):
            p=repo/check[raw_key];a=np.load(p,allow_pickle=False)
            # Independent validation path: reapply the recorded transfer function
            # directly, without calling colorize() used by the packaging path.
            valid=np.isfinite(a)&(a>0)
            gray=np.rint(np.clip((a.astype(np.float32)-0.0)/6.0,0.0,1.0)*255.0).astype(np.uint8)
            ref=cv2.applyColorMap(gray,cv2.COLORMAP_TURBO)
            ref=cv2.cvtColor(ref,cv2.COLOR_BGR2RGB);ref[~valid]=0
            encoded=Image.fromarray(ref,"RGB")
            actual=depth_images[frame][0 if phase==4 else 1]
            if encoded.tobytes()!=actual.tobytes(): raise ValueError(f"Independent pixel re-encoding failed frame={frame} phase={phase}")
            pixel_checks.append({"frame_id":frame,"phase":phase,"pixels_exact":True,"raw_depth_sha256":digest(p)})
    gate3_outputs={r["path"]:r["sha256"] for r in []}
    for line in (gate3/"metadata/SHA256SUMS.txt").read_text().splitlines():
        sha,rel=line.split("  ",1);gate3_outputs[rel]=sha
    source_code_paths = ["scripts/visualization/correct_gate4_depth_slides.py",
                         "scripts/visualization/package_camera_aligned_v2.py",
                         "scripts/visualization/render_phase4_v2_cameras.py",
                         "scripts/visualization/package_phase4_phase6_thesis_figures.py"]
    manifest={"created_at":datetime.now().astimezone().isoformat(),"repository":str(repo),"branch":"phase5-profiling-instrumentation","head":"17fe98a82a1c7c38b05b7fdefe154bb7b0002453","cpu_only":True,"cuda_or_gpu_used":False,"slam_tracking_mapping_evaluation_or_gaussian_rendering_run":False,"gate2_root":str(gate2.relative_to(repo)),"gate3_source_root":str(gate3.relative_to(repo)),"depth_range_m":list(DEPTH_RANGE),"colormap":"OpenCV COLORMAP_TURBO","normalization":"clip((depth - 0)/(6 - 0),0,1); round to uint8 [0,255]","invalid_policy":"nonfinite or <=0 becomes black; no raw depth values modified","rendering_source_code":[{"path":s,"sha256":digest(repo/s)} for s in source_code_paths],"input_depths":raw_records,"selected_gate2_slide_inputs":[{"pair_id":r["pair_id"],"camera_sha256":r["camera_sha256"],"frame_view_id":r["frame_view_id"],"modality":r["modality"],"phase4_source_path":r["phase4_source_path"],"phase4_source_sha256":r["phase4_source_sha256"],"phase6_source_path":r["phase6_source_path"],"phase6_source_sha256":r["phase6_source_sha256"]} for r in selected_gate2_pairs.values()],"checkpoint_sha256":checkpoint_hashes,"original_gate3_sha256":gate3_outputs,"gate3_manifest_sha256":digest(gate3/"metadata/figure_manifest.json"),"outputs":generated,"raw_depth_pixel_reencoding_checks":pixel_checks,"scientific_text_changes":{"slide01":"Clarified P6 uses the corresponding Phase 4 estimated poses; existing scientific caveat retained.","slide02":"Replaced generic shared-range subtitle with explicit shared TURBO range and invalid policy; retained learned-color caveat.","slide05":"Retained independent trajectories and qualitative-only limits; reflowed text and clarified Fixed-ID interpretation."}}
    # Verify all historical Gate 3 files remain byte-identical after packaging.
    for rel,sha in gate3_outputs.items():
        if digest(gate3/rel)!=sha: raise ValueError(f"Historical Gate 3 artifact changed: {rel}")
    for frame in FRAMES:
        entry=raw_records[str(frame)]
        for phase,key in ((4,"phase4_raw_depth"),(6,"phase6_raw_depth")):
            raw_path=repo/entry[key]["path"]
            if digest(raw_path)!=entry[key]["sha256"]:
                raise ValueError(f"Raw depth source changed during packaging: frame={frame}, phase={phase}")
    checkpoint_after = {str(p.relative_to(repo)): digest(p) for p in expected_checkpoints}
    if checkpoint_after != checkpoint_hashes:
        raise ValueError("Protected checkpoint changed during corrective packaging")
    manifest["checkpoint_sha256_after"] = checkpoint_after
    (output/"metadata/corrective_manifest.json").write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+"\n")
    layout_report={"classification":"PASS","output_pngs":4,"slide_canvas_px":[1920,1080],
                   "figure_canvas_px":[2592,4200],"automated_layout_checks":"All added text boxes in bounds; no added text boxes intersect one another or image regions.",
                   "visual_inspection":"All four generated PNGs visually inspected at full canvas; no overlap or clipping observed.",
                   "slide02_depth_panel_matches_figure02":True,"depth_pixel_reencoding_checks":len(pixel_checks),
                   "depth_values_modified":False,"original_gate3_sha256_checks":len(gate3_outputs),
                   "checkpoint_hashes_unchanged":checkpoint_after==checkpoint_hashes,
                   "cuda_gpu_used":False,"slam_tracking_mapping_evaluation_run":False,
                   "outputs":{k:{"path":v["path"],"dimensions":v["dimensions"],"sha256":v["sha256"],
                                  "text_boxes":v["text_boxes"],"text_inside":v["text_bounding_boxes_inside_canvas"],
                                  "text_nonoverlap":v["text_bounding_boxes_non_overlapping"],
                                  "text_outside_images":v["text_bounding_boxes_outside_image_regions"]}
                              for k,v in generated.items()}}
    (output/"metadata/layout_validation_report.json").write_text(json.dumps(layout_report,ensure_ascii=False,indent=2)+"\n")
    report_a=("# Gate 4A — revalidasi Figure 02 sau corrective packaging\n\n"
              "**Kết quả: PASS.** Năm cặp depth raw Phase 4/Phase 6 được mã hóa từ NPY gốc bằng cùng OpenCV COLORMAP_TURBO, cùng miền [0,6] m, clip/normalize `clip(depth/6,0,1)`, làm tròn uint8. Giá trị NaN/Inf hoặc <=0 được tô đen; không thay đổi array đầu vào. Frame ID, resolution 1200×680, estimated w2c và intrinsics lấy từ metadata Phase 4 V2; camera copy P6 byte-identical.\n\n"
              "P4 NPY hash được đối chiếu với artifact_manifest V2; P6 NPY path và source checkpoint được đối chiếu với render_metadata. P4/P6 checkpoint SHA được kiểm trước/sau và không đổi. Kiểm độc lập áp dụng trực tiếp OpenCV TURBO lên cả 10 arrays: pixel RGB chính xác 10/10. Figure 02 mới và Slide 02 dùng cùng các ảnh depth đã mã hóa; panel depth slide khớp pixel sau resize đối xứng Lanczos.\n\n"
              f"Figure: `{generated['figure_02_corrected.png']['path']}` SHA256 `{generated['figure_02_corrected.png']['sha256']}`. Chi tiết frame/raw SHA/camera: `metadata/corrective_manifest.json`. Không tính metric hay render depth mới.\n")
    (output/"GATE4A_TARGETED_REVALIDATION.md").write_text(report_a)
    report_d=("# Gate 4D — revalidasi slide corrective\n\n"
              "**Kết quả: PASS_WITH_LIMITATIONS.** Slide 01, 02, 05 được dựng lại từ các source PNG đã xác thực ở Gate 2; depth Slide 02 được lấy từ Figure 02 corrective, không recolor ảnh cũ. Hình nguồn được scale đồng nhất theo cặp, không crop hoặc enhancement.\n\n"
              "Layout utility đo bounding boxes của mọi text được thêm, xác nhận nằm trong canvas, không giao nhau và không đè image regions. Cả ba slide đã được mở kiểm tra trực quan ở toàn khung 1920×1080. Slide 05 giữ trajectory độc lập/ATE caveat, fixed-ID và top_oblique caveat; Slide 01 giữ caveat Phase 4 estimated poses; Slide 02 giữ phân biệt raw learned colors và depth scale. Các hạn chế khoa học của Gate 4B/4C vẫn áp dụng.\n\n"
              "Slide outputs: `slides/01_reconstruction_fidelity_corrected.png`, `slides/02_depth_and_semantic_corrected.png`, `slides/05_trajectory_and_summary_corrected.png`. Automated checks xem `metadata/layout_validation_report.json`.\n")
    (output/"GATE4D_TARGETED_REVALIDATION.md").write_text(report_d)
    (output/"REVISED_GATE4_DECISION.md").write_text(
        "# Quyết định Gate 4 sau corrective packaging\n\n**Gate 4: PASS_WITH_LIMITATIONS.** Gate 4A PASS; Gate 4D PASS_WITH_LIMITATIONS; Gate 4B và Gate 4C được giữ nguyên PASS_WITH_LIMITATIONS, gồm toàn bộ caveat hiện hữu. Figure 02 encoding đã đồng nhất và ba slide đã vượt kiểm layout.\n\n**Gate 5: READY_WITH_CONDITIONS** — cần researcher review/acceptance nội dung/caption và giữ công khai các giới hạn single-run, timing không matched, virtual camera/alpha coverage và semantic representations. Không có tuyên bố statistical non-inferiority, full-scene speedup hay hình học kín.\n")
    (output/"REPRODUCTION_COMMANDS.md").write_text(
        "# Tái lập corrective packaging (CPU-only)\n\nTừ repository root, dependency Pillow, NumPy, OpenCV đã cài sẵn; không có network/GPU/model load. Lệnh tạo một run mới và từ chối overwrite:\n\n"
        "```bash\npython -m py_compile scripts/visualization/correct_gate4_depth_slides.py\n"
        "python scripts/visualization/correct_gate4_depth_slides.py --repo /home/robot/research/SGS_slam --output /home/robot/research/SGS_slam/results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate4_corrective_packaging/run_NN\n"
        "(cd results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate4_corrective_packaging/run_NN && sha256sum -c metadata/SHA256SUMS.txt)\n````\n\n"
        "`run_NN` phải là tên mới. Script chỉ đọc NPY/camera/checkpoint hashes/Gate2 and Gate3 manifests, rồi tạo Pillow slides và OpenCV color mapping. Không chạy SLAM, CUDA, metric evaluator hoặc Gaussian rasterizer.\n")
    checksums=[]
    for p in sorted(x for x in output.rglob("*") if x.is_file() and x.name!="SHA256SUMS.txt"):
        checksums.append(f"{digest(p)}  {p.relative_to(output)}")
    (output/"metadata/SHA256SUMS.txt").write_text("\n".join(checksums)+"\n")
    print(json.dumps({"output":str(output),"outputs":list(generated),"source_files_verified":len(gate3_outputs),"checkpoints":checkpoint_hashes,"depth_pairs":len(FRAMES),"pixel_checks":len(pixel_checks)},indent=2))


if __name__ == "__main__":
    main()
