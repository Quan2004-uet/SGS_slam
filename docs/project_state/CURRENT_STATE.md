# Legacy Migration State Snapshot — 2026-10-04

> **Status authority note:** This document is a historical migration/transport
> snapshot. It is not an independent current-state authority and is not updated
> merely to mirror dynamic status. For current project state use
> `project_management/PROJECT_STATUS.md`. For the current resume point use
> `project_management/SESSION_HANDOFF.md`.

## Later reconciliation pointer — 2026-10-17

This migration snapshot is retained as historical evidence and is not a live
status authority. The later project state is: P6-BAM-006-FULL completed with
`PASS_P6_BAM_006_FULL_SCENE_QUALITY_CONSTRAINED`; its single V-A2 full-scene
quality screen and all three Phase 6 visualization packages are preserved.
Matched full-scene runtime speedup remains unverified, and the predominantly
LOW/45 behavior does not establish superiority over fixed-45 mapping. No new
SLAM/evaluation run is authorized automatically. For the current publication
checkpoint, see `project_management/PROJECT_STATUS.md`,
`project_management/SESSION_HANDOFF.md`, and
`docs/research/phase6_bam/P6_BAM_006_FINAL_SESSION_HANDOFF.md`.

## Local reconciliation pointer — 2026-10-19

This addendum records a later completed experiment without replacing the
historical room0/Phase 4/Phase 5 snapshot below. Canonical status and operational
handoff remain in the project-management files.

- Phase 6 V-A2 Replica/room1 run `p6_bam_ms_room1_gate3_0_1999_r01`, frozen
  source `002927f3b24dd69418c17da08bd4ae987bae9ee2`, frames 0–1999: Gate 4
  PASS; Gate 5 PASS; overall `ROOM1_GATE5_CLOSED_QUALIFIED`.
- Saved model: 2,000 frames, 6,682,135 Gaussians, 402 keyframes. Metrics:
  PSNR 34.096186264494705 dB; MS-SSIM 0.9714362002964924; LPIPS-Alex
  0.09135246086410453; Depth L1 0.004393707946328413 m; GT-palette-assisted
  semantic-color mIoU 0.9265354206849918; released ATE Mean
  0.004655330867990601 m; true ATE RMSE 0.004802019103114381 m.
- Process wall 16,075.75 s / 0.124411 FPS; PyTorch allocated/reserved
  9.521/11.654 GiB; peak process RSS 18.234 GiB. Device-wide NVML peak and
  separate Gate 5 runtime are NOT_MEASURED; CUDA-event timing is unvalidated.
- Integrity: Gate 4 checksums 7/7, artifact manifest 1,623/1,623, Gate 5
  checksums 1,614/1,614, source hashes 17/17, CPU artifact validation PASS.
  Artifacts remain on the GPU server under `results/runtime_artifacts/phase6_bam/`.
- GitHub publication and Hugging Face upload are NOT_REQUESTED. Room2
  preparation is PLANNED_NOT_STARTED and requires separate authorization and
  dataset/config/source/resource/output-isolation preflight. No run is
  authorized. Full qualifications and artifact paths are in
  `docs/experiments/PHASE6_MULTISCENE_ROOM1_GATE5_FINAL_REPORT.md`.

## Local Phase 4 room1 closure pointer — 2026-10-21

This addendum records final archival and closure of one additional Phase 4
Variant B scene. It does not replace the historical room0 result or mean that
the eight-scene Replica extension is complete.

- Replica room1 run `p4_vb001_room1_full_0_1999_r01`, frozen source
  `68f9060f7ff4d8d141be1d5f71339401327edd06`, frames 0–1999:
  `CLOSED_EVALUATED`; online exit 0; 2,000/2,000 frames and poses; 6,663,167
  Gaussians; 402 keyframes. Offline status `PASS_OFFLINE_EVALUATION` covers
  401 E4 image/depth/semantic views, 2,000 trajectory poses, and a separate
  same-view supplementary standard Depth RMSE pass. Optional 3D visualization
  is `DEFERRED_OPTIONAL`.
- Final metrics, exact provenance, performance scopes, and evidence locations
  are in `docs/research/phase4_multiscene/PHASE4_ROOM1_FINAL_RESULTS.md`.
- At the time of this room1 reconciliation, remaining Phase 4 Replica scenes
  were room2 and office0–office4; room2 was subsequently closed in the dated
  addendum below. Phase 6/7 records are unchanged. P5-LEAN remains the
  independent active workstream.

## Local Phase 4 room2 closure pointer — 2026-10-21

- Phase 4 Variant B Replica room2 run `p4_vb001_room2_full_0_1999_r01`, frozen
  source `68f9060f7ff4d8d141be1d5f71339401327edd06`, frames 0–1999:
  `CLOSED_EVALUATED`. Online exit 0, 2,000/2,000 frames, checkpoint
  `PASS_CHECKPOINT_VALIDATION` and SHA256
  `d772e65a3c0bc163cf20960d30bd0b88f9182477462f9c1fe8dadd0a86155c3f`;
  offline `PASS_OFFLINE_EVALUATION` covers 401 E4 views, 2,000 poses and 401
  supplementary standard Depth RMSE values. E4 process exit code was not
  retained. Optional visualization is `DEFERRED_OPTIONAL`.
- Exact results and paths are in
  `docs/research/phase4_multiscene/PHASE4_ROOM2_FINAL_RESULTS.md`. Remaining
  Phase 4 Replica scenes are office0–office4; the eight-scene extension is not
  complete. Phase 6/7 and P5-LEAN remain unchanged.

This snapshot records the state used for the 2026-10-04 migration checkpoint.
Detailed evidence is in the linked runtime records.

## Administrative transition pointer — 2026-10-15

This legacy snapshot is not the current authority. The original Phase 5 execution plan is administratively superseded as `SUPERSEDED_BY_P5_LEAN_INCOMPLETE`; its technical completion is `NOT_ACHIEVED`. P5-LEAN is `PLANNED_NOT_STARTED`, with `P5-LEAN-001` pending researcher review. See the canonical project-management files and `docs/research/phase5/PHASE5_TO_P5_LEAN_TRANSITION.md`.

## Current checkpoint pointer — 2026-10-12

This section is a convenience pointer requested for the session checkpoint; it
does not promote this legacy file to current-state authority. Canonical values
remain in `project_management/PROJECT_STATUS.md` and the exact resume point in
`project_management/SESSION_HANDOFF.md`.

- PHASE4-VB-001 validation, full-scene state preservation, and released
  `room0` evaluation are complete.
- Runtime/output status: `PASS_FULL_OUTPUT_SAVE_TELEMETRY`; Replica `room0` frames
  0–1999 completed with 4,956,467 Gaussians and 402 keyframes ending
  `[1989, 1994, 1998, 1999]`.
- Runtime was 14,173.47515856901 s. Peak GPU allocated/reserved was
  5,817,509,888 / 7,189,037,056 B; process RSS/HWM was 17,960,493,056 B host
  RAM.
- A readable final `params.npz`, RGB/semantic PLY files, and standalone
  `keyframe_time_indices.npy` now exist under
  `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/`.
- The historical detailed full-scene run remains classified
  `PASS_RUNTIME_VALIDATOR_BUG` and supplies detailed residency-invariant
  evidence. The minimal output-save harness intentionally did not duplicate
  that heavy residency telemetry.
- Latest quantitative gate: `PASS_EVAL_E4_FULL_RELEASED`. The released protocol evaluated
  401 RGB/depth/semantic frames and all 2,000 finite trajectory poses without
  rerunning SLAM. PSNR/MS-SSIM/LPIPS/Depth L1/semantic mIoU are recorded in
  `docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md`.
- Latest completed gate is now `PASS_QUALITATIVE_EXPORT`: representative
  camera-view RGB/depth/semantic comparisons and GT references for frames
  `[0,499,999,1499,1999]` are under
  `results/qualitative/phase4_vb001_room0_representative/`. Existing E4
  per-frame values were attached as annotations without metric recomputation.
  This does not mean the paper-style reconstructed/semantic 3D map view has
  been produced.
- Paper reproduction, cross-scene generalization, and post-SLAM optimization
  are not claimed or complete.
- The next workflow is a Scene Reconstruction / 3D Segmentation Visualization
  Audit for the saved RGB and semantic PLY maps. Paper / Baseline Comparison
  Audit remains subsequent. Do not resume from output saving, evaluation Gates
  E1--E4, or the completed camera-view export.

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

## Local Phase 4 office0 closure pointer — 2026-10-22

- Phase 4 Variant B Replica office0 run `p4_vb001_office0_full_0_1999_r01`, frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06`, frames 0–1999: `CLOSED_EVALUATED`. Online exit 0; 2,000/2,000 frames; checkpoint SHA256 `6d0f180d7677a38c29295ae9ffc10d745f726aac700f40338543a062a9bf7390`, CRC/schema validation PASS. Offline `PASS_OFFLINE_EVALUATION`; final integrity `PASS_FINAL_INTEGRITY_VALIDATION`; 401 E4 views, 2,000 poses, 401 supplementary standard Depth RMSE records, and 1,612/1,612 original E4 manifest entries unchanged. E4 exit code/stdout/stderr were not retained.
- Optional 3D visualization is `DEFERRED_OPTIONAL`. Exact metrics, performance scope and evidence paths are in `docs/research/phase4_multiscene/PHASE4_OFFICE0_FINAL_RESULTS.md`. Remaining scenes are office1–office4; the eight-scene extension is incomplete. Phase 6/7 and P5-LEAN remain unchanged.

## Local Phase 4 office1 closure pointer — 2026-10-22

- Phase 4 Variant B Replica office1 run `p4_vb001_office1_full_0_1999_r01`, frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06`, frames 0–1999: `CLOSED_EVALUATED`. Online `CORE_ARTIFACTS_VALIDATED`, exit 0, 2,000/2,000 frames; checkpoint SHA256 `f2bcf577a62655929b066ea0ce05148f64ded7509c27eba88002f5090490704b`, CRC/schema validation PASS. Offline and final integrity are `PASS_OFFLINE_EVALUATION` and `PASS_FINAL_INTEGRITY_VALIDATION`; 401 E4 views, 2,000 trajectory poses, 401 supplementary standard Depth RMSE records, and 1,612/1,612 original E4 manifest entries are verified unchanged.
- Optional 3D visualization is `DEFERRED_OPTIONAL`. Exact results and artifact paths are in `docs/research/phase4_multiscene/PHASE4_OFFICE1_FINAL_RESULTS.md`. Remaining scenes are office2, office3, and office4; the multiscene campaign remains incomplete. This dated record does not change Phase 5/6/7 or P5-LEAN.

## Local Phase 4 office2 closure pointer — 2026-10-22

- Phase 4 Variant B Replica office2 run `p4_vb001_office2_full_0_1999_r01`, frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06`, frames 0–1999: `CLOSED_EVALUATED`. Online `CORE_ARTIFACTS_VALIDATED`, exit 0; checkpoint SHA256 `7508fc2a3fb6916dd6211221b75693ae868b97b3b830bb1fac9227a5e697726d`, CRC PASS; offline `PASS_OFFLINE_EVALUATION`; final integrity `PASS_FINAL_INTEGRITY_VALIDATION`. Evidence validates 401 E4 views, 2,000 trajectory poses, 401 supplementary standard Depth RMSE records, and 1,612/1,612 original E4 manifest files unchanged.
- Optional visualization is `DEFERRED_OPTIONAL`. Exact metrics and paths are in `docs/research/phase4_multiscene/PHASE4_OFFICE2_FINAL_RESULTS.md`. Remaining Phase 4 scenes are office3 and office4; the multiscene campaign remains incomplete. This dated local record does not change Phase 5/6/7 state.
