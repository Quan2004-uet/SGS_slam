# Research Changelog

## 2026-10-27 (Asia/Tokyo) — SESSION_005 Gate 3 preparation

- Prepared one guarded Gate 3 BCGM-on run for Replica `room0`, frames 0–1999;
  only the run identity and frame range differ from Gate 2. Execution remains
  `NOT_STARTED`.
- Added a Gate 3-only NVML CSV parser fix and CPU regression coverage. The
  preserved Gate 2 CSV recovers 2,334 samples and a 4,877 MiB sampled peak.
- Added CPU-only Global Cap boundary/admission tests; the CPU suite passed
  20 tests. No CUDA/SLAM workload was started.
- Audited reusable Phase 4 full-scene evidence and documented its validator,
  checkpoint, timing-scope, and metric limitations. No Phase 4 rerun planned.
- Software/data/storage/RAM checks passed at observation; current Codex GPU
  visibility remains `CODEX_GPU_NOT_VERIFIED`. Gate 3 preparation is
  `PARTIAL_GATE3_PREFLIGHT_READY`; direct-host preflight is pending.

## 2026-10-27 (Asia/Tokyo) — SESSION_005 Gate 2 evidence closure

- Validated saved BCGM-on Replica `room0` frames 0–499 evidence: exit 0,
  COMPLETE, 500 poses, 499 insertion transitions, checkpoint CRC and numeric
  integrity, and six finite 101-view metric arrays.
- Verified 1,562,329 valid candidates, 1,478,249 admitted, 84,080 rejected,
  41 Event Cap activations, and zero Global Cap activations.
- Recovered 2,334 valid NVML samples and a 4,877 MiB device-wide sampled peak
  from the original CSV. Documented the verified four-column/three-column
  aggregation mismatch and preserved the original summary and CSV.
- Added Gate 2 final validation, metric comparison, NVML recovery, and evidence
  manifest records. Historical Phase 4 Gate 4 remains contextual only; no
  matched speedup, quality retention, or NVML improvement is claimed.
- Gate 2: `PASS_GATE2_WITH_COMPARISON_LIMITATIONS`; Gate 3: `NOT_STARTED`.
  `SESSION_005` remains ACTIVE. No SLAM/CUDA rerun, algorithm/config/source
  change, checkpoint deletion, commit, push, or upload occurred in this
  evidence-closure task.

## 2026-10-27 (Asia/Tokyo) — SESSION_005 initialized; Gate 2 readiness

- Created the Phase 7 `SESSION_005` ACTIVE record from the Gate 1B handoff.
- Reverified all 322 Gate 1B manifest entries against their hashes and byte
  sizes; no Gate 1B artifact was changed.
- Recorded current storage (28 GiB free) and unresolved GPU readiness
  (`nvidia-smi` could not communicate with the driver).
- Added the Gate 2 500-frame, three-arm readiness plan and metric/timing
  limitations. Gate 2 remains `NOT_STARTED`.
- No source, scientific config, CUDA workload, commit, or push was changed or
  performed by this session initialization.

## 2026-10-27 (Asia/Tokyo) — Phase 7 Gate 1B evidence closure and handoff

- Recorded the bounded three-arm Replica `room0` frames 0–99 result as
  `PASS_WITH_LIMITATIONS`; all arms exited normally with 100 saved poses and
  99 insertion events.
- Preserved the 7/7 BCGM-on admission checks and the saved metric comparison.
- Documented limitations: no global-cap activation, full-scene claim,
  statistically proven speedup, conventional Depth RMSE, or true ATE RMSE.
- Gate 2 remains `NOT_STARTED`; the next design target is `room0` frames 0–499.
- No active Phase 7 session ID could be verified. No session ledger was
  created or closed. The branch-local handoff is
  `docs/research/phase7/PHASE7_GATE1B_SESSION_HANDOFF.md`.
- Closure changed documentation only. No source, config, runner, worker,
  dataset, checkpoint, or experiment artifact was changed; no commit/push or
  Phase 7 publication occurred.


> Historical change record. This file does not define current Phase, Session,
> `STOPPED HERE`, or `NEXT TASK`; use `PROJECT_STATUS.md` and
> `SESSION_HANDOFF.md` for current state.

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


## 2026-10-27 (Asia/Tokyo) — SESSION_005 Gate 4 evidence closure

- Closed the administrative evidence review for Gate 3; Phase 7 is `RESEARCH_COMPLETED_WITH_LIMITATIONS`, Gate 3 `COMPLETE_WITH_LIMITATIONS`, Gate 4 `FINAL_EVIDENCE_CLOSURE_COMPLETE`. SESSION_005 remains ACTIVE for researcher review.
- Added thesis-ready aggregate metric table, BCGM contribution/limitations analysis, final closure/handoff, and SHA256 manifest. Revalidated run completion, checkpoint CRC/hash, all 1,999 BCGM admission records, six 401-entry evaluator arrays, offline ATE, NVML CSV, and advanced visualization inventory.
- Preserved the contextual-only Phase 4 comparison and lack of a matched Phase 6 quantitative room0 baseline; recorded missing standalone Gate 0 report and user-reported laptop transfer without claiming independent remote hashes.
- No scientific source/config, experiment artifacts, checkpoint, dataset or Phase 4/6 evidence changed. No SLAM/CUDA/rendering, commit, push or upload.


## 2026-10-27 (Asia/Tokyo) — SESSION_006 R1 room1 fast-track preparation

- Audited room1 dataset and Phase 4/6 full-scene evidence; prepared one BCGM-on 0–1999 config, guarded full-scene runner, CPU-only offline ATE tool, and R1 reports. No short-run arms or advanced visualization.
- R1 Gate 0 is `HOST_EXECUTION_REQUIRED`: Codex cannot currently query the NVIDIA driver; direct-host GPU/process/CUDA readiness remains unverified. No SLAM run started.
- SESSION_005 remains ACTIVE; separate SESSION_006 is ACTIVE. No room0/Phase4/Phase6 artifacts were modified.


## 2026-10-28 (Asia/Tokyo) — SESSION_006 R1 room1 quantitative closure

- Verified full-scene completion, checkpoint/PLY, six 401-value metric arrays, 2,000-pose offline ATE, NVML CSV, and all 1,999 BCGM admission records.
- Created room1 final quantitative reports and supplemental integrity manifest for offline ATE files omitted from the immutable run manifest.
- Updated R1 current status/roadmap/handoff: Gate 0 PASS, Gate 1 COMPLETE, Gate 2 PASS_WITH_LIMITATIONS. SESSION_006 and separate SESSION_005 remain ACTIVE.
- No experiment rerun, CUDA, rendering, scientific source/config modification, artifact rewrite/deletion, commit, push, or upload.


## 2026-10-28 (Asia/Tokyo) — Phase 7 final state sync and SESSION_006 closure

- Independently revalidated room0 and room1 run summaries, checkpoint SHA256/ZIP CRC, metric-array means and original evidence manifests. Room0 Gate 4 manifest: 209/209 entries; room1 runtime manifest: 1,629/1,629; room1 supplemental offline ATE manifest: 3/3.
- Synchronized current project status, operational handoff and roadmap. Phase 7 quantitative research is `COMPLETE_WITH_LIMITATIONS`; room0 remains `RESEARCH_COMPLETED_WITH_LIMITATIONS`; room1 remains `PASS_WITH_LIMITATIONS`.
- Closed `SESSION_006` on 2026-10-28 (Asia/Tokyo) after verifying its room1 workstream ownership and evidence. `SESSION_005` remains ACTIVE and unchanged for room0.
- Added consolidated `docs/research/phase7/PHASE7_FINAL_PROJECT_STATE_AND_HANDOFF.md`; room1 final handoff now reflects session closure. Room1 advanced visualization A–H remains deferred by research decision.
- No experiment, CUDA workload, rendering, source/config or original artifact mutation, Git commit/push, or Hugging Face upload. Local closure status: `LOCAL_SESSION_CLOSED_PUBLICATION_PENDING`.


## 2026-10-28 (Asia/Tokyo) — SESSION_007 post-implementation audit started

- Started P7-POST-01 selective Git archival and artifact preservation, to be followed by P7-POST-02 technical/trade-off audit.
- Preserved room0 and room1 scientific outcomes and original artifacts; no experiment, source/config modification, rendering, deletion or upload is in scope.
- `SESSION_005` remains ACTIVE and `SESSION_006` remains CLOSED. The remote target branch is absent; publication status remains pending staged-file/security review.
