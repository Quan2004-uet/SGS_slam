# P5-G3A-R2 — Next step

Do not run 0–99 yet.

The smallest safe next task is a diagnostic bounded run design that adds
passive per-frame Gaussian-count and append/prune observables to OFF only, or a
0–3 OFF repeat if those observables can be obtained without source changes.
The purpose is to locate the first divergence frame and classify whether the
variation is baseline CUDA nondeterminism or profiler-induced. Any added hook
must be profiling-only, preserve RNG/order, and be reviewed before execution.

After that evidence is available, obtain separate approval before rerunning
LIGHT/DETAILED or expanding the horizon.
