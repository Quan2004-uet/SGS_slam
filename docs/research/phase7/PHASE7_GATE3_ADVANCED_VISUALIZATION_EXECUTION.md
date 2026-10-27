# Phase 7 Gate 3 — Advanced visualization execution record

**Status:** `EXECUTION_COMPLETE_WITH_COMPARISON_LIMITATIONS`
**Date:** 2026-10-27
**Run:** `p7_bcgm_g3_room0_on_0_1999_r01`
**Scope:** offline rendering and packaging from the saved map only. No SLAM,
training, map optimization, dataset reload, or quality-metric evaluation.

## Source and input identity

- Phase 7 branch/HEAD: `phase7-bcgm` / `68f9060f7ff4d8d141be1d5f71339401327edd06`.
- Checkpoint `params.npz` SHA256:
  `a02dd4b4ecfd9c982866cf4a4c38c187ef22c75049b8328e18eea20608944917`.
- `params.ply`: `409d1c3637e3f951f950d14bf066a88df66de8dc41a01762c312a0871ab300fc`.
- `seg_params.ply`: `98a41a36e69e113c7e7da8dcfcd8c279c08c25da8af7525e26dcbdb7df262b89`.
- Phase 7 `scripts/slam.py`: `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999`.
- Phase 7 `utils/bcgm.py`: `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400`.
- New visualization helper:
  `tools/phase7/gate3_advanced_visualization.py`, SHA256
  `d7381a073fe50480781a88c981234805d33f3e5c32920621c9b7da03be2172bf`.
- V3A renderer implementation:
  `/home/robot/research/SGS_slam/scripts/visualization/visualize_full_scene_v3a.py`;
  exact hash is recorded in the visualization manifest. Its generated
  metadata identifies the renderer checkout as branch
  `phase5-profiling-instrumentation`, HEAD
  `809d5ea2fd93ce8a97f8082840b44b134bc86519`. This identifies the renderer
  tool checkout, not the Phase 7 map/checkpoint source, which is recorded
  separately above.

## Host preflight and execution

Direct-host preflight passed using the authorized host context:

- GPU: NVIDIA GeForce RTX 5080, 16,303 MiB.
- At preflight: 818 MiB used, 0% GPU utilization; PyTorch 2.7.1+cu128,
  CUDA available.
- Final post-render observation: 818 MiB used, 0% utilization.
- Free disk: 25 GiB on `/dev/sda2` (98% used).
- Peak CUDA allocated/reserved reported by V3A render: 1,038,653,440 /
  1,346,371,584 bytes. This is renderer allocator memory, not NVML VRAM.

`--render-observed` rendered frames **0, 499, 999, 1499, 1999** sequentially
from the immutable checkpoint. Each frame produced native Gaussian RGB,
raw learned `semantic_colors`, float32 camera-z depth NPY in metres, and a
depth PNG. The observed rendering uses the Phase 4 saved `estimated_w2c` and
intrinsics, 1200×680, `setup_camera` black background, and fixed `[0,6]` m
Turbo display with invalid depth black.

The audited Phase 4 V3A renderer then produced full-scene saved-map outputs
using the exact copied `trajectory_observed`, `room_overview`, and
`top_oblique` Phase 4 JSON cameras at 960×540. It reported technical
completion and source integrity true, all 2,000 trajectory poses, and no
SLAM/evaluation/optimization activity. Its deterministic Gaussian-center
projection uses 650,000 centers (PCG64 seed 20261013), matching the V3A
display method.

The CPU packaging step copied existing Phase 7 V1 free-view artifacts into
the new tree (copy only; no rerender), normalized all three phases' raw metric
depth arrays to the Phase 4 `[0,6]` m Turbo display, and formed the
Phase 4 | Phase 6 | Phase 7 boards.

## Recovery notes

Two non-scientific invocation mistakes occurred and were corrected:

1. The first V3A call used a nonexistent mapping CSV path. It failed before
   loading/rendering the checkpoint and left only empty output directories;
   those empty directories were removed after verifying they contained no
   files. The corrected Phase 4 audit mapping path is
   `/home/robot/research/SGS_slam/results/runtime_artifacts/phase4_vb001_visualization_audit/semantic_mapping.csv`.
2. The initial board packaging pass referenced the Phase 6 trajectory image
   under the wrong subdirectory. Packaging stopped at that missing file. It
   resumed without replacing completed boards after correcting the path.
   Semantic boards were subsequently separated into V1 free-view and V3A
   camera groups to avoid the shared filename `top_oblique` conflating two
   different canonical viewpoints.

No source algorithm, configuration, checkpoint, Phase 4/6 reference, or
existing Phase 7 free-view source file was changed.

## Output map

Root:
`results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/advanced_visualization/`

- `phase7_only/observed_camera/`: 15 frame artifacts (RGB, learned semantic,
  depth PNG and depth NPY for five frames).
- `phase7_only/v3a_diagnostics_r02/`: full-scene RGB, geometry, raw learned
  semantics, fixed-ID maps, class panels, legends and estimated trajectory.
- `phase7_only/free_view/`: copied existing Phase 7 overview/oblique/
  top-oblique RGB, learned semantic and paired views.
- `compare_phase4_phase6_phase7/`: 46 comparison boards plus 15 standardized
  per-phase depth display references, for 61 PNGs total.
- `cameras/`: exact five observed frame metadata and three V3A camera JSONs.
- `metadata/advanced_visualization_manifest.json`: per-output SHA256 and
  210 Phase 4/6 reference SHA256 entries.

The package contains 143 checksummed payload files plus the manifest itself;
total advanced visualization size is approximately 116 MB. No checkpoint or
large PLY is duplicated into this package.
