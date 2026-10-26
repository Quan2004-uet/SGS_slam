# P5-G3B Readiness

Status: **`BLOCKED_BY_P5_G3A_RETRY1`**

The earlier sandbox preflight blocker remains preserved in the historical
P5-G3A report. CUDA was subsequently recovered and a fresh direct-host retry
ran C0/C1/C2 on Replica room0 frames 0–99. C0 and C1 completed. C2 completed
the horizon but emitted `dropped_cuda_event_spans=1958` (pending events were
zero), violating the P5-G3A zero-drop gate. Final Gaussian counts also differed,
so bit-exact numerical equivalence is not established.

Before any 0–499 run:

1. Diagnose and repair detailed CUDA-event span drops without changing the SLAM algorithm.
2. Repeat a fresh 0–99 C0/C1/C2 comparison with unique run IDs.
3. Require zero pending events, zero dropped spans, valid telemetry, and an explicit equivalence review.
4. Obtain separate researcher approval for P5-G3B.

No frames beyond 99, second scene, optimization variant, cache, paging,
submapping, or semantic scheduler was executed in this retry.
