# P6-BAM-003-R1 — matched 0–49 V0 / V-A / V-A2 comparison

All three runs used Replica room0, frames 0–49, seed 0, 680×1200 input, 40 tracking iterations, mapping maximum 60, the same keyframe/offload/append/prune/evaluator policy and LIGHT settings. Only the controller budget differs. V0 and V-A are the already-saved P6-BAM-003 runs; neither was rerun. V-A2 uses LOW/MID/FULL=45/60/60 and unchanged novelty thresholds 0.01/0.05. The new configuration was frozen before its single run.

## Execution and resources

| Measure | V0 | V-A | V-A2 | V-A2 vs V0 |
|---|---:|---:|---:|---:|
| Mapping iterations / 3,000 | 3,000 | 1,740 | 2,445 | −18.50% |
| Tier counts FULL/MID/LOW | 50/0/0 | 1/14/35 | 1/12/37 | — |
| Process wall (s) | 192.27 | 143.28 | 170.49 | −11.33% |
| LIGHT profiler wall (s) | 189.44 | 140.44 | 167.67 | — |
| Mapping optimization-loop wall (s) | 104.714 | 58.127 | 83.585 | −20.18% |
| Tracking wall (s) | 68.828 | 66.844 | 68.211 | −0.90% |
| Peak allocated / reserved GPU (GB, decimal) | 2.109 / 2.720 | 2.119 / 2.617 | 2.203 / 2.970 | +4.49% / +9.19% |
| Process peak RSS (GB, decimal) | 4.022 | 4.065 | 4.066 | +1.08% |
| Sampled process HWM (GB, decimal) | 2.520 | 2.466 | 2.480 | −1.57% |
| CPU archive logical bytes | 313,344,000 | 313,344,000 | 313,344,000 | same |
| H2D events / cumulative bytes | 2,371 / 61.912 GB | 1,341 / 35.016 GB | 1,906 / 49.769 GB | −19.61% bytes |
| Final Gaussians | 1,122,223 | 1,122,614 | 1,121,742 | −481 (−0.043%) |
| Keyframes | 12, same IDs | 12, same IDs | 12, same IDs | same |
| Finite state / dropped LIGHT spans | pass / 0 | pass / 0 | pass / 0 | pass / 0 |

Process wall is directly timed around the full command and includes initialization, scheduled final evaluation and saving. The reported mapping wall is the optimizer-loop timer, not all mapping work. No separately delimited online wall was measured. Mapping/tracking/H2D/selection spans may nest or overlap; they must not be summed as online wall. One pair gives an exploratory whole-process ratio only, not statistical speedup evidence. LIGHT's H2D totals are observed telemetry and do not establish transfer overlap or causal runtime attribution.

## Quality against saved V0

Metrics are means over identical final-map training views `[0,4,9,14,19,24,29,34,39,44,49]`; trajectory metrics use all 50 poses and the same Horn alignment. For low-is-better metrics, degradation is `(candidate−V0)/V0`; for high-is-better metrics it is `(V0−candidate)/V0`. PSNR is reported in dB and separately converted to MSE ratio `10**((PSNR_V0−PSNR_candidate)/10)`.

| Metric | V0 | V-A | V-A2 | V-A2 change vs V0 | 15% limit |
|---|---:|---:|---:|---:|---|
| PSNR (dB) | 40.61135 | 39.87230 | 40.10971 | −0.50164 dB; implied MSE +12.244% | PASS |
| MS-SSIM | 0.995780 | 0.995552 | 0.995550 | −0.0231% relative | PASS |
| LPIPS-Alex | 0.025973 | 0.026240 | 0.025720 | −0.973% (improvement) | PASS |
| Depth L1 (m) | 0.00189272 | 0.00225720 | 0.00206472 | +9.087% | PASS |
| Semantic mIoU | 0.937575 | 0.935289 | 0.935846 | −0.1844% relative | PASS |
| ATE Mean (m) | 0.000369742 | 0.000332316 | 0.000367335 | −0.651% (improvement) | PASS |
| ATE RMSE (m) | 0.000408083 | 0.000378266 | 0.000427646 | +4.794% | PASS |

All seven researcher-defined 15% checks pass versus V0. The original P5-LEAN provisional constraints are not overwritten: PSNR ≤0.5 dB decrease, MS-SSIM ≤0.01 absolute decrease, LPIPS ≤0.02 absolute increase, Depth L1 ≤10% increase, mIoU ≤0.02 absolute decrease, and ATE RMSE ≤max(10% relative, 1 mm absolute). V-A2's PSNR delta misses its old limit narrowly (0.00164 dB); other listed metric margins pass. Its process-wall reduction is 11.33%, but P5's ≥20% target is for online wall and remains NOT MEASURED.

V-A2 improves the aggregate screen over V-A: PSNR +0.23742 dB, Depth L1 −8.53%, LPIPS −1.98%, MS-SSIM −0.00000185, semantic mIoU +0.000556, ATE Mean +10.54% (higher error than V-A but still within V0's 15% limit), and ATE RMSE +13.06% (also within V0's limit). This is consistent with a more conservative iteration allocation improving some quality tradeoffs, but a single matched run per variant cannot establish causality or non-inferiority. Full per-frame V0/V-A/V-A2 values and deltas are preserved in `results/runtime_artifacts/phase6_bam/p6_bam_003_r1_comparison/per_frame_quality.csv`.

## Interpretation and next action

V-A2 used 705 more iterations than V-A but 555 fewer than V0, with 18.5% fewer iterations and 20.18% lower mapping-loop time than V0. Whole-process time improved 11.33% versus V0; no standalone online-wall speedup is claimed. All required sampled metrics satisfy the new 15% screen, while the older provisional PSNR target is narrowly missed. Baseline run-to-run variability at 0–49 remains unmeasured; previous OFF-vs-OFF evidence covers only 0–10 and cannot furnish a variance estimate for this horizon. Metrics are sampled final-map views, not a full-scene or per-event causal assessment.

Classification: `PASS_P6_BAM_003_R1_QUALITY_CONSTRAINED_0_49` (candidate screening only). Recommend researcher review before authorizing a single matched 0–499 V0/V-A2 LIGHT comparison. Keep the thresholds frozen and preserve the P6-BAM-003 historical INCONCLUSIVE classification. No run beyond frame 49 was started.
