# SGS-SLAM Project Status

> **CURRENT PROJECT-STATE AUTHORITY.** Repository/source/config/runtime
> evidence has highest priority. This file defines the current phase and gate;
> use `SESSION_HANDOFF.md` for the exact operational resume point.

Last reconciled: 2026-10-11.

## Project Identity

- Repository: SGS-SLAM — Semantic Gaussian Splatting for Neural Dense SLAM.
- Current branch: `phase4-vb-001-cpu-keyframe-offload`.
- Checkpoint parent HEAD: `68f9060f7ff4d8d141be1d5f71339401327edd06`.
- Released baseline: `e4183986204242a8bb422624618af07780a49d26` (`main`).
- Dataset/config: Replica `room0`, `configs/replica/slam.py`, seed 0.

## Current Phase

- Phase: Phase 4 — Memory-management research variant.
- Status: PHASE4-VB-001 validation and full-scene state preservation complete.
- Variant: `PHASE4-VB-001` — CPU offload of resident keyframe payloads.
- Latest gate: full-scene output-saving frames 0–1999.
- Latest status: `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.

The next gate is **Evaluation / Export Audit** from the saved full-scene state.
Evaluation itself remains `NOT RUN` and must not begin until that audit defines
the saved-state loading and metric protocols.

## Latest Session

- Session ID: `SESSION_004`.
- Status: `CLOSED`.
- Started: 2026-10-10.
- Last active/closed: 2026-10-11.

## Completed Baseline and Variant Work

- Phase 1 research documentation: PASS.
- Phase 2 baseline reproduction audit: PASS.
- Phase 3 environment, renderer, dataset, compatibility, initialization, and
  bounded online gates: PASS through frames 0–499.
- Phase 3 unchanged baseline full scene: OOM at frame 1294 after frame 1293;
  allocator-only attempt: OOM at frame 1333. Phase 3 is closed with this
  documented RTX 5080 16 GB memory limitation.
- PHASE4-VB-001 Gates 1 and 2: PASS.
- Gate 3 frames 0–99, Gate 4 frames 0–499, and Gate 5 frames 0–999:
  `PASS_FRAME_LIMIT`.
- Earlier Variant-B full-scene runtime completed frames 0–1999 with corrected
  classification `PASS_RUNTIME_VALIDATOR_BUG`. Its old harness omitted the
  released `num_frames-2` terminal keyframe in its expectation and stopped
  before final saving.
- Minimal output-save smoke 0–49: `PASS_MINIMAL_OUTPUT_SAVE_SMOKE`.
- Telemetry output-save smoke 0–49: `PASS_TELEMETRY_OUTPUT_SAVE_SMOKE`.
- Final full-scene output-save 0–1999:
  `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.

## Final Full-Scene Output-Save Result

- Frames completed: 2,000, exactly 0–1999; final frame 1999.
- Runtime: 14,173.47515856901 s (approximately 3 h 56 m 13 s).
- Final Gaussians: 4,956,467.
- Logical keyframes: 402; tail `[1989, 1994, 1998, 1999]`.
- Save success / artifact completeness / telemetry completeness: true/true/true.
- Tracking/mapping/overall FPS: 0.3354664059815056 /
  0.25086898791330586 / 0.14110865384985266.
- Peak GPU allocated/reserved: 5,817,509,888 / 7,189,037,056 B.
- Process RSS/HWM: 17,960,493,056 B. This is host RAM, not VRAM.
- Final serialization: 9.3924627660017 s.

The minimal harness did not collect detailed Variant-B residency telemetry;
those fields are `UNKNOWN` for this run and are not a failure. The prior
detailed full-scene run established CPU authority, zero persistent GPU archive
payload, at most one staged archived payload, and cleanup invariants.

## Saved State

Stable output directory:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/`

Evidence directory:
`results/runtime_artifacts/phase4_vb001_minimal_output_save_full_0_1999/`

The saved state includes readable `params.npz`, `params.ply`,
`seg_params.ply`, and `keyframe_time_indices.npy`. It contains Gaussian/map
state, estimated and GT camera trajectories, intrinsics, `w2c`, timestep,
semantic IDs/colors, keyframe indices, and original image dimensions. It is
sufficient to attempt later evaluation without rerunning online SLAM, subject
to a saved-state loading audit.

Artifact sizes and SHA256 values are recorded in
`docs/experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md` and the
Git-ignored runtime manifest. Large binary artifacts and logs remain on the
server and are intentionally not committed.

## Scientific Interpretation

`RUNTIME VERIFIED`: PHASE4-VB-001 removes the measured GPU-memory scalability
failure that caused the unchanged Phase 3 baseline to OOM on this RTX 5080.
For Replica `room0`, the variant reached frame 1999 without GPU OOM and saved
a reloadable final online state. Peak allocated/reserved GPU memory was about
5.82/7.19 GB versus 16.61 GB physical memory.

No reconstruction-accuracy improvement, paper-metric reproduction, or
generalization to another scene/dataset is claimed.

## Evaluation and Paper Status

- Evaluation: `NOT RUN`.
- ATE, PSNR, SSIM, LPIPS, DepthL1, and mIoU: `NOT RUN`.
- Rendering and semantic metrics: `NOT RUN`.
- Post-SLAM optimization: `NOT RUN`.
- Paper metrics: `NOT REPRODUCED YET`.
- Full rendered RGB/depth/semantic export: `NOT RUN`.

## Immediate Operational Next Task

Perform an **Evaluation / Export Audit** using:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`.

The audit must establish before any evaluation executes:

1. exact repository saved-state loading entry point;
2. renderer invocation and required reconstructed state;
3. RGB PSNR/SSIM/LPIPS protocol;
4. depth/DepthL1 protocol and units;
5. trajectory/ATE alignment protocol;
6. semantic/mIoU protocol and label mapping;
7. frame sampling and GT alignment;
8. evaluation/export output paths and provenance.

If saved-state loading succeeds, no online SLAM rerun is required. Stop after
the audit and request separate authorization before executing evaluation.

## Future Track

PHASE4-VB002 runtime optimization remains a future, separate research track.
Do not start it before the saved-state evaluation/export protocol is audited.

## STOPPED HERE

PHASE4-VB-001 full-scene output saving and telemetry are complete with
`PASS_FULL_OUTPUT_SAVE_TELEMETRY`. The next action is Evaluation / Export
Audit from saved state—not a full-scene rerun, evaluation execution, post-opt,
or VB002 implementation.
