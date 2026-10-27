# Phase 7 Gate 1B — saved-artifact metric comparison

**Scope:** Replica room0 frames 0–99, seed 0, one completed run per arm. The three run IDs are `p7_bcgm_g1b_room0_p4_0_99_r01`, `p7_bcgm_g1b_room0_off_0_99_r01`, `p7_bcgm_g1b_room0_on_0_99_r01`. Source/config hashes and hashes for all enumerated run artifacts are in `PHASE7_GATE1B_EVIDENCE_MANIFEST.json`; individual RGB-D/semantic dataset files are not hashed there. Common loaded input config after removing only `run_name` and `bcgm`: `21fe6546fec201254f320f090cdac4b5d3a00f54c666834075834968df859935`. All comparisons below are descriptive, not statistical estimates.

## Full-precision saved values and measured performance

| Metric | Scope / unit | P4 original | BCGM off | BCGM on | On − P4 | On − off |
|---|---|---:|---:|---:|---:|---:|
| Total process wall | s; process startup + SLAM + eval + save | 403.883937 | 402.661730 | 400.355505 | -3.528432 (-0.874%) | -2.306225 (-0.573%) |
| End-to-end throughput | frames/s; 100/process wall | 0.247596 | 0.248347 | 0.249778 | +0.002182 (+0.881%) | +0.001431 (+0.576%) |
| Tracking reciprocal FPS | frames/s; reciprocal source mean frame time | 0.684277 | 0.684747 | 0.688587 | +0.004311 (+0.630%) | +0.003840 (+0.561%) |
| Mapping reciprocal FPS | frames/s; excludes pixel insertion | 0.442359 | 0.443668 | 0.446289 | +0.003930 (+0.888%) | +0.002621 (+0.591%) |
| CUDA peak allocated | MiB; PyTorch process allocator | 1951.903320 | 1962.746094 | 1922.678711 | -29.224609 (-1.497%) | -40.067383 (-2.041%) |
| CUDA peak reserved | MiB; PyTorch process allocator | 2898.000000 | 2812.000000 | 2824.000000 | -74.000000 (-2.553%) | +12.000000 (+0.427%) |
| NVML peak device used | MiB; sampled device-wide at 1 Hz | 4073.000000 | 4025.000000 | 3955.000000 | -118.000000 (-2.897%) | -70.000000 (-1.739%) |
| Final Gaussians | count; params.npz | 1404952 | 1406470 | 1375645 | -29307 (-2.086%) | -30825 (-2.192%) |
| PSNR | dB; mean of 21 saved training-view scores | 40.521147 | 40.287181 | 40.558197 | +0.037051 (+0.091%) | +0.271016 (+0.673%) |
| MS-SSIM | unitless; mean of 21 saved scores | 0.994983 | 0.994788 | 0.995030 | +0.000047 (+0.005%) | +0.000242 (+0.024%) |
| LPIPS Alex | unitless; mean of 21 saved scores | 0.030688 | 0.032529 | 0.031424 | +0.000736 (+2.400%) | -0.001105 (-3.397%) |
| Depth L1 | m; mean of 21 saved scores | 0.001940 | 0.001907 | 0.001888 | -0.000052 (-2.696%) | -0.000019 (-1.011%) |
| Semantic-color mIoU | unitless; GT-palette-assisted, mean of 21 | 0.917751 | 0.918328 | 0.918203 | +0.000453 (+0.049%) | -0.000125 (-0.014%) |

**Definition and direction:** Δ = BCGM on minus comparator; percentages divide by comparator. Higher PSNR/MS-SSIM/mIoU is better; lower LPIPS, depth L1, runtime, memory, and Gaussian count is better. The 100-frame wall clock includes startup, tracking, mapping, evaluation and save. Tracking/mapping FPS are source-stage reciprocal averages, not end-to-end FPS; mapping timing excludes pixel admission. CUDA allocated, CUDA reserved and NVML used memory have different scopes and are not interchangeable. NVML values include desktop use and 1 Hz sampling can miss peaks. The insertion host-call timer is unsynchronized and is not a GPU-cost benchmark.

**Depth units:** `eval/l1.txt` and `eval/rmse.txt` are elementwise identical in all three runs. The evaluator takes `sqrt(error²)` before an arithmetic mean, so its printed “Depth RMSE” is **Depth L1**, in metres in the saved arrays (multiply by 100 for cm). Conventional Depth RMSE is **NOT_MEASURED**. Source: `utils/eval_helpers.py`, `eval()`, depth computation and saved metric arrays.

**ATE:** the console prints “Final Average ATE RMSE” as 0.14 cm (P4), 0.13 cm (off), 0.13 cm (on), rounded to 0.01 cm. `evaluate_ate()` computes the mean of aligned translation errors; it does not save the full-precision result and does not compute true RMSE. A full-precision ATE difference, conventional ATE RMSE, and uncertainty interval are **NOT_MEASURED**. Source: `utils/eval_helpers.py`, `evaluate_ate()` and `eval()`; console logs are hashed in the manifest.

**Quality protocol:** 21 saved sampled training-view scores per metric, corresponding to frame 0 and every fifth frame through 99. MS-SSIM is from `ms_ssim`, LPIPS uses Alex, and semantic mIoU recolors rendered semantic colors against a palette derived from GT. These are neither held-out views nor full-scene scores. The rounded console averages (P4/off/on PSNR 40.52/40.29/40.56, MS-SSIM 0.995 each, LPIPS 0.031/0.033/0.031, mIoU 0.9178/0.9183/0.9182) conceal the differences shown above. Source: each arm's `eval/*.txt`, `stdout_stderr.log`, and `utils/eval_helpers.py`.

**Interpretation:** BCGM on has 29,307 fewer final Gaussians (−2.086%) than P4, 118 MiB lower sampled NVML peak, and 3.528 s shorter observed process wall in this single 100-frame run. LPIPS is 2.400% worse than P4 while PSNR, MS-SSIM, depth L1 and mIoU are similar or improved. The approximately 10% quality target is a screening budget; these one-run results do not establish a statistically proven speedup or general quality preservation. Global cap behavior and full-scene outcome remain untested.
