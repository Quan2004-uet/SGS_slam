# SESSION_015 — P6-BAM-003 Matched LIGHT 0–49 Bounded Comparison

- Date: 2026-10-16.
- Status: CLOSED.
- Execution branch/HEAD: `phase5-profiling-instrumentation`, `bb830b1f6a0a31028f14fe390b8cb4e1a50c47fe` (documentation-only descendant of P6-BAM-001 FIX1 source `a3aefc7`).
- Result: `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME`.

Performed one V0 and one V-A sequential LIGHT Replica room0 run, each exactly frames 0–49. Both had 50 mapping events, finite saved state, valid CPU keyframe archive/staging, zero dropped profiler spans and isolated outputs under `results/runtime_artifacts/phase6_bam/`. V0 executed 3,000/3,000 mapping iterations; V-A executed 1,740/3,000, with 1 FULL, 14 MID and 35 LOW decisions, 49 valid novelty events and no unexpected fallbacks. All mapping loops covered required prune iteration 20. No source, profiler, CPU-offload or released-config changes were made.

The single matched pair observed process wall 192.27 s (V0) versus 143.28 s (V-A). The final-map evaluator sampled the same 11 training views and a CPU read of saved poses assessed all 50 trajectory frames. V-A PSNR was 0.739 dB lower and Depth L1 19.26% higher, exceeding the P5-LEAN provisional quality targets. This is a quality warning, not causal proof or validated non-inferiority; historical OFF-vs-OFF variability remains relevant. No runtime speedup claim is certified.

Reports: `docs/research/phase6_bam/P6_BAM_003_0_49_REPORT.md` and `P6_BAM_003_0_49_COMPARISON.md`. Logs, configs, process timing, telemetry and CPU validator JSON are preserved under `results/runtime_artifacts/phase6_bam/p6_bam_003_comparison/` and the distinct run/telemetry directories. Phase 4 and prior P6-BAM-002 checksums remained unchanged; historical untracked evidence and `vds` were untouched.

Stop here. Recommend targeted review of the PSNR/depth differences and baseline variability before researcher authorization of P6-BAM-004 0–99 fixed-budget ablation. No retry, longer run, extra variant/scene, threshold tuning, additional GPU evaluation or push occurred.
