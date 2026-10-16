# Current Session Handoff

> **CURRENT OPERATIONAL HANDOFF AUTHORITY.** Use `PROJECT_STATUS.md` for project-wide state; source/config/runtime evidence takes precedence.

Last reconciled: 2026-10-16.

## Session and gate

- Session: `SESSION_015` — P6-BAM-003 Matched LIGHT 0–49 Bounded Comparison; `CLOSED` on 2026-10-16.
- Execution branch/HEAD: `phase5-profiling-instrumentation`, `bb830b1f6a0a31028f14fe390b8cb4e1a50c47fe`. Algorithm implementation/FIX1 remains `a3aefc745b73da520fa2ae53e77b0349fd25fa00`; the later HEAD was documentation-only.
- Phase 4 reference tag: `37522db553ff18b96592073f9de699db7fa48600`, verified and preserved.
- Gate: `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME`. Structural integration and bounded runtime completed, but preliminary PSNR/Depth L1 quality exceeded provisional degradation targets. No validated speedup, quality non-inferiority or full-scene feasibility claim.
- Original Phase 5 remains `SUPERSEDED_BY_P5_LEAN_INCOMPLETE`. P5-LEAN-001, P6-BAM-001/FIX1 and P6-BAM-002 PASS statuses remain historical and unchanged.
- Deadline 2026-11-05; code/config freeze target 2026-10-28.

## Completed evidence

Exactly one sequential V0 and one V-A LIGHT run completed Replica room0 frames 0–49 inclusive under matched source, data, seed, tracking/keyframe/append/prune/offload policy, profiler and evaluator. V0 run ID `p6_bam_003_room0_0_49_v0_r01` executed 3,000/3,000 mapping iterations. V-A run ID `p6_bam_003_room0_0_49_va_r01` executed 1,740/3,000, with one FULL, 14 MID and 35 LOW events, 49 valid current-event novelty signals and no unexpected fallback. Both had 50 mapping events, finite checkpoints, 12 identical archived keyframe IDs, active CPU archive/H2D staging, and zero dropped LIGHT spans. Every loop reached required prune iteration 20 by source-call-site and completed-budget evidence; LIGHT lacks a direct per-prune-call counter.

Whole-process wall was 192.27 s (V0) versus 143.28 s (V-A), a provisional single-pair observation. The automatic evaluator produced matched final-map metrics on 11 training views. V-A PSNR was 0.739 dB lower and Depth L1 19.26% higher; the P5-LEAN provisional targets were 0.5 dB and 10%. ATE Mean/RMSE used all 50 saved relative-w2c poses with the Phase 4 Horn formula and did not show analogous deterioration. Baseline numerical variability remains unresolved, so the quality observation is a warning, not causal proof.

Exact commands, effective configs, source/launcher hashes, full logs, process-time records, CPU-only validator and per-run JSON are in `results/runtime_artifacts/phase6_bam/p6_bam_003_comparison/`. The saved states/evaluation outputs and LIGHT telemetry reside in independent `p6_bam_003_room0_0_49_*_r01/` and `telemetry/<run_id>/` directories. Research interpretation is in `docs/research/phase6_bam/P6_BAM_003_0_49_REPORT.md` and `P6_BAM_003_0_49_COMPARISON.md`.

The Phase 4 authoritative checkpoint SHA256 remained `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`; P6-BAM-002 checkpoint and LIGHT-summary hashes remained unchanged. All new outputs are isolated below `results/runtime_artifacts/phase6_bam/`. No populated directory was reused, and old untracked P5 reports, sessions 007–010 and `vds` remain untouched. Source/config/profiler files were not changed. Do not broadly stage untracked files.

## STOPPED HERE / next decision

Stop at `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME`. The immediate next action is researcher review of per-frame PSNR/depth differences, OFF-vs-OFF variability and provisional margins. P6-BAM-004 0–99 fixed-budget ablation is `PLANNED_NOT_STARTED` and requires separate approval; do not launch automatically. No retry, extra scene/variant, threshold tuning, DETAILED profiling, algorithm change or push is authorized by this handoff.

Next-session startup: read `AGENTS.md`, verify branch/HEAD/tag and `git status --short --untracked-files=all`, inspect the P6-BAM-003 reports plus raw comparison/quality evidence, and preserve the Phase 4 and prior Phase 6 outputs before any separately authorized action. The output-directory guard is non-atomic; future authorized runs need fresh IDs and immediate absent-path checks.
