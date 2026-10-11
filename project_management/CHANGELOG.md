# Research Changelog

> Historical change record. This file does not define current Phase, Session,
> `STOPPED HERE`, or `NEXT TASK`; use `PROJECT_STATUS.md` and
> `SESSION_HANDOFF.md` for current state.

## 2026-10-11 — PHASE4-VB-001 full-scene output-save checkpoint

### Experiments and artifacts

- Recorded `PASS_FULL_OUTPUT_SAVE_TELEMETRY` for Replica `room0` frames
  0–1999: 2,000 frames completed, final frame 1999, 4,956,467 Gaussians, and
  402 keyframes ending `[1989, 1994, 1998, 1999]`.
- Recorded runtime 14,173.47515856901 s, tracking/mapping/overall FPS of
  0.3354664059815056 / 0.25086898791330586 / 0.14110865384985266, peak GPU
  allocated/reserved of 5,817,509,888 / 7,189,037,056 B, and process RSS/HWM
  of 17,960,493,056 B host RAM.
- Verified readable `params.npz`, `params.ply`, `seg_params.ply`, and
  `keyframe_time_indices.npy`; recorded their sizes and SHA256 values in the
  dedicated result document. Runtime binaries/logs remain Git-ignored.

### Project state

- Marked PHASE4-VB-001 validation and full-scene state preservation complete.
- Set the next task to Evaluation / Export Audit from saved state, not another
  online SLAM run.
- Kept evaluation and paper metrics `NOT RUN` / `NOT REPRODUCED YET`.
- Kept PHASE4-VB002 as future work; no algorithm/config change was made.

## 2026-10-11 — PHASE4-VB-001 full-scene audit checkpoint

### Runtime evidence reconciliation

- Recorded that PHASE4-VB-001 completed online Replica `room0` frames 0–1999
  with no OOM and met its measured memory objective.
- Preserved the original harness `FAIL_RUNTIME` evidence while recording the
  corrected audit classification `PASS_RUNTIME_VALIDATOR_BUG`. The validator
  omitted the released terminal `time_idx == num_frames-2` keyframe; expected
  and observed final keyframe counts are both 402.
- Recorded peak GPU allocated/reserved of 6,774,482,432 / 8,009,023,488 B,
  final CPU archive of 10,497,024,000 B, and GPU archived payload of 0 B.

### Output and handoff

- Recorded that no final `params.npz`, map/checkpoint, reloadable camera
  trajectory, keyframe-index `.npy`, PLY, or evaluation output was saved
  because the harness stopped before the released final `save_params(...)`
  path.
- Set the next-session workflow to read-only dry-run inspection, then one
  bounded output-save smoke test for frames 0–49, followed by smoke-artifact
  review and an explicit approval stop.
- Full-scene output-saving 0–1999 and all evaluation/metric work remain
  unauthorized until their respective gates. No source/config/algorithm
  change, experiment, evaluation, commit, or push occurred in this checkpoint.

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
