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
| Evaluation / Export Audit from saved state | NEXT |
| Online evaluation execution | Not started; requires audit and approval |
| Post-opt | Pending |
| Paper comparison | Pending |
| PHASE4-VB002 runtime optimization | Future track; not started |
| Phase 5+ — Research improvements | Pending evaluation baseline |

Immediate planning gate: audit the exact saved-state loader, renderer,
RGB/depth/trajectory/semantic metric protocols, frame sampling, GT alignment,
and output paths. Do not execute evaluation during the audit and do not rerun
online SLAM if the saved state loads successfully.

Gate evidence: [runtime index](../baseline_reproduction/runtime/README.md),
[full-scene output-save result](../experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md),
and Git-ignored runtime evidence under `results/runtime_artifacts/`.
