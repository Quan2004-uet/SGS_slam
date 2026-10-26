# SESSION_010 — P5-G3A-R2 Minimal Equivalence Precheck

Status: `PAUSED`
Date: 2026-10-15
Branch: `phase5-profiling-instrumentation`
FIX1 commit: `302e3e6`

## Result

OFF-A and OFF-B completed Replica room0 frames 0–10 with seed 0 and unchanged
40/60 tracking/mapping iterations. Keyframe insertion and logged mapping
selection traces matched, but final Gaussian counts were 879,862 and 879,218
(difference 644); camera translations also differed. No per-frame Gaussian
trace exists, so the first divergence frame is unknown.

LIGHT and DETAILED were not run. Gate: `BLOCKED_P5_G3A_R2`.

## Evidence

`results/runtime_artifacts/phase5_profiling/p5_g3a_r2_precheck_room0_0_10/`
and the four R2 reports under `docs/research/phase5/`.

## Next task

Design/review passive OFF-only diagnostics to locate the first Gaussian
append/prune divergence. Do not run LIGHT/DETAILED or expand to 0–99 until the
baseline discrepancy is classified.
