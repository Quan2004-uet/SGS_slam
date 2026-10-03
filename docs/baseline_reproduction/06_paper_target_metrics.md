# Paper Target Metrics

Source: local `2402.03246v6.pdf`. Values below are `VERIFIED FROM PAPER`. They
are targets for comparison, not claims of released-code reproduction.

## Canonical Replica targets

| Dataset | Scene / Avg | Stage | Metric | Paper value | Table / section | Priority |
|---|---|---|---|---:|---|---|
| Replica | room0 | Training-view rendering; online vs post-opt not stated | PSNR | 32.50 dB | Table 1 | High |
| Replica | room0 | Same ambiguity | SSIM | 0.976 | Table 1 | High |
| Replica | room0 | Same ambiguity | LPIPS | 0.070 | Table 1 | High |
| Replica | 8-scene avg | Same ambiguity | PSNR | 34.66 dB | Table 1 | Medium after room0 |
| Replica | 8-scene avg | Same ambiguity | SSIM | 0.973 | Table 1 | Medium |
| Replica | 8-scene avg | Same ambiguity | LPIPS | 0.096 | Table 1 | Medium |
| Replica | room0 | Semantic training-view result; stage not stated | mIoU | 92.95% | Table 3 | High |
| Replica | 4-scene avg | Same ambiguity | mIoU | 92.72% | Table 3 | Medium |
| Replica | room0 | Online trajectory expected; table says ATE RMSE | ATE RMSE | 0.46 cm | Table 6 | High |
| Replica | 8-scene avg | Online trajectory expected | ATE RMSE | 0.41 cm | Table 6 | Medium |
| Replica | 8-scene avg | Not explicitly staged | Depth L1 | 0.356 cm | Table 2 | Medium |
| Replica | 8-scene avg | Tracking output | ATE Mean | 0.327 cm | Table 2 | Medium |
| Replica | 8-scene avg | Tracking output | ATE RMSE | 0.412 cm | Table 2 | Medium |
| Replica | 8-scene avg | Online runtime on paper hardware | Tracking FPS | 5.27 | Table 2 | Low/hardware-dependent |
| Replica | 8-scene avg | Online runtime on paper hardware | Mapping FPS | 3.52 | Table 2 | Low/hardware-dependent |
| Replica | 8-scene avg | Online runtime on paper hardware | SLAM FPS | 2.11 | Table 2 | Low/hardware-dependent |

The paper's implementation section reports an NVIDIA A100 40 GB and states that
typical GPU memory consumption is below 12 GB. FPS comparison is meaningful only
with hardware/software/workload disclosures and is not a Phase 3 first-run gate.

## Additional per-scene values for later full-table reproduction

Table 1, scene order `room0, room1, room2, office0, office1, office2, office3,
office4`:

- PSNR: `32.50, 34.25, 35.10, 38.54, 39.20, 32.90, 32.05, 32.75`.
- SSIM: `0.976, 0.978, 0.981, 0.984, 0.980, 0.967, 0.966, 0.949`.
- LPIPS: `0.070, 0.094, 0.070, 0.086, 0.087, 0.101, 0.115, 0.148`.

Table 6 ATE RMSE in cm, same scene order:
`0.46, 0.45, 0.29, 0.46, 0.23, 0.45, 0.42, 0.55`.

Table 3 semantic scenes `room0, room1, room2, office0`:
`92.95%, 92.91%, 92.10%, 92.90%`.

## Stage and protocol caveats

- Table 1 says training-view rendering and Table 3 reports semantic reconstruction,
  but the paper does not unambiguously say whether the published values use the
  final online map or post-SLAM optimization. `UNKNOWN / NEEDS RUNTIME
  VERIFICATION`
- Trajectory ATE necessarily evaluates tracked online camera estimates; post-opt
  freezes cameras and uses GT cameras for map refinement in released source.
  This stage mapping is `INFERRED FROM SOURCE`.
- Paper “SSIM” and “ATE RMSE” labels do not match the exact released evaluator
  operations documented in `05_evaluation_protocol.md`. Values should be compared
  first with the released evaluator unchanged, while reporting the mismatch.
- No tolerance is paper-specified. Do not declare reproduction solely because a
  run completes or one metric is close.
