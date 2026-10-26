# Phase 4 Variant B — Replica room1 final results

**Experiment status:** `CLOSED_EVALUATED`  
**Optional 3D visualization:** `DEFERRED_OPTIONAL`  
**Run ID:** `p4_vb001_room1_full_0_1999_r01`  
**Source:** frozen Phase 4 commit `68f9060f7ff4d8d141be1d5f71339401327edd06`  
**Scene/horizon:** Replica `room1`, frames 0–1999 (2,000 frames)  
**Variant:** Phase 4 Variant B, CPU Keyframe Offload

## Result

The online full-scene process exited 0 and validated all 2,000 frames. The final saved checkpoint passed NPZ CRC, schema, finite-value, pose-count, and auxiliary-artifact checks. Frozen E4 saved-state evaluation completed its 401 sampled image/depth/semantic training views and the trajectory evaluator completed all 2,000 poses. A separate read-only rendering pass computed conventional per-frame Depth RMSE on the same 401 views. Final offline status is `PASS_OFFLINE_EVALUATION`.

The final results support a single-scene execution and saved-state evaluation record. They do not establish benchmark-wide performance or generalization. Room0 remains an independent earlier experiment and Phase 6 room1 uses a different mapping method.

## Provenance and integrity

| Item | Path / identity | SHA256 / status |
|---|---|---|
| Frozen source | Phase 4 detached worktree, commit `68f9060f7ff4d8d141be1d5f71339401327edd06` | exact Git SHA recorded in `run_metadata.json` |
| Online source file | `scripts/slam.py` | `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3` |
| Full-scene execution runner | `tools/phase4_multiscene/run_room1_fullscene.py` | `5796898c41508a6f39339d687b3209b3c4e95f3f67a3e83c20a988fdc83d3018` |
| Run config | `configs/replica/phase4_vb001_room1_full_0_1999_r01.py` | `8800f87639cc474942b3249b0376fda516c5646a10483126106ddb386eb33106` |
| Base config | `configs/replica/slam.py` | `08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3` |
| Offline evaluator config | `configs/replica/phase4_vb001_room1_full_0_1999_r01_eval.py` | `f4785d6df02bf6896fbb86483a800f3341396f39865efa5b1f55c50f4c580c14` |
| Offline evaluator | `scripts/eval_novel_view.py` | `2d37e1804bd7d35232f1cc5ed66eda30d8e6ae62acd1ddb966b1cf61bfe74a94` |
| Metric implementation | `utils/eval_helpers.py` | `e94366ca256ec2b51b5d0264a5daba2a895cc0375d7b91e976e4ea0e9e28194e` |
| Final checkpoint | `experiments/Replica/p4_vb001_room1_full_0_1999_r01/params.npz` | `3ab49193b0a1160405ff90ee6387a8e06c713c127c1e2bf2f1ca9cdf1b0443f4` |
| RGB Gaussian PLY | `experiments/Replica/p4_vb001_room1_full_0_1999_r01/params.ply` | `84777ea58b5a56776234090eea34316fb09a03a7ba93703d9fa76c9092505564` |
| Semantic-color PLY | `experiments/Replica/p4_vb001_room1_full_0_1999_r01/seg_params.ply` | `a0210636b4307d640c66add3d40a15e94df6460477b954ff74f8d6a96d49cf79` |
| Keyframe indices | `experiments/Replica/p4_vb001_room1_full_0_1999_r01/keyframe_time_indices.npy` | `fb91f05c127819f6666259668c4d88a2d36a46f575659f576adde37b227e6d37` |

Final checkpoint SHA was re-read and matched both `checkpoint_validation.json` and the supplementary evaluation record. The NPZ archive CRC test passed. All 11 paths in `artifact_manifest.json` were checked against recorded size and SHA256. Both PLY files contain 6,663,167 vertices; embedded and standalone keyframe indices agree.

## Final evaluation metrics

| Metric | Result | Unit / scope |
|---|---:|---|
| PSNR | 33.93622684716584 | dB; unweighted mean of 401 views |
| MS-SSIM | 0.9699054904412153 | unweighted mean of 401 views |
| Single-scale SSIM | `NOT_AVAILABLE` | The frozen E4 path computes MS-SSIM, not single-scale SSIM |
| LPIPS-Alex | 0.09743846615223664 | unweighted mean of 401 views |
| Depth L1 | 0.00436371473823105 | m; valid-GT-pixel masked MAE, averaged by frame |
| **Standard Depth RMSE** | **0.020464102616935584** | **m; per-frame valid-pixel RMSE, then unweighted mean over 401 views** |
| Aligned ATE mean | 0.004262120556727725 | m; 2,000 poses, Horn rigid alignment without scale |
| True aligned ATE RMSE | 0.004411847720561559 | m; 2,000 pose translation errors |
| Semantic-color mIoU | 0.9236634195237521 | unweighted mean of 401 per-frame values |

The E4 image/depth/semantic frame IDs are `{0} ∪ {5k−1 | k=1..400}` (401 total). The evaluator walks the 2,000-frame training split; this is a sampled training-view evaluation, not a 2,000-view or held-out/NVS evaluation. Trajectory metrics use all 2,000 poses. Metric definitions and units follow `evaluation_protocol.json`, `evaluation_metrics.json`, `trajectory_metrics.json`, and `depth_rmse_supplementary/depth_rmse_summary.json`.

### Supplementary Depth RMSE

The released `utils/eval_helpers.py` value stored as `rmse.txt` applies square root pointwise before taking the mean, so it is mathematically the same masked absolute error as Depth L1. That original E4 value remains unchanged and is not reported as conventional RMSE. The supplementary pass captured the numerical rendered-depth tensor before E4's visualization normalization and JET color map, used the same Phase 4 transforms, camera setup, rasterizer, 1200×680 resolution, dataset GT depth in meters (Replica scale 6553.5), same 401 frame IDs, and exact valid mask `GT depth > 0`. For each frame it computed `sqrt(mean((predicted_depth - gt_depth)^2))` over valid pixels; the reported value is the unweighted mean of those 401 per-frame RMSE values. All 401 values are finite. The supplementary files are separate and do not overwrite E4 output.

### Semantic metric scope

`semantic-color mIoU` uses rendered trainable `semantic_colors`, recolors each rendered pixel to its nearest color in that frame's GT RGB semantic palette, excludes black/unlabeled GT pixels, calculates IoU for non-black GT colors present in each frame, averages within frame, then averages the 401 frame scores without weighting. It is GT-palette-assisted semantic-color mIoU, not a class-ID confusion-matrix score and not evidence that fixed `semantic_ids` are a per-pixel prediction.

## Full-scene performance

| Measure | Result | Measurement scope |
|---|---:|---|
| Frames | 2,000 / 2,000 | validated full-scene frames |
| Process wall-clock | 18,472.333261692 s | whole runner process |
| End-to-end SLAM FPS | 0.1082700258633601 | 2,000 frames / process wall-clock |
| Tracking throughput | 0.255512569872522 FPS | inverse of source-log average tracking frame time; not end-to-end FPS |
| Mapping throughput | 0.19319996808390055 FPS | inverse of source-log average mapping frame time; not end-to-end FPS |
| Online-loop FPS | `NOT_AVAILABLE` | frozen source does not separately instrument a clean online-loop wall scope |
| Peak NVML memory | 11,341 MiB | sampled GPU-wide peak; 17,917 samples; not per-process allocator memory |
| PyTorch peak allocated | 8,066,530,816 B (7.512542 GiB) | worker allocator from immediately before `rgbd_slam` through return/synchronization |
| PyTorch peak reserved | 10,626,269,184 B (9.896484 GiB) | same allocator scope; distinct from NVML |
| Final Gaussians | 6,663,167 | validated NPZ and PLY counts |
| Keyframes | 402 | validated saved keyframe indices |

Primary source: `results/runtime_artifacts/phase4_multiscene/p4_vb001_room1_full_0_1999_r01/performance_summary.json`; online completion and failure state: `run_metadata.json`; raw device telemetry: `gpu_telemetry.csv`. Tracking/mapping throughputs are derived from their respective source-log average frame times, not separately timed total-stage FPS. End-to-end throughput uses whole-process wall time. NVML device-wide usage and PyTorch worker allocator peaks are separate measurements and must not be conflated.

## Artifact inventory

All paths below are retained in the isolated Phase 4 worktree `/home/robot/research/SGS_slam_phase4_multiscene`:

- Model/checkpoint and auxiliary files: `experiments/Replica/p4_vb001_room1_full_0_1999_r01/` (`params.npz`, `params.ply`, `seg_params.ply`, `keyframe_time_indices.npy`, source config and intermediate checkpoints).
- Online run evidence: `results/runtime_artifacts/phase4_multiscene/p4_vb001_room1_full_0_1999_r01/` (`run_metadata.json`, `performance_summary.json`, `checkpoint_validation.json`, `artifact_manifest.json`, `effective_config.json`, `stdout_stderr.log`, `gpu_telemetry.csv`).
- Original E4 saved-state evaluation: `results/runtime_artifacts/phase4_multiscene/offline_eval/p4_vb001_room1_full_0_1999_r01_offline_eval/` (`evaluation_metrics.json`, `per_frame_metrics.csv`, `trajectory_metrics.json`, `evaluation_protocol.json`, `evaluation_runtime.json`, rendered RGB/depth/semantic PNGs and logs).
- Supplementary depth RMSE: `results/runtime_artifacts/phase4_multiscene/offline_eval/p4_vb001_room1_full_0_1999_r01_offline_eval/depth_rmse_supplementary/` (`depth_rmse_per_frame.csv`, `depth_rmse_summary.json`, `depth_rmse_runtime.json`, `evaluation_status_final.json`).
- Consolidated online/offline report: `docs/research/phase4_multiscene/PHASE4_ROOM1_OFFLINE_EVALUATION_REPORT.md` in the main repository; this report is the closure summary.

## Comparability and limitations

- Phase 4 room0 and this room1 run are separate scenes and independent results. The matching E4 protocol allows descriptive scene-level reporting, not paired causal claims.
- Phase 6 room1 is a different adaptive mapping method. Its values may be displayed descriptively with explicit method/protocol qualifiers; this single pair does not establish causal improvement.
- Evaluation covers 401 sampled training views, although online mapping processed all 2,000 frames. There is no held-out-view claim.
- Semantic-color mIoU is GT-palette-assisted as defined above. Fixed semantic IDs are not scored as class predictions.
- Single-scale SSIM is unavailable; MS-SSIM is the supported structural metric.
- NVML is sampled GPU-wide memory; PyTorch peaks cover the worker allocator. The online-loop-only FPS and isolated process-stage totals are unavailable.
- Optional room1 3D visualization is `DEFERRED_OPTIONAL`; no room1 V3A/V3B visualization was run or is marked complete.
- This closure covers Phase 4 room1 only. It does not mark all eight Replica scenes complete. With room0 and room1 recorded, the remaining Phase 4 scenes are room2 and office0–office4.

## Closure decision

`CLOSED_EVALUATED` for the Phase 4 Variant B Replica room1 full-scene experiment. Required online checkpoint integrity and final saved-state evaluation evidence passed. `DEFERRED_OPTIONAL` for room1 3D visualization. No source algorithm, online checkpoint, original E4 metric artifact, room0 output, Phase 6/7 result, or Git history was changed by this archival closure. No commit, push, or upload was performed.
