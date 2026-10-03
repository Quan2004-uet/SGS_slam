# Research Decision Log

> Historical decision record. Current durable decisions are maintained in
> `docs/project_state/DECISIONS.md`; do not maintain two active decision logs.

## DEC-001 — Preserve the released baseline through reproduction

Date: 2026-10-03\
Session: SESSION_002\
Status: ACCEPTED

### Context

The project is still establishing runtime behavior for the released SGS-SLAM baseline. Compatibility recovery has been needed, but the bounded runs have not required algorithm or experiment-config changes.

### Decision

Keep the released source, algorithm, and experiment config unchanged while completing baseline recovery and bounded reproduction. Record environment compatibility changes separately with evidence. Propose research modifications only after the baseline gate or in a separately authorized research session.

### Rationale

This preserves attribution between upstream behavior, compatibility recovery, and later research changes, and follows the baseline-preservation policy in `AGENTS.md`.

### Alternatives Considered

- Modify algorithm/config during reproduction to address observed behavior: deferred until a failure is classified and baseline reproduction is complete.
- Treat paper-described components absent from the active source path as part of the released runtime: rejected without source evidence.

### Consequences

Bounded reproduction keeps the active source/config fixed. Paper/source differences and runtime unknowns remain explicitly documented.

### Evidence

- `AGENTS.md`, “Baseline Preservation” and “Paper vs Released Source”.
- `docs/baseline_reproduction/runtime/09_opencv_numpy_recovery.md`.
- `docs/baseline_reproduction/runtime/10_first_frame_gaussian_initialization.md`.
- `docs/baseline_reproduction/runtime/11_bounded_online_2_5_frames.md` through `13_bounded_online_50_frames.md`.

### Supersedes

None.
