# SESSION_017 — P6-BAM-005 matched 0–499 V0/V-A2 validation

- Date: 2026-10-16.
- Status: CLOSED after P6-BAM-005 review and documentation checkpoint.
- Branch: `phase5-profiling-instrumentation`.
- Source revision at experiment start: `937cd4bb7df25824e5b43de555d5de78ce11f16c`; Phase 4 tag resolves to `37522db553ff18b96592073f9de699db7fa48600`.
- Gate: `PASS_P6_BAM_005_0_499_QUALITY_CONSTRAINED` (single-pair bounded screening only).

Executed exactly one sequential V0 run followed by one V-A2 run on Replica room0, frames 0–499, LIGHT profiling, seed 0 and parity-checked effective configurations. Both returned 0, completed all 500 frames/events, and saved finite final Gaussian/camera checkpoints, 500-pose trajectories, keyframes, six evaluator outputs, and matched RGB/depth/semantic renders for frames `[0,49,99,149,199,249,299,349,399,449,499]`. V0 executed 30,000 iterations. V-A2 executed 22,695 (1 FULL, 12 MID, 487 LOW); 499 novelty signals were valid and frame 0 safely fell back to FULL. All 500 events recorded the 21-iteration pruning floor. CPU keyframe archive and H2D staging remained active.

A measurement-only monotonic host timer was added around the online loop in `scripts/slam.py`; it introduced no CUDA synchronization and no algorithm behavior change. Online wall was 2,319.05 s (V0) versus 1,963.46 s (V-A2), −15.33%; mapping wall sum decreased 25.85%, process wall decreased 15.13%, and mapping iterations decreased 24.35%. The older ≥20% online-wall target was not reached. One run pair does not establish statistical speedup.

Same-protocol final-map quality evaluation on 11 matched sampled views and 500-pose Horn alignment passed all seven researcher-defined 15% checks and all historical P5 quality margins. The detailed report includes per-frame deltas, resource/staging metrics, exact protocol, limitations, and artifacts. Phase 4 and prior P6 reference hashes remained unchanged; no historical directory was overwritten. Original P6-BAM-003 remains historically INCONCLUSIVE. No repeat, other variant, extra scene/horizon, P6-BAM-004 or 0–1999 run was executed.

Reports: `docs/research/phase6_bam/P6_BAM_005_0_499_REPORT.md` and `P6_BAM_005_0_499_COMPARISON.md`. Detailed runtime-only evidence is isolated under `results/runtime_artifacts/phase6_bam/p6_bam_005_comparison/` and the two unique run/telemetry directories.

Next: researcher review before any 0–1999 full-scene authorization. Do not launch another run or push automatically.
