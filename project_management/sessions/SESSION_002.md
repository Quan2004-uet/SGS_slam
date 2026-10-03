# SESSION_002 — Baseline Recovery and Bounded Runtime Reproduction

## Metadata

Session ID: SESSION_002\
Title: Baseline Recovery and Bounded Runtime Reproduction\
Status: PAUSED\
Started: 2026-10-02\
Last active: 2026-10-03\
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

Baseline recovery and online runtime verification are paused between bounded gates. Phase 3C-3 passed its 0–49 stop boundary; the overall Phase 3 objective has not been closed.

## STOPPED HERE

Frames 0–49 completed continuously under the released online path. The guard intercepted dataset index 50. Persistent result JSON/log are present under the Git-ignored `results/runtime_artifacts/phase3c3/`. No frame 50+, evaluation, post-opt, or Phase 4 task has started.

## NEXT TASK

Resume this Session, then run Phase 3C-4 through frame 99 continuously from frame 0, with the same baseline config and a dataset guard that intercepts index 100 before the actual loader. Follow the command and artifact details in `project_management/SESSION_HANDOFF.md`; save separate JSON/log evidence and stop after reviewing finite state and VRAM trends.

## DO NOT

- Do not call the 0–49 run a full-scene reproduction.
- Do not run a full scene or metrics until explicitly selected as the next gate.
- Do not change the released source/config or enable paper-described components absent from the active path during baseline reproduction.
- Do not start Phase 4 or later research work before the baseline gate is established.
