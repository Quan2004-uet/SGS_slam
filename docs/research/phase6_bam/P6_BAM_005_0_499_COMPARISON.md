# P6-BAM-005 — V0 vs V-A2 Comparison

Source commit `937cd4bb7df25824e5b43de555d5de78ce11f16c`, same RTX 5080/Python/PyTorch/CUDA environment, seed 0 and frozen 500-frame configuration parity. The only algorithmic configuration difference was `mapping.budget_control`. Exact configs, run identity, hashes, launch records and raw outputs are retained under `results/runtime_artifacts/phase6_bam/p6_bam_005_comparison/` and the two immutable run directories.

## Execution

| | V0 | V-A2 |
|---|---:|---:|
| Run ID | `p6_bam_005_room0_0_499_v0_r01` | `p6_bam_005_room0_0_499_va2_r01` |
| Frames / mapping events | 500 / 500 | 500 / 500 |
| Configured / executed iterations | 60 / 30,000 | 60 / 22,695 |
| FULL / MID / LOW | OFF 500 events | 1 / 12 / 487 |
| Valid novelty events | n/a; controller OFF | 499 (frame 0 initial signal invalid) |
| Online loop wall | 2,319.05 s | 1,963.46 s |
| Mapping wall sum | 1,355.20 s | 1,004.94 s |
| Tracking stage sum | 925.36 s | 920.05 s |
| Whole process wall | 2,349.67 s | 1,994.25 s |
| Peak GPU allocated / reserved | 3.597 / 4.662 GB | 3.778 / 4.582 GB |
| Process peak RSS (`/usr/bin/time`) | 7,423,840 KiB | 7,426,524 KiB |
| CPU archive logical bytes / count | 2,663,424,000 / 102 | same |
| H2D events / cumulative bytes | 28,164 / 735,418,368,000 | 21,271 / 555,428,352,000 |
| Final Gaussians / keyframes | 2,248,654 / 102 | 2,270,111 / 102 |

Changes V-A2 vs V0: mapping iterations −24.35%; mapping wall sum −25.85%; online-loop wall −15.33%; process wall −15.13%. Online ratio V0/V-A2=1.181× and whole-process ratio=1.178×. Process wall is not substituted for online time. Tracking stage sums are nearly equal (−0.57%); profiler substage sums can be nested and should not be summed to reconstruct online wall. The older provisional ≥20% online-wall target is not met; a positive measured runtime reduction is present in this single pair.

Online timing is the monotonic host interval immediately before the `scripts/slam.py` frame loop through its final iteration, including the existing per-frame profiler calls and `torch.cuda.empty_cache()`, excluding initialization, final evaluation and final serialization. The measurement-only timer added no CUDA synchronization. LIGHT mapping/tracking values are the existing profiler's host wall-time aggregates. `/usr/bin/time` includes startup, online work, final evaluation and output saving. The process RSS field and sampled `/proc` RSS/HWM use distinct measurement conventions.

## Quality and saved evaluation

Final map metrics were evaluated with the same existing evaluator on frames `[0,49,99,149,199,249,299,349,399,449,499]`; ATE uses all 500 saved poses. `paired_per_frame_metrics.csv` contains all paired frame values and deltas. `paired_validation.json` is the CPU-only aggregation and validation output.

| Metric | V0 | V-A2 | Change | 15% limit |
|---|---:|---:|---:|---|
| ATE Mean (m) | 0.00254617 | 0.00230700 | −9.39% | PASS |
| ATE RMSE (m) | 0.00308668 | 0.00281463 | −8.81% | PASS |
| PSNR (dB) | 36.19163 | 36.12453 | −0.06710 dB | PASS; MSE-equivalent +1.557% |
| MS-SSIM | 0.989386 | 0.988725 | −0.067% relative | PASS |
| LPIPS-Alex | 0.051610 | 0.050332 | −2.48% (better) | PASS |
| Depth L1 (m) | 0.00312353 | 0.00320590 | +2.64% | PASS |
| Semantic mIoU | 0.908787 | 0.907979 | −0.089% | PASS |

All researcher-defined 15% quality constraints pass. All historical P5-LEAN provisional **quality** margins pass as well. The old ≥20% online runtime target does not pass. This remains one bounded matched run pair, without repeat-run variability estimates; no claim of statistical non-inferiority, causality or full-scene performance is justified.

## Budget, invariants, and interpretation

V-A2 used unchanged tiers 45/60/60 at novelty thresholds 0.01/0.05. Distribution: 1 FULL (frame 0), 12 MID, 487 LOW. Valid signal fraction range was 0.00013538–0.01692406 (median 0.00073655); no unexpected fallbacks occurred. LOW dominated all frame segments after 0–99. Each event retained a configured maximum of 60 and prune floor 21. Both run summaries say `completed`, with zero dropped/pending LIGHT CUDA-event spans; both final checkpoints have finite floating arrays and all 500 poses. CPU archive and H2D staging were active in both.

The quality/runtime observations are consistent with a promising bounded trade-off but do not isolate all numerical variability or establish that reduced iterations alone caused the observed quality values. The 15% thresholds are researcher-defined screens, not statistical acceptance intervals. Historical Phase 4/P6 checkpoint hashes match the pre-run inventory. The `nvidia-smi` host query failed during V0, so system-wide GPU telemetry was unavailable; allocator peaks are reported from the run's own LIGHT samples.

**Gate: `PASS_P6_BAM_005_0_499_QUALITY_CONSTRAINED`.** Recommend researcher review before any 0–1999 authorization. No further run was executed.
