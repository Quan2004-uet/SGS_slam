# Research Decision Log

> **DURABLE DECISION LOG.** Record accepted research/project-management
> decisions here. This file does not define the current Phase, Session,
> `STOPPED HERE`, or `NEXT TASK`; those belong to `PROJECT_STATUS.md` and
> `SESSION_HANDOFF.md`.

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

## DEC-002 — Canonicalize project-state authority

Date: 2026-10-05\
Session: SESSION_002 (remains PAUSED)\
Status: ACCEPTED

### Context

Both `project_management/` and `docs/project_state/` described themselves as
the current authority. Their research phase values were compatible, but their
authority declarations and immediate next-task wording conflicted.

### Decision

Use this precedence:

1. Repository/source/config/runtime evidence.
2. `project_management/PROJECT_STATUS.md`.
3. `project_management/SESSION_HANDOFF.md`.
4. `project_management/sessions/SESSION_NNN.md`.
5. `project_management/DECISIONS.md` and `CHANGELOG.md`.
6. `docs/project_state/` historical, migration, roadmap, or derived records.

`docs/project_state/state.yaml` may remain as a derived machine-readable
snapshot but cannot override the canonical human-readable state. The roadmap
does not decide the current Session or immediate task.

### Consequences

Startup reads the canonical project-management files after Git inspection.
Shutdown updates the current Session, then project status, and writes the
operational handoff last. Historical reports and legacy snapshots remain
unchanged except for explicit authority notes.

### Evidence

- Phase 3C-3 JSON/log under `results/runtime_artifacts/phase3c3/`.
- `docs/baseline_reproduction/runtime/13_bounded_online_50_frames.md`.
- Git state at documentation HEAD `63943487478cd876339e8ec1660e91bab1215fab`.

## DEC-010 — Evaluate PHASE4-VB-001 from saved full-scene state

- Date: 2026-10-11.
- Session: SESSION_004.
- Status: ACCEPTED.

### Context

PHASE4-VB-001 completed Replica `room0` frames 0–1999 and saved a readable
final `params.npz`, Gaussian/semantic PLY exports, standalone keyframe indices,
and timing/memory telemetry. Save success, artifact completeness, and telemetry
completeness all passed. No evaluation has run.

### Decision

Use the saved full-scene state at
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/`
for the next Evaluation / Export Audit. Do not rerun online SLAM if saved-state
loading succeeds. Audit evaluator loading, rendering, metric definitions,
sampling, GT alignment, trajectory alignment, semantic labels, and output
paths before separately authorizing metric execution.

Keep PHASE4-VB002 as a future optimization track. Do not introduce it into the
PHASE4-VB-001 evaluation baseline.

### Rationale

The output-saving result is complete and checksummed, so another online run
would spend substantial compute without adding required state. Separating the
read-only evaluation audit from execution preserves metric attribution and
prevents accidental use of the wrong online/post-opt or paper protocol.

### Consequences

- Evaluation, ATE, PSNR, SSIM, LPIPS, DepthL1, mIoU, rendering metrics,
  semantic metrics, and paper metrics remain `NOT RUN` until separately
  authorized.
- Runtime binary artifacts remain Git-ignored on the server; documentation
  records their paths, sizes, hashes, and provenance.
- The historical validator-bug run remains authoritative for detailed
  residency invariants; the minimal output-save run does not claim detailed
  residency telemetry it did not collect.

### Evidence

- `docs/experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md`.
- `results/runtime_artifacts/phase4_vb001_minimal_output_save_full_0_1999/`.
- `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/`.

## Migrated durable decision index

The following accepted decisions were first summarized in the 2026-10-04
legacy migration snapshot `docs/project_state/DECISIONS.md`. They are indexed
here so that future work does not need to treat that legacy file as an active
decision authority:

- **DEC-003:** Use the runtime-verified environment at
  `/home/quan/miniconda3/envs/sgs_slam_baseline`; revalidate it on a destination
  host before runtime work.
- **DEC-004:** Retain NumPy 1.26.4 with `opencv-python` 4.9.0.80 unless explicit
  compatibility evidence requires a change.
- **DEC-005:** Use the recovered maintainer-distributed Replica package.
- **DEC-006:** Use continuous bounded prefixes before full `room0`; choose each
  later horizon from measured evidence.
- **DEC-007:** Preserve runtime JSON/logs outside `/tmp`.
- **DEC-008:** Fast instrumentation may reduce logging overhead but must preserve
  algorithmic settings.
- **DEC-009:** Do not optimize memory, optimizer behavior, or keyframes during
  baseline reproduction.

These decisions constrain work but do not themselves define the current task.
