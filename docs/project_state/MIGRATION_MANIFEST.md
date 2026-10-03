# GPU server migration manifest — 2026-10-03

This manifest describes the migration snapshot at
`migration/SGS_SLAM_MIGRATION_2026-10-03/`. The compressed archive is
`migration/SGS_SLAM_MIGRATION_2026-10-03.tar.zst`. The Replica ZIP is a
**separate transfer asset** and is not inside the archive.

## Hub transport verification — 2026-10-04

`hf upload` completed to the private dataset repository
`QuanDinh/SGS-SLAM-assets` at
<https://huggingface.co/datasets/QuanDinh/SGS-SLAM-assets>. Remote `data/`
and `migration/` are present. A complete filename comparison found all
96,111 local files remotely; Hub-generated `.gitattributes` is the sole extra
remote file. Remote sizes match the local `data/Replica_data.zip`
(13,221,213,627 bytes) and migration `.tar.zst` (80,630,663 bytes); the
adjacent archive checksum file is also present. No new experiment or
source/config change occurred during upload.

This archive is a 2026-10-03 snapshot. The GitHub `main` documentation can be
newer than its `overlay/`; restore missing evidence from the archive without
overwriting newer files from the GitHub checkout. See `SERVER_MIGRATION.md`.

## Research state and provenance

| Item | Snapshot |
|---|---|
| Git HEAD / branch | `e4183986204242a8bb422624618af07780a49d26` / `main` |
| Git history | `git/sgs-slam-history.bundle`, created with `git bundle create ... --all`; `git bundle verify` passed |
| Latest completed gate | Phase 3C-3, one continuous online Replica `room0` run over frames 0–49 — **PASS** (`RUNTIME VERIFIED`) |
| Next gate | Phase 3C-4, one continuous online run over frames 0–99 — **NOT STARTED**; guard before dataset index 100 |
| Session | `SESSION_002`, paused; Phase 3 baseline reproduction remains open |
| Old GPU | NVIDIA GeForce GTX 1650 Ti, 4,096 MiB; driver 580.178.04 at packaging |
| Latest verified horizon | Frame 49 only; no claim for frame 99 or a full scene |
| Source/config/algorithm | No tracked changes; no migration change to SGS-SLAM source, experiment config, or algorithm |

The bundle includes `AGENTS.md`, the complete `docs/project_state/` directory,
`docs/repository_understanding/`, `docs/baseline_reproduction/`, archival
`project_management/`, the local paper PDF, repository dependency files, the
Git history bundle, environment snapshots, and the Phase 3C-3 JSON/log. The
manifest `ARTIFACT_PATHS.tsv` maps each archive file to its original path.
`CHECKSUMS.sha256` covers every included regular file except itself. Use the
adjacent `SGS_SLAM_MIGRATION_2026-10-03.tar.zst.sha256` for the compressed
archive. Historical untracked documentation is copied because it is absent
from the Git bundle.

## Runtime evidence

| Original path | SHA-256 |
|---|---|
| `results/runtime_artifacts/phase3c3/phase3c3_results.json` | `e3fd9fa0d2958e8d22f1c04908f5a2d31b7e364ac48ea1345eef6847457f82ba` |
| `results/runtime_artifacts/phase3c3/phase3c3_bounded_online.log` | `1e900212d8fa9be0c3d247b077fe4d2e2c9c2fc7e30bb1c97e16a3c3b66ec5fd` |

The JSON parses, reports `status=PASS_FRAME_LIMIT`, `max_frame=49`, 50 frame
records, and a stop before loading dataset index 50. The interpretation and
runtime measurements are in
`docs/baseline_reproduction/runtime/13_bounded_online_50_frames.md`.

## Separate dataset asset

| Item | Value |
|---|---|
| Local path | `data/Replica_data.zip` |
| Size | 13,221,213,627 bytes |
| SHA-256 | `1e4a71b656936f2b75a91fb938cde2b22d690175410fd9be32d0a198471bf041` |
| Extracted path | `data/Replica`, with `room0` present |
| Identity | Maintainer-distributed 2,000-frame Replica package; see `docs/baseline_reproduction/runtime/08_dataset_recovery.md` |

The ZIP was hashed locally during packaging and matches the earlier recovery
record. No author-published checksum is known. The extracted dataset and ZIP
are excluded from the main migration archive; transfer the ZIP separately.

## Environment and renderer

Environment snapshots are under `environment/`: `conda_env_export.yml`,
`conda_explicit.txt`, `pip_freeze.txt`, `python_package_versions.txt`,
`nvidia-smi.txt`, `nvcc_version.txt`, and `compiler_versions.txt`. The baseline
environment is `/home/quan/miniconda3/envs/sgs_slam_baseline`: Python 3.9.25,
PyTorch 2.0.1, torchvision 0.15.2, PyTorch CUDA 11.8, NumPy 1.26.4, OpenCV
4.9.0 (`opencv-python` 4.9.0.80). The CUDA compiler is 11.8.89 and GCC/G++
are 11.4.0. The Conda export has an old-host `prefix`, and `pip freeze`
contains local `file://` references. These files are evidence, not a
portable one-command installation specification.

Renderer: `https://github.com/JonathonLuiten/diff-gaussian-rasterization-w-depth.git`
at `cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110`. Its source, binary, and
temporary build directory are **not** in the archive. Rebuild this exact
revision on the destination GPU after checking its CUDA/PyTorch/compiler ABI;
the old build command and smoke evidence are in
`docs/baseline_reproduction/runtime/03_renderer_build_and_smoke_test.md`.

At packaging, an in-sandbox `nvidia-smi` could not reach the driver, whereas
the outside-sandbox capture succeeded and identified the GTX 1650 Ti. The
in-sandbox Python report therefore says `CUDA available: False`; it is a
packaging-context observation, not a regression of the earlier runtime gates.

## Missing or non-portable items

- `/tmp/sgs_phase3c1_bounded_online.py` is absent; no persistent copy was
  found. Reconstruct it only when preparing Phase 3C-4, using the released
  functions and prior runtime documentation. This packaging task did not
  recreate it.
- The renderer source/build and old host Conda binaries are excluded. The
  destination driver, GPU, CUDA toolkit, compiler, and package availability
  must be checked before replaying a bounded regression.
- Results beyond frame 49, online evaluation, post-opt, and paper comparison
  remain unverified.

No new SGS-SLAM experiment, package installation, algorithm change, or config
change was performed for this migration.
