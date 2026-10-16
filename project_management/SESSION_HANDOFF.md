# Current Session Handoff

> **CURRENT OPERATIONAL HANDOFF AUTHORITY.** Use `PROJECT_STATUS.md` for project-wide state; source/config/runtime evidence takes precedence.

Last reconciled: 2026-10-16.

## Session and gate

- Session: `SESSION_016` — P6-BAM-003-R1 V-A2 quality-constrained 0–49 screen; `CLOSED` on 2026-10-16.
- Run source branch/HEAD: `phase5-profiling-instrumentation`, `60372fcc4fac2caa1bfa09c712d9092467289228`. P6-BAM-001/FIX1 implementation source remains `a3aefc745b73da520fa2ae53e77b0349fd25fa00`; this session adds one isolated V-A2 config wrapper and documentation only.
- Phase 4 reference tag: `37522db553ff18b96592073f9de699db7fa48600`, verified and preserved.
- Historical P6-BAM-003 Gate remains `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME`. The separate R1 candidate screen is `PASS_P6_BAM_003_R1_QUALITY_CONSTRAINED_0_49`: one V-A2 run completed 50 frames and all researcher-defined 15% checks passed against saved V0. The historical P5 PSNR limit was narrowly missed, online wall was not separately measured, and no validated speedup, quality non-inferiority or full-scene feasibility claim is made.
- Original Phase 5 remains `SUPERSEDED_BY_P5_LEAN_INCOMPLETE`. P5-LEAN-001, P6-BAM-001/FIX1 and P6-BAM-002 PASS statuses remain historical and unchanged.
- Deadline 2026-11-05; code/config freeze target 2026-10-28.

## Completed evidence

Exactly one sequential V0 and one V-A LIGHT run completed Replica room0 frames 0–49 inclusive under matched source, data, seed, tracking/keyframe/append/prune/offload policy, profiler and evaluator. V0 run ID `p6_bam_003_room0_0_49_v0_r01` executed 3,000/3,000 mapping iterations. V-A run ID `p6_bam_003_room0_0_49_va_r01` executed 1,740/3,000, with one FULL, 14 MID and 35 LOW events, 49 valid current-event novelty signals and no unexpected fallback. Both had 50 mapping events, finite checkpoints, 12 identical archived keyframe IDs, active CPU archive/H2D staging, and zero dropped LIGHT spans. Every loop reached required prune iteration 20 by source-call-site and completed-budget evidence; LIGHT lacks a direct per-prune-call counter.

Whole-process wall was 192.27 s (V0) versus 143.28 s (V-A), a provisional single-pair observation. The automatic evaluator produced matched final-map metrics on 11 training views. V-A PSNR was 0.739 dB lower and Depth L1 19.26% higher; the P5-LEAN provisional targets were 0.5 dB and 10%. ATE Mean/RMSE used all 50 saved relative-w2c poses with the Phase 4 Horn formula and did not show analogous deterioration. Baseline numerical variability remains unresolved, so the quality observation is a warning, not causal proof.

Exact commands, effective configs, source/launcher hashes, full logs, process-time records, CPU-only validator and per-run JSON are in `results/runtime_artifacts/phase6_bam/p6_bam_003_comparison/`. The saved states/evaluation outputs and LIGHT telemetry reside in independent `p6_bam_003_room0_0_49_*_r01/` and `telemetry/<run_id>/` directories. Research interpretation is in `docs/research/phase6_bam/P6_BAM_003_0_49_REPORT.md` and `P6_BAM_003_0_49_COMPARISON.md`.

The V-A2 run ID is `p6_bam_003_r1_room0_0_49_va2_r01`. It executed 2,445/3,000 mapping iterations (FULL/MID/LOW=1/12/37), process wall 170.49 s versus saved V0 192.27 s, and mapping-loop wall 83.585 s versus 104.714 s. All 49 post-initial novelty signals were valid; pruning iteration 20 remained covered. Final map metrics on the matched 11 views passed all seven new 15% constraints versus V0; PSNR decreased 0.50164 dB (derived MSE +12.244%), Depth L1 increased 9.087%. The original P5-LEAN PSNR limit of 0.5 dB was narrowly exceeded; old provisional margins and R1 constraints are both recorded in the reports. Process wall is not online-wall measurement and one pair is not statistical evidence.

Phase 4 checkpoint SHA256 remained `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`; captured P6-BAM-002/003 hashes remained unchanged. All V-A2 outputs are isolated below `results/runtime_artifacts/phase6_bam/`. No populated directory was reused, and old untracked P5 reports, sessions 007–010 and `vds` remain untouched. No source algorithm, profiler, tracking, keyframe, CPU offload, or Gaussian lifecycle code changed. The only source-tree addition is the experiment wrapper; do not broadly stage untracked files.

## STOPPED HERE / next decision

Stop after `PASS_P6_BAM_003_R1_QUALITY_CONSTRAINED_0_49` candidate screening. The immediate next action is researcher review; a matched LIGHT V0/V-A2 run to frame 499 may be considered only after separate authorization. Original P6-BAM-003 remains historically inconclusive and P6-BAM-004 fixed-budget ablation remains `PLANNED_NOT_STARTED`. Do not launch 0–499, repeat, extra scene/variant, tune thresholds, run DETAILED profiling, alter algorithms or push automatically.

Next-session startup: read `AGENTS.md`, verify branch/HEAD/tag and `git status --short --untracked-files=all`, inspect the P6-BAM-003 reports plus raw comparison/quality evidence, and preserve the Phase 4 and prior Phase 6 outputs before any separately authorized action. The output-directory guard is non-atomic; future authorized runs need fresh IDs and immediate absent-path checks.
