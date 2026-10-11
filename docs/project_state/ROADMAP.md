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
| Paper / Baseline Comparison Audit | NEXT |
| Post-opt | Pending |
| Paper comparison | Pending |
| PHASE4-VB002 runtime optimization | Future track; not started |
| Phase 5+ — Research improvements | Pending evaluation baseline |

Immediate planning gate: compare the audited released-code `room0` results
with paper/released baseline values, verify protocol and stage comparability,
prepare a baseline-versus-PHASE4-VB-001 table, and identify remaining
scenes/experiments. Do not rerun online SLAM or E1--E4 for this audit.

Gate evidence: [runtime index](../baseline_reproduction/runtime/README.md),
[full-scene output-save result](../experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md),
[evaluation result](../experiments/PHASE4_VB001_EVALUATION_RESULT.md),
and Git-ignored runtime evidence under `results/runtime_artifacts/`.
