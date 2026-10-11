# Current Session Handoff

> **CURRENT OPERATIONAL HANDOFF AUTHORITY.** Use `PROJECT_STATUS.md` for
> project-wide state. Repository/runtime evidence overrides either document.

Last reconciled: 2026-10-12.

## Session

- Session ID: `SESSION_004`.
- Title: Phase 4 Variant B Full-Scene Validation, State Preservation,
  Released Evaluation, and Qualitative Export.
- Status: `CLOSED`.
- Started: 2026-10-10.
- Closed: 2026-10-12.
- Branch: `phase4-vb-001-cpu-keyframe-offload`.
- Evaluation run HEAD: `63adf3aed8ae2201a46d11cec473672f9e91fd0e`.
- Qualitative export run HEAD: `7122eb56222031dc6bdb96033f2f15a22293b9da`.

## Authoritative Completed Checkpoint

- Latest gate: `PASS_QUALITATIVE_EXPORT`.
- Evaluation: complete for Replica `room0` released training-view protocol.
- Camera-view qualitative export: complete for frames
  `[0,499,999,1499,1999]`.
- 3D map reconstruction/segmentation visualization: not run; next audit.
- Online SLAM rerun: not required.
- E4 image export: not performed. A separate representative qualitative export
  completed afterward.
- Paper reproduction: not claimed and not complete.

Validation chain: E1 load-only PASS; E2 frame-0 RGB/depth/semantic render PASS;
E3 frames `[0,4,9,14,19]` metric subset PASS; E4 full released evaluation
PASS; representative camera-view export PASS. Future sessions must not resume
from output saving, E1--E4, or the completed camera-view export.

## Saved State and Full-Scene Runtime

Saved state:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`

- Frames 0–1999 completed; 4,956,467 Gaussians; 402 logical keyframes ending
  `[1989,1994,1998,1999]`.
- Runtime: 14,173.47515856901 s.
- Tracking/mapping/overall FPS: 0.3354664059815056 /
  0.25086898791330586 / 0.14110865384985266.
- Peak SLAM GPU allocated/reserved: 5,817,509,888 / 7,189,037,056 B.
- Process HWM: 17,960,493,056 B host RAM.

## E4 Result

- Image/depth/semantic metric frames: 401, exact released sample
  `0,4,9,...,1989,1994,1999`; no skipped frames.
- Trajectory frames: 2,000.
- PSNR: 33.313067 dB.
- MS-SSIM: 0.979470.
- LPIPS: 0.067555.
- Depth L1: 0.00495158 m / 0.495158 cm.
- Semantic-color mIoU: 0.916585.
- Released Horn-aligned mean w2c translation error: 0.00274075 m. It is not
  true RMSE despite the released source label.
- Supplementary true RMSE: 0.00339827 m.
- Evaluation runtime: 74.4107 s.
- Evaluation peak GPU allocated/reserved: 1,846,789,120 /
  2,057,306,112 B.
- Renderer/metrics: yes. SLAM rerun/image export/OOM/non-finite metric: no.

Audit:
`docs/experiments/PHASE4_VB001_EVALUATION_EXPORT_AUDIT.md`

Result:
`docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md`

E4 evidence:
`results/runtime_artifacts/phase4_vb001_eval_e4_full_released/`

## Qualitative Export Result

- Status: `PASS_QUALITATIVE_EXPORT`.
- Selected frames: `[0,499,999,1499,1999]`.
- Every frame passed rendered/GT RGB, metric-depth raw/visualization,
  semantic raw/recolored/GT, side-by-side, and composite validation.
- Root contact sheet and 69-artifact manifest are present and checksummed.
- Runtime: 9.213427657989087 s.
- Peak GPU allocated/reserved: 1,774,468,608 / 1,935,671,296 B.
- Renderer invoked: yes. New metrics computed: no. SLAM rerun: no.
- E4 per-frame values were copied as annotations, not recomputed.
- Output root:
  `results/qualitative/phase4_vb001_room0_representative/`.
- Result:
  `docs/experiments/PHASE4_VB001_QUALITATIVE_EXPORT_RESULT.md`.

This is camera-view qualitative evidence. The paper-style reconstructed RGB
3D map and semantic-colored 3D map have not been visualized yet.

## Immediate Operational Next Task

Perform a read-only **Scene Reconstruction / 3D Segmentation Visualization
Audit**:

1. inspect repository-native support for viewing/exporting `params.ply` and
   `seg_params.ply`;
2. establish RGB-map and semantic-map color/view conventions;
3. define bounded, reproducible camera/background/crop/output settings;
4. distinguish this 3D map-view product from completed camera-view renders;
5. stop with a proposed execution gate before producing new visualization.

Do not automatically render a 3D scene, run another scene/evaluator, post-opt,
or VB002. Paper / Baseline Comparison Audit remains the task after this
visualization track and must not be dropped.

## Relevant Evidence

- `project_management/PROJECT_STATUS.md`
- `project_management/sessions/SESSION_004.md`
- `docs/experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md`
- `docs/experiments/PHASE4_VB001_EVALUATION_EXPORT_AUDIT.md`
- `docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md`
- `docs/experiments/PHASE4_VB001_QUALITATIVE_EXPORT_RESULT.md`
- `results/runtime_artifacts/phase4_vb001_eval_e1_load_only/`
- `results/runtime_artifacts/phase4_vb001_eval_e2_single_frame_render/`
- `results/runtime_artifacts/phase4_vb001_eval_e3_bounded_subset/`
- `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/`
- `results/qualitative/phase4_vb001_room0_representative/`

## STOPPED HERE

SESSION_004 ends at `PASS_QUALITATIVE_EXPORT`. Resume with the Scene
Reconstruction / 3D Segmentation Visualization Audit. No SLAM/evaluation
rerun, metric recomputation, or repeated camera-view export is needed or
authorized by this handoff.
