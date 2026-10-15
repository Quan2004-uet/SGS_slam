# P5-G3A-FIX1 — Numerical reproducibility audit

Retry1 final Gaussian counts were:

```text
OFF      1,404,715
LIGHT    1,405,052
DETAILED 1,403,275
```

Logged keyframe insertion and observable selected-mapping traces matched, and
all saved arrays were finite. LIGHT/DETAILED state samples show the first
available sampled-count difference at frame 5 (LIGHT 867,597; DETAILED
867,788). OFF has no per-frame profiler state trace, so the first OFF-vs-other
divergence is not observable from saved artifacts.

The source audit found no profiler RNG calls, tensor clones for timing, or
algorithmic callbacks. Nevertheless, CUDA reduction ordering, pruning near
thresholds, allocator/synchronization scheduling, or existing baseline
nondeterminism remain unresolved hypotheses. The profiler repair does not force
counts to match and does not claim bit-exact equivalence.

Recommended future test (not executed here): repeat a fresh bounded 0–3 or
0–10 comparison with identical environment and per-frame Gaussian-count
telemetry in all modes, then compare deterministic flags and state hashes before
authorizing another 0–99 run.
