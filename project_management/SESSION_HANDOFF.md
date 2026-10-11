# Current Session Handoff

> **CURRENT OPERATIONAL HANDOFF AUTHORITY.** Use `PROJECT_STATUS.md` for
> project-wide state. Repository/runtime evidence overrides either document.

Last reconciled: 2026-10-11.

## Session

- Session ID: `SESSION_004`.
- Title: Phase 4 Variant B Full-Scene Validation, State Preservation, and
  Released Evaluation.
- Status: `CLOSED`.
- Started: 2026-10-10.
- Closed: 2026-10-11.
- Branch: `phase4-vb-001-cpu-keyframe-offload`.
- Evaluation run HEAD: `63adf3aed8ae2201a46d11cec473672f9e91fd0e`.

## Authoritative Completed Checkpoint

- Latest gate: `PASS_EVAL_E4_FULL_RELEASED`.
- Evaluation: complete for Replica `room0` released training-view protocol.
- Online SLAM rerun: not required.
- Image export: not performed.
- Paper reproduction: not claimed and not complete.

Validation chain: E1 load-only PASS; E2 frame-0 RGB/depth/semantic render PASS;
E3 frames `[0,4,9,14,19]` metric subset PASS; E4 full released evaluation
PASS. Future sessions must not resume from output saving or E1--E4.

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

## Immediate Operational Next Task

Perform a read-only **Paper / Baseline Comparison Audit**:

1. locate the paper/released `room0` comparison values and their stage;
2. verify protocol and sampling comparability;
3. distinguish released-code reproduction from paper-table reproduction;
4. prepare a baseline-versus-PHASE4-VB-001 result table;
5. identify defensible claims and remaining scenes/experiments.

Do not automatically run another scene, evaluator, post-opt, or VB002. The
comparison audit requires separate scope and should stop before new execution.

## Relevant Evidence

- `project_management/PROJECT_STATUS.md`
- `project_management/sessions/SESSION_004.md`
- `docs/experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md`
- `docs/experiments/PHASE4_VB001_EVALUATION_EXPORT_AUDIT.md`
- `docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md`
- `results/runtime_artifacts/phase4_vb001_eval_e1_load_only/`
- `results/runtime_artifacts/phase4_vb001_eval_e2_single_frame_render/`
- `results/runtime_artifacts/phase4_vb001_eval_e3_bounded_subset/`
- `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/`

## STOPPED HERE

SESSION_004 ends at `PASS_EVAL_E4_FULL_RELEASED`. Resume with Paper / Baseline
Comparison Audit. No SLAM/evaluation rerun is needed or authorized by this
handoff.
