# Research Changelog

> Historical change record. This file does not define current Phase, Session,
> `STOPPED HERE`, or `NEXT TASK`; use `PROJECT_STATUS.md` and
> `SESSION_HANDOFF.md` for current state.

## 2026-10-14 — Phase 4 closure

### Evidence consolidation

- Closed Phase 4 and PHASE4-VB-001 with `PASS_PHASE4_CLOSURE` after locating the authoritative Phase 3 baseline, variant gates, full-scene telemetry, saved state, E4 metrics, and visualization V1–V3C evidence.
- Preserved the distinction between the detailed full-scene telemetry run and the independent output-save run; no values were merged across those executions without attribution.
- Created `results/runtime_artifacts/phase4_closure/` with the closure report, evidence index, final metrics, baseline/variant comparison, limitations, next-phase recommendations, hashes, validation metadata, and checksums.
- Verified the final checkpoint, PLYs, visualization manifests/metadata, and evaluation JSON by SHA256 before and after documentation work.

### State and scope

- Reconciled canonical project status and handoff, created `SESSION_005`, recorded durable decision DEC-014, and updated the derived state and roadmap.
- Marked visualization Gates V1, V2, V3A, V3B, and V3C complete.
- Kept the next phase planned and not started. No SLAM/evaluation run, metric recomputation, source/config change, checkpoint mutation, commit, push, or tag occurred.

## 2026-10-13 — PHASE4-VB-001 visualization V1/V2 checkpoint

### Visualization evidence

- Recorded `PASS_V1_VISUALIZATION_AUDIT` for the final saved-state RGB/raw
  semantic 3D visualization pipeline, Gaussian diagnostics, camera analysis,
  and verified 29-ID semantic mapping.
- Recorded that current exterior cameras lie substantially outside the
  observed trajectory, most Gaussians are high-opacity, and PNG clipping plus
  dense overlap contribute to poor interpretability. Diagnostics did not
  support a widespread giant-scale failure.
- Recorded `PASS_V2_CAMERA_ALIGNED_QUALITATIVE` for five complete packages at
  frames `[0,499,999,1499,1999]`, common-scale metric-depth comparison,
  scientifically labeled semantic panels, four presentation summaries, and a
  verified 29-class legend.
- Preserved the semantic distinction between continuous learned colors,
  GT-palette-assisted evaluation recoloring, and categorical semantic IDs.
- Verified authoritative checkpoint/PLY hashes remained unchanged. V2
  packaging used CPU only and performed no SLAM, renderer invocation, metric
  computation, algorithm/config change, or checkpoint mutation.

### Documentation and handoff

- Reconciled SESSION_004, canonical project status, operational handoff,
  derived state, roadmap, changelog, and durable decisions with completed V1
  and V2 evidence.
- Set the exact next task to `PHASE4-VIS-GATE-V3-A — Bounded Full-Scene 3D
  Visualization Proof`.
- Required V3-A to retain unfiltered reference views, use aligned-ID
  categorical semantics separately, preserve V2 as primary fidelity evidence,
  and keep any filtering visualization-only and reproducible.
- No Gate V3-A work, SLAM/evaluation rerun, commit, push, or upload occurred in
  this checkpoint.

## 2026-10-12 — PHASE4-VB-001 qualitative export checkpoint

### Qualitative evidence

- Recorded `PASS_QUALITATIVE_EXPORT` for representative Replica `room0`
  training-camera frames `[0,499,999,1499,1999]`.
- Recorded validated rendered/GT RGB, raw and visualized metric depth,
  raw/recolored rendered semantic color, GT semantic color, side-by-side
  comparisons, per-frame grids, and the five-frame contact sheet.
- Preserved existing E4 per-frame values as annotations without recomputing
  metrics.
- Recorded 9.213427657989087 s export runtime and peak GPU
  allocated/reserved of 1,774,468,608 / 1,935,671,296 B.
- Runtime images, NPY files, manifest, and checksums remain Git-ignored in
  `results/qualitative/phase4_vb001_room0_representative/`.

### Documentation and handoff

- Added the dedicated qualitative result and reconciled SESSION_004,
  project status, derived state, roadmap, evaluation docs, and handoff.
- Distinguished completed camera-view qualitative evidence from the not-yet-run
  paper-style RGB/semantic 3D map visualization.
- Set the immediate next task to Scene Reconstruction / 3D Segmentation
  Visualization Audit; retained Paper / Baseline Comparison Audit as the
  subsequent task.
- No SLAM/evaluation rerun, metric recomputation, additional rendering,
  source/config change, artifact upload, or Git LFS change was part of this
  documentation checkpoint.

## 2026-10-11 — PHASE4-VB-001 full released evaluation checkpoint

### Evaluation

- Recorded E1/E2/E3/E4 PASS chain ending in
  `PASS_EVAL_E4_FULL_RELEASED` without rerunning online SLAM.
- Evaluated exactly 401 released image/depth/semantic frames and all 2,000
  finite trajectory frames; no sampled frame was skipped.
- Recorded PSNR 33.313067, MS-SSIM 0.979470, LPIPS 0.067555, Depth L1
  0.00495158 m, semantic-color mIoU 0.916585, released Horn-aligned mean w2c
  translation error 0.00274075 m, and supplementary true RMSE 0.00339827 m.
- Recorded 74.4107 s evaluation runtime and peak GPU allocated/reserved of
  1,846,789,120 / 2,057,306,112 B. No image export, OOM, or non-finite metric
  occurred.

### Documentation and handoff

- Added the dedicated evaluation result and updated the audit with staged gate
  outcomes.
- Closed SESSION_004 at the E4 checkpoint and set the next task to Paper /
  Baseline Comparison Audit.
- Preserved the distinction between released-code results, the supplementary
  true trajectory RMSE, and unverified paper-table comparability.
- No source/config/algorithm change, new metric computation, or artifact
  upload was part of this documentation checkpoint.

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
