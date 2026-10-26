# Phase 4 Variant B — Replica Room2 Final Results

**Experiment status: `CLOSED_EVALUATED`.** Offline status is
`PASS_OFFLINE_EVALUATION` per the final integrity record. Optional 3D
visualization remains `DEFERRED_OPTIONAL`. This closes Room2 only; the complete
eight-scene Replica extension remains unfinished.

## Identity and provenance

| Field | Value |
|---|---|
| Run | `p4_vb001_room2_full_0_1999_r01` |
| Dataset | Replica `room2`; `/home/robot/research/SGS_slam/data/Replica/room2` |
| Frame range | 0–1999 (2000 frames) |
| Frozen worktree | `/home/robot/research/SGS_slam_phase4_multiscene` (detached) |
| Source commit | `68f9060f7ff4d8d141be1d5f71339401327edd06` |
| `scripts/slam.py` SHA256 | `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3` |
| Effective online config SHA256 | `02ac9bc54bdf7c7d018a44fe43b39584a80d7e61c5c023509b12aab2dcfc022c` |
| E4 config SHA256 | `635e347e829f6db38d7458599d3405b59ee7ab3c1c73e2b1b7ab3674615375cd` |
| Base `configs/replica/slam.py` SHA256 | `08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3` |
| Dataset camera config SHA256 | `4c1e33544bef24c146c4ec9a622bb3ad7a314168db8d192c191db08bad3edf58` |
| E4 implementation SHA256 | `utils/eval_helpers.py`: `e94366ca256ec2b51b5d0264a5daba2a895cc0375d7b91e976e4ea0e9e28194e` |
| Checkpoint SHA256 | `d772e65a3c0bc163cf20960d30bd0b88f9182477462f9c1fe8dadd0a86155c3f` |
| Checkpoint size / integrity | 363,364,185 bytes; NPZ CRC `PASS`; `PASS_CHECKPOINT_VALIDATION` |

The checkpoint validator reports 2,000 camera poses and finite required arrays.
Online metadata records exit code 0, 2,000/2,000 validated frames, failure
classification `NONE`, and completion `CORE_ARTIFACTS_VALIDATED`. The 11-entry
online artifact manifest was independently hash-checked using its separate
`evidence` and `model` roots; all 11 entries matched. Checkpoint SHA256 matches
the online manifest, checkpoint validation, and supplementary before/after
records.

## Final metrics

Image/depth/semantic metrics are unweighted means over 401 E4 training views;
trajectory metrics use all 2,000 poses.

| Metric | Result | Scope and interpretation |
|---|---:|---|
| PSNR | 35.08130356082298 dB | 401 sampled training views |
| MS-SSIM | 0.9833379945255575 | E4 `ssim.txt` stores MS-SSIM; single-scale SSIM is unavailable |
| LPIPS-Alex | 0.07416503871802677 | 401 sampled training views |
| Depth L1 | 0.00573806987524943 m (0.573806987524943 cm) | GT depth > 0 mask; mean of per-view masked L1 values |
| Standard Depth RMSE | 0.04636771678851954 m (4.636771678851954 cm) | Supplementary numerical depth render; per-view pixel RMSE, then unweighted mean of 401 values |
| Aligned ATE mean | 0.002571350682804283 m (0.2571350682804283 cm) | 2,000 aligned translation errors; Horn rigid alignment, no scale |
| True aligned ATE RMSE | 0.0027287721506437973 m (0.27287721506437973 cm) | Square root of mean squared aligned translation errors over the same 2,000 poses |
| Semantic-color mIoU | 0.9162398735108886 | GT-palette-assisted color matching, per-frame scoring and unweighted frame mean; not class-ID confusion-matrix mIoU |

The released E4 `rmse.txt` is mislabeled for standard RMSE: it is byte
identical to `l1.txt` (SHA256
`b4aa9b6c717143dd298e790ace14c2019421d045cea5f9341162d4091b19a8ce`) and
the frozen implementation computes mean absolute depth error. The standard
Depth RMSE above is separate, computed per view as
`sqrt(mean((predicted_depth_m - GT_depth_m)^2))` over valid GT depth pixels,
then averaged without weighting across 401 views. Its CSV has 401 finite rows
and independently recomputes to 0.04636771678851953 m; the final-digit
difference from JSON is floating-point summation order. This is not a pooled
all-pixel RMSE.

Semantic-color mIoU uses rendered learned semantic colors and each frame's GT
color palette to map colors, ignores black/unlabeled GT, averages IoU over
present non-black colors per frame, then averages the 401 frame scores. It is
not categorical semantic-ID mIoU.

## Evaluation protocol and integrity

E4 uses `eval_every=5` and the frozen evaluator's frame condition, yielding
`{0} ∪ {5k−1 | k=1..400}`: 401 sampled training views at 1200×680. Each E4
metric array for PSNR, MS-SSIM, LPIPS-Alex, Depth L1, mislabeled depth RMSE,
and semantic-color mIoU contains 401 finite values. RGB, depth, semantic, and
plot output sets each contain 401 readable images. The separate trajectory
record contains 2,000 finite aligned errors.

The final records `supplementary/evaluation_status_final.json` and
`supplementary/final_integrity_validation.json` both report
`PASS_OFFLINE_EVALUATION`. They record unchanged original E4 metric hashes,
unchanged checkpoint SHA256, online manifest integrity, finite supplementary
depth rows, the verified RMSE formula/aggregate, and no observed CUDA OOM. E4
process exit code and stdout/stderr were not retained; completion is evidenced
by complete finite metric arrays and render sets, not a claimed exit code.

The supplementary helper's initial status was
`PARTIAL_SUPPLEMENTARY_DEPTH_RMSE`. Its directory-wide integrity comparison
included the helper's own newly created supplementary output subtree and thus
reported a self-inclusion false positive. Original E4 metric/config hashes
remained unchanged. Final independent integrity validation checked the
original hashes, all 401 supplementary rows and aggregate, and resolved the
status to `PASS_OFFLINE_EVALUATION`. The original partial status and execution
evidence remain preserved; no retry occurred.

## Runtime and GPU memory

| Measurement | Result | Scope |
|---|---:|---|
| Online process wall-clock | 17,895.405414523004 s | Runner wall time for the 2,000-frame process |
| End-to-end SLAM FPS | 0.11176053035249492 | 2,000 frames / process wall-clock |
| Online-loop FPS | `NOT_AVAILABLE` | Not separately instrumented in frozen source |
| Tracking average / reciprocal throughput | 3.494788026213646 s/frame / 0.2861403874853688 FPS | Source log stage average and reciprocal, not whole-system FPS |
| Mapping average / reciprocal throughput | 5.313655699849129 s/frame / 0.1881943536590813 FPS | Source log stage average and reciprocal, not whole-system FPS |
| NVML sampled peak | 9,341 MiB of 16,303 MiB | GPU-wide sampled memory; 17,379 samples at 1 s interval |
| PyTorch peak allocated | 6,737,296,384 bytes | Worker allocator window around `rgbd_slam` |
| PyTorch peak reserved | 8,529,117,184 bytes | Same allocator window; distinct from NVML |
| Final Gaussians / keyframes | 5,587,273 / 402 | Validated checkpoint and run metadata |

Checkpoint serialization duration was not separately instrumented.
Tracking/mapping reciprocal values are stage summaries, not substitutes for
end-to-end FPS.

## Artifact inventory

- Model/checkpoint: `/home/robot/research/SGS_slam_phase4_multiscene/experiments/Replica/p4_vb001_room2_full_0_1999_r01/` (`params.npz`, `params.ply`, `seg_params.ply`, `keyframe_time_indices.npy`, config snapshot).
- Online evidence: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/p4_vb001_room2_full_0_1999_r01/` (`run_metadata.json`, `checkpoint_validation.json`, `artifact_manifest.json`, `effective_config.json`, `gpu_telemetry.csv`, `performance_summary.json`, `stdout_stderr.log`).
- Original E4 output: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/offline_eval/p4_vb001_room2_full_0_1999_r01_offline_eval/eval_train/`.
- Supplementary evaluation and final integrity: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/offline_eval/p4_vb001_room2_full_0_1999_r01_offline_eval/supplementary/` (`evaluation_metrics.json`, `trajectory_metrics.json`, `depth_rmse_supplementary/depth_rmse_per_frame.csv`, `depth_rmse_summary.json`, `evaluation_status_final.json`, `final_integrity_validation.json`).
- Preceding offline evidence report: `docs/research/phase4_multiscene/PHASE4_ROOM2_OFFLINE_EVALUATION_REPORT.md`.

## Limitations and interpretation

- These are one-scene results for Phase 4 Variant B; Room1 and Room0 are
  separate experiments. Cross-scene metric differences alone do not establish
  a method improvement or causal effect.
- E4 process exit status and stdout/stderr are unavailable. Final offline PASS
  is based on validated artifacts and final integrity records.
- Single-scale SSIM is unavailable; the reported structural metric is
  MS-SSIM. E4 `rmse.txt` is an L1 value; only the separate supplementary render
  provides standard Depth RMSE.
- Semantic-color mIoU is GT-palette-assisted, not class-ID mIoU.
- No 3D visualization was run; it remains `DEFERRED_OPTIONAL`.
- No SLAM, evaluation, or visualization was rerun for archival. No checkpoint
  or algorithm source was changed; no commit, push, or upload occurred.
