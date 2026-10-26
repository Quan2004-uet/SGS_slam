# Research Roadmap

> **Planning document.** This file records the phase/gate sequence and a dated
> planning snapshot. It does not determine the current Phase, active Session,
> `STOPPED HERE`, or immediate `NEXT TASK`. Use
> `project_management/PROJECT_STATUS.md` and
> `project_management/SESSION_HANDOFF.md` for those values.

| Gate | Status |
|---|---|
| Phase 1 — Research Documentation | PASS |
| Phase 2 — Baseline Reproduction Audit | PASS |
| Phase 3A — Environment and renderer recovery | PASS |
| Phase 3B — Dataset and first-frame initialization | PASS |
| Phase 3C-1 — Continuous frames 0–4 | PASS |
| Phase 3C-2 — Continuous frames 0–19 | PASS |
| Phase 3C-3 — Continuous frames 0–49 | PASS |
| Phase 3C-4 — Continuous frames 0–99 | PASS |
| Phase 3C-6 — Continuous frames 0–499 | PASS |
| Phase 3 baseline full Replica `room0` | CLOSED — OOM limitation documented |
| PHASE4-VB-001 bounded validation through 0–999 | PASS |
| PHASE4-VB-001 full-scene runtime audit | `PASS_RUNTIME_VALIDATOR_BUG` |
| PHASE4-VB-001 output-save smoke gates | PASS |
| PHASE4-VB-001 full-scene output save 0–1999 | `PASS_FULL_OUTPUT_SAVE_TELEMETRY` |
| Evaluation / Export Audit from saved state | PASS |
| E1 saved-state load-only | `PASS_EVAL_E1_LOAD_ONLY` |
| E2 single-frame render | `PASS_EVAL_E2_SINGLE_FRAME_RENDER` |
| E3 bounded released metrics | `PASS_EVAL_E3_BOUNDED_SUBSET` |
| E4 full released `room0` evaluation | `PASS_EVAL_E4_FULL_RELEASED` |
| Representative camera-view qualitative export | `PASS_QUALITATIVE_EXPORT` |
| Final RGB/raw-semantic 3D map visualization | Generated; diagnostic exterior views retained |
| PHASE4-VIS-GATE-V1 visualization audit | `PASS_V1_VISUALIZATION_AUDIT` |
| PHASE4-VIS-GATE-V2 camera-aligned qualitative packaging | `PASS_V2_CAMERA_ALIGNED_QUALITATIVE` |
| PHASE4-VIS-GATE-V3A full-scene 3D visualization proof | `PASS_V3A_FULL_SCENE_VISUALIZATION_PROOF` |
| PHASE4-VIS-GATE-V3B final presentation package | `PASS_V3B_FINAL_PRESENTATION_PACKAGE` |
| PHASE4-VIS-GATE-V3C presentation refinement | `PASS_V3C_PRESENTATION_REFINEMENT` |
| Phase 4 final synthesis and closure | `PASS_PHASE4_CLOSURE` |
| Controlled multi-scene validation | PLANNED / NOT STARTED |
| CPU-offload transport optimization | PLANNED / NOT STARTED |
| Post-opt | Pending |
| Paper comparison | Pending |
| Original Phase 5 — Multi-Scene Validation & Performance Profiling | `SUPERSEDED_BY_P5_LEAN_INCOMPLETE` — technical completion not achieved |
| P5-LEAN-001 — 21-Day Research Replan & Budget-Aware Mapping Feasibility Audit | `PASS_P5_LEAN_001_21DAY_DESIGN_READY` |
| P6-BAM-001 — Budget-Aware Mapping Minimal Implementation | `PASS_P6_BAM_001_CPU_STATIC` and FIX1 CPU/static PASS |
| P6-BAM-002 — Matched LIGHT 0–10 Smoke Validation | `PASS_P6_BAM_002_SMOKE_INTEGRATION`; `ADAPTIVE_ACTIVATION_CONFIRMED` |
| P6-BAM-003 — Matched LIGHT 0–49 Validation | `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME`; structural PASS, preliminary PSNR/Depth L1 concern |
| P6-BAM-003-R1 — V-A2 quality-constrained 0–49 screen | `PASS_P6_BAM_003_R1_QUALITY_CONSTRAINED_0_49`; 15% screens pass vs V0, historical PSNR provisional margin narrowly missed; screening only |
| P6-BAM-005 — matched V0/V-A2 0–499 quality-constrained validation | `PASS_P6_BAM_005_0_499_QUALITY_CONSTRAINED`; 500-frame single-pair screen, online wall −15.33%, all seven 15% checks pass; ≥20% historical online-wall target missed |
| P6-BAM-006 — authorized V-A2 full-scene 0–1999 execution/evaluation | `PASS_P6_BAM_006_FULL_SCENE_QUALITY_CONSTRAINED`; 2,000 frames, 401 E4 views, all seven 15% checks pass vs stored Phase 4; original, V1-matched, and extended V2/V3A camera-family 3D visualization packages pass; matched full-scene runtime speedup unverified |
| P6-BAM-004 — 0–99 fixed-budget ablation | PLANNED / NOT STARTED; requires quality review and separate authorization |
| Optional bounded GPU Keyframe Reuse | DEFERRED / CONDITIONAL |

Phase 4 is complete. The closure package is
`results/runtime_artifacts/phase4_closure/`. Camera-aligned V2 evidence remains
the primary qualitative fidelity evidence; V3A–V3C virtual views remain
diagnostic/presentation evidence and do not establish novel-view accuracy.

Recommended next research action after SESSION_020 publication/closure: package the Phase 4 versus Phase 6 qualitative comparison and prepare thesis/report materials. P6-BAM-006 completed one V-A2 0–1999 run and passes the seven 15% screens against stored Phase 4 E4 metrics; this is single-run quality screening, not statistical non-inferiority. Matched full-scene runtime speedup remains unverified because no full-scene V0 was run and historical Phase 4 process timing is not comparable to the new online-loop timer. The controller selected LOW/45 for 1,987/2,000 events; no advantage over fixed-45 has been established. The original Phase 5 plan remains administratively superseded and technically incomplete; original P6-BAM-003 remains inconclusive. No additional run is authorized automatically.

Gate evidence: [runtime index](../baseline_reproduction/runtime/README.md),
[full-scene output-save result](../experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md),
[evaluation result](../experiments/PHASE4_VB001_EVALUATION_RESULT.md),
[qualitative export result](../experiments/PHASE4_VB001_QUALITATIVE_EXPORT_RESULT.md),
[Phase 4 closure](../../results/runtime_artifacts/phase4_closure/PHASE4_CLOSURE_REPORT.md),
and Git-ignored runtime evidence under `results/runtime_artifacts/`.

## Local Phase 6 room1 reconciliation — 2026-10-19

- Phase 6 V-A2 Replica/room1 full-scene run `p6_bam_ms_room1_gate3_0_1999_r01` (frames 0–1999; frozen source `002927f3b24dd69418c17da08bd4ae987bae9ee2`) has Gate 4 PASS and Gate 5 PASS. Overall: `ROOM1_GATE5_CLOSED_QUALIFIED`. The detailed metrics, memory/runtime qualifications, and local evidence locations are recorded in `docs/experiments/PHASE6_MULTISCENE_ROOM1_GATE5_FINAL_REPORT.md`.
- Model, evidence, telemetry, and Gate 5 results remain on the GPU server. Gate 4 hashes are 7/7, its artifact manifest is 1,623/1,623, Gate 5 hashes are 1,614/1,614, and source hashes are 17/17. GitHub publication and Hugging Face upload are `NOT_REQUESTED`.
- Next Phase 6 experiment candidate: **Phase 6 V-A2 — Replica/room2 preparation**, `PLANNED_NOT_STARTED`. Before any execution, separately authorize a preparation gate covering dataset identity, configuration and source locks, available resources, and isolated output destinations. This planning entry does not authorize preparation automatically or authorize a room2 run. P5-LEAN remains an independent workstream; historical room0 and prior gate records above remain unchanged.

## Local Phase 4 Replica room1 closure — 2026-10-21

- Phase 4 Variant B room1 run `p4_vb001_room1_full_0_1999_r01`, frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06`, frames 0–1999: `CLOSED_EVALUATED`. Online and saved-state artifacts validate; final offline evaluation is `PASS_OFFLINE_EVALUATION` with 401 E4 views, all 2,000 poses, and supplementary standard Depth RMSE. Optional 3D visualization is `DEFERRED_OPTIONAL`.
- Detailed metric/performance values and artifact paths are in `docs/research/phase4_multiscene/PHASE4_ROOM1_FINAL_RESULTS.md`. Room0 remains a separate result. At the time of this room1 entry, the remaining scenes were room2 and office0–office4; room2 was subsequently closed below, and the eight-scene extension remains incomplete.
- This is local documentation only. Phase 6/7 results are unchanged and P5-LEAN remains the active independent research workstream. No new experiment is authorized by this entry.

## Local Phase 4 Replica room2 closure — 2026-10-21

- Phase 4 Variant B room2 run `p4_vb001_room2_full_0_1999_r01`, frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06`, frames 0–1999: `CLOSED_EVALUATED`; online exit 0 and 2,000 validated frames. Checkpoint CRC/SHA256 and all 11 manifest entries pass. Offline status is `PASS_OFFLINE_EVALUATION` with 401 E4 views, 2,000 trajectory poses, and 401 supplementary standard Depth RMSE values. E4 exit code was not retained. Optional 3D visualization is `DEFERRED_OPTIONAL`.
- See `docs/research/phase4_multiscene/PHASE4_ROOM2_FINAL_RESULTS.md` for exact metric/performance values and artifact paths. Remaining Phase 4 Replica scenes are office0–office4; the eight-scene extension is incomplete.
- Local Room2 documentation only; Phase 6/7 and P5-LEAN are unchanged. No experiment is authorized by this entry.

## Local Phase 4 Replica office0 closure — 2026-10-22

- Phase 4 Variant B Office0 run `p4_vb001_office0_full_0_1999_r01`, frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06`, frames 0–1999: `CLOSED_EVALUATED`. Online exit 0; checkpoint validation/CRC PASS; offline `PASS_OFFLINE_EVALUATION`; final integrity `PASS_FINAL_INTEGRITY_VALIDATION`. Evidence covers 401 E4 views, 2,000 trajectory poses, 401 supplementary standard Depth RMSE values and 1,612/1,612 original E4 manifest files unchanged. E4 exit code was not retained. Optional 3D visualization is `DEFERRED_OPTIONAL`.
- See `docs/research/phase4_multiscene/PHASE4_OFFICE0_FINAL_RESULTS.md` for metrics and artifact paths. Remaining Phase 4 scenes are office1–office4; the eight-scene extension is incomplete. This local record does not alter Phase 6/7 or P5-LEAN and authorizes no new run.

## Local Phase 4 Replica office1 closure — 2026-10-22

- Phase 4 Variant B Office1 run `p4_vb001_office1_full_0_1999_r01`, frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06`, frames 0–1999: `CLOSED_EVALUATED`. Online status is `CORE_ARTIFACTS_VALIDATED` (exit 0, 2,000/2,000); checkpoint validation/CRC PASS; offline `PASS_OFFLINE_EVALUATION`; final integrity `PASS_FINAL_INTEGRITY_VALIDATION`. Evidence covers 401 E4 views, 2,000 trajectory poses, 401 supplementary standard Depth RMSE values, and 1,612/1,612 original E4 manifest files unchanged. Optional 3D visualization is `DEFERRED_OPTIONAL`.
- See `docs/research/phase4_multiscene/PHASE4_OFFICE1_FINAL_RESULTS.md` for exact metrics and artifact paths. Remaining scenes are office2–office4; the multiscene campaign remains incomplete. No Phase 5/6/7 state changed and no new scene is authorized by this closure record.

## Local Phase 4 Replica office2 closure — 2026-10-22

- Phase 4 Variant B Office2 run `p4_vb001_office2_full_0_1999_r01`, frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06`, frames 0–1999: `CLOSED_EVALUATED`. Online, checkpoint/CRC, offline, trajectory, supplementary depth, and final integrity evidence pass. The checkpoint SHA256 is `7508fc2a3fb6916dd6211221b75693ae868b97b3b830bb1fac9227a5e697726d`; evidence covers 401 E4 views, 2,000 poses, 401 standard Depth RMSE records and 1,612/1,612 original E4 manifest files unchanged. Optional visualization is `DEFERRED_OPTIONAL`.
- See `docs/research/phase4_multiscene/PHASE4_OFFICE2_FINAL_RESULTS.md`. Remaining Phase 4 Replica experiments are office3 and office4; the multiscene campaign is not complete. This local closure does not modify earlier scene results or Phase 5/6/7 state and does not start Office3.

## Local Phase 4 Replica office4 closure — 2026-10-22

- Phase 4 Variant B Office4 run `p4_vb001_office4_full_0_1999_r01`, frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06`, frames 0–1999: `CLOSED_EVALUATED`. Gate 5.1 independently verified the online run and checkpoint, 401 E4 metric views and image groups, all 1,612 original E4 manifest entries, 401 standard Depth RMSE records, and 2,000 Horn-aligned trajectory poses. Optional visualization is `DEFERRED_OPTIONAL`.
- See `docs/research/phase4_multiscene/PHASE4_OFFICE4_FINAL_RESULTS.md` and `PHASE4_OFFICE4_OFFLINE_EVALUATION_REPORT.md` for exact results and evidence paths. The eight-scene Replica Phase 4 inventory has no remaining scenes; the campaign record does not imply completion of Phase 5/6/7.


## Pre-Phase 7 planning state — 2026-10-27

- Phase 4 CPU Keyframe Offload: eight-scene Replica closure/evaluation records exist; optional visualization remains deferred where specified by the scene reports.
- Original Phase 5 remains `SUPERSEDED_BY_P5_LEAN_INCOMPLETE`; P5-LEAN is independently `IN PROGRESS`.
- Phase 6 BAM V-A2 room0 and room1 full-scene records and P6-BAM-007 Gate 5C closure are documented with their existing limitations.
- Phase 7 BCGM is researcher-selected as a proposed direction only: `PLANNED_NOT_IMPLEMENTED`, implementation/validation `NOT_VERIFIED`. No Phase 7 gate is claimed complete or active by this planning note.
