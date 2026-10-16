# SESSION_014 — P6-BAM-002 Matched LIGHT 0–10 GPU Smoke Validation

- Date: 2026-10-16.
- Status: CLOSED.
- Branch/source: `phase5-profiling-instrumentation`, `a3aefc745b73da520fa2ae53e77b0349fd25fa00`.
- Result: `PASS_P6_BAM_002_SMOKE_INTEGRATION`; `ADAPTIVE_ACTIVATION_CONFIRMED`.

Executed one V0 and one V-A LIGHT run, sequentially, on Replica room0 frames 0–10. Both completed 11 frames and 11 mapping events without OOM or non-finite saved state. V0 executed 660/660 mapping iterations. V-A executed 420/660 with frame 0 FULL, four MID and six LOW decisions from ten valid append-novelty signals. The required zero-based prune iteration 20 was reached in every mapping event according to source call-site and executed-loop evidence. CPU keyframe archive/staging remained active. No source, profiler, released config, Phase 4 output or historical untracked evidence was modified.

Exact commands, logs, metadata, effective configs, telemetry, validation JSON and saved bounded outputs are under `results/runtime_artifacts/phase6_bam/`. The research reports are `docs/research/phase6_bam/P6_BAM_002_SMOKE_REPORT.md` and `P6_BAM_002_COMPARISON.md`. The Phase 4 authoritative checkpoint SHA256 remained `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2` before and after.

This gate validates only 0–10 integration and adaptive activation. The one-pair timing difference is exploratory; speedup, quality non-inferiority and full-scene feasibility remain unvalidated. Next proposed gate is P6-BAM-003 0–49 only after researcher review and separate authorization. No automatic continuation or push.
