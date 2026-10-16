# P6-BAM-006 — Full-Scene Comparison

## Comparison basis

This is one full-scene V-A2 run compared with the stored Phase 4 VB-001 E4 reference, not a matched full-scene V0/V-A2 pair. The image/depth/semantic evaluation uses the same Phase 4 E4 implementation and 401 final-map views; trajectory evaluation covers all 2,000 relative-w2c poses using Horn alignment without scale. P6-BAM-005 supplies the available matched V0/V-A2 runtime/quality evidence only for frames 0–499.

## Quality

| Metric | Phase 4 | V-A2 0–1999 | Difference | 15% criterion |
|---|---:|---:|---:|---|
| ATE Mean (m) | 0.00274074868 | 0.00284398782 | +3.7668% | PASS |
| True ATE RMSE (m) | 0.00339827059 | 0.00343679457 | +1.1336% | PASS |
| PSNR (dB) | 33.3130670 | 32.9445524 | −0.3685146 dB | PASS; implied MSE +8.8558% |
| MS-SSIM | 0.979470255 | 0.978003691 | −0.1497% | PASS |
| LPIPS-Alex | 0.067555264 | 0.070752040 | +4.7321% | PASS |
| Depth L1 (m) | 0.004951577 | 0.004943029 | −0.1726% | PASS |
| Semantic-color mIoU | 0.916585480 | 0.913530865 | −0.3333% | PASS |

No metric is averaged against another. PSNR-implied MSE is a transform of the mean PSNR difference, not a direct aggregate pixel-MSE measurement. Stored per-frame values and exact IDs are in `per_frame_metrics.json`; machine-readable aggregate comparison is in `phase4_quality_comparison.json`/`.csv`.

## Runtime and resources

V-A2 online loop: 12,383.451 s (0.161506 frames/s); process: 12,766.40 s (0.156661 frames/s). Process peak RSS was 17,627,216 KiB. Mapping and tracking LIGHT host-span sums were 6,072.273 s and 6,070.039 s; they overlap and must not be added to infer online time. Torch allocator high-water was 7.443 GB allocated / 8.227 GB reserved; periodic LIGHT sampled maxima were 2.163 GB / 8.204 GB. CPU keyframe archive was 402 entries / 10.497 GB logical; H2D was 85,969 events / 2.245 TB cumulative.

Historical Phase 4 process time was approximately 14,173.475 s under a different timing protocol. It is context only, `NOT_COMPARABLE` to the online-loop interval and insufficient for a full-scene runtime improvement claim. P6-BAM-005 did measure a matched 0–499 online-wall reduction of 15.33%; this bounded result does not establish full-scene speedup.

## Budget and model

2,000 events; 90,195 executed mapping iterations versus 120,000 all-60 equivalent (24.8375% fewer iterations). Tiers: 1 FULL, 12 MID, 1,987 LOW. There were 1,999 valid novelty events; frame 0 alone used the expected initial-signal FULL fallback. Final Gaussian count: 5,004,577; keyframes: 402, ending at 1999. All events executed their selected iteration count and preserved the 21-iteration prune floor.

## Conclusion

All seven 15% quality checks pass for this one full-scene V-A2 run against the stored Phase 4 E4 baseline. This is execution-and-quality screening, not statistical non-inferiority and not a matched full-scene runtime comparison. Classification: `PASS_P6_BAM_006_FULL_SCENE_QUALITY_CONSTRAINED`; independently, `FULL_SCENE_RUNTIME_SPEEDUP_UNVERIFIED`.
