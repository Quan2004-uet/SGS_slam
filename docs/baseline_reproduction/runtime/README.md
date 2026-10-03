# Phase 3A Runtime Evidence

## Status

**Phase 3A — Environment & CUDA Renderer Recovery: PASS.**

`RUNTIME VERIFIED BASELINE ENVIRONMENT` means only that the isolated environment,
core imports, exact released renderer build/import, and a minimal synthetic CUDA
forward/backward test passed. No dataset, SLAM entry point, post-opt, evaluation,
or benchmark was run.

| Item | Runtime result |
|---|---|
| Baseline | `main` at `e4183986204242a8bb422624618af07780a49d26` |
| Environment | `/home/quan/miniconda3/envs/sgs_slam_baseline` |
| Python / PyTorch | 3.9.25 / 2.0.1 |
| PyTorch CUDA / toolkit | 11.8 / nvcc 11.8.89 |
| GPU | NVIDIA GeForce GTX 1650 Ti, 4096 MiB, SM 7.5 |
| Driver | 580.178.04; driver reports CUDA compatibility 13.0 |
| Renderer | `diff-gaussian-rasterization-w-depth` at `cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110` |
| Renderer import | PASS |
| Synthetic forward/backward | PASS / PASS |
| Source/config modification | None |

Documents:

- [Host inventory](00_host_inventory.md)
- [Environment installation](01_environment_installation.md)
- [Dependency verification](02_dependency_verification.md)
- [Renderer build and smoke test](03_renderer_build_and_smoke_test.md)
- [Phase 3A status](04_phase3a_status.md)
- [Environment snapshot](sgs_slam_baseline_environment.yml)

The next authorized phase is **Phase 3B — Dataset Integrity & First-Frame
Initialization**. It was not started here.

## Phase 3B updates

The initial Phase 3B attempt was **PARTIAL / BLOCKED — DATASET** because the
old Dropbox share was empty. Phase 3B-R subsequently recovered the current
author-distributed 2,000-frame package from the maintainer's replacement Google
Drive link.

Phase 3B-C then resolved an OpenCV-wheel/NumPy ABI incompatibility with the
documented environment-only pin `opencv-python==4.9.0.80`, preserving NumPy
1.26.4. `ReplicaDataset[0]` passes for full-resolution `room0` frame 0 on CUDA.
PyTorch CUDA backward, `pip check`, and the pinned renderer import remain PASS.

Phase 3B first-frame initialization subsequently passed at full resolution.
The released path created 815,998 finite, shape-consistent initial Gaussians
from the 815,998 positive-depth pixels. Peak PyTorch allocation was about
163.3 MiB, establishing that the 4 GiB GPU can complete this bounded stage.
No frame 1, render, optimizer, tracking, mapping, or evaluation was run.

- [Replica room0 integrity and acquisition evidence](05_replica_room0_integrity.md)
- [First-frame initialization boundary](06_first_frame_initialization.md)
- [Phase 3B status](07_phase3b_status.md)
- [Dataset recovery and provenance verification](08_dataset_recovery.md)
- [OpenCV/NumPy compatibility recovery](09_opencv_numpy_recovery.md)
- [First-frame Gaussian initialization](10_first_frame_gaussian_initialization.md)
- [Bounded online reproduction, frames 0-4](11_bounded_online_2_5_frames.md)
- [Bounded online reproduction, frames 0-19](12_bounded_online_20_frames.md)
- [Bounded online reproduction, frames 0-49](13_bounded_online_50_frames.md)

Phase 3C-1 subsequently passed for frame indices 0-4. Released tracking,
pixel-driven Gaussian addition, keyframes, mapping, pruning, and Adam state all
executed with finite losses. Index 5 was blocked before dataset loading. The
maximum corrected per-frame PyTorch allocation was about 1.60 GiB; this does
not establish memory sufficiency beyond frame 4.

Phase 3C-2 subsequently passed in one continuous run over frame indices 0-19.
All tracking/mapping losses and checked state remained finite; index 20 was
blocked before loading. The map reached 937,970 Gaussians and five resident
keyframes. Maximum allocated/reserved peaks were approximately 1.77/2.19 GiB,
so the measured prefix fits the 4 GiB GPU without establishing full-scene
sufficiency.

Phase 3C-3 subsequently passed in one continuous run over frame indices 0-49.
All 1,960 tracking and 3,000 mapping iterations remained finite; index 50 was
blocked before dataset loading. The map reached 1,118,590 Gaussians and 11
resident keyframes. Maximum allocated/reserved peaks were approximately
2.18/2.83 GiB, so the measured prefix fits the 4 GiB GPU without establishing
full-scene sufficiency. Based on the measured late growth and memory margin,
the next recommended gate is a bounded 100-frame run, not a full scene.

The next authorized gate is **Phase 3C-4 — Bounded Online Reproduction: 100
frames**. It has not been started.
