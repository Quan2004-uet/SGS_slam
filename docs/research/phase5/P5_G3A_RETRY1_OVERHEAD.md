# P5-G3A Retry 1 — Profiling overhead

Classification: **`PRELIMINARY_SINGLE_RUN_ESTIMATE`**.

The comparison uses the rounded online progress-loop durations shown by the
three logs, not historical Phase 4 timing: OFF ≈386 s, LIGHT ≈385 s, DETAILED
≈386 s. Therefore the approximate overheads are LIGHT `-0.26%` and DETAILED
`0.00%`. These values are not statistically stable and should not be used as a
benchmark claim. The profiler's recorded whole-process wall times were
408.4769 s (LIGHT) and 409.1983 s (DETAILED); OFF intentionally has no profiler
summary, so those values are not a directly paired timing basis.

Detailed mode produced finite component measurements and zero pending events at
close, but dropped 1,958 CUDA event spans. Until the drop cause is corrected,
the detailed overhead/timing record is diagnostic only.
