# Phase 7 Gate 2 — metric comparison

**Run:** `p7_bcgm_g2_room0_on_0_499_r01`<br>
**Status:** `PASS_GATE2_WITH_COMPARISON_LIMITATIONS`

## Gate 2 BCGM-on measurements

Raw per-view values are read from the six saved files under
`experiments/Replica/p7_bcgm_g2_room0_on_0_499_r01/eval/`; each contains 101
finite values. Reported image/depth/semantic metrics below are their arithmetic
means, following `utils/eval_helpers.py`.

| Metric | BCGM-on Gate 2 | Measurement scope / label |
|---|---:|---|
| Process wall | 2,370.501740 s | Guarded runner process interval |
| E2E FPS | 0.21092581 | 500 frames / process wall; includes runner-side overhead |
| `rgbd_slam` call wall | 2,367.595040 s | Worker around `rgbd_slam` |
| Tracking | 1.818299 s/frame; 0.549964 FPS | Source-reported average frame time and reciprocal |
| Mapping | 2.648452 s/frame; 0.377579 FPS | Source-reported average frame time and reciprocal; stage scope, not E2E |
| CUDA peak allocated | 2,948,930,048 B = 2,812.08 MiB | PyTorch process allocator peak, worker scope |
| CUDA peak reserved | 3,856,662,528 B = 3,678.31 MiB | PyTorch process allocator peak, worker scope |
| NVML sampled peak | 4,877 MiB | Device-wide sampled memory used; recovered from CSV |
| Final Gaussians | 2,198,608 | Final checkpoint `means3D` rows |
| RGB PSNR | 36.190108 dB | Mean of 101 saved evaluator views |
| MS-SSIM | 0.989880 | Mean of 101 saved evaluator views |
| LPIPS-Alex | 0.050048 | Mean of 101 saved evaluator views |
| Depth L1 | 0.00284632 m | Mean saved `l1.txt`; not RMSE |
| Semantic mIoU | 0.902575 | Mean of 101 saved evaluator views |
| Trajectory | 0.00286229 m (0.286229 cm) | Evaluator's Horn-aligned mean translation error; not conventional ATE RMSE |

The evaluator saves `rmse.txt` byte-identically to `l1.txt` for this run.
Despite its “Depth RMSE” print label, this is the implementation's depth L1
quantity and is not a true depth RMSE. `evaluate_ate()` aligns translations
with Horn's method and averages Euclidean per-pose translation errors; the
printed “ATE RMSE” is therefore not a conventional trajectory RMSE. The
full-precision mean above was recalculated from the saved 500-pose checkpoint
using that same alignment and aggregation. The console rounds it to 0.29 cm.

Tracking and mapping reciprocal FPS are stage measurements. They must not be
compared as if they were whole-system FPS. CUDA allocated/reserved are two
allocator quantities; NVML is a sampled device-wide measurement and must not
be substituted for either.

## Historical Phase 4 Gate 4 context

The comparison source is
`PHASE7_GATE2_BASELINE_REUSE_AUDIT.md`, which records Gate 4's limitations.

| Quantity | Gate 4 historical reference | Gate 2 BCGM-on | Interpretation |
|---|---:|---:|---|
| Runtime | 2,564.527929 s | 2,370.501740 s | Raw difference is not a matched speedup: Gate 4 disabled evaluation/save and used a different continuous-run timing scope; effective source hash is incomplete |
| CUDA allocated peak | 3,468,590,592 B | 2,948,930,048 B | Context only; source identity and measured path/scope are not fully locked equivalently |
| CUDA reserved peak | 4,525,654,016 B | 3,856,662,528 B | Context only; same limitations; distinct from NVML |
| Final Gaussian count | 2,255,038 | 2,198,608 | BCGM-on result is 56,430 lower (2.50%); useful output context, not quality or causal proof |
| NVML peak | Not measured | 4,877 MiB | No historical comparison |
| RGB/depth/semantic quality | Not measured | Available for Gate 2 | No matched 500-frame quality retention/delta claim |
| Trajectory / ATE | Not measured | Available for Gate 2 | No matched trajectory comparison |

Gate 4 was a bounded CPU Keyframe Offload reference with a recorded
uncommitted Phase 4 script diff, no full effective source hash, and no
complete effective config snapshot. Its runtime omitted evaluation/save
hooks. Accordingly, Gate 2 does not establish a matched 500-frame speedup,
quality retention, NVML improvement, or statistically significant benefit.

Gate 2's Global Cap (4,500,000) never activated. Its runtime behavior remains
`NOT_RUNTIME_VERIFIED`. BCGM insertion host-call sum is 3.298734 s, but this
unsynchronized aggregate includes broader insertion work and does not isolate
selection/sorting cost; isolated profiling is `NOT_MEASURED`.
