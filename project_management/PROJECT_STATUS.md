# SGS-SLAM Project Status

> Historical snapshot (2026-10-03). Current rolling state is authoritative in
> `docs/project_state/CURRENT_STATE.md` and `docs/project_state/state.yaml`.
> Do not update this file as a parallel current-state record.

## Project Identity

Repository: SGS-SLAM — Semantic Gaussian Splatting for Neural Dense SLAM\
Current HEAD: `e4183986204242a8bb422624618af07780a49d26` (`main`)\
Audited commit: `e4183986204242a8bb422624618af07780a49d26`\
Research objective: establish and characterize the released SGS-SLAM baseline before proposing changes.\
Dataset: author-distributed semantic Replica package at `data/Replica`\
Canonical scene/config: Replica `room0`, `configs/replica/slam.py`, seed 0

Snapshot verified: 2026-10-03. Tracked files are clean. Untracked paths are `2402.03246v6.pdf`, `AGENTS.md`, `docs/`, and `project_management/`; the Phase 3C-3 runtime evidence is under Git-ignored `results/runtime_artifacts/phase3c3/`.

## Current Phase

Phase: Phase 3 — Baseline Recovery & Reproduction\
Status: IN PROGRESS\
Objective: complete bounded runtime verification of the released online pipeline.\
Entry condition: Phase 1 documentation and Phase 2 static reproduction audit are complete.\
Exit / stop condition: finish the authorized baseline recovery/reproduction gates; stop before algorithmic research modifications unless separately authorized.

## Active Session

Session ID: SESSION_002\
Status: PAUSED\
Started: 2026-10-02\
Last active: 2026-10-03

## COMPLETE

- Phase 1 — Research Documentation: PASS. Static repository understanding is recorded under `docs/repository_understanding/`.
- Phase 2 — Baseline Reproduction Audit: PASS. Static contract and reproduction plan are recorded under `docs/baseline_reproduction/`.
- Phase 3A — Environment and CUDA renderer recovery: PASS. Runtime evidence is in `docs/baseline_reproduction/runtime/00_host_inventory.md` through `04_phase3a_status.md`.
- Phase 3B-R — Dataset recovery: PASS. Author-distributed semantic Replica data is documented in `docs/baseline_reproduction/runtime/08_dataset_recovery.md`.
- Phase 3B-C — OpenCV/NumPy compatibility recovery: PASS. NumPy 1.26.4 was preserved with the documented OpenCV compatibility pin; see `09_opencv_numpy_recovery.md`.
- Phase 3B — Dataset and first-frame initialization: PASS. `room0` frame 0 loaded and 815,998 initial Gaussians were created; see `10_first_frame_gaussian_initialization.md`.
- Phase 3C-1 — bounded online frames 0–4: PASS; see `11_bounded_online_2_5_frames.md`.
- Phase 3C-2 — bounded online frames 0–19: PASS; see `12_bounded_online_20_frames.md`.
- Phase 3C-3 — bounded online frames 0–49: PASS; guard intercepted frame 50; see `13_bounded_online_50_frames.md` and ignored runtime evidence under `results/runtime_artifacts/phase3c3/`.

Historical snapshot note: `07_phase3b_status.md` records the original dataset-blocked attempt, and the Phase 2 contract records the then-unverified runtime state. Later recovery and runtime reports supersede those earlier statuses; the historical documents are retained as provenance.

## IN PROGRESS

- Phase 3 — Baseline Recovery & Reproduction remains unfinished and is paused at the handoff. The 50-frame prefix is verified; the next bounded horizon has not started.

## NOT STARTED

- Phase 3C-4 — bounded online reproduction through frame 99.
- Phase 3 full-scene execution and paper-protocol evaluation.
- Phase 4 — Mathematical / Algorithmic Verification as runtime work.
- Later research phases, including limitation characterization and method changes.

## BLOCKED

- No blocker is currently known for the next bounded 100-frame runtime gate.

## UNKNOWN / REQUIRES VERIFICATION

- Runtime behavior, memory sufficiency, and numerical stability beyond frame 49.
- Full `room0` baseline completion and paper-protocol metric reproduction.
- Whether reported paper targets can be compared directly to this repository's evaluator and online/post-optimization outputs.
- Any runtime claims beyond the frame ranges documented in the runtime evidence files.

## Current Baseline

Released source/config baseline: commit `e4183986204242a8bb422624618af07780a49d26`, branch `main`; source and experiment config have not been modified. Runtime environment: `/home/quan/miniconda3/envs/sgs_slam_baseline`, Python 3.9.25, PyTorch 2.0.1, torchvision 0.15.2, CUDA 11.8, NumPy 1.26.4, OpenCV 4.9.0.80; GTX 1650 Ti with 4096 MiB. Dataset is author-distributed `data/Replica`, scene `room0`, 680×1200, 2,000 frames. The renderer is `diff-gaussian-rasterization-w-depth` at revision `cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110`.

The released online pipeline has runtime evidence through frame 49 only. This does not establish full-scene metrics or full-scene VRAM sufficiency. Compatibility recovery is documented separately from source/config behavior.

## Current Research Question

How do Gaussian count, keyframe residency, optimizer state, numerical stability, and GPU memory evolve beyond the verified 50-frame prefix under the unchanged released `room0` online config?

## NEXT MILESTONE

Complete a guarded 100-frame run (indices 0–99) from frame 0, then review actual growth and memory evidence before selecting another horizon.

## NEXT TASK

Resume SESSION_002 (`PAUSED` → `ACTIVE`) and run Phase 3C-4 — bounded online reproduction through frame 99 in a continuous state from frame 0. Use `configs/replica/slam.py` and released `scripts/slam.py::rgbd_slam`; start from the existing bounded harness if it remains available, set its guard to 99, and write separate diagnostic output/evidence paths. Keep baseline algorithmic settings unchanged, verify frame 100 is intercepted before dataset loading, and record per-frame losses, Gaussian/keyframe/optimizer state, and VRAM. Completion criterion: frames 0–99 finish with finite tracking/mapping/state, the frame 100 guard is observed, and memory evidence is retained. Do not start automatically as part of this status bootstrap.
