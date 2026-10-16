# P6-BAM-003 — 0–49 V0 versus V-A comparison

One matched LIGHT run per variant on Replica room0 frames 0–49, source `bb830b1f6a0a31028f14fe390b8cb4e1a50c47fe`. The exact protocol, commands, evidence paths and quality method are in `P6_BAM_003_0_49_REPORT.md`. Gate: `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME` due to preliminary quality signals, despite successful functional execution.

| Measure | V0 | V-A | Difference / interpretation |
|---|---:|---:|---|
| Process wall, `/usr/bin/time` | 192.27 s | 143.28 s | −48.99 s, −25.48%; observed factor 1.342× |
| Profiler active wall | 189.443 s | 140.442 s | −49.001 s; includes evaluation/serialization |
| Mapping wall, LIGHT stage sum | 104.714 s | 58.127 s | −46.587 s, −44.49% |
| Tracking wall, LIGHT stage sum | 68.828 s | 66.844 s | −1.985 s; not an equivalence test |
| Separately delimited online wall | NOT_MEASURED | NOT_MEASURED | Stage sums exclude other online work; process wall includes eval/save |
| Configured / executed mapping iterations | 3,000 / 3,000 | 3,000 / 1,740 | −1,260 actual, −42.0% |
| FULL / MID / LOW events | 50 / 0 / 0 | 1 / 14 / 35 | V-A valid append signal on frames 1–49 |
| H2D event count / cumulative bytes | 2,371 / 61,911,552,000 B | 1,341 / 35,016,192,000 B | −1,030 / −26,895,360,000 B |
| CPU archive count / logical bytes | 12 / 313,344,000 B | 12 / 313,344,000 B | Identical IDs |
| Peak sampled GPU allocated / reserved | 2,108,559,872 / 2,720,006,144 B | 2,118,638,080 / 2,617,245,696 B | Allocated slightly higher; reserved lower |
| Peak process RSS, `/usr/bin/time` | 3,928,140 kB | 3,969,280 kB | Different sampling window from LIGHT HWM |
| Peak sampled process HWM | 2,519,588,864 B | 2,466,287,616 B | No long-horizon capacity conclusion |
| Final Gaussians | 1,122,223 | 1,122,614 | V-A +391; not a quality proxy |
| Archived keyframes | 12 | 12 | `[0,4,9,14,19,24,29,34,39,44,48,49]` |
| OOM / non-finite / dropped LIGHT spans | none / none / 0 | none / none / 0 | Structural PASS |

The LIGHT `mapping.wall_time` interval is the optimization loop, not the entire frame's mapping work; it excludes at least append and overlap-keyframe selection. Tracking, mapping, H2D and selection spans may overlap or nest and must not be summed as a purported online wall time. Process wall includes import, initialization, final evaluator and serialization. The 1.342× factor is an **observed whole-process ratio from one pair**, not a statistically validated speedup or the protocol's ≥20% *online-wall* target.

Matched final-map evaluator results over frames `[0,4,9,14,19,24,29,34,39,44,49]` show V-A −0.739 dB PSNR and +19.26% Depth L1 relative to V0. These exceed the P5-LEAN provisional design margins of −0.5 dB and +10%, respectively. V-A's ATE Mean/RMSE were slightly lower; MS-SSIM, LPIPS and semantic mIoU changed less than their provisional margins. PSNR decreased on 9/11 samples and Depth L1 worsened on all 11; this warrants targeted review before expanding the horizon. It is not causal proof because only one seed/run pair was observed, mapping RNG consumption differs and historical OFF-vs-OFF numerical variability is documented. No quality non-inferiority or full-scene feasibility claim is made.
