# Current Session Handoff

> **CURRENT OPERATIONAL HANDOFF AUTHORITY.** Use `PROJECT_STATUS.md` for
> project-wide state. Repository/runtime evidence overrides either document.

Last reconciled: 2026-10-11.

## Session

- Previous session: `SESSION_003` — Phase 4 Variant B Bounded Validation.
- Session ID: `SESSION_004`.
- Title: Phase 4 Variant B Full-Scene Validation and State Preservation.
- Status: `CLOSED`.
- Started: 2026-10-10.
- Last active/closed: 2026-10-11.
- Phase: Phase 4 — Memory-management research variant.
- Variant: `PHASE4-VB-001` — CPU offload of resident keyframe payloads.

## Current Checkpoint

PHASE4-VB-001 full-scene output saving is complete.

- Status: `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.
- Frames: 0–1999, 2,000 completed.
- Final Gaussians: 4,956,467.
- Logical keyframes: 402; tail `[1989, 1994, 1998, 1999]`.
- Runtime: 14,173.47515856901 s (approximately 3 h 56 m 13 s).

The final state is saved and reloadable. `params.npz` is readable and contains
Gaussian/map state, estimated camera parameters, GT trajectory, intrinsics,
`w2c`, timestep, keyframe indices, semantic state, and original dimensions.
Standalone keyframe indices and RGB/semantic PLY exports also exist.

Stable output:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/`

Evidence:
`results/runtime_artifacts/phase4_vb001_minimal_output_save_full_0_1999/`

Canonical result:
`docs/experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md`

## Runtime Telemetry Available

- Tracking FPS: 0.3354664059815056.
- Mapping FPS: 0.25086898791330586.
- Overall SLAM FPS: 0.14110865384985266.
- Peak GPU allocated/reserved: 5,817,509,888 / 7,189,037,056 B.
- Process RSS/HWM: 17,960,493,056 B host RAM.

Detailed residency fields were intentionally not collected by the minimal
harness and remain `UNKNOWN` for this run. Use the earlier full-scene
Variant-B evidence for residency invariants; do not infer those values from
the minimal harness.

## Evaluation Status

Evaluation is `NOT RUN`. No ATE, PSNR, SSIM, LPIPS, DepthL1, mIoU, rendering
metrics, semantic metrics, post-SLAM optimization, full rendered-image export,
or paper metrics were run or reproduced.

The saved state appears sufficient for future evaluation without rerunning
online SLAM, but its loading/evaluation path must first be audited.

## STOPPED HERE

Full-scene online processing, final state saving, artifact verification, and
lightweight telemetry are complete. Stop before evaluation execution.

## Immediate Operational Next Task

Perform an **Evaluation / Export Audit** from:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`.

Read source/config only and establish:

- exact saved-state loader and required parameter reconstruction;
- renderer entry point for RGB/depth/semantic output;
- RGB PSNR/SSIM/LPIPS protocol;
- depth/DepthL1 protocol;
- trajectory/ATE Mean and RMSE alignment protocol;
- semantic/mIoU protocol and label mapping;
- frame sampling, GT alignment, and output directories;
- whether any field is missing before evaluation is authorized.

Stop after the audit and request explicit authorization for evaluation/export.
Do not rerun online SLAM if saved-state loading succeeds.

## Evaluation Targets for the Later Gate

- RGB rendered/GT comparisons and PSNR, SSIM, LPIPS.
- Depth rendered/GT comparisons and DepthL1.
- Semantic rendered/GT comparisons and mIoU.
- Estimated/GT trajectory and ATE Mean/RMSE.
- Existing runtime metrics: tracking, mapping, and overall FPS; peak GPU
  allocated/reserved; process RSS/HWM.

## Relevant Files

- `AGENTS.md`
- `project_management/PROJECT_STATUS.md`
- `project_management/sessions/SESSION_004.md`
- `docs/experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md`
- `docs/experiments/PHASE4_VB001_FULL_SCENE_AUDIT.md`
- `docs/experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_DRY_RUN_PLAN.md`
- `docs/experiments/PHASE4_VB002_RUNTIME_OPTIMIZATION_PLAN.md`
- `results/runtime_artifacts/phase4_vb001_minimal_output_save_full_0_1999/`

## Do Not

- Do not rerun 0–49 or 0–1999 online SLAM.
- Do not execute evaluation before its audit and separate approval.
- Do not start post-SLAM optimization or PHASE4-VB002.
- Do not change algorithm/config/precision/resolution/iterations/keyframes.
- Do not commit or upload the large ignored artifacts through regular Git.
