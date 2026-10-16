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
| P6-BAM-004 — 0–99 fixed-budget ablation | PLANNED / NOT STARTED; requires quality review and separate authorization |
| Optional bounded GPU Keyframe Reuse | DEFERRED / CONDITIONAL |

Phase 4 is complete. The closure package is
`results/runtime_artifacts/phase4_closure/`. Camera-aligned V2 evidence remains
the primary qualitative fidelity evidence; V3A–V3C virtual views remain
diagnostic/presentation evidence and do not establish novel-view accuracy.

Recommended next action: researcher review of the P6-BAM-005 0–499 matched V0/V-A2 result before any 0–1999 full-scene validation. The bounded pair shows 15.33% lower online-loop wall and passes all seven researcher-defined 15% quality checks; it misses the older ≥20% online-wall target and is not statistical evidence. The original Phase 5 plan remains administratively superseded and technically incomplete. P5-LEAN-001 design readiness, P6-BAM-001/FIX1 CPU/static, and P6-BAM-002 bounded smoke statuses remain intact. Original P6-BAM-003 remains inconclusive. The R1 V-A2 0–49 candidate screen remains a historical PASS. No subsequent run is authorized automatically. Bounded keyframe reuse remains conditional.

Gate evidence: [runtime index](../baseline_reproduction/runtime/README.md),
[full-scene output-save result](../experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md),
[evaluation result](../experiments/PHASE4_VB001_EVALUATION_RESULT.md),
[qualitative export result](../experiments/PHASE4_VB001_QUALITATIVE_EXPORT_RESULT.md),
[Phase 4 closure](../../results/runtime_artifacts/phase4_closure/PHASE4_CLOSURE_REPORT.md),
and Git-ignored runtime evidence under `results/runtime_artifacts/`.
