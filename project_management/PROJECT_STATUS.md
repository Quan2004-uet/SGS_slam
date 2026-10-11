# SGS-SLAM Project Status

> **CURRENT PROJECT-STATE AUTHORITY.** Repository/source/config/runtime
> evidence has highest priority. This file defines the current phase and gate;
> use `SESSION_HANDOFF.md` for the exact operational resume point.

Last reconciled: 2026-10-12.

## Project Identity

- Repository: SGS-SLAM — Semantic Gaussian Splatting for Neural Dense SLAM.
- Current branch: `phase4-vb-001-cpu-keyframe-offload`.
- Evaluation run HEAD: `63adf3aed8ae2201a46d11cec473672f9e91fd0e`.
- Qualitative export run HEAD: `7122eb56222031dc6bdb96033f2f15a22293b9da`.
- Released baseline: `e4183986204242a8bb422624618af07780a49d26` (`main`).
- Dataset/config: Replica `room0`, `configs/replica/slam.py`, seed 0.

## Current Phase and Checkpoint

- Phase: Phase 4 — Memory-management research variant.
- Variant: `PHASE4-VB-001` — CPU offload of resident keyframe payloads.
- Runtime/output checkpoint: `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.
- Latest completed gate: `PASS_QUALITATIVE_EXPORT`.
- Evaluation status: complete for the Replica `room0` released training-view
  protocol.
- Camera-view qualitative export: complete for representative frames
  `[0,499,999,1499,1999]`.
- 3D map reconstruction/segmentation visualization: not run.
- Paper reproduction status: not claimed and not complete.
- Immediate next task: **Scene Reconstruction / 3D Segmentation Visualization
  Audit**.

SESSION_004 is closed. Future work must not resume from output saving, Gates
E1--E4, or camera-view qualitative export. The saved full-scene state and PLY
exports remain the authoritative inputs for later visualization/analysis; no
online SLAM or evaluation rerun is required.

## Validated PHASE4-VB-001 Chain

- Gates 1 and 2: PASS.
- Gate 3 frames 0–99, Gate 4 frames 0–499, Gate 5 frames 0–999:
  `PASS_FRAME_LIMIT`.
- Historical full-scene online run: frames 0–1999 completed; corrected status
  `PASS_RUNTIME_VALIDATOR_BUG` because the old validator omitted the released
  `num_frames-2` terminal keyframe.
- Minimal output-save smoke 0–49: `PASS_MINIMAL_OUTPUT_SAVE_SMOKE`.
- Telemetry output-save smoke 0–49: `PASS_TELEMETRY_OUTPUT_SAVE_SMOKE`.
- Full-scene output save 0–1999: `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.
- E1 load-only: `PASS_EVAL_E1_LOAD_ONLY`.
- E2 single-frame render: `PASS_EVAL_E2_SINGLE_FRAME_RENDER`.
- E3 bounded five-frame metrics: `PASS_EVAL_E3_BOUNDED_SUBSET`.
- E4 full released evaluation: `PASS_EVAL_E4_FULL_RELEASED`.
- Representative camera-view qualitative export:
  `PASS_QUALITATIVE_EXPORT`.

## Full-Scene Runtime and Saved State

- Frames: 2,000, exactly 0–1999; final frame 1999.
- Runtime: 14,173.47515856901 s (approximately 3 h 56 m 13 s).
- Final Gaussians: 4,956,467.
- Logical keyframes: 402; tail `[1989, 1994, 1998, 1999]`.
- Tracking/mapping/overall FPS: 0.3354664059815056 /
  0.25086898791330586 / 0.14110865384985266.
- Peak GPU allocated/reserved: 5,817,509,888 / 7,189,037,056 B.
- Process RSS/HWM: 17,960,493,056 B host RAM, not GPU VRAM.

Stable output:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/`

The readable `params.npz` contains Gaussian/map state, estimated and GT camera
trajectories, intrinsics, `w2c`, timestep, semantic state, keyframe indices,
and original dimensions. RGB/semantic PLY files and standalone keyframe indices
also exist. Artifact sizes and SHA256 values are recorded in
`docs/experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md`.

## Full Released Evaluation Result

- Status: `PASS_EVAL_E4_FULL_RELEASED`.
- Image/depth/semantic frames: 401, exact rule
  `{0} union {5k-1 | k=1..400}`; first `[0,4,9]`, tail
  `[1989,1994,1999]`; none skipped.
- Trajectory frames: all 2,000 finite-pose frames.
- PSNR: 33.313067 dB.
- MS-SSIM: 0.979470. The released source labels this “SSIM”, but computes
  multi-scale SSIM.
- LPIPS-Alex: 0.067555.
- Depth L1: 0.00495158 m / 0.495158 cm.
- Semantic-color mIoU: 0.916585.
- Released Horn-aligned mean relative-w2c translation error:
  0.00274075 m / 0.274075 cm. This is not true RMSE.
- Supplementary true RMSE from the same aligned errors:
  0.00339827 m / 0.339827 cm.
- Evaluation wall time: 74.4107 s; renderer 10.0479 s; metrics 50.8178 s;
  trajectory 0.0101 s.
- Evaluation peak GPU allocated/reserved: 1,846,789,120 /
  2,057,306,112 B (11.12% / 12.39% of physical VRAM).
- Renderer invoked and metrics computed: yes. SLAM rerun and E4 image export:
  no. A later separately authorized qualitative gate exported five selected
  camera views without recomputing metrics.
- CUDA OOM, non-finite metrics, and hidden skipped frames: none.

Canonical evaluation record:
`docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md`.

Runtime evidence:
`results/runtime_artifacts/phase4_vb001_eval_e4_full_released/`.

## Camera-View Qualitative Export

- Status: `PASS_QUALITATIVE_EXPORT`.
- Frames: `[0,499,999,1499,1999]`.
- RGB, metric-depth, semantic-color, GT reference, side-by-side, and composite
  artifacts passed validation for all five frames.
- RGB PNG visualization clamps to `[0,1]`; raw depth NPY files remain meters;
  depth PNGs use a common 0--6 m Turbo scale; semantic comparisons use released
  nearest-current-GT-palette recoloring.
- Runtime: 9.213427657989087 s.
- Peak GPU allocated/reserved: 1,774,468,608 / 1,935,671,296 B.
- Renderer invoked: yes. New metrics computed and SLAM rerun: no.
- Output root:
  `results/qualitative/phase4_vb001_room0_representative/`.
- Canonical record:
  `docs/experiments/PHASE4_VB001_QUALITATIVE_EXPORT_RESULT.md`.

This is a selected training-camera comparison package. Paper-style 3D
reconstruction and semantic-map visualization have not run.

## Protocol Boundaries

- RGB uses GT RGB divided by 255, GT-depth-valid masking, released
  `calc_psnr`, MS-SSIM, and LPIPS AlexNet with clamped `[0,1]` inputs.
- Depth uses Replica scale 6553.5 and masked mean absolute error in meters.
- Semantic evaluation renders `semantic_colors`, recolors to the nearest
  current-frame GT palette, ignores GT black, and averages frame mIoU values.
  It does not compare `semantic_ids` directly.
- Trajectory uses normalized real-first quaternions, relative w2c, and Horn
  rigid rotation+translation alignment without scale.

## Scientific Interpretation and Limits

`RUNTIME VERIFIED`: for Replica `room0` on the tested RTX 5080,
PHASE4-VB-001 removes the measured GPU-memory scalability failure that caused
the unchanged Phase 3 baseline to OOM, reaches frame 1999, saves a reloadable
state, and completes the audited released-code evaluation from that state.

These are `room0` released-code metrics. They do not establish full paper
reproduction, superiority over the paper or baseline, benchmark-wide results,
or generalization to other scenes/datasets. Post-SLAM optimization was not run.

## Immediate Operational Next Task

Perform a read-only **Scene Reconstruction / 3D Segmentation Visualization
Audit**. It must inspect the repository-native visualization path for
`params.ply` and `seg_params.ply`, establish camera/viewer, color, background,
crop, output, and provenance conventions, and propose a bounded visualization
gate without rendering it during the audit.

The Paper / Baseline Comparison Audit remains the subsequent research task; it
must still establish protocol/stage comparability before any reproduction or
superiority claim.

Do not start PHASE4-VB002 in this checkpoint. It remains a future runtime
optimization track.

## STOPPED HERE

PHASE4-VB-001 full-scene runtime, state preservation, released Replica `room0`
evaluation, and camera-view qualitative export are complete through
`PASS_QUALITATIVE_EXPORT`. Resume with the Scene Reconstruction / 3D
Segmentation Visualization Audit—not another SLAM, evaluation, or camera-view
export run.
