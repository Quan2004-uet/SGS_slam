# Phase 4 Variant B — Replica Office1 Final Results

**Experiment status:** `CLOSED_EVALUATED`  
**Offline status:** `PASS_OFFLINE_EVALUATION`  
**Final integrity:** `PASS_FINAL_INTEGRITY_VALIDATION`  
**Optional 3D visualization:** `DEFERRED_OPTIONAL`  
**Run ID:** `p4_vb001_office1_full_0_1999_r01`

## Experiment identity and provenance

| Item | Verified value |
|---|---|
| Dataset / scene | Replica `office1` |
| Frame range | 0–1999 inclusive; 2,000 frames |
| Frozen worktree | `/home/robot/research/SGS_slam_phase4_multiscene` |
| Frozen source commit | `68f9060f7ff4d8d141be1d5f71339401327edd06` |
| `scripts/slam.py` SHA256 | `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3` |
| Online config SHA256 | `1729185d0f8ab8a148d7f0ba1ba7e3e36ae8f5c737acfb2204376442a7165dfb` |
| E4 config SHA256 | `1b4e9c08b2f688794b3218a0366a0550e5b4c593c0558455a708fdda02bf7626` |
| Seed | 0 |

The released Phase 4 Variant B CPU Keyframe Offload implementation and algorithm parameters were preserved. This is a single-scene result; cross-scene differences are descriptive and do not constitute a controlled comparison.

## Dataset and evaluation protocol

Office1 provides 2,000 ordered RGB, depth, semantic-ID, semantic-color, and instance-color files and 2,000 finite camera poses. The evaluation uses the 401 E4 training views `{0} ∪ {5k−1 | k=1..400}` at 1200×680. The trajectory metrics use all 2,000 saved camera poses.

Image, depth, and semantic values below are the unweighted means of their 401 per-view E4 values. Standard Depth RMSE is calculated separately as per-frame `sqrt(mean((rendered_depth−GT_depth)^2))` over pixels where GT depth is positive, followed by an unweighted mean over the 401 views. Trajectory alignment uses Horn rigid alignment with no scale correction. The aligned ATE mean and true RMSE are separate aggregates.

## Final quality metrics

| Metric | Result | Scope / definition |
|---|---:|---|
| PSNR | 39.432348237073334 dB | 401 E4 training views |
| MS-SSIM | 0.9826767333130587 | 401 views; E4 `ssim.txt` is MS-SSIM |
| LPIPS-Alex | 0.09379343187756967 | 401 E4 training views |
| Depth L1 | 0.0029153336996985994 m | 401 E4 views |
| Standard Depth RMSE | 0.015814388257670755 m (1.5814388257670755 cm) | 401 supplementary per-view RMSE values; GT depth > 0 mask |
| Aligned ATE mean | 0.0019245655435345093 m (0.19245655435345094 cm) | Mean aligned translation error over 2,000 poses |
| True aligned ATE RMSE | 0.0021758263025428584 m (0.21758263025428584 cm) | Root mean square aligned translation error over 2,000 poses |
| Semantic-color mIoU | 0.9509944874842283 | 401 views; released GT-palette-assisted color protocol |

The released E4 `rmse.txt` values equal `l1.txt` exactly. The implementation therefore reports masked Depth L1 under the `rmse.txt` filename; those values are **not** conventional standard Depth RMSE. Standard RMSE is the independently rendered supplementary measurement above. Semantic-color mIoU uses the released GT-palette-assisted recoloring protocol and is not class-ID mIoU. The released image metric is MS-SSIM, not single-scale SSIM.

## Runtime, memory, and model size

| Measurement | Result | Scope |
|---|---:|---|
| Online process wall time | 15,728.539716726009 s | Full online runner process |
| End-to-end FPS | 0.12715738625583686 | 2,000 frames / process wall time |
| Tracking average / reciprocal throughput | 3.1307195452451704 s/frame / 0.31941538855461066 FPS | Online source log |
| Mapping average / reciprocal throughput | 4.604963395357132 s/frame / 0.21715699217245274 FPS | Online source log |
| PyTorch peak allocated / reserved | 6,457,900,544 / 8,359,247,872 bytes | Worker allocator during `rgbd_slam` and synchronization |
| NVML sampled device-wide peak | 9,179 MiB | 15,272 approximately one-second GPU-wide samples |
| Final Gaussian count | 5,549,520 | Validated checkpoint |
| Keyframe count | 402 | Validated checkpoint indices |

Frozen source does not separately instrument online frame-loop FPS or final checkpoint serialization time. PyTorch allocator peaks and NVML sampled device-wide memory have different scopes and should not be compared as the same measurement.

## Checkpoint and final integrity

- Online status `CORE_ARTIFACTS_VALIDATED`; 2,000/2,000 frames; process exit 0.
- Checkpoint status `PASS_CHECKPOINT_VALIDATION`; NPZ CRC `PASS`; 2,000 camera poses; required state fields finite.
- Final `params.npz` SHA256: `f2bcf577a62655929b066ea0ce05148f64ded7509c27eba88002f5090490704b`.
- Trajectory status `PASS_TRAJECTORY_METRICS`; 2,000 poses; Horn rigid alignment, no scale correction.
- Supplementary Depth RMSE status `PASS_SUPPLEMENTARY_DEPTH_RMSE`; 401 finite frame records; checkpoint SHA256 unchanged before/after.
- Offline status `PASS_OFFLINE_EVALUATION` with no listed blockers.
- Final integrity status `PASS_FINAL_INTEGRITY_VALIDATION`.
- All six E4 metric arrays contain 401 finite entries; rendered RGB, depth, semantic, and plots each contain the exact 401 expected frame files.
- Original E4 manifest: 1,612 expected files, 1,612 size/SHA256 matches, 0 missing, 0 changed. Manifest SHA256: `c2593a47f764f04caa7f565c7188f89c2b97f8ba4efe4d207ee5c93f451a31ba`.

Manifest verification covered exactly its original E4 entries. Supplementary outputs created later were excluded. No failed checks or blockers remain in the final status record.

## Artifact paths and preservation

All runtime artifacts remain in the frozen worktree and were preserved in place:

- Model/checkpoint: `/home/robot/research/SGS_slam_phase4_multiscene/experiments/Replica/p4_vb001_office1_full_0_1999_r01/`
- Online metadata, checkpoint validation, telemetry, logs, and artifact manifest: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/p4_vb001_office1_full_0_1999_r01/`
- E4 output: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/offline_eval/p4_vb001_office1_full_0_1999_r01_offline_eval/`
- Final supplementary JSON: E4 `supplementary/trajectory_metrics.json`, `evaluation_metrics.json`, `final_integrity_validation.json`, and `evaluation_status_final.json`.
- Supplementary standard Depth RMSE evidence: E4 `supplementary/depth_rmse_supplementary/`.

Raw online, E4, and supplementary rendering evidence was not overwritten or moved. The protected Room0, Room1, Room2, and Office0 checkpoint SHA256 values were freshly rechecked as `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`, `3ab49193b0a1160405ff90ee6387a8e06c713c127c1e2bf2f1ca9cdf1b0443f4`, `d772e65a3c0bc163cf20960d30bd0b88f9182477462f9c1fe8dadd0a86155c3f`, and `6d0f180d7677a38c29295ae9ffc10d745f726aac700f40338543a062a9bf7390`, respectively. Phase 5/6/7 records remain independent and unchanged.

## Limitations

- This is one Office1 run and is not a statistically controlled comparison with another scene or baseline.
- No Office1-specific matched full-scene baseline comparison is established.
- Standard Depth RMSE is supplementary; the released `rmse.txt` filename is misleading because it equals Depth L1.
- Semantic-color mIoU uses the GT-palette-assisted released protocol, not direct class-ID prediction.
- Online frame-loop FPS and checkpoint serialization duration were not separately instrumented.
- Optional 3D visualization is deferred and is not required for this numerical closure.

## Closure verdict

Office1 is `CLOSED_EVALUATED` for Phase 4 Variant B. Optional visualization is `DEFERRED_OPTIONAL`. The remaining Phase 4 Replica multiscene scenes are **office2, office3, and office4**. This closure does not complete the full multiscene campaign or start another scene.
