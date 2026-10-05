# Research Changelog

> Historical change record. This file does not define current Phase, Session,
> `STOPPED HERE`, or `NEXT TASK`; use `PROJECT_STATUS.md` and
> `SESSION_HANDOFF.md` for current state.

## 2026-10-05 — Documentation-only state reconciliation

### Documentation

- Promoted `project_management/PROJECT_STATUS.md` and
  `project_management/SESSION_HANDOFF.md` as the canonical current-state and
  operational-handoff authorities.
- Reclassified `docs/project_state/CURRENT_STATE.md` as a legacy migration
  snapshot, `state.yaml` as derived machine-readable state, and `ROADMAP.md` as
  planning context.
- Separated the destination runtime restore/validation task from the next
  research gate, Phase 3C-4. No Session status, research phase, runtime result,
  source, config, environment, or dataset changed.

## 2026-10-02 — SESSION_001

### Added

- Static repository-understanding knowledge base and baseline reproduction contract, both tied to commit `e4183986204242a8bb422624618af07780a49d26`.

### Documentation

- Recorded source/config/paper discrepancies and runtime unknowns separately; no experiment was run in this session.

## 2026-10-02 — SESSION_002

### Fixed

- Recovered an isolated baseline environment, the pinned depth renderer, author-distributed semantic Replica data, and an OpenCV/NumPy-compatible package state. The OpenCV recovery preserved NumPy 1.26.4.

### Instrumentation

- Added temporary bounded runtime harness instrumentation; later persisted Phase 3C-3 result JSON and run log under the Git-ignored `results/runtime_artifacts/phase3c3/` path.

### Experiments

- Runtime gates verified first-frame initialization and continuous online prefixes through frames 0–4, 0–19, and 0–49. No full scene or paper-metric evaluation has been recorded.

### Documentation

- Added environment, dataset, initialization, and bounded-run evidence under `docs/baseline_reproduction/runtime/`.

## 2026-10-03 — SESSION_002

### Added

- Persistent project status, session handoff, session history, changelog, and decision records to support continuation across work periods.
