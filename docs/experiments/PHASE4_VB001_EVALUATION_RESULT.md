# PHASE4-VB-001 Full Released Evaluation Result

## Experiment identity

- Date: 2026-10-11.
- Gate: PHASE4-VB-001 Evaluation Gate E4.
- Status: `PASS_EVAL_E4_FULL_RELEASED`.
- Branch: `phase4-vb-001-cpu-keyframe-offload`.
- Evaluation HEAD: `63adf3aed8ae2201a46d11cec473672f9e91fd0e`.
- Dataset/scene: Replica `room0`, 2,000 frames, 1200 × 680.
- GPU: NVIDIA GeForce RTX 5080, 16,609,378,304 physical bytes.
- Python/PyTorch/CUDA runtime: 3.10.22 / 2.7.1+cu128 / 12.8.

## Objective and saved-state source

Evaluate the final PHASE4-VB-001 online state using the audited released
training-view protocol without rerunning SLAM or post-SLAM optimization.

Saved state:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`

The NPZ is readable, is 322,361,795 bytes, and has SHA256
`dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`.
It contains 4,956,467 Gaussians, 2,000 estimated/GT camera frames, semantic
state, intrinsics, first-frame `w2c`, dimensions, and 402 keyframe indices.

## Validation chain

- Full-scene runtime: `PASS_RUNTIME_VALIDATOR_BUG` after correcting the old
  keyframe validator formula.
- Output-save smoke: `PASS_MINIMAL_OUTPUT_SAVE_SMOKE`.
- Telemetry smoke: `PASS_TELEMETRY_OUTPUT_SAVE_SMOKE`.
- Full-scene output save: `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.
- E1 selective load-only: `PASS_EVAL_E1_LOAD_ONLY`.
- E2 frame-0 render: `PASS_EVAL_E2_SINGLE_FRAME_RENDER`.
- E3 frames `[0,4,9,14,19]`: `PASS_EVAL_E3_BOUNDED_SUBSET`.
- E4 full released evaluation: `PASS_EVAL_E4_FULL_RELEASED`.

## Released sampling protocol

Image/depth/semantic metrics use exactly 401 frames:

```text
{0} union {5k - 1 | k=1..400}
= 0, 4, 9, 14, ..., 1989, 1994, 1999
```

No sampled frame was skipped. Trajectory evaluation uses all 2,000 finite
corresponding poses.

## Metric definitions

### RGB

- GT RGB is divided by 255.
- Rendered and GT RGB are multiplied by `GT depth > 0`.
- PSNR uses `utils.slam_external.calc_psnr`.
- The released metric labeled “SSIM” calls `pytorch_msssim.ms_ssim`; it is
  reported here as MS-SSIM.
- LPIPS uses TorchMetrics AlexNet with `normalize=True`; inputs are clamped to
  `[0,1]` as in the released evaluator.
- Aggregates are unweighted means over the 401 sampled frames.

### Depth

- Replica PNG scale is 6553.5, yielding meters.
- Valid pixels satisfy `GT depth > 0`.
- Depth L1 is masked mean absolute error in meters.
- The aggregate is the unweighted mean of frame-level values.

### Semantic

- The renderer uses per-Gaussian `semantic_colors`.
- Each rendered pixel is recolored to the nearest color in the current frame's
  GT semantic palette.
- GT black `[0,0,0]` is ignored.
- Frame mIoU is the mean IoU over non-black GT colors present in that frame;
  overall mIoU is the unweighted mean of frame mIoU values.
- Saved `semantic_ids` are not directly compared with GT IDs.

### Trajectory

- Estimated poses use `cam_unnorm_rots` and `cam_trans` in relative-w2c
  convention.
- Quaternions are normalized and interpreted real-first `[w,x,y,z]`.
- Horn alignment estimates rigid rotation and translation without scale.
- The released scalar is the mean Euclidean aligned translation error. Although
  released output may call it “ATE RMSE”, it is not true RMSE.
- A true RMSE over the same aligned per-frame errors is reported separately as
  a supplementary metric.

## Final metrics

| Metric | Value | Protocol note |
|---|---:|---|
| PSNR | 33.313067 dB | Released `calc_psnr`, 401-frame mean |
| MS-SSIM | 0.979470 | Released “SSIM” is multi-scale SSIM |
| LPIPS | 0.067555 | AlexNet, `normalize=True` |
| Depth L1 m | 0.00495158 m | Masked MAE |
| Depth L1 cm | 0.495158 cm | Same metric converted to cm |
| Semantic mIoU | 0.916585 | Semantic-color palette protocol |
| Released Horn mean translation error m | 0.00274075 m | Mean, not RMSE |
| Supplementary true RMSE m | 0.00339827 m | Same aligned errors |
| Tracking FPS | 0.3354664059815056 | Full online run telemetry |
| Mapping FPS | 0.25086898791330586 | Full online run telemetry |
| Overall SLAM FPS | 0.14110865384985266 | 2,000 / online wall time |
| Peak SLAM GPU allocated | 5,817,509,888 B | Full online run |
| Peak SLAM GPU reserved | 7,189,037,056 B | Full online run |
| Peak evaluation GPU allocated | 1,846,789,120 B | E4 |
| Peak evaluation GPU reserved | 2,057,306,112 B | E4 |

## Evaluation timing and memory

- Total evaluation wall time: 74.41067515600298 s.
- Saved-state load: 0.11304837799980305 s.
- Renderer total: 10.04786258484819 s.
- Metric total: 50.817799856871716 s.
- Trajectory evaluation: 0.01010405299894046 s.
- Evidence serialization: 0.13544405999709852 s.
- Peak GPU allocated/reserved percentages: 11.118953919878155% /
  12.386412509519056%.
- No CUDA OOM or non-finite metric occurred.

Evaluation timing is not SLAM FPS. The online timing values in the table remain
the authoritative SLAM runtime metrics.

## Full-scene runtime context

- Frames 0–1999 completed in 14,173.47515856901 s.
- Final map: 4,956,467 Gaussians.
- Keyframes: 402; tail `[1989,1994,1998,1999]`.
- Process RSS/HWM: 17,960,493,056 B host RAM.
- Final state saving and telemetry completeness: PASS.

## Artifact inventory and checksums

Stable output directory:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/`

| Artifact | Size (bytes) | SHA256 |
|---|---:|---|
| `params.npz` | 322,361,795 | `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2` |
| `params.ply` | 337,040,173 | `d9b4d22ba11c73f8c1d6d0ea5f874bbb5d3254f25b333362a502a5940f604502` |
| `seg_params.ply` | 337,040,173 | `6cd5a258a8147fe0c0515d04ea702d618f82c2411fc464ab9bfebd2fc2f3b726` |
| `keyframe_time_indices.npy` | 3,344 | `fb91f05c127819f6666259668c4d88a2d36a46f575659f576adde37b227e6d37` |

Evidence directories:

- E1: `results/runtime_artifacts/phase4_vb001_eval_e1_load_only/`
- E2: `results/runtime_artifacts/phase4_vb001_eval_e2_single_frame_render/`
- E3: `results/runtime_artifacts/phase4_vb001_eval_e3_bounded_subset/`
- E4: `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/`
- Full output save:
  `results/runtime_artifacts/phase4_vb001_minimal_output_save_full_0_1999/`

The E4 harness was `/tmp/phase4_vb001_eval_e4_full_released.py`, SHA256
`8c31b131e1b294fb0a089589c4f934e1c9912a4969573169f2abe333c847d5e6`.
It selectively loaded renderer-required tensors, retained metadata on CPU where
possible, released frame-local tensors, exported no images, and did not invoke
online SLAM.

## Scientific interpretation and limitations

`RUNTIME VERIFIED`: PHASE4-VB-001 enables full Replica `room0` processing on
the tested RTX 5080 without the unchanged Phase 3 baseline GPU OOM, preserves a
reloadable final state, and completes the audited released-code training-view
evaluation from that state.

The metrics above are reproduced for one scene under the audited released-code
protocol. They do not establish full paper reproduction, superiority over the
paper or baseline, generalization to other Replica scenes, or a benchmark-wide
contribution. No post-SLAM optimization or full qualitative image export was
performed. Paper-table comparability remains to be established separately.

## Next step

Perform a **Paper / Baseline Comparison Audit**: establish exact protocol and
stage comparability, prepare a baseline-versus-PHASE4-VB-001 table, identify
defensible claims, and list remaining scenes/experiments. Do not start VB002 or
new evaluation during this checkpoint.
