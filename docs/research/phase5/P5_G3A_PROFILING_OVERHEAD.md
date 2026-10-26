# P5-G3A Profiling Overhead

Status: `NOT MEASURED — BLOCKED_P5_G3A`

No wall-time or telemetry measurements exist because the CUDA preflight failed before C0. Consequently:

```text
C0 runtime: NOT RUN
C1 runtime: NOT RUN
C2 runtime: NOT RUN
LIGHT overhead: NOT COMPUTABLE
DETAILED overhead: NOT COMPUTABLE
```

The provisional `<=5%` LIGHT target was not evaluated. No claim is made about CUDA event accuracy, synchronization cost, telemetry volume, allocator attribution or profiling perturbation.

Future overhead must use same-commit C0/C1/C2 runs and report:

```text
(T_light - T_off) / T_off * 100
(T_detailed - T_off) / T_off * 100
```

With one run per condition, results must be labeled `PRELIMINARY_SINGLE_RUN_ESTIMATE`.
