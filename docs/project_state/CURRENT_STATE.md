# Legacy Migration State Snapshot — 2026-10-04

> **Status authority note:** This document is a historical migration/transport
> snapshot. It is not an independent current-state authority and is not updated
> merely to mirror dynamic status. For current project state use
> `project_management/PROJECT_STATUS.md`. For the current resume point use
> `project_management/SESSION_HANDOFF.md`.

This snapshot records the state used for the 2026-10-04 migration checkpoint.
Detailed evidence is in the linked runtime records.

## Baseline

- Released SGS-SLAM baseline commit: `e4183986204242a8bb422624618af07780a49d26`; branch: `main`. The research repository may have later documentation commits; do not substitute their HEAD for this baseline revision.
- Tracked SGS-SLAM source and experiment configs remain unchanged. Research documentation and project state are in Git; raw runtime artifacts and migration assets remain Git-ignored locally and have private Hugging Face transport copies.

## Initial GitHub publication

- **SUCCESS** — research repository `https://github.com/Quan2004-uet/SGS_slam.git` on `main`.
- Initial research publication commit and `origin/main` at verification on 2026-10-03: `edcb98a8772653fa567a09fd2cfa39b834efa18b`. The final migration checkpoint is a later documentation commit on `main`.
- Annotated tag `migration-2026-10-03` is published and resolves to the same commit. `upstream` remains `https://github.com/ShuhongLL/SGS-SLAM.git`.
- GitHub publication is infrastructure work; it does not complete or start a research gate. The released baseline commit above remains the source reference.

## Private artifact transport — 2026-10-04

- **SUCCESS** — `QuanDinh/SGS-SLAM-assets`, Hugging Face repo type `dataset`, visibility `private`: <https://huggingface.co/datasets/QuanDinh/SGS-SLAM-assets>.
- Uploaded local `data/` to remote `data/` and local `migration/` to remote `migration/` using `hf upload`. Remote filenames were compared with local filenames: **96,111/96,111 local files present**; the only extra remote file is Hub-generated `.gitattributes`.
- `data/Replica_data.zip` (13,221,213,627 B), `migration/SGS_SLAM_MIGRATION_2026-10-03.tar.zst` (80,630,663 B), and its adjacent `.sha256` file are present remotely. The ZIP and archive remote byte sizes match local files. See [migration manifest](MIGRATION_MANIFEST.md) and [GPU server restore guide](SERVER_MIGRATION.md).
- Upload and verification were transport work only: no new SGS-SLAM experiment, source/config change, or algorithm change. The local PDF is research documentation already included in the migration archive; it remains untracked in Git.

## Workflow snapshot at migration checkpoint

- Current session: `SESSION_002` — `PAUSED`; started 2026-10-02, last active for research work 2026-10-03. Its Phase 3 baseline-reproduction objective remains open.
- Latest completed gate: **Phase 3C-3 — Bounded Online Reproduction, continuous frames 0–49 — PASS** (`RUNTIME VERIFIED`).
- Next gate: **Phase 3C-4 — Bounded Online Reproduction, continuous frames 0–99**; not started.
- Earlier gates: Phase 1, Phase 2, Phase 3A, Phase 3B, Phase 3C-1 (0–4), and Phase 3C-2 (0–19) PASS per their existing records.

## Verified environment

- Conda: `/home/quan/miniconda3/envs/sgs_slam_baseline` (checked directly; no environment is currently active in the shell).
- Python 3.9.25; PyTorch 2.0.1; torchvision 0.15.2; PyTorch CUDA 11.8; NumPy 1.26.4; `opencv-python` 4.9.0.80 (`cv2.__version__` reports 4.9.0).
- GPU: NVIDIA GeForce GTX 1650 Ti, 4096 MiB VRAM. Renderer: `diff-gaussian-rasterization-w-depth` revision `cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110`, per [Phase 3A runtime evidence](../baseline_reproduction/runtime/README.md).

## Dataset

- Replica, root `data/Replica`, scene `room0`; both directories exist.
- 2,000 frames at 680 × 1200, previously verified with the released loader. The recovered package has [maintainer-distributed provenance](../baseline_reproduction/runtime/08_dataset_recovery.md); no dataset revalidation was run during this recovery.

## Latest runtime

Continuous frame 0–49 run: final frame 49; 1,118,590 Gaussians; 11 resident keyframes with IDs `[0,4,9,14,19,24,29,34,39,44,49]`; keyframe tensor payload 287,232,704 B. At frame 49, tracking Adam state was 107,224,316 B and mapping Adam state was 134,230,824 B. Across the run, maximum allocated peak was 2,340,127,232 B (frame 48), and maximum reserved peak was 3,040,870,400 B (frame 42). **4 GiB VRAM was sufficient through frame 49 only.**

`RUNTIME VERIFIED`: tracking ran 40 iterations on frames 1–49; mapping ran 60 iterations on frames 0–49. Pruning was active; gradient clone/split and opacity reset were inactive. Trainable `semantic_colors` and non-trainable `semantic_ids` remained finite. Zero-LR tracking Gaussian groups acquired Adam state when gradients were present. The paper-described semantic-mIoU keyframe filter remained inactive in the released online path; see [Phase 3C-3 record](../baseline_reproduction/runtime/13_bounded_online_50_frames.md) and `AGENTS.md`.

## Unknowns recorded at migration checkpoint

- Whether 4 GiB VRAM suffices through frame 99 or a long/full `room0` run.
- Online evaluation metrics and paper comparison; online versus post-opt paper-stage attribution.
- Post-opt GPU capacity.

## Persistent evidence

- [Phase 3C-3 runtime report](../baseline_reproduction/runtime/13_bounded_online_50_frames.md).
- `results/runtime_artifacts/phase3c3/phase3c3_results.json` and `results/runtime_artifacts/phase3c3/phase3c3_bounded_online.log` (present, Git-ignored).
- The prior `/tmp/sgs_phase3c1_bounded_online.py` harness is absent; no persistent harness copy was found. Recover or recreate a bounded harness from released source and prior runtime documentation during Phase 3C-4 preparation. It must orchestrate released SGS-SLAM functions only, without reimplementing tracking or mapping or changing algorithmic settings.

## Historical Next Exact Action recorded at migration checkpoint

On the GPU server, clone the GitHub repository, download and verify the private Hugging Face assets, restore the migration evidence without overwriting newer GitHub state, and validate the destination GPU/runtime as specified in [SERVER_MIGRATION.md](SERVER_MIGRATION.md). Then resume `SESSION_002` and prepare **Phase 3C-4 — one continuous run over frames 0–99**, with a strict guard before dataset index 100. Fast instrumentation may reduce logging overhead while preserving algorithmic settings. No evaluation, post-opt, or algorithm changes. Do not start this gate as part of migration recovery.

## Do Not Re-do

Do not repeat completed environment, dataset, renderer, first-frame, 5-frame, 20-frame, or 50-frame gates unless regression evidence appears.
