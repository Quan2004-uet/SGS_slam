# SESSION_008 — Phase 5 P5-G3A Retry 1

Status: `PAUSED`
Date: 2026-10-15
Branch: `phase5-profiling-instrumentation`
Commit: `0118d2cf99bf1fe089f34dea20696ac71101b30d`

## Objective

Retry P5-G3A on Replica room0 frames 0–99 after CUDA environment recovery,
using OFF/LIGHT/DETAILED conditions and preserving the earlier blocked evidence.

## Result

C0, C1, and C2 completed frames 0–99. C2 telemetry reported
`pending_cuda_events_at_close=0` and `dropped_cuda_event_spans=1958`, violating
the zero-drop gate. Final Gaussian counts differed across conditions, so exact
numerical equivalence was not established. Gate result:
`BLOCKED_P5_G3A_RETRY1`.

## Evidence

- Retry root: `results/runtime_artifacts/phase5_profiling/p5_g3a_retry1_room0_0_99/`
- Reports: `docs/research/phase5/P5_G3A_RETRY1_0_99_REPORT.md`,
  `P5_G3A_RETRY1_EQUIVALENCE.md`, `P5_G3A_RETRY1_OVERHEAD.md`,
  `P5_G3B_READINESS.md`
- Previous blocked root was preserved unchanged.

## Next task

Diagnose and repair detailed CUDA-event span drops, then request a fresh
0–99 validation. Do not run P5-G3B (0–499) until P5-G3A passes.
