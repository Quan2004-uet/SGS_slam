# P6-BAM-003-R1 — V-A2 quality-constrained 0–49 validation

Date: 2026-10-16. This was one bounded Replica `room0` LIGHT run, frames 0–49 inclusive, source revision `60372fcc4fac2caa1bfa09c712d9092467289228`. The isolated wrapper was uncommitted during execution and is included in this checkpoint; its hash and effective-config hash are in `results/runtime_artifacts/phase6_bam/p6_bam_003_r1_comparison/r1_provenance.json` and `va2_effective_config.json`. Pre-run output/reference hashes are in `r1_preflight_manifest.json`.

## Frozen variant and provenance

V-A2 changes only the adaptive budget values from V-A: LOW/MID/FULL = 45/60/60; `low_max=0.01`, `mid_max=0.05`, configured maximum 60. The novelty proxy and controller source were unchanged. CPU/static checks loaded the wrapper through the repository's actual config path, compared all non-budget/non-identity fields against the saved V0 and V-A configs, verified seed 0, Replica room0, `[start,end,stride,num_frames]=[0,50,1,50]`, tracking 40, mapping max 60, CPU-offload inheritance and LIGHT settings, and passed all 15 `tests.test_mapping_budget` tests.

Exact launch command:

```bash
P6_BAM_RUN_ID=p6_bam_003_r1_room0_0_49_va2_r01 PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/time -f 'elapsed_seconds=%e peak_rss_kb=%M exit_status=%x' \
  -o results/runtime_artifacts/phase6_bam/p6_bam_003_r1_comparison/va2_process_time.txt \
  /home/robot/miniconda3/envs/sgs_slam_5080/bin/python scripts/slam.py \
  results/runtime_artifacts/phase6_bam/p6_bam_003_r1_comparison/va2_config.py
```

Environment: NVIDIA GeForce RTX 5080; driver 580.167.08; Python 3.10.22; PyTorch 2.7.1+cu128; CUDA runtime 12.8; seed 0. The existing in-run LIGHT evaluation policy rendered its 11 scheduled training-camera views; no separate evaluator or rerun was launched. Process return code was 0 and process wall was 170.49 s. The run completed frame IDs 0–49, 50 mapping events, saved finite numeric `params.npz`, 12 keyframes `[0,4,9,14,19,24,29,34,39,44,48,49]`, and 1,121,742 Gaussians. No OOM, exception, non-finite saved state, or dropped/pending CUDA-event span was found.

## Runtime integration and resources

Telemetry records 49 valid current-event novelty signals. Frame 0 had the expected invalid initial append signal and used FULL=60; the remaining 49 events had no fallback. Tier counts were 1 FULL, 12 MID and 37 LOW. Every event retained configured maximum 60, executed exactly its effective budget, and covered the required zero-based prune iteration 20 (21 iterations minimum). Total execution was 2,445/3,000 mapping iterations. The unchanged CPU keyframe archive recorded 12 keyframes and 313,344,000 logical bytes; LIGHT staging recorded 1,906 events and 49,769,472,000 cumulative bytes. Peak sampled GPU allocated/reserved were 2,203,185,152 / 2,969,567,232 B; process peak RSS was 3,970,536 kB and sampled HWM was 2,480,365,568 B. No direct pruning-call counter exists in LIGHT, so prune coverage is established from effective-loop coverage plus unchanged source schedule, not an event-level prune-call measurement.

Evidence is preserved under:

- Run: `results/runtime_artifacts/phase6_bam/p6_bam_003_r1_room0_0_49_va2_r01/`
- LIGHT telemetry: `results/runtime_artifacts/phase6_bam/telemetry/p6_bam_003_r1_room0_0_49_va2_r01/`
- Frozen configs, launch/log/process timing, pre/post integrity manifest, CPU validation and derived metric table: `results/runtime_artifacts/phase6_bam/p6_bam_003_r1_comparison/`

## Quality assessment and decision

The unchanged evaluator produced PSNR, MS-SSIM (`ssim.txt`), LPIPS-Alex, valid-depth L1 and GT-palette-assisted semantic mIoU for the same 11 frames `[0,4,9,14,19,24,29,34,39,44,49]`. CPU Horn alignment of the saved 50-pose trajectory produced ATE Mean and supplementary true ATE RMSE. Full V0/V-A/V-A2 per-frame values and deltas are in `p6_bam_003_r1_comparison/per_frame_quality.csv`; aggregate values and per-metric 15% decisions are in `va2_validation.json`.

Against the saved V0 0–49 run, all researcher-defined 15% checks pass: PSNR decrease 0.50164 dB corresponds to an implied MSE increase of 12.244%; MS-SSIM decrease 0.0231%; LPIPS improves 0.973%; Depth L1 increases 9.087%; semantic mIoU decreases 0.1844%; ATE Mean improves 0.651%; ATE RMSE increases 4.794%. These are screening results from one run pair, not statistical non-inferiority.

The historical P5-LEAN provisional margins remain unchanged: PSNR decrease ≤0.5 dB, MS-SSIM decrease ≤0.01, LPIPS increase ≤0.02, Depth L1 increase ≤10%, semantic mIoU absolute decrease ≤0.02, and ATE RMSE degradation ≤max(10% relative, 1 mm absolute). V-A2 narrowly exceeds the old PSNR bound by 0.00164 dB; its other listed metric bounds pass. The historical ≥20% target is for matched online wall time, which was not separately measured here. Mapping-loop time decreased 20.18%, while whole-process time decreased 11.33%; neither substitutes for the specified online-wall measurement.

**Gate: `PASS_P6_BAM_003_R1_QUALITY_CONSTRAINED_0_49`.** This means only that the authorized 50-frame run completed with valid adaptive telemetry, isolated artifacts, all new 15% quality constraints passed, and whole-process runtime improved versus saved V0. P6-BAM-003's historical `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME` remains unchanged. No full-scene, speedup-statistics, or general quality claim is made.

Recommendation: proceed to researcher review for a single matched LIGHT 0–499 V0/V-A2 comparison, with unchanged thresholds and explicit acknowledgment of the narrowly missed historical PSNR provisional bound and unmeasured online-wall criterion. Do not launch it automatically. No repeat, extra variant, scene, frame range, evaluator workload, controller change, threshold tuning, or push was performed.

Phase 4 checkpoint checksum remained `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`; captured hashes for P6-BAM-002/003 reference artifacts also matched post-run. No source algorithm, released config, profiler, tracking, keyframe selection, CPU offload, Gaussian append/prune, or Phase 4 artifact was modified.
