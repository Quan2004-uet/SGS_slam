# P5-G3A-R2 — CUDA event validation

Online LIGHT and DETAILED validation: **not run**.

The FIX1 profiler commit was checkpointed as `302e3e6` and its prior synthetic
CUDA result remains valid (648 resolved, 0 dropped, 0 pending). This precheck
did not extend that result to SGS-SLAM because the required OFF-A/OFF-B control
was not reproducible enough to justify profiling comparisons.
