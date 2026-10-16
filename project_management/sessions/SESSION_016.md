# SESSION_016 — P6-BAM-003-R1 V-A2 quality-constrained 0–49 screen

- Date: 2026-10-16.
- Status: CLOSED.
- Branch: `phase5-profiling-instrumentation`.
- Run source revision: `60372fcc4fac2caa1bfa09c712d9092467289228`; P6-BAM-001/FIX1 source ancestor remains `a3aefc745b73da520fa2ae53e77b0349fd25fa00`.
- Result: `PASS_P6_BAM_003_R1_QUALITY_CONSTRAINED_0_49` (candidate screening only).

Added only `configs/replica/phase6_bam_va2.py` as a V-A2 wrapper with LOW/MID/FULL=45/60/60 and unchanged thresholds 0.01/0.05. CPU/static config parity checks passed and `tests.test_mapping_budget` passed 15/15. Executed exactly one LIGHT run on Replica room0 frames 0–49, run ID `p6_bam_003_r1_room0_0_49_va2_r01`; no repeat, other variant, scene, horizon or evaluator was launched. V-A2 completed 50/50 frames, 50 events, 49 valid novelty signals, 1 FULL/12 MID/37 LOW decisions, 2,445/3,000 iterations, finite saved state and zero dropped CUDA spans. All events covered prune iteration 20. CPU archive/H2D staging remained active.

Against the already saved P6-BAM-003 V0 0–49 run, all seven researcher-defined 15% metric checks passed. Mean PSNR decreased 0.50164 dB (derived MSE increase 12.244%), Depth L1 increased 9.087%; other constraints passed. The historical P5-LEAN PSNR target (≤0.5 dB) is narrowly missed by 0.00164 dB. Process wall improved 11.33%, mapping-loop wall improved 20.18%, but separately delimited online wall remains unmeasured. These are single-run screening observations, not statistical speedup or non-inferiority evidence. Original P6-BAM-003 stays `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME`.

Reports: `docs/research/phase6_bam/P6_BAM_003_R1_VA2_REPORT.md` and `P6_BAM_003_R1_VA2_COMPARISON.md`. Run outputs, effective config, launch log/timing, telemetry, CPU validation and per-frame table are isolated under `results/runtime_artifacts/phase6_bam/`; Phase 4, P6-BAM-002, and P6-BAM-003 reference hashes matched after the run. No algorithm, profiler, released config, tracking, selection, offload or Gaussian lifecycle source changed.

Recommended next action: researcher review, then separately authorize a matched LIGHT 0–499 V0/V-A2 comparison if desired. No 0–499 run is started by this session. No push.
