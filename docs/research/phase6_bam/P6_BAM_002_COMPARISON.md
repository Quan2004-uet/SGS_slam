# P6-BAM-002 — V0 versus V-A, Replica room0 frames 0–10

Source `a3aefc745b73da520fa2ae53e77b0349fd25fa00`; one sequential LIGHT run per variant, same scene, frame range, seed, tracking, CPU offload, evaluator/output policy and mapping maximum. Gate `PASS_P6_BAM_002_SMOKE_INTEGRATION`; `ADAPTIVE_ACTIVATION_CONFIRMED`. Detailed provenance and limitations are in `P6_BAM_002_SMOKE_REPORT.md`.

| Measure | V0 (budget OFF) | V-A (adaptive) | Interpretation |
|---|---:|---:|---|
| Completed frames / mapping events | 11 / 11 | 11 / 11 | Identical 0–10 horizon |
| Tier distribution FULL/MID/LOW | 11/0/0 | 1/4/6 | 10 valid V-A novelty signals |
| Configured / executed iterations | 660 / 660 | 660 / 420 | 240 fewer actual iterations, −36.36% |
| Mapping wall, LIGHT stage sum | 21.045 s | 13.455 s | −7.590 s; exploratory |
| Tracking wall, LIGHT stage sum | 12.768 s | 12.755 s | Similar, not proof of equivalence |
| Whole process wall, `/usr/bin/time` | 42.19 s | 34.62 s | −7.57 s (−17.94%); includes imports/eval/save |
| Profiler active wall | 39.386 s | 31.816 s | Includes non-online work |
| Peak sampled GPU allocated / reserved | 1,806,090,240 / 2,151,677,952 B | 1,797,682,176 / 2,051,014,656 B | 11-frame sample only |
| Peak process RSS, `/usr/bin/time` | 3,267,472 kB | 3,309,660 kB | Different window from sampled HWM |
| Peak sampled CPU HWM | 2,267,922,432 B | 2,311,671,808 B | No memory-capacity claim |
| CPU archive logical bytes | 78,336,000 | 78,336,000 | 3 archived keyframes each |
| H2D staging events / bytes | 375 / 9,792,000,000 | 215 / 5,614,080,000 | −160 events / −4,177,920,000 B |
| Final Gaussians / keyframes | 879,811 / 3 | 880,721 / 3 | Different states, same archive IDs `[0,4,9]` |
| Non-finite state / OOM / CUDA failure | none | none | Bounded smoke only |

At frame 10, mapping selected the same keyframe *set* but different order: V0 `[4,0,9,10]`, V-A `[0,4,9,10]`. Different mapping iteration counts change subsequent RNG consumption; exact state equality is neither expected nor established. Historical matched OFF-A/OFF-B runs also differed numerically (879,862 versus 879,218 final Gaussians), with V0's 879,811 lying within that observed range; those runs are not a bit-exact reference for this comparison. The V-A final map has 910 more Gaussians, and maximum saved translation-component difference was about 0.000661 m. Neither observation establishes quality change.

The 0–10 elapsed-time difference is an exploratory single-pair observation, **not** a validated speedup. Mapping stage-sum time and process wall cover different windows; do not interchange them or infer online wall exactly from either. The progress display rounded online completion to roughly 34 s (V0) and 26 s (V-A). No quality metric or full-scene comparison is claimed.

Evidence: `results/runtime_artifacts/phase6_bam/p6_bam_002_comparison/{v0_validation.json,va_validation.json,v0_run.log,va_run.log,v0_process_time.txt,va_process_time.txt}`; LIGHT JSONL/summary/metadata under `results/runtime_artifacts/phase6_bam/telemetry/<run_id>/`; and saved state under each independent Phase 6 result directory. No Phase 4 output was modified.
