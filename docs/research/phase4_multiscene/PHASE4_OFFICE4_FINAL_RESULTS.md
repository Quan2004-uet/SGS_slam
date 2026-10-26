# Phase 4 Variant B — Replica Office4 Final Results

**Experiment:** `p4_vb001_office4_full_0_1999_r01`
**Status:** `CLOSED_EVALUATED`
**Online:** `CORE_ARTIFACTS_VALIDATED`
**Checkpoint:** `PASS_CHECKPOINT_VALIDATION` (NPZ CRC `PASS`)
**Offline evidence:** `PASS_OFFLINE_EVALUATION`; final Gate 5.1 integrity `PASS`
**Optional 3D visualization:** `DEFERRED_OPTIONAL`

## Experiment identity and frozen source

| Item | Verified value |
|---|---|
| Dataset | Replica `office4`, 2,000 frames, 0–1999 inclusive |
| Run ID | `p4_vb001_office4_full_0_1999_r01` |
| Frozen worktree commit | `68f9060f7ff4d8d141be1d5f71339401327edd06` |
| Frozen `scripts/slam.py` SHA256 | `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3` |
| Online config SHA256 | `92a0a54660ed71b0f618521941f06b1e221d62ee3a25c07fcefe89484fc39ca8` |
| Saved-state E4 config SHA256 | `0cc073433dae43413987d200262f74abfb4757a653df738e461b8a8f381a65b2` |
| Seed / image size | 0 / 1200×680 |
| Replica depth scale | 6553.5 |

This is the frozen Phase 4 Variant B CPU Keyframe Offload experiment. Office4 effective online/E4 configuration parity with the validated Office3 protocol is recorded in the Office4 preparation report: scene/run/checkpoint identities changed as required; scientific and algorithmic settings remained fixed. No algorithm source, config, checkpoint, online artifact, or E4 artifact was changed during closure.

## Dataset and evaluation protocol

Online SLAM processed frames 0–1999 (2,000/2,000). E4 uses saved-state training-view evaluation with `eval_every=5`, producing frame IDs `{0} ∪ {5k−1 | k=1..400}` for 401 image/depth/semantic views. Trajectory metrics use all 2,000 matched poses. Standard Depth RMSE uses, per view, `sqrt(mean((prediction−GT)^2))` over GT depth > 0, followed by an unweighted arithmetic mean over 401 views. ATE uses Horn rigid alignment without scale correction.

## Final quality metrics

| Metric | Office4 result | Scope / definition |
|---|---:|---|
| PSNR | 31.98514147351805 dB | Mean over 401 E4 views |
| MS-SSIM | 0.9481332642479133 | Mean over 401 E4 views |
| LPIPS-Alex | 0.15473074450197066 | Mean over 401 E4 views |
| Depth L1 | 0.013629693485984574 m | Mean over 401 E4 views |
| Standard Depth RMSE | 0.07042747174302234 m | Per-view masked RMSE, then unweighted mean over 401 views |
| Aligned ATE mean | 0.005827276646533747 m | Mean aligned translation error over 2,000 poses |
| True aligned ATE RMSE | 0.0065538699635214704 m | RMS aligned translation error over 2,000 poses |
| Semantic-color mIoU | 0.8949128346457764 | Released GT-palette-assisted exact-color IoU, averaged over 401 views |

## Runtime, memory and model size

| Measure | Result | Measurement scope |
|---|---:|---|
| Full process wall time | 14,896.24389675702 s | Complete online runner process |
| End-to-end FPS | 0.13426203369531356 | 2,000 frames / process wall time |
| Tracking average / reciprocal throughput | 3.065659881711006 s/frame / 0.3261940458449944 FPS | Source-log average |
| Mapping average / reciprocal throughput | 4.2547724332809445 s/frame / 0.23503019625161925 FPS | Source-log average |
| PyTorch peak allocated | 6,389,555,200 bytes | Worker allocator around `rgbd_slam` call |
| PyTorch peak reserved | 8,065,646,592 bytes | Same allocator scope |
| NVML sampled device-wide peak | 8,819 MiB | 14,464 one-second GPU-wide samples |
| Final Gaussians | 5,244,062 | Checkpoint, PLY and online metadata |
| Keyframes | 402 | Embedded list and sidecar agree |

PyTorch allocator peaks and NVML device-wide sampled usage are different measurements. End-to-end FPS includes process wall time and is not tracking FPS. Office4 versus another scene is a cross-scene observation, not a controlled speedup claim.

## Checkpoint and E4 integrity

The final checkpoint is `/home/robot/research/SGS_slam_phase4_multiscene/experiments/Replica/p4_vb001_office4_full_0_1999_r01/params.npz`, SHA256 `5ad2f28b79a8e1868fcb3ab6dc234f867e8ceeba03e0a5a974e59383f7f9263c`. Online validation reports `PASS_CHECKPOINT_VALIDATION`, NPZ CRC `PASS`, 2,000 camera poses, 5,244,062 Gaussians, and 402 keyframes. The online artifact manifest verifies 11/11 entries, including both PLYs and the keyframe sidecar.

All six E4 metric arrays contain 401 finite values. `rendered_rgb`, `rendered_depth`, `rendered_seg`, and `plots` each contain 401 PNGs with exact E4 frame IDs; `metrics.png` is the additional summary image. The original E4 manifest SHA256 is `7b3c6e4d8d35268ebf1cf5edb730b19e9921dbca3d250cd472bae7d361572e7d`; all 1,612 entries match recorded size and SHA256, with zero missing, changed, or unlisted original-scope files. Supplementary files are outside the original manifest comparison.

Supplementary Depth RMSE is `PASS_SUPPLEMENTARY_DEPTH_RMSE`, 401/401 views. Its CSV arithmetic mean is `0.07042747174302232 m`, within floating-point summation error of the summary value. The supplementary evaluator took 14.18448802101193 s and recorded PyTorch allocated/reserved peaks of 1,536,239,104 / 3,122,659,328 bytes (no CUDA OOM); these figures are separate from the online run. The summary confirms the checkpoint hash and original E4 manifest remained unchanged. Trajectory status is `PASS_TRAJECTORY_METRICS`, with 2,000 finite errors and matching checkpoint SHA256.

## Metric caveats and limitations

- E4 `rmse.txt` is byte-identical to Depth L1 (`l1.txt`), so it is not conventional standard Depth RMSE. The conventional value above comes from the separate supplementary evaluator.
- The released `evaluate_ate` scalar is mean aligned translation error, not mathematical RMSE. The true RMS value above is independently computed from the 2,000 per-pose aligned errors.
- Semantic-color mIoU uses GT-palette-assisted exact-color comparison and excludes unlabeled black pixels; it is not direct semantic-ID classification mIoU.
- E4 process exit code/stdout/stderr were not recorded in the retained artifacts. The metrics, render groups, original manifest, and supplementary evidence were verified directly; no E4 exit code is inferred.
- The 401 E4 outputs are sampled training views, not 2,000 rendered images or held-out novel-view results.
- Runtime and memory comparisons across scenes are uncontrolled cross-scene comparisons.
- Optional 3D visualization is deferred and not required for this numerical closure.

## Artifact paths and preservation

- Checkpoint and PLYs: `/home/robot/research/SGS_slam_phase4_multiscene/experiments/Replica/p4_vb001_office4_full_0_1999_r01/`
- Online metadata, logs and telemetry: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/p4_vb001_office4_full_0_1999_r01/`
- E4 and supplementary evidence: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/offline_eval/p4_vb001_office4_full_0_1999_r01_offline_eval/`
- Detailed audit: `docs/research/phase4_multiscene/PHASE4_OFFICE4_OFFLINE_EVALUATION_REPORT.md`

## Final closure verdict

All required Gate 5.1 integrity checks pass. Replica Office4 is `CLOSED_EVALUATED`; optional 3D visualization is `DEFERRED_OPTIONAL`. The previously evaluated Replica room0 record plus Room1, Room2, and Office0–Office4 account for the eight-scene experiment inventory; no Phase 4 Replica scenes remain. This local archival does not modify prior scene artifacts or Phase 5/6/7 state, and does not represent remote publication.
