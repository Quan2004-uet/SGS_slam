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

## DEC-011 — Treat E4 as released-code room0 evaluation, not paper reproduction

- Date: 2026-10-11.
- Session: SESSION_004.
- Status: ACCEPTED.

### Context

The saved PHASE4-VB-001 state passed load, render, bounded-metric, and full
released evaluation gates. E4 produced 401-frame RGB/depth/semantic metrics and
2,000-frame trajectory results. The audit also established that released
labels and formulas do not always match conventional or paper terminology.

### Decision

Record E4 as `PASS_EVAL_E4_FULL_RELEASED` for Replica `room0`. Preserve the
released PSNR, MS-SSIM, LPIPS, Depth L1, semantic-color mIoU, and Horn-aligned
mean translation error exactly as audited. Keep the separately calculated true
trajectory RMSE labeled supplementary.

Do not claim full paper reproduction, superiority, cross-scene generalization,
or benchmark-wide contribution. Make the next task a Paper / Baseline
Comparison Audit. Keep PHASE4-VB002 as a later optimization track.

### Consequences

- No further output-save or E1--E4 rerun is required for this checkpoint.
- Future comparisons must disclose the 401-frame released sampling and metric
  definitions, especially MS-SSIM and the non-RMSE released trajectory mean.
- Additional scenes or paper-table claims require separately scoped evidence.

### Evidence

- `docs/experiments/PHASE4_VB001_EVALUATION_EXPORT_AUDIT.md`.
- `docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md`.
- `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/`.

## DEC-012 — Separate camera-view qualitative evidence from 3D map visualization

- Date: 2026-10-12.
- Session: SESSION_004.
- Status: ACCEPTED.

### Context

The representative qualitative gate passed for five training-camera frames and
produced rendered/GT RGB, metric depth, and semantic-color comparisons. The
saved output package also contains `params.ply` and `seg_params.ply`, but no
paper-style free-view or map-view `Scene Reconstruction | 3D Segmentation`
visualization has been produced.

### Decision

Classify the five-frame result as `PASS_QUALITATIVE_EXPORT` for camera-view
evidence only. Treat RGB reconstructed-map and semantic-colored 3D map
visualization as a distinct gate. Audit the repository-native PLY/viewer path,
camera, color, background, crop, output, and provenance conventions before
authorizing new rendering.

Make that visualization audit the immediate next task. Preserve Paper /
Baseline Comparison Audit as the subsequent research task. Do not rerun online
SLAM or E1--E4 for either task.

### Consequences

- Camera-view qualitative export is complete and should not be repeated.
- 3D reconstruction/segmentation map visualization remains `NOT RUN`.
- Existing E4 values may annotate selected frames but are not recomputed by
  qualitative export.
- Neither qualitative evidence nor E4 alone constitutes full paper
  reproduction or cross-scene validation.

### Evidence

- `docs/experiments/PHASE4_VB001_QUALITATIVE_EXPORT_RESULT.md`.
- `results/qualitative/phase4_vb001_room0_representative/`.
- `docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md`.

## DEC-013 — Use observed-camera evidence as fidelity evidence and keep 3D presentation diagnostic

- Date: 2026-10-13.
- Session: SESSION_004.
- Status: ACCEPTED.

### Context

Visualization Gate V1 established that the existing final-Ply exterior views
use deterministic matching RGB/semantic cameras but place them substantially
outside the observed trajectory. Most primitives are high-opacity, PNG
display clipping is substantial, and diagnostics do not support a widespread
giant-Gaussian scale failure. Gate V2 then packaged five observed-camera
RGB/depth/semantic comparisons without new rendering or metric computation.

The semantic state contains fixed aligned `semantic_ids` and trainable
continuous `semantic_colors`. Released per-frame recoloring uses the current
GT palette and is therefore not an independent categorical prediction.

### Decision

1. Treat V2 camera-aligned observed views as the primary qualitative fidelity
   evidence for this checkpoint.
2. Retain existing exterior overview renders as unfiltered diagnostic/reference
   evidence, not as a reconstruction-quality verdict.
3. Never label raw learned semantic colors as categorical classes or present
   GT-palette-assisted recoloring as an independent prediction.
4. Require Gate V3-A to create ID-categorical 3D semantics separately from
   aligned per-Gaussian `semantic_ids`, while preserving the raw learned-color
   view.
5. Permit filtering only as an explicitly labeled visualization-only
   diagnostic paired with an unfiltered reference and exact saved
   masks/thresholds/cameras. It cannot alter model state, evaluation, or
   scientific metrics.

### Consequences

- Free-view 3D presentation complements but does not replace E4 metrics or V2
  observed-camera evidence.
- Gate V3-A begins with a bounded proof of camera, geometry, trajectory, and
  ID-semantic visualization; it does not immediately produce a polished
  publication set.
- `params.npz`, `params.ply`, `seg_params.ply`, Gaussian parameters, and
  evaluation outputs remain immutable inputs.

### Evidence

- `results/runtime_artifacts/phase4_vb001_visualization_audit/GATE_V1_AUDIT_REPORT.md`.
- `results/runtime_artifacts/phase4_vb001_visualization_audit/gaussian_diagnostics.json`.
- `results/runtime_artifacts/phase4_vb001_visualization_audit/semantic_mapping.csv`.
- `results/runtime_artifacts/phase4_vb001_visualization_v2/GATE_V2_REPORT.md`.

## DEC-014 — Close Phase 4 as a bounded memory-management contribution

- Date: 2026-10-14.
- Session: SESSION_005.
- Status: ACCEPTED.

### Context

The unchanged Phase 3 baseline OOMed during mapping at frame 1294 on the tested RTX 5080. PHASE4-VB-001 completed Replica `room0` frames 0–1999, saved a reloadable final state, passed released E4 evaluation, and completed visualization Gates V1 through V3C. The detailed telemetry run and the independent output-save run used different instrumentation and have different runtime/memory measurements.

### Decision

1. Close Phase 4 with `PASS_PHASE4_CLOSURE` as a memory-management/systems result.
2. Attribute detailed archive residency and staging evidence to the detailed full-scene run; attribute the final checkpoint to the output-save run. Do not combine their runtime or peak-memory values as if they came from one execution.
3. State the validated contribution narrowly: CPU-authoritative archived `color`, `depth`, `semantic_id`, and `semantic_color`, synchronous pageable H2D staging, GPU-resident `est_w2c`, unchanged keyframe/optimization policy, and full `room0` completion on the tested hardware.
4. Do not claim full-scene accuracy equivalence to the baseline, benchmark-wide superiority, novel-view accuracy, or categorical per-pixel prediction from fixed semantic IDs.
5. Keep the next phase planned but not started. Treat multi-scene validation, transport optimization, caching, archive compaction, and keyframe eviction as separately gated hypotheses.

### Consequences

Phase 4 evidence is consolidated under `results/runtime_artifacts/phase4_closure/`. The V2 observed-camera package remains the principal qualitative fidelity evidence; V3 full-scene outputs remain diagnostic/presentation evidence. Future work must preserve the immutable checkpoint and explicitly isolate systems changes from algorithmic keyframe-policy changes.

### Evidence

- `docs/experiments/PHASE3_BASELINE_CLOSURE_2026-10-10.md`.
- `docs/experiments/PHASE4_VB001_FULL_SCENE_AUDIT.md`.
- `docs/experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md`.
- `docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md`.
- `results/runtime_artifacts/phase4_closure/PHASE4_CLOSURE_REPORT.md`.

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

## DEC-015 — Retire the incomplete original Phase 5 plan

- Date: 2026-10-15.
- Session: SESSION_011 / P5-TRANSITION-001.
- Status: ACCEPTED.

Administratively close the original Multi-Scene Validation & Performance Profiling plan as `SUPERSEDED_BY_P5_LEAN_INCOMPLETE`, while preserving every historical gate classification and artifact. Its technical completion remains `NOT_ACHIEVED`. The next planned scope is P5-LEAN-001; no technical PASS transfers to that scope. Phase 4 V0, P5-G1/G2, FIX1 preflight, and R2 evidence remain reusable. Budget-Aware Mapping is a priority hypothesis, not an implemented method.

## DEC-016 — Select novelty-aware mapping budget as the lean initial hypothesis

- Date: 2026-10-15.
- Session: SESSION_012 / P5-LEAN-001.
- Status: ACCEPTED FOR IMPLEMENTATION AUDIT, NOT VALIDATED.

Use the number/fraction of Gaussians appended before each mapping event to select a discrete low/mid/full iteration budget. Keep V0 at 60 iterations, require a fixed-budget control, preserve Replica pruning iteration 20, and fall back to the configured budget when disabled or invalid. Defer residual stopping because random-view losses are not directly comparable and host decisions can synchronize CUDA. Defer comprehensive DETAILED profiling; use matched LIGHT measurement for bounded validation.
