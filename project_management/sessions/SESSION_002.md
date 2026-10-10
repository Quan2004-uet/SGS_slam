# SESSION_002 — Baseline Recovery and Bounded Runtime Reproduction

> **SESSION HISTORY.** This file is the permanent record of `SESSION_002` and
> preserves what was known at each dated work period. It is not the authority
> for the current immediate task. Use `../PROJECT_STATUS.md` for current project
> state and `../SESSION_HANDOFF.md` for the exact resume point. Historical task
> statements below are retained as provenance.

## Metadata

Session ID: SESSION_002\
Title: Baseline Recovery and Bounded Runtime Reproduction\
Status: READY-FOR-CLOSURE-REVIEW\
Started: 2026-10-02\
Last active: 2026-10-10\
Closed: —\
Phase: Phase 3 — Baseline Recovery & Reproduction\
Objective: recover the provenance-valid released runtime inputs and verify the online SGS-SLAM path on bounded Replica `room0` prefixes without changing its algorithm or experiment config.

The start date is reconstructed from the dated Phase 3 runtime records. This Session ID is reused across dates because the baseline-reproduction objective continues.

## Starting State

Static repository understanding and Phase 2 baseline audit were complete at commit `e4183986204242a8bb422624618af07780a49d26`. The author-linked dataset share was reported empty, the working environment and renderer were not yet runtime recovered, and no online frame execution was established.

## Session Scope

Recover and verify the environment, CUDA renderer, author-distributed semantic Replica dataset, loader, and first-frame initialization; then run increasingly long bounded prefixes of the released online pipeline. Do not conflate compatibility recovery with algorithm changes, and do not infer full-scene or paper-metric success from a prefix.

## Work Log

### 2026-10-02

- Recovered the Python 3.9/PyTorch 2.0.1/CUDA 11.8 environment and built/imported the specified depth renderer; Phase 3A runtime evidence is in `docs/baseline_reproduction/runtime/00_host_inventory.md` through `04_phase3a_status.md`.
- Recovered the author-distributed semantic Replica dataset and validated `room0`; recovered OpenCV 4.9.0.80 compatibility while preserving NumPy 1.26.4; see `08_dataset_recovery.md` and `09_opencv_numpy_recovery.md`.
- Ran the exact released frame-0 loader and initialization path, creating 815,998 initial Gaussians; see `10_first_frame_gaussian_initialization.md`.
- Completed the bounded Phase 3C-1 prefix, frames 0–4; see `11_bounded_online_2_5_frames.md`.
- Completed the bounded Phase 3C-2 prefix, frames 0–19; see `12_bounded_online_20_frames.md`.
- Completed a fresh continuous Phase 3C-3 run for frames 0–49. The index-50 guard fired before dataset loading; no evaluation or post-optimization ran. Detailed measurements and persistent evidence are in `docs/baseline_reproduction/runtime/13_bounded_online_50_frames.md` and `results/runtime_artifacts/phase3c3/`.

### 2026-10-03

- Established persistent project/session handoff files to make the current state and next bounded task recoverable without chat history.
- Session shutdown verification: HEAD remained `e4183986204242a8bb422624618af07780a49d26` on `main`; tracked source/config had no diff. The persistent Phase 3C-3 JSON still reports loaded frames 0–49 and blocked index 50. No new experiment ran. The unfinished objective remains `PAUSED`, with the original `Started` date and `Closed: —` preserved.

## Findings

### VERIFIED

- Dataset provenance, environment compatibility, renderer revision, loader behavior, and first-frame initialization are documented in the Phase 3 runtime evidence files.
- The released online runtime executed frames 0–49 with finite observed tracking/mapping losses and shape-consistent Gaussian/semantic state. Frame 50 was intercepted before loading.
- Released source/config remained unchanged for the recorded bounded runs.

### MEASURED

- The 50-frame run ended at 1,118,590 Gaussians and 11 resident keyframes. Maximum measured PyTorch allocated peak was 2,340,127,232 bytes; maximum reserved peak was 3,040,870,400 bytes on the 4,096 MiB GTX 1650 Ti.
- Runtime timings, frame-level growth, pruning, optimizer state, and memory are recorded in `13_bounded_online_50_frames.md` and the JSON evidence.

### DERIVED

- The measured prefix completed within device memory. This conclusion applies only to frames 0–49.
- Additions accelerated in frames 20–29 and declined across frames 30–49; this is descriptive prefix behavior, not a full-scene forecast.

### INFERRED

- A 100-frame guarded run is a reasonable next diagnostic horizon based on the measured frame-49 memory margin and late-prefix growth. It has not been executed.

### UNKNOWN

- Runtime stability/resource requirements after frame 49, full-scene completion, full-scene VRAM sufficiency, and paper-protocol metrics.
- Whether observed cross-run Gaussian-count differences disappear under a fully deterministic runtime; the released execution has not been established as bit-exact.

## Experiments

- Phase 3C-1: bounded online prefix frames 0–4; PASS; record: `11_bounded_online_2_5_frames.md`.
- Phase 3C-2: continuous prefix frames 0–19; PASS; record: `12_bounded_online_20_frames.md`.
- Phase 3C-3: continuous prefix frames 0–49; PASS; record and persistent raw evidence: `13_bounded_online_50_frames.md`, `results/runtime_artifacts/phase3c3/phase3c3_results.json`, and `phase3c3_bounded_online.log`.
- No full-scene run, evaluation, metric comparison, post-opt, or Phase 4 runtime verification was executed.

## Files Changed

- Compatibility and runtime findings are recorded under `docs/baseline_reproduction/runtime/`; the original released source and experiment config were not changed by the Phase 3 runs.
- This Session's persistent state is recorded in `project_management/`.
- Pre-existing untracked paths observed before this handoff update: `2402.03246v6.pdf`, `AGENTS.md`, and `docs/`. They were not staged, committed, pushed, reset, or deleted. `AGENTS.md` was updated by this task only to keep its phase status and continuity protocol aligned with current project-management state.

## Errors and Failed Attempts

- The initial README-linked Dropbox share was empty. The later author-distributed replacement source and recovery evidence are documented in `08_dataset_recovery.md`.
- OpenCV 4.11.0.80 failed `cv2.resize()` against NumPy 1.26.4; the documented compatibility recovery used OpenCV 4.9.0.80 and preserved NumPy 1.26.4. See `09_opencv_numpy_recovery.md`.
- The Phase 3C-2 documentation is a historical 20-frame report. Its then-current claims that later runtime was not performed were superseded by the separately documented Phase 3C-3 run, not silently rewritten.
- `07_phase3b_status.md` retains the original dataset-blocked snapshot; dataset recovery and loader/initialization PASS are documented later in `08_dataset_recovery.md` through `10_first_frame_gaussian_initialization.md`.

## Decisions

- Preserve the released source/config while baseline reproduction is in progress; environment compatibility recovery must remain separately documented. See `DEC-001`.
- Do not treat bounded-prefix memory success as full-scene sufficiency.

## Blockers

- None known for the next bounded 100-frame run.
- Full-scene and metric reproduction remain unknown/unstarted, not classified as a current runtime blocker.

## Session Outcome

Baseline recovery, bounded online runtime verification, and full-scene failure
characterization are complete. Phase 3 baseline runtime reproduction is closed
with a documented memory limitation. `SESSION_002` remains open only for
closure review and is **READY-FOR-CLOSURE-REVIEW**, not formally completed.

## STOPPED HERE

The destination RTX 5080 validation passed. Phase 3C-4 frames 0–99 and Phase
3C-6 frames 0–499 completed with finite observed state under the unchanged
released online path. The baseline full-scene attempt completed frames 0–1293
and OOMed in mapping at frame 1294. The allocator-opt runtime-only attempt
completed frames 0–1332 and OOMed in mapping at frame 1333. Neither reached
frame 1999. No evaluation, post-opt, paper comparison, source/config change,
commit, or push occurred.

Current conclusion: `docs/experiments/PHASE3_RUNTIME_CONCLUSION_2026-10-10.md`.

## Historical Next Research Task at the 2026-10-03 Pause

Resume this Session, then run Phase 3C-4 through frame 99 continuously from frame 0, with the same baseline config and a dataset guard that intercepts index 100 before the actual loader. Follow the command and artifact details in `project_management/SESSION_HANDOFF.md`; save separate JSON/log evidence and stop after reviewing finite state and VRAM trends.

Operational migration/restore prerequisites were documented later. They do not
change this historical research-gate record; consult the canonical handoff
before resuming.

## 2026-10-10 — Phase 3 runtime conclusion update

- Destination-host validation passed on the RTX 5080, including the pinned
  renderer, dataset index 0, first-frame initialization, and migration
  regression frames 0–4.
- Phase 3C-4 passed frames 0–99; Phase 3C-6 passed frames 0–499.
- Full-scene released baseline did not complete: OOM during mapping at frame
  1294 after frame 1293 completed.
- Runtime-only allocator attempt did not complete: OOM during mapping at frame
  1333 after frame 1332 completed.
- The allocator attempt improved the completed horizon by 39 frames but did not
  reduce reserved-memory pressure enough to complete 2,000 frames.
- No paper metrics were reproduced; evaluation, ATE, rendering metrics, and
  post-SLAM optimization were not run.
- This conclusion was prepared for researcher review; the subsequent closure
  decision is recorded in the section below.

Evidence: `docs/experiments/PHASE3_RUNTIME_CONCLUSION_2026-10-10.md` and
`docs/experiments/FULL_SCENE_MEMORY_OPTIMIZATION_LOG.md`.

## Phase 3 Runtime Closure — 2026-10-10

- Destination-host validation on the RTX 5080: PASS.
- Phase 3C-4 bounded online frames 0–99: PASS.
- Phase 3C-6 bounded online frames 0–499: PASS; this is the latest completed
  bounded gate.
- Released full-scene baseline frames 0–1999: `CUDA_OOM`; frames 0–1293
  completed, with OOM during mapping around frame 1294.
- Runtime-only allocator/low-overhead retry: `CUDA_OOM_ALLOCATOR_OPT`; frames
  0–1332 completed, with OOM during mapping around frame 1333.
- Allocator-only settings extended the completed horizon by about 39 frames but
  did not produce a full-scene PASS.
- Conclusion: Phase 3 baseline runtime reproduction is closed with a documented
  RTX 5080 16 GB memory limitation.
- No evaluation, ATE, rendering metrics, post-SLAM optimization, paper
  comparison, or paper-metric reproduction was performed.
- Recommended next phase, if authorized: Phase 4 memory-management analysis
  and explicitly non-baseline variant design; alternatively, obtain
  larger-VRAM infrastructure for an unchanged full-scene baseline run.

Closure record:
`docs/experiments/PHASE3_BASELINE_CLOSURE_2026-10-10.md`.

## DO NOT

- Do not call the 0–49 run a full-scene reproduction.
- Do not run a full scene or metrics until explicitly selected as the next gate.
- Do not change the released source/config or enable paper-described components absent from the active path during baseline reproduction.
- Do not start Phase 4 or later research work without explicit authorization
  and a separately tracked Session/variant.

## Phase 4 Variant B Checkpoint — 2026-10-10

Variant:
`PHASE4-VB-001` — CPU offload of resident keyframe payloads

Implementation state:

- Branch: `phase4-vb-001-cpu-keyframe-offload`.
- `scripts/slam.py` is modified for Variant B only.
- Archived `color`, `depth`, `semantic_id`, and `semantic_color` are
  CPU-authoritative.
- `est_w2c` remains GPU-resident.
- CPU-to-GPU staging is synchronous.
- No pinned memory, non-blocking transfer, persistent GPU cache, or eviction.
- No precision change and no algorithm-policy change.

Validation status:

- Gate 1: `PASS`.
  Dataset index 0, CPU archive equality, CPU-to-GPU stage equality, unchanged
  RNG state, 26,112,000-byte staged allocation, and return of allocated memory
  to the pre-stage level after staged references were released were verified.
- Gate 2: `PASS`.
  First-frame Gaussian count was 815,998; initialization state was finite;
  RGB/depth/semantic renderer integration passed; the first keyframe payload
  was CPU-authoritative; `est_w2c` was GPU-resident; no persistent GPU payload
  copy remained.
- Gate 3: `PASS_FRAME_LIMIT` for frames 0–99.
  Index 100 was intercepted before the real loader; 21 logical keyframes were
  observed; GPU archived payload was 0 bytes; final Gaussians were 1,405,708;
  maximum allocated/reserved memory was 2,308,579,328 / 3,776,970,752 bytes;
  frame-99 long-lived allocated memory was reduced by 613,895,680 bytes versus
  Phase 3; online behavior was preserved at the observed level.
- Gate 4: `PASS_FRAME_LIMIT` for frames 0–499.
  Index 500 was intercepted before the real loader; 101 logical keyframes
  were observed; CPU archive was 2,637,312,000 bytes; GPU archived payload
  was 0 bytes; GPU `est_w2c` was 6,464 bytes; final Gaussians were 2,255,038
  versus 2,257,421 in Phase 3 (delta -2,383, about -0.106%); sampled Gaussian
  deltas remained below 1%; tracking/mapping iterations were 19,960/30,000;
  pruning removals were 102,139; densification calls were 0; losses, state,
  and optimizer state were finite. Maximum allocated/reserved memory was
  3,468,590,592 / 4,525,654,016 bytes, versus Phase 3 peaks of
  6,254,666,752 / 8,025,800,704 bytes. Frame-499 long-lived allocated
  reduction was 2,786,778,112 bytes (about 75.8%). Runtime was 2,247.42 s
  for Phase 3 and 2,564.53 s for Variant B (about +14.1%). Logical keyframe
  IDs and iteration contract matched; no evidence indicated changed logical
  keyframe behavior. Historical ordered selection-trace equivalence remains
  `UNKNOWN` because Phase 3 did not preserve an equivalent ordered trace.

Classification:

- Phase 4 Variant B is a research variant.
- It is not pure released-baseline reproduction.
- Phase 3 baseline closure remains immutable; see
  `docs/experiments/PHASE3_BASELINE_CLOSURE_2026-10-10.md` and
  `docs/experiments/PHASE3_RUNTIME_CONCLUSION_2026-10-10.md`.

Evidence:

- `results/runtime_artifacts/phase4_vb001_gate1/`
- `results/runtime_artifacts/phase4_vb001_gate2/`
- `results/runtime_artifacts/phase4_vb001_gate3_0_99/`
- `results/runtime_artifacts/phase4_vb001_gate4_0_499/`

## Phase 4 Variant B Unresolved Items — UNTESTED / UNKNOWN

- Frames 500+ and bounded 0–999.
- Full online Replica `room0` frames 0–1999.
- Checkpoint/resume runtime equivalence.
- Full-scene host-RAM growth and transfer overhead.
- Evaluation, ATE, rendering metrics, semantic metrics, and post-SLAM
  optimization.
- Paper metric equivalence.
- Ordered selection-trace equivalence to historical Phase 3.

## Phase 4 Variant B Next-Session Plan

1. Gate 5: bounded Replica `room0` frames 0–999, with index 1000
   intercepted before the real loader.
2. Only if Gate 5 passes, review memory, CPU RAM, runtime, Gaussian
   divergence, residency invariants, and finite state.
3. Only after researcher approval, attempt full Replica `room0` frames
   0–1999.
4. Evaluation remains prohibited until a full-scene online PASS and required
   outputs are successfully saved.

Full scene is not authorized by this checkpoint alone.
