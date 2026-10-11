# PHASE4-VB-001 Camera-View Qualitative Export Result

## Objective and identity

- Date: 2026-10-12 (Asia/Tokyo checkpoint; export timestamp
  2026-10-11T15:35:18Z).
- Status: `PASS_QUALITATIVE_EXPORT`.
- Branch: `phase4-vb-001-cpu-keyframe-offload`.
- Export run HEAD: `7122eb56222031dc6bdb96033f2f15a22293b9da`.
- Dataset/scene: Replica `room0`, native resolution 1200 x 680.
- Representative frames: `[0, 499, 999, 1499, 1999]`.
- GPU: NVIDIA GeForce RTX 5080, 16,609,378,304 physical bytes.

The gate exports representative training-camera RGB, depth, and semantic
comparisons from the saved PHASE4-VB-001 state. It does not rerun online SLAM,
recompute E4 metrics, run post-SLAM optimization, or modify source/config.

Saved state:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`

Output root:
`results/qualitative/phase4_vb001_room0_representative/`

## Rendering and export protocol

The temporary export harness reused the E1--E4 selective saved-state loader,
released camera reconstruction, and three native rasterizer paths for RGB,
depth/silhouette, and `semantic_colors`. Frames were processed sequentially;
frame-local CUDA tensors were released before the next frame.

### RGB

- GT RGB uses the exact Replica frame in RGB channel order.
- Raw renderer values were retained transiently for export processing.
- Only 8-bit visualization PNGs clamp rendered values to `[0,1]`.
- No display clamp changed the already completed E4 metric evidence.

### Depth

- `rendered_depth_raw.npy` and `gt_depth_raw.npy` are float32 metric depth in
  meters at 680 x 1200.
- Both visualization PNGs use the same 0--6 m range and OpenCV Turbo colormap.
- Colorized PNGs are display artifacts, not numeric depth.

### Semantic

- The raw render uses saved per-Gaussian `semantic_colors`.
- The comparison image applies the released nearest-current-GT-palette
  recoloring used by semantic mIoU.
- GT uses Replica semantic-color images; `semantic_ids` are not substituted.

No new metric was computed. Per-frame values below were copied from the
existing E4 `per_frame_metrics.json` because all five selected frames belong
to the released sample `{0} union {5k-1}`.

## Output inventory

Each of `frame_0000/`, `frame_0499/`, `frame_0999/`, `frame_1499/`, and
`frame_1999/` contains:

- RGB: `rendered_rgb.png`, `gt_rgb.png`, `rgb_side_by_side.png`;
- depth: `rendered_depth_raw.npy`, `gt_depth_raw.npy`,
  `rendered_depth.png`, `gt_depth.png`, `depth_side_by_side.png`;
- semantic: `rendered_semantic_raw.png`,
  `rendered_semantic_recolored.png`, `gt_semantic.png`,
  `semantic_side_by_side.png`;
- composite: `qualitative_grid.png`.

Root evidence:

- `contact_sheet_all_frames.png`;
- `per_frame_metric_annotations.json`;
- `qualitative_manifest.json`;
- `qualitative_metadata.json`;
- `artifact_checksums.sha256`;
- `QUALITATIVE_EXPORT_SUMMARY.md`.

The manifest contains 69 artifacts excluding itself and the checksum file.
All listed checksums passed post-export verification. Important root hashes:

| Artifact | Size (bytes) | SHA256 |
|---|---:|---|
| `contact_sheet_all_frames.png` | 2,569,461 | `dec2e6bcf067a2f4775a611d70768e6fe14db7ddedec13a4c6846161ce2ac315` |
| `qualitative_manifest.json` | 15,802 | `cfaa583e99b9ee2057e50f8ef55d55f95f86c508da559521d6fadb25ea746482` |
| `qualitative_metadata.json` | 2,120 | `2c89141b1e5b3ea2558e819330518dca11d44484f24a799f4dcfd5b686bad416` |

## Existing E4 metric annotations

| Frame | PSNR (dB) | MS-SSIM | LPIPS | Depth L1 (m) | Depth L1 (cm) | Semantic mIoU |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 32.882659912109375 | 0.9810872077941895 | 0.08778916299343109 | 0.005040761083364487 | 0.5040761083364487 | 0.9139452217645019 |
| 499 | 33.975608825683594 | 0.9834632873535156 | 0.08893603086471558 | 0.0059888893738389015 | 0.5988889373838902 | 0.8867164518703912 |
| 999 | 33.07167053222656 | 0.9776255488395691 | 0.046051230281591415 | 0.0034372464288026094 | 0.34372464288026094 | 0.945431086708004 |
| 1499 | 30.15478515625 | 0.9623193740844727 | 0.10165969282388687 | 0.015287519432604313 | 1.5287519432604313 | 0.8634091858385644 |
| 1999 | 36.80352783203125 | 0.9898234009742737 | 0.04646023362874985 | 0.0030452224891632795 | 0.30452224891632795 | 0.9376516688684893 |

These annotations preserve E4 values exactly; the qualitative gate did not
interpolate or recompute them.

## Runtime, memory, and validation

- Total export runtime: 9.213427657989087 s.
- Saved-state load: 0.1845726119936444 s.
- Total renderer time: 0.1887064349721186 s.
- Peak GPU allocated/reserved: 1,774,468,608 / 1,935,671,296 B
  (10.6835% / 11.6541% of physical VRAM).
- Renderer invoked: yes.
- New metrics computed: no.
- SLAM rerun: no.
- CUDA OOM: no.

All five frames passed RGB, depth, semantic, and composite validation. Every
native image is readable at 1200 x 680; both raw-depth arrays per frame are
readable, float32, shape 680 x 1200, and finite. The contact sheet, manifest,
metadata, and checksum inventory are readable and present.

## Scientific boundary and next step

This result is a **camera-view qualitative export** from selected training
poses. It is not the paper-style `Scene Reconstruction | 3D Segmentation`
free-view/map-view visualization, and it does not establish paper reproduction,
cross-scene generalization, or a new quantitative result.

The next immediate task is a read-only **Scene Reconstruction / 3D
Segmentation Visualization Audit**. It should determine the repository-native
viewer/export path for `params.ply` as the RGB reconstructed map and
`seg_params.ply` as the semantic-colored 3D map before any new visualization
is rendered. The Paper / Baseline Comparison Audit remains a subsequent
research task.
