# Phase 4 / Phase 6 / Phase 7 Comparison — Replica room1 and room0

R1 run p7_bcgm_r1_full_room1_on_0_1999_r01: room1 0–1999, seed 0, 1200x680, 401 evaluation IDs. Phase 4 room1 run p4_vb001_room1_full_0_1999_r01 is primary same-scene reference. Phase 6 room1 run p6_bam_ms_room1_gate3_0_1999_r01 includes BAM/adaptive mapping. Phase 7 room0 is a different scene. Evaluator helper SHA256 matches across Phase 4, Phase 6 and R1: e94366ca256ec2b51b5d0264a5daba2a895cc0375d7b91e976e4ea0e9e28194e.

All deltas below are R1 room1 minus reference. These are descriptive single-run observations, not causal estimates.

## Phase 4 room1

| Metric | Reference | R1 room1 | Delta (R1 - ref) |
|---|---:|---:|---:|
| PSNR (dB) | 33.936226847 | 33.326330803 | -0.609896044 |
| MS-SSIM | 0.969905490 | 0.968103481 | -0.001802009 |
| LPIPS | 0.097438466 | 0.107388632 | +0.009950166 |
| Depth L1 (m) | 0.004363715 | 0.005512088 | +0.001148374 |
| Semantic mIoU | 0.923663420 | 0.919729327 | -0.003934092 |
| ATE Mean (m) | 0.004262121 | 0.005537752 | +0.001275632 |
| ATE RMSE (m) | 0.004411848 | 0.005674387 | +0.001262539 |
| Runtime (s) | 18472.333262 | 14564.629470 | -3907.703792 |
| E2E FPS | 0.108270 | 0.137319 | +0.029049 |
| Tracking FPS | 0.255513 | 0.339028 | +0.083516 |
| Mapping FPS | 0.193200 | 0.248121 | +0.054921 |
| CUDA allocated (B) | 8,066,530,816 | 5,628,716,544 | -2,437,814,272 |
| CUDA reserved (B) | 10,626,269,184 | 7,761,559,552 | -2,864,709,632 |
| NVML peak (MiB) | 11,341 | 10,355 | -986 |
| Gaussians | 6,663,167 | 4,498,964 | -2,164,203 |

Phase 4 shares scene/horizon/seed/resolution, CPU Keyframe Offload lineage and 401-view evaluator protocol. Quality metrics have strong protocol comparability; trajectory values use rigid alignment without scale. Runtime is limited: Phase 4’s offline evaluation took a separate 370.505805 s, whereas R1 wrapper wall includes its in-run evaluation/save path. Do not claim a matched speedup. CUDA allocator peaks are process allocator metrics; NVML is device-wide sampled memory; run-time background/process conditions also differ. Do not equate these memory values.

## Phase 6 room1

| Metric | Reference | R1 room1 | Delta (R1 - ref) |
|---|---:|---:|---:|
| PSNR (dB) | 34.096186264 | 33.326330803 | -0.769855461 |
| MS-SSIM | 0.971436200 | 0.968103481 | -0.003332719 |
| LPIPS | 0.091352461 | 0.107388632 | +0.016036171 |
| Depth L1 (m) | 0.004393708 | 0.005512088 | +0.001118380 |
| Semantic mIoU | 0.926535421 | 0.919729327 | -0.006806093 |
| ATE Mean (m) | 0.004655331 | 0.005537752 | +0.000882421 |
| ATE RMSE (m) | 0.004802019 | 0.005674387 | +0.000872368 |

Same scene and nominal horizon/evaluator source, but BAM/adaptive mapping is enabled in Phase 6. This is a method comparison with a confound, not a BCGM-only ablation. No Phase 6 performance/memory delta is asserted here.

## Phase 7 room0

| Metric | Reference | R1 room1 | Delta (R1 - ref) |
|---|---:|---:|---:|
| PSNR (dB) | 32.444045252 | 33.326330803 | +0.882285551 |
| MS-SSIM | 0.975780540 | 0.968103481 | -0.007677059 |
| LPIPS | 0.076533440 | 0.107388632 | +0.030855192 |
| Depth L1 (m) | 0.005907558 | 0.005512088 | -0.000395470 |
| Semantic mIoU | 0.913442026 | 0.919729327 | +0.006287301 |
| ATE Mean (m) | 0.002489759 | 0.005537752 | +0.003047993 |
| ATE RMSE (m) | 0.003249278 | 0.005674387 | +0.002425109 |
| Runtime (s) | 14165.030218 | 14564.629470 | +399.599252 |
| E2E FPS | 0.141193 | 0.137319 | -0.003874 |
| Tracking FPS | 0.347069 | 0.339028 | -0.008041 |
| Mapping FPS | 0.256793 | 0.248121 | -0.008671 |
| CUDA allocated (B) | 5,442,630,656 | 5,628,716,544 | +186,085,888 |
| CUDA reserved (B) | 6,784,286,720 | 7,761,559,552 | +977,272,832 |
| NVML peak (MiB) | 7,684 | 10,355 | +2,671 |
| Gaussians | 4,499,583 | 4,498,964 | -619 |

Same Phase 7 method/config family but different scene. It is cross-scene descriptive evidence, not a paired estimate.

## Metric and evidence limitations

ssim.txt is MS-SSIM (source calls ms_ssim). R1 rmse.txt equals l1.txt and does not establish true Depth RMSE. Evaluator console “Final Average ATE RMSE” reports mean aligned translation residual; R1 offline true ATE RMSE is separate. Evaluation covers 401 sampled views. One seed/run per condition means no uncertainty interval or significance claim. LPIPS is better lower; PSNR/MS-SSIM/mIoU better higher; Depth L1 and ATE better lower.
