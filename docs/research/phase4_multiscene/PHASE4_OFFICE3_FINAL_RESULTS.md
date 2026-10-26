# Phase 4 Variant B — Replica Office3 Final Results

**Experiment:** `p4_vb001_office3_full_0_1999_r01`
**Status:** `CLOSED_EVALUATED`
**Online:** `CORE_ARTIFACTS_VALIDATED`
**Checkpoint:** `PASS_CHECKPOINT_VALIDATION` (NPZ CRC `PASS`)
**Offline evidence:** `PASS` (independently reconciled from preserved E4 and supplementary artifacts)
**Optional 3D visualization:** `DEFERRED_OPTIONAL`

## Identity and provenance

| Item | Verified value |
|---|---|
| Dataset | Replica `office3`, 2,000 frames, 0–1999 inclusive |
| Frozen worktree commit | `68f9060f7ff4d8d141be1d5f71339401327edd06` |
| Frozen `scripts/slam.py` SHA256 | `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3` |
| Online config SHA256 | `3c53069d2c35917675ff755d52dfd9a43ce7ba46b44605fc93d57d6381633f9f` |
| Saved-state E4 config SHA256 | `90501711e2f2c24b05b6c1c0dbd9fac9dc5f3438593df341279783c3b04e844e` |
| Seed | 0 |
| Run output | Frozen worktree `experiments/Replica/p4_vb001_office3_full_0_1999_r01/` |

`VERIFIED_SOURCE`: CPU Keyframe Offload experiment source remained frozen. `VERIFIED_CONFIG`: effective online config matches Office2 after scene/run identity normalization. E4 config also changes only the expected run/scene/checkpoint identity and preserves saved-state evaluation, 1200×680 resolution, Replica depth scale 6553.5, and `eval_every=5`.

## Evaluation protocol and quality

E4 image, depth, and semantic metrics are means across the 401 training views `{0} ∪ {5k−1 | k=1..400}` at 1200×680. Trajectory metrics use all 2,000 matched camera poses. The saved-state trajectory was aligned by Horn rigid alignment without scale correction.

| Metric | Office3 result | Evaluation scope and definition |
|---|---:|---|
| PSNR | 29.992374439191938 dB | Mean over 401 E4 views |
| MS-SSIM | 0.9503379866963907 | Mean over 401 views; E4 `ssim.txt` |
| LPIPS-Alex | 0.11827323098952633 | Mean over 401 E4 views |
| Depth L1 | 0.014195865046864658 m | Mean over 401 E4 views |
| Standard Depth RMSE | 0.0853922480437391 m | Per-view RMSE over pixels with GT depth > 0, then unweighted mean over 401 views |
| Aligned ATE mean | 0.003248163677829446 m | Mean aligned translation error over 2,000 poses |
| True aligned ATE RMSE | 0.003592273487731734 m | Square root of mean squared aligned translation error over 2,000 poses |
| Semantic-color mIoU | 0.8436161550655589 | Mean of released GT-palette-assisted color IoU over 401 views |

The depth summary and per-frame CSV contain 401 views; independently recomputed CSV mean agrees with the reported standard RMSE. The trajectory record contains 2,000 finite errors and its checkpoint SHA matches the final checkpoint. As an independent GT provenance check, the frozen Replica relative-pose convention applied to `office3/traj.txt` agrees with checkpoint `gt_w2c_all_frames` within maximum absolute difference `8.399078832432849e-7`.

## Runtime, memory, and model

| Measure | Result | Scope |
|---|---:|---|
| Online process wall time | 14,158.963376194995 s | Full runner process |
| End-to-end FPS | 0.1412532787084212 | 2,000 frames divided by process wall |
| Tracking average / reciprocal throughput | 2.9503237673044205 s/frame / 0.33894585098829866 FPS | Frozen source-log averages |
| Mapping average / reciprocal throughput | 4.004411844134331 s/frame / 0.24972456353728995 FPS | Frozen source-log averages |
| PyTorch peak allocated | 6,299,927,552 bytes | Worker CUDA allocator, `rgbd_slam` call through return/sync attempt |
| PyTorch peak reserved | 8,197,767,168 bytes | Same allocator scope |
| NVML sampled GPU-wide peak | 9,025 MiB | Device-wide, 13,747 samples, RTX 5080 |
| Final Gaussians | 5,116,198 | Checkpoint and PLY validation |
| Keyframes | 402 | Embedded and sidecar indices agree |

PyTorch allocator peaks and device-wide NVML samples have different measurement scopes. The run is a single-scene result; cross-scene runtime or memory differences do not establish a controlled speedup.

## Integrity and evidence

- Online metadata: `CORE_ARTIFACTS_VALIDATED`, 2,000/2,000 frames, process exit code 0.
- Checkpoint SHA256: `2c5c30a16ac179d4be37e2ca622945d72c8b16993f4378c331a566349b6ca26c`; checkpoint validation and NPZ CRC pass; 2,000 camera poses are finite.
- Online manifest: 11/11 recorded artifacts verified by size and SHA256. Both PLYs pass recorded hash checks; their vertex count is 5,116,198.
- E4 metrics: six arrays with 401 finite values each. Rendered RGB, depth, semantic, and plot directories each contain 401 PNGs.
- Original E4 manifest: 1,612 entries, 1,612 verified, 0 missing, 0 changed, 0 unlisted original-scope files. Manifest SHA256: `0a329f1add7e656c64027cc99cac176d6cea1ba2fa3a66307701169097dc7123`.
- Supplementary Depth RMSE: `PASS_SUPPLEMENTARY_DEPTH_RMSE`, 401/401 records; checkpoint and original E4 manifest unchanged before/after.
- Trajectory: `PASS_TRAJECTORY_METRICS`, 2,000 poses, Horn rigid/no-scale; checkpoint hash matches.

`E4 rmse.txt` is byte-identical to `l1.txt`, so its value is Depth L1, not conventional standard Depth RMSE. The released E4 ATE label is an aligned mean scalar and is not substituted for the independently computed true ATE RMSE. Semantic mIoU uses GT-palette-assisted exact-color comparison, not direct semantic-ID classification. E4 process exit code/stdout/stderr were not retained (`NOT_VERIFIED`); completion evidence is the fully verified arrays, images, and original-file manifest.

## Artifact locations and preservation

- Checkpoint and PLYs: `/home/robot/research/SGS_slam_phase4_multiscene/experiments/Replica/p4_vb001_office3_full_0_1999_r01/`
- Online logs, metadata, performance and telemetry: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/p4_vb001_office3_full_0_1999_r01/`
- E4 renders and supplementary evidence: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/offline_eval/p4_vb001_office3_full_0_1999_r01_offline_eval/`
- Detailed offline audit: [Office3 offline evaluation and Gate 5 audit](PHASE4_OFFICE3_OFFLINE_EVALUATION_REPORT.md)

Raw frozen-worktree evidence was read only in this closure task. Project-state changes are limited to the Office3 closure record and do not change Room0–Room2, Office0–Office2, or Phase 5/6/7 evidence. Office3 visualization remains optional and deferred. **Office4 is the only remaining Phase 4 multiscene scene; the overall multiscene campaign is not complete.**
