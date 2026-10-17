#!/usr/bin/env python3
"""Offline Figure 8B validation using immutable SGS-SLAM checkpoints.

Each invocation renders one method/camera at a specified resolution. A full
checkpoint is passed to the repository-native rasterizer; no chunk merging.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
import time
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from scripts.visualization.visualize_full_scene_v3a import (  # noqa: E402
    load_palette, nearest_pixels, paint_points, project_points,
)

CHECKPOINTS = {
    "phase4": ("experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz", "dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2"),
    "phase6": ("results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/params.npz", "1193f5d5a854225d6e9fc68154d459b5eb026e056a91b5f00639b8da0facd0a5"),
}
SAMPLES = {
    "phase4": "results/runtime_artifacts/phase4_vb001_visualization_v3a/metadata/gaussian_center_sample_indices.npy",
    "phase6": "results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/cross_modal_overview/metadata/gaussian_center_sample_indices.npy",
}
PALETTE = "results/runtime_artifacts/phase4_vb001_visualization_audit/semantic_mapping.csv"
CAMERAS = "results/runtime_artifacts/phase4_vb001_visualization_v3a/cameras"
EXPECTED_CAMERA_HASHES = {"room_overview": "f5598e540e78c8c838f3db0e83194520477e528735b65336c5f66a590b7a8cfc", "top_oblique": "a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d"}
EXPECTED_SAMPLE_HASHES = {"phase4": "c355470c05cb622828107764a9bda647521acbb07c0941eec571f787a05e3e60", "phase6": "85acc76af930b9e4183a3893681adc352d361a22c6b20e0c45486f5710219a9f"}
EXPECTED_PALETTE_HASH = "935f4968131737eeab1f1119bd2ecc9a73d6f713c16ea4e76a427b1e8c317613"


def sha(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def checked(rel: str, expected: str) -> Path:
    path = ROOT / rel
    if not path.is_file() or sha(path) != expected:
        raise ValueError(f"Missing or SHA256 mismatch: {path}")
    return path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--method", choices=CHECKPOINTS, required=True)
    ap.add_argument("--camera", choices=EXPECTED_CAMERA_HASHES, required=True)
    ap.add_argument("--output", type=Path, required=True, help="New, empty per-render directory")
    ap.add_argument("--width", type=int, default=960)
    ap.add_argument("--height", type=int, default=540)
    args = ap.parse_args()
    if args.width < 1 or args.height < 1:
        ap.error("positive dimensions required")
    output = args.output.resolve()
    if output.exists() and any(output.iterdir()):
        raise FileExistsError(f"Refusing to overwrite {output}")
    ckpt = checked(*CHECKPOINTS[args.method])
    sample_path = checked(SAMPLES[args.method], EXPECTED_SAMPLE_HASHES[args.method])
    palette_path = checked(PALETTE, EXPECTED_PALETTE_HASH)
    camera_path = checked(f"{CAMERAS}/{args.camera}.json", EXPECTED_CAMERA_HASHES[args.camera])
    camera = json.loads(camera_path.read_text())
    native_width, native_height = camera["resolution"]
    if (args.width / native_width) != (args.height / native_height):
        raise ValueError("Resolution must preserve native aspect ratio")
    k = np.array(camera["intrinsics"], dtype=np.float64)
    k[0] *= args.width / native_width
    k[1] *= args.height / native_height
    camera["intrinsics"] = k.tolist()
    camera["resolution"] = [args.width, args.height]
    w2c = np.array(camera["world_to_camera_w2c"], dtype=np.float64)
    c2w = np.array(camera["camera_to_world_c2w"], dtype=np.float64)
    if camera["view_name"] != args.camera or not np.allclose(w2c @ c2w, np.eye(4), atol=1e-6):
        raise ValueError("Camera invalid")
    start = time.perf_counter()
    with np.load(ckpt, allow_pickle=False) as z:
        names = ("means3D", "unnorm_rotations", "logit_opacities", "log_scales", "semantic_colors", "semantic_ids")
        params = {n: np.asarray(z[n]).copy() for n in names}
    count = len(params["means3D"])
    if any(len(v) != count for v in params.values()):
        raise ValueError("Gaussian parameter lengths differ")
    if any(not np.isfinite(v).all() for v in params.values() if np.issubdtype(v.dtype, np.floating)):
        raise ValueError("Nonfinite Gaussian parameter")
    palette, _, _ = load_palette(palette_path)
    ids = params["semantic_ids"]
    if set(np.unique(ids).tolist()) - set(palette):
        raise ValueError("Unmapped semantic IDs")
    lut = np.zeros((256, 3), dtype=np.uint8)
    for key, color in palette.items():
        lut[key] = color
    samples = np.load(sample_path, allow_pickle=False)
    if len(samples) != 650000 or samples.min() < 0 or samples.max() >= count or len(np.unique(samples)) != len(samples):
        raise ValueError("Invalid saved sample indices")
    sample_points = params["means3D"][samples]
    chosen, pixels, point_stats = nearest_pixels(sample_points, camera)
    point_rgb = paint_points(lut[ids[samples]], chosen, pixels, (args.width, args.height))
    point_mask = np.zeros(args.width * args.height, dtype=bool)
    point_mask[pixels] = True
    displayed_mask = np.any(point_rgb != np.array([248, 248, 248], dtype=np.uint8), axis=2)
    # Count all projectable full-map centers using bounded CPU batches.
    full_projectable = 0
    for i in range(0, count, 250000):
        full_projectable += int(project_points(params["means3D"][i:i + 250000], camera)[3].sum())
    cpu_stage_seconds = time.perf_counter() - start

    import torch
    import torch.nn.functional as F
    from diff_gaussian_rasterization import GaussianRasterizer
    from utils.recon_helpers import setup_camera
    if not torch.cuda.is_available():
        raise RuntimeError("CUDA unavailable; no output written")
    device = "cuda:0"
    free_before, total = torch.cuda.mem_get_info()
    if free_before < 4 * (1 << 30):
        raise RuntimeError(f"Only {free_before} VRAM bytes free; refuse full-map render")
    gpu_start = time.perf_counter()
    torch.cuda.reset_peak_memory_stats()
    with torch.no_grad():
        means = torch.from_numpy(params["means3D"]).to(device)
        rotations = F.normalize(torch.from_numpy(params["unnorm_rotations"]).to(device))
        opacities = torch.sigmoid(torch.from_numpy(params["logit_opacities"]).to(device))
        scales = torch.exp(torch.from_numpy(np.tile(params["log_scales"], (1, 3))).to(device))
        means2d = torch.zeros_like(means)
        semantic = torch.from_numpy(params["semantic_colors"]).to(device)
        fixed_colors = torch.from_numpy(lut[ids].astype(np.float32) / 255).to(device)
        common = dict(means3D=means, means2D=means2d, rotations=rotations, opacities=opacities, scales=scales)
        settings = setup_camera(args.width, args.height, k, w2c, camera["near_plane_m"], camera["far_plane_m"], device=device)
        results = {}
        for mode, colors in (("B_learned_semantic_splats", semantic), ("C_fixed_id_palette_splats", fixed_colors)):
            white = settings._replace(bg=torch.ones(3, dtype=torch.float32, device=device))
            t0 = time.perf_counter()
            image, radii, _ = GaussianRasterizer(raster_settings=white)(**common, colors_precomp=colors)
            torch.cuda.synchronize()
            render_seconds = time.perf_counter() - t0
            rgb = np.rint(np.clip(image.permute(1, 2, 0).cpu().numpy(), 0, 1) * 255).astype(np.uint8)
            # The existing depth/silhouette pass renders a constant-one channel.
            # White-on-black with identical Gaussian geometry gives accumulated alpha.
            black = settings._replace(bg=torch.zeros(3, dtype=torch.float32, device=device))
            alpha_rgb, _, _ = GaussianRasterizer(raster_settings=black)(**common, colors_precomp=torch.ones_like(colors))
            torch.cuda.synchronize()
            alpha = np.clip(alpha_rgb[0].cpu().numpy(), 0, 1)
            if not np.allclose(alpha_rgb[0].cpu().numpy(), alpha_rgb[1].cpu().numpy(), atol=1e-4):
                raise ValueError("Constant-one alpha channels differ")
            results[mode] = dict(rgb=rgb, alpha=alpha, render_seconds=render_seconds,
                alpha_pass_seconds=time.perf_counter() - t0 - render_seconds,
                visible_gaussians=int((radii > 0).sum().item()))
        gpu_total_seconds = time.perf_counter() - gpu_start
        peak_allocated = torch.cuda.max_memory_allocated()
        peak_reserved = torch.cuda.max_memory_reserved()

    # Writes start only after all source, camera, and renderer checks pass.
    output.mkdir(parents=True, exist_ok=True)
    Image.fromarray(point_rgb).save(output / "A_center_points.png")
    for mode, data in results.items():
        Image.fromarray(data["rgb"]).save(output / f"{mode}.png")
        Image.fromarray(np.rint(data["alpha"] * 65535).astype(np.uint16)).save(output / f"{mode}_alpha16.png")
    result = {
        "method": args.method, "camera": args.camera, "resolution": [args.width, args.height],
        "checkpoint": str(ckpt), "checkpoint_sha256": sha(ckpt), "camera_path": str(camera_path),
        "camera_sha256": sha(camera_path), "sample_path": str(sample_path), "sample_sha256": sha(sample_path),
        "palette_path": str(palette_path), "palette_sha256": sha(palette_path), "gaussian_count": count,
        "sample_count": len(samples), "full_projectable_centers": full_projectable,
        "sample_projectable_centers": point_stats["projectable_point_count"],
        "point_occupied_pixels": point_stats["occupied_pixel_count"],
        "point_occupancy_ratio": float(point_mask.mean()),
        "point_display_coverage_ratio": float(displayed_mask.mean()),
        "point_display_background_rgb": [248, 248, 248],
        "point_display_coverage_note": "RGB inequality can undercount palette colors exactly equal to background; inspect mask if needed.",
        "cpu_stage_seconds": cpu_stage_seconds, "gpu_total_seconds": gpu_total_seconds,
        "peak_gpu_allocated_bytes": peak_allocated, "peak_gpu_reserved_bytes": peak_reserved,
        "gpu_free_before_bytes": free_before, "gpu_total_bytes": total,
        "torch_version": torch.__version__, "gpu_name": torch.cuda.get_device_name(0),
        "backend": "diff_gaussian_rasterization.GaussianRasterizer via utils.recon_helpers.setup_camera",
        "background_rgb": [255, 255, 255], "prefiltered": False, "scale_modifier": 1.0,
        "no_gaussian_filtering": True,
        "alpha_method": "constant-one colors on black background, identical Gaussian geometry and camera; native depth/silhouette convention",
        "modes": {},
    }
    for mode, data in results.items():
        a = data["alpha"]
        result["modes"][mode] = {
            "render_seconds": data["render_seconds"], "alpha_pass_seconds": data["alpha_pass_seconds"],
            "visible_gaussians_radii_positive": data["visible_gaussians"],
            "alpha_mean": float(a.mean()), "alpha_median": float(np.median(a)),
            "alpha_gt_0_1": float((a > 0.1).mean()), "alpha_gt_0_5": float((a > 0.5).mean()),
            "alpha_gt_0_9": float((a > 0.9).mean()), "background_alpha_le_0_1": float((a <= 0.1).mean()),
        }
    result["outputs"] = {p.name: sha(p) for p in sorted(output.glob("*.png"))}
    (output / "render_metadata.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({k: result[k] for k in ("method", "camera", "resolution", "gaussian_count", "gpu_total_seconds", "peak_gpu_reserved_bytes", "modes")}, indent=2))


if __name__ == "__main__":
    main()
