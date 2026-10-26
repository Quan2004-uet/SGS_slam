# P5-G3A Equivalence Report

Status: `NOT RUN — BLOCKED_P5_G3A`

No C0/C1/C2 execution occurred. Therefore the following comparisons are unavailable:

- frame horizon and processed-frame trace;
- keyframe insertion indices;
- per-iteration mapping observation selection;
- Gaussian growth and final tensor state;
- archive bytes, staging events and cumulative H2D bytes;
- finite-loss and schedule equivalence;
- numerical parameter differences.

The implementation-level CPU/static evidence remains the P5-G2 result: 20/20 CPU tests passed, the released config and keyframe-selection hashes were unchanged, and CUDA stayed uninitialized during tests. That evidence does not establish online equivalence.

Required future comparison: run C0, C1 and C2 from commit `0118d2cf99bf1fe089f34dea20696ac71101b30d`, with the same Replica `room0` 0–99 contract, seed, GPU and environment. Compare exact frame/keyframe traces where recorded, schedule counts, finite state, tensor keys/shapes, archive/staging counters and declared numeric tolerances.
