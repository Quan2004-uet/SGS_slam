# Phase 4 Variant B — Replica Office2 Final Results

**Experiment status:** `CLOSED_EVALUATED`  
**Online:** `CORE_ARTIFACTS_VALIDATED`  
**Checkpoint:** `PASS_CHECKPOINT_VALIDATION` (NPZ CRC `PASS`)  
**Offline:** `PASS_OFFLINE_EVALUATION`  
**Final integrity:** `PASS_FINAL_INTEGRITY_VALIDATION`  
**Optional 3D visualization:** `DEFERRED_OPTIONAL`  
**Run ID:** `p4_vb001_office2_full_0_1999_r01`

## Experiment identity and provenance

| Item | Verified value |
|---|---|
| Dataset / scene | Replica `office2` |
| Frame range | 0–1999 inclusive; 2,000/2,000 online frames |
| Frozen worktree | `/home/robot/research/SGS_slam_phase4_multiscene` |
| Frozen source commit | `68f9060f7ff4d8d141be1d5f71339401327edd06` |
| `scripts/slam.py` SHA256 | `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3` |
| Online config SHA256 | `01b8445ecfbfe9909cd7b34b8a757c9759d9446cb6ef519292ca5caad9b02189` |
| Saved-state E4 config SHA256 | `8ffe57f6d1022d52080a5029018399541a2dff773c6f658e11efa6dd18082732` |
| Seed | 0 |

The released Phase 4 Variant B CPU Keyframe Offload source and algorithm settings were preserved. Online and E4 config snapshots match across their source, model/evidence snapshots, metadata, and E4 output as recorded in final integrity evidence.

## Dataset and evaluation protocol

The frozen Replica Office2 dataset and its saved trajectory were used by the validated run. Online processing covered all 2,000 frames. Image, depth, and semantic metrics use saved-state E4 training views at 1200×680 with frame IDs `{0} ∪ {5k−1 | k=1..400}` (401 views). Trajectory metrics use all 2,000 matched frame indices 0–1999.

Image/depth/semantic values are arithmetic means over the 401 E4 per-view values. Standard Depth RMSE is calculated per view as `sqrt(mean((prediction−GT)^2))` over pixels with GT depth > 0, then averaged without view weighting. Trajectory uses Horn rigid alignment with no scale correction; aligned ATE mean and true RMS are separate aggregates.

## Final quality metrics

| Metric | Result | Scope / definition |
|---|---:|---|
| PSNR | 32.05055297223707 dB | Arithmetic mean, 401 E4 views |
| MS-SSIM | 0.9669492452816476 | Arithmetic mean, 401 views; E4 `ssim.txt` |
| LPIPS-Alex | 0.09961088107634067 | Arithmetic mean, 401 E4 views |
| Depth L1 | 0.006733047930080156 m | Arithmetic mean, 401 E4 views |
| Standard Depth RMSE | 0.04190794845461125 m (4.1907948454611255 cm) | Per-view RMSE over GT depth > 0, unweighted mean over 401 views |
| Aligned ATE mean | 0.0030677457674380725 m (0.30677457674380726 cm) | Mean aligned translation error over 2,000 poses |
| True aligned ATE RMSE | 0.0033443906342707497 m (0.33443906342707497 cm) | `sqrt(mean(per-pose aligned translation error²))`, 2,000 poses |
| Semantic-color mIoU | 0.9062349859139421 | 401 views; released GT-palette-assisted protocol |

Trajectory status is `PASS_TRAJECTORY_METRICS`; all 2,000 aligned pose errors are finite. The saved Office2 trajectory agrees with the loader-derived relative-pose ground truth within maximum absolute difference `4.815935930047033e-7`. The released E4 “ATE RMSE” label is not used as the true aligned ATE RMSE above.

**Metric-label caveats:** E4 `rmse.txt` is identical to `l1.txt`; it reports masked Depth L1, not conventional standard Depth RMSE. E4 `ssim.txt` is MS-SSIM. Semantic-color mIoU follows the released GT-palette-assisted recoloring protocol and is not direct class-ID mIoU.

## Runtime, memory, and model size

| Measurement | Result | Scope |
|---|---:|---|
| Online process wall time | 13,293.532819613989 s | Full online runner process |
| End-to-end FPS | 0.15044909634924833 | 2,000 frames / process wall time |
| Tracking average / reciprocal throughput | 2.7042347106933593 s/frame / 0.36979038692377497 FPS | Frozen source log average and reciprocal |
| Mapping average / reciprocal throughput | 3.8219406394958497 s/frame / 0.26164718249834185 FPS | Frozen source log average and reciprocal |
| PyTorch peak allocated | 5,246,518,784 bytes | Worker CUDA allocator during `rgbd_slam` call and attempted synchronization |
| PyTorch peak reserved | 7,342,129,152 bytes | Same worker allocator scope |
| NVML sampled GPU-wide peak | 8,209 MiB | 12,909 device-wide samples; NVIDIA GeForce RTX 5080 |
| Final Gaussians | 4,424,471 | Checkpoint and PLY validation |
| Keyframes | 402 | Validated saved indices |

PyTorch allocator peaks and NVML sampled device-wide memory have different measurement scopes. The frozen source does not separately instrument frame-loop FPS or checkpoint serialization duration. Cross-scene runtime and memory values are descriptive observations, not controlled speedup comparisons.

## Checkpoint and E4 integrity

- Online metadata: `CORE_ARTIFACTS_VALIDATED`, exit code 0, 2,000/2,000 frames, failure classification `NONE`.
- Checkpoint validation: `PASS_CHECKPOINT_VALIDATION`; NPZ CRC `PASS`; 2,000 camera poses; 4,424,471 Gaussians; 402 keyframes.
- Final checkpoint SHA256: `7508fc2a3fb6916dd6211221b75693ae868b97b3b830bb1fac9227a5e697726d`.
- Offline status: `PASS_OFFLINE_EVALUATION`; trajectory `PASS_TRAJECTORY_METRICS`; supplementary standard Depth RMSE `PASS_SUPPLEMENTARY_DEPTH_RMSE`; final integrity `PASS_FINAL_INTEGRITY_VALIDATION`; no blockers.
- Six E4 metric arrays each contain 401 finite values. Rendered RGB, depth, semantic, and plot groups each contain 401 expected PNGs.
- Original E4 manifest: 1,612 expected, 1,612 verified, 0 missing, 0 changed, and 0 unlisted original files. Manifest SHA256: `c13b00d2eb47c767af4d6a619e4ae8b74491e3cec3f5e5a0a0344aebc4cad9b6`. Supplementary files are excluded from this original-manifest comparison.
- Supplementary standard Depth RMSE contains 401 records; checkpoint SHA256 was unchanged before and after rendering.
- E4 process exit code/stdout/stderr were not retained and are recorded as `NOT_RECORDED_IN_EXISTING_ARTIFACTS`.
- The frozen `scripts/slam.py` commit and SHA256 above were rechecked. The Office2 checkpoint and previous Room0, Room1, Room2, Office0, and Office1 checkpoints retain their validated hashes. Room0 (`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`) was rehashed in the main repository as `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`; Room1, Room2, Office0, and Office1 were rehashed in the frozen worktree.

## Artifact paths and preservation

Runtime artifacts remain in the frozen worktree:

- Checkpoint and PLYs: `/home/robot/research/SGS_slam_phase4_multiscene/experiments/Replica/p4_vb001_office2_full_0_1999_r01/`
- Online metadata, checkpoint validation, performance, telemetry, logs, and manifest: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/p4_vb001_office2_full_0_1999_r01/`
- E4 output and rendered views: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/offline_eval/p4_vb001_office2_full_0_1999_r01_offline_eval/`
- Supplementary evidence: E4 `supplementary/trajectory_metrics.json`, `evaluation_metrics.json`, `final_integrity_validation.json`, `evaluation_status_final.json`, `original_e4_files_manifest.json`, and `depth_rmse_supplementary/`.
- Detailed Gate 4 evidence: [Office2 offline evaluation report](PHASE4_OFFICE2_OFFLINE_EVALUATION_REPORT.md).

Raw checkpoint, online logs, E4 files, and supplementary rendering were not modified or moved during archival. No remote publication occurred.

## Limitations

This is a single Office2 run without a matched controlled baseline. Runtime comparisons across scenes do not establish an algorithmic speedup. E4 did not retain its process exit code. Standard Depth RMSE is supplementary and distinct from E4 Depth L1; semantic-color mIoU is palette-assisted; and the released E4 ATE RMSE label is not the independently computed true aligned RMS reported here. Optional 3D visualization is not part of numerical closure.

## Closure verdict

Replica Office2 is formally `CLOSED_EVALUATED` for Phase 4 Variant B. Gate 5 archival and local closure pass based on the verified online, checkpoint, offline, and final integrity evidence. Optional 3D visualization is `DEFERRED_OPTIONAL`. The remaining Phase 4 Replica multiscene experiments are **office3** and **office4**; the campaign remains incomplete.
