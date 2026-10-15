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
| P6-BAM-001 — Budget-Aware Mapping Minimal Implementation | PLANNED / NOT STARTED |
| Optional bounded GPU Keyframe Reuse | DEFERRED / CONDITIONAL |

Phase 4 is complete. The closure package is
`results/runtime_artifacts/phase4_closure/`. Camera-aligned V2 evidence remains
the primary qualitative fidelity evidence; V3A–V3C virtual views remain
diagnostic/presentation evidence and do not establish novel-view accuracy.

Recommended next research order: (1) validate unchanged PHASE4-VB-001 across
additional Replica scenes; (2) isolate pinned-memory/non-blocking/streamed
staging as a systems experiment with transfer timing; (3) evaluate a bounded
reuse-aware GPU cache; (4) investigate archive precision/compression; and only
then (5) study eviction as a separate algorithmic/keyframe-policy experiment.
The original Phase 5 plan remains administratively superseded and technically incomplete. P5-LEAN-001 completed design readiness for a novelty-aware mapping-budget hypothesis under a 15 October–5 November schedule. P6-BAM-001 is next but not started; bounded keyframe reuse remains conditional.

Gate evidence: [runtime index](../baseline_reproduction/runtime/README.md),
[full-scene output-save result](../experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md),
[evaluation result](../experiments/PHASE4_VB001_EVALUATION_RESULT.md),
[qualitative export result](../experiments/PHASE4_VB001_QUALITATIVE_EXPORT_RESULT.md),
[Phase 4 closure](../../results/runtime_artifacts/phase4_closure/PHASE4_CLOSURE_REPORT.md),
and Git-ignored runtime evidence under `results/runtime_artifacts/`.
