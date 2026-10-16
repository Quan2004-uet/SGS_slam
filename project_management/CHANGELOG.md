# Research Changelog

## 2026-10-16 — SESSION_018 addendum / P6-BAM-006 performance and artifact coverage

- Appended a dated follow-up to the P6-BAM-006 CPU/static report documenting the existing online `perf_counter` scope and FPS derivation, `/usr/bin/time` process throughput/RSS, LIGHT mapping/tracking and allocator/archive/H2D/budget telemetry, and sampled Gaussian/memory trends.
- Mapped which existing stages produce the recovery/final checkpoints, RGB and semantic-color PLYs, per-frame/aggregate evaluation products, 3D map visualizations, and SHA256 inventory. Confirmed the saved checkpoint retains semantic IDs/colors and source/dataset provenance; categorical-ID PLY export remains not implemented.
- Re-ran 45 CPU-only preparation, mapping-budget, and profiler tests successfully. No source/config/profiler changes, GPU/CUDA calls, SLAM, evaluation, rendering, or PLY conversion occurred. P6-BAM-006-FULL remains unauthorized.

## 2026-10-16 — SESSION_018 / P6-BAM-006 CPU/static preflight fix

- Added an isolated V-A2 full-scene wrapper with explicit 0–1999 frame bounds,
  LIGHT profiling, 401-view E4 cadence, frame-1999 checkpointing, and parity to
  the validated P6-BAM-005 V-A2 settings except intended horizon/run changes.
- Added a full-wrapper-only finalization flag in `scripts/slam.py`: save
  complete final state and both Gaussian PLY exports, validate
  NPZ/container/schema/horizon and exports on CPU, then run the existing
  in-process evaluator. Existing configs retain their previous order. Added an
  exclusive effective config snapshot for saved-state recovery.
- Added a Phase 6-only saved-checkpoint evaluator using the unchanged metric
  helper, exact 401-frame schedule, full 2000-pose ATE mean/true RMSE, output
  validation, and fail-closed artifact paths.
- Passed 45 CPU tests plus Python compilation and diff checks. No SLAM/CUDA,
  evaluation, rendering, or PLY conversion ran. Phase 4/P6 historical artifacts
  remain untouched; the prior P6-BAM-006 preflight blocker is preserved as
  historical evidence and followed by `PASS_P6_BAM_006_PREFLIGHT_FIX_CPU_STATIC_READY`.
- Full-scene V-A2 remains pending separate researcher authorization; no run or
  push was performed.

## 2026-10-16 — SESSION_017 / P6-BAM-005 matched 0–499 V0/V-A2 validation

- Added a measurement-only monotonic host timer around the online frame loop in `scripts/slam.py`; it adds no CUDA synchronization and changes no algorithm behavior.
- Ran one matched sequential LIGHT V0/V-A2 pair on Replica room0 frames 0–499 using frozen, parity-checked effective configurations. Both completed 500 frames and were saved with final maps, poses, keyframes, telemetry, metrics, and matched RGB/depth/semantic samples.
- V0 executed 30,000 mapping iterations; V-A2 executed 22,695 (−24.35%). V-A2 online loop wall was 1,963.46 s versus 2,319.05 s (−15.33%); process wall was −15.13%. All seven researcher-defined 15% quality screens and all historical P5 provisional quality margins passed. The historical ≥20% online-wall target was not met.
- Recorded `PASS_P6_BAM_005_0_499_QUALITY_CONSTRAINED` as a bounded single-pair result only. Preserved the original P6-BAM-003 INCONCLUSIVE status and all Phase 4/P6 reference hashes. No 0–1999 run or push occurred.

## 2026-10-16 — SESSION_016 / P6-BAM-003-R1 V-A2 quality-constrained screen

- Added the isolated `configs/replica/phase6_bam_va2.py` wrapper with LOW/MID/FULL budgets 45/60/60 and frozen thresholds 0.01/0.05; no controller or algorithm source changed.
- Passed CPU/static config parity checks and all 15 mapping-budget unit tests. Ran exactly one matched LIGHT Replica room0 0–49 V-A2 execution; 50/50 frames completed with 2,445/3,000 iterations, valid budget telemetry, finite saved state, active CPU archive/H2D staging and zero dropped LIGHT spans.
- Against saved V0, all researcher-defined 15% quality checks passed; process wall improved 11.33%. Historical P5 provisional PSNR bound was narrowly exceeded and online-wall target was not measured. Classified the candidate screen `PASS_P6_BAM_003_R1_QUALITY_CONSTRAINED_0_49`; original P6-BAM-003 remains historically INCONCLUSIVE.
- Preserved Phase 4 and previous P6 hashes, with all outputs isolated below `results/runtime_artifacts/phase6_bam/`. No reruns, other horizons/variants, tuning, push, or P6-BAM-004 execution.

## 2026-10-16 — SESSION_015 / P6-BAM-003 bounded 0–49 comparison

- Froze matched V0/V-A room0 frames 0–49 LIGHT configs on documentation HEAD `bb830b1` and ran exactly one sequential GPU execution per variant in new isolated Phase 6 result/telemetry directories.
- Both completed 50 frames and 50 mapping events with finite saved state, valid CPU offload/staging, zero dropped LIGHT spans and preserved prune-iteration coverage. V0 executed 3,000 mapping iterations; V-A 1,740 (1 FULL, 14 MID, 35 LOW).
- Observed process wall 192.27 versus 143.28 s, but matched preliminary final-map evaluation showed PSNR −0.739 dB and Depth L1 +19.26% for V-A. Classified `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME` under provisional quality targets; no speedup or non-inferiority claim.
- Preserved Phase 4 and P6-BAM-002 checksums, old untracked evidence and algorithm/config/profiler source. No additional evaluator, retry, 0–99 run or push.

## 2026-10-16 — SESSION_014 / P6-BAM-002 matched LIGHT smoke

- Ran exactly one V0 and one V-A Replica room0 frames 0–10 LIGHT GPU validation under source `a3aefc7`, in separate new directories under `results/runtime_artifacts/phase6_bam/`.
- Both completed 11 frames and 11 mapping events with finite saved state and zero dropped LIGHT spans. V0 executed 660/660 configured mapping iterations; V-A executed 420/660 with 1 FULL, 4 MID and 6 LOW events. Prune iteration 20 remained reachable in all events.
- Recorded `PASS_P6_BAM_002_SMOKE_INTEGRATION` and `ADAPTIVE_ACTIVATION_CONFIRMED`. Runtime/quality/full-scene conclusions remain unvalidated. Phase 4 reference checkpoint checksum remained unchanged.
- Preserved logs, effective configs, telemetry and CPU validation under the isolated Phase 6 root; no algorithm, profiler or released config edit and no push.

## 2026-10-16 — SESSION_013 / P6-BAM-001 FIX1 lifecycle clarification

- Verified the reported 30-to-60 cross-event leak was absent in `e644df4` because the configured budget was reloaded inside the per-frame loop.
- Separated configured and effective mapping-iteration locals at each mapping event and added a source-AST six-event regression.
- Passed 38 CPU tests; recorded `PASS_P6_BAM_001_FIX1_CPU_STATIC` while retaining the original P6-BAM-001 PASS and `NOT_RUNTIME_VALIDATED` status.

## 2026-10-16 — SESSION_013 / P6-BAM-001 CPU/static implementation

- Added a CPU-only novelty-aware mapping budget selector and narrow hook around the existing mapping iteration loop, disabled by default.
- Added isolated P6 V0, V-A and fixed 30/45 configurations, host scalar budget telemetry and output-directory existence guards.
- Passed 14 new controller tests and 23 existing profiler tests with CUDA hidden; no SLAM/CUDA workload ran.
- Recorded `PASS_P6_BAM_001_CPU_STATIC` and `NOT_RUNTIME_VALIDATED`; P6-BAM-002 remains a separately authorized next gate.

## 2026-10-16 — SESSION_012 closure / P6-BAM handoff

- Closed SESSION_012 after the committed P5-LEAN-001 design checkpoint `c3a76c0`.
- Added the mandatory Phase 4 artifact-isolation contract and dedicated Phase 6 output root `results/runtime_artifacts/phase6_bam/`.
- Preserved P6-BAM-001 as `PLANNED_NOT_STARTED`; no algorithm, profiler, SLAM, or CUDA work was performed during handoff.

## 2026-10-15 — SESSION_012 / P5-LEAN-001 21-day design gate

- Audited the active mapping loop and existing Phase 4/P5 evidence without running SLAM or CUDA.
- Selected novelty-aware tiered mapping budgets as the initial hypothesis, with fixed-budget controls and a pruning-floor invariant.
- Added lean profiling/evaluation protocols, selective ablation plan, three-week schedule and P6-BAM-001 implementation contract.
- Gate result: `PASS_P5_LEAN_001_21DAY_DESIGN_READY`; no algorithm or profiler source changed.

## 2026-10-15 — SESSION_011 / P5-TRANSITION-001

- Administratively retired the original Phase 5 execution plan as `SUPERSEDED_BY_P5_LEAN_INCOMPLETE`; technical completion is not claimed.
- Preserved historical G1/G2, G3A, FIX1, R2, and Phase 4 evidence and documented unexecuted R3/G3B/multi-scene work.
- Prepared P5-LEAN-001 as planned/not started, with Budget-Aware Mapping recorded as a hypothesis rather than a validated contribution.

> Historical change record. This file does not define current Phase, Session,
> `STOPPED HERE`, or `NEXT TASK`; use `PROJECT_STATUS.md` and
> `SESSION_HANDOFF.md` for current state.

## 2026-10-15 — SESSION_008 / P5-G3A retry 1

### Runtime validation

- Reused the recovered direct-host CUDA environment and ran Replica room0 frames 0–99 under OFF, LIGHT, and DETAILED conditions with fresh retry directories.
- C0, C1, and C2 reached frame 99 without OOM or non-finite saved state. Logged keyframe traces matched; final Gaussian counts were not bit-exact.
- LIGHT telemetry closed with zero pending and zero dropped spans. DETAILED telemetry closed with zero pending but 1,958 dropped CUDA event spans.

### Gate boundary

- Gate result: `BLOCKED_P5_G3A_RETRY1`. No 0–499 run, second scene, V1–V4 implementation, push, or Phase 4 artifact modification occurred.
- Retry artifacts and compact comparisons are under `results/runtime_artifacts/phase5_profiling/p5_g3a_retry1_room0_0_99/`; the previous blocked evidence remains unchanged.

## 2026-10-15 — P5-G3A-FIX1 profiler repair

- Verified that Retry1 drops came from queue overflow between frame-boundary resolutions at `max_pending_cuda_events=512`.
- Added bounded chunked event resolution and explicit requested/sampled/accepted/resolved/pending/dropped accounting.
- CPU suite passed 23/23 without CUDA initialization. A 0.09-second synthetic RTX 5080 microtest resolved 648/648 spans with zero drops and zero pending events.
- Result: `PASS_P5_G3A_FIX1_PREFLIGHT`; no Replica or online SLAM workload was rerun. Gaussian-count reproducibility remains unresolved.

## 2026-10-15 — P5-G3A-R2 minimal precheck

- Checkpointed FIX1 as `302e3e6` with message `fix(profiler): prevent CUDA event queue overflow`.
- Ran only OFF-A and OFF-B on Replica room0 frames 0–10. Both completed with finite state and matching logged keyframe traces, but final Gaussian counts differed by 644.
- Stopped before LIGHT/DETAILED per contract. Gate result: `BLOCKED_P5_G3A_R2`; no 0–99 or 0–499 run occurred.

## 2026-10-15 — SESSION_007 / P5-G3A preflight

### Checkpoint

- Created the P5-G2 implementation checkpoint `0118d2cf99bf1fe089f34dea20696ac71101b30d` with message `perf: add phase5 profiling instrumentation`.
- Repaired only the local Phase 4 branch pointer to validated commit `37522db553ff18b96592073f9de699db7fa48600`.

### Runtime boundary

- Prepared immutable room0 frames 0–99 off/light/detailed configs.
- Blocked before C0: PyTorch reported no CUDA device and `nvidia-smi` could not communicate with the NVIDIA driver.
- No CUDA workload, online SLAM frame, 0–499 run, second scene, optimization variant, or push occurred.
- Saved preflight and blocker evidence under `results/runtime_artifacts/phase5_profiling/p5_g3a_room0_0_99/`.

## 2026-10-15 — P5-G3A CUDA environment recovery

- Confirmed the initial failure was sandbox GPU visibility plus use of `/usr/bin/python`, not a broken validated PyTorch environment.
- Direct-host `nvidia-smi` and `/home/robot/miniconda3/envs/sgs_slam_5080/bin/python` now expose the RTX 5080 with driver 580.167.08 and PyTorch `2.7.1+cu128`.
- A one-element CUDA tensor smoke test passed with `CUDA_SMOKE_PASS`.
- Recorded `PASS_P5_G3A_CUDA_ENV_RECOVERED`; no SGS-SLAM, C0/C1/C2, frame, or profiling workload was executed.

## 2026-10-15 — SESSION_006 / Phase 5 P5-G1 and P5-G2

### Documentation

- Checkpointed the nine P5-G1 research-design documents at `86ac4f990932563c721187a5cb458f3e07be9ce6` and created the isolated `phase5-profiling-instrumentation` branch.
- Added P5-G2 implementation, telemetry-schema, CPU-test, and P5-G3-readiness reports.

### Instrumentation

- Added disabled-by-default `off`, `light`, and `detailed` profiling with bounded structured telemetry and minimal hooks around the unchanged online SGS-SLAM execution path.
- Added CPU/GPU timing categories, archive/staging counters, Gaussian/optimizer/storage attribution, PyTorch allocator metrics, and process RSS/HWM sampling. CUDA-specific measurements remain pending bounded runtime validation.

### Validation

- Passed 20 CPU-only tests with CUDA hidden and uninitialized, plus Python compilation and static diff checks.
- No CUDA workload, online SLAM, experiment, optimization variant, released config/hyperparameter change, Phase 4 artifact mutation, P5-G2 implementation commit, or push occurred.

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
