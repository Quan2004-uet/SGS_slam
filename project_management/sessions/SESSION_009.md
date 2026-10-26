# SESSION_009 — P5-G3A-FIX1 Profiler Repair

Status: `PAUSED`
Date: 2026-10-15
Branch: `phase5-profiling-instrumentation`
Commit at start: `0118d2cf99bf1fe089f34dea20696ac71101b30d`

## Result

Retry1's 1,958 detailed drops were verified as bounded-queue overflow: events
were resolved only at frame boundaries while production exceeded 512 pending
events. `utils/performance_profiler.py` now drains a full bounded chunk before
creating the next span and reports explicit event accounting.

CPU tests passed 23/23 with CUDA uninitialized. The synthetic CUDA microtest
resolved 648/648 spans in approximately 0.09 seconds with zero drops and zero
pending events. No Replica or online SLAM workload ran.

Gate: `PASS_P5_G3A_FIX1_PREFLIGHT`.

## Remaining uncertainty

Retry1 OFF/LIGHT/DETAILED Gaussian counts differed. The source audit found no
profiler RNG operations, but CUDA reduction/pruning nondeterminism and scheduling
effects remain unclassified. A new small bounded equivalence test requires
separate approval; do not run 0–99 or 0–499 automatically.
