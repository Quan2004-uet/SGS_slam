# P5-G3A-FIX1 — Synthetic CUDA microvalidation

Command:

```text
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python tests/cuda_microtest_profiler.py
```

The test used no dataset and did not import or invoke SGS-SLAM. Runtime was
approximately `0.09 s` on the RTX 5080.

Results:

- 648 requested/sampled/accepted spans.
- 648 resolved spans.
- 0 dropped spans.
- 0 pending spans at close.
- 648 finite, nonnegative CUDA elapsed measurements.
- Real small H2D spans and logical staging counters exercised.
- Shared CUDA storage aliasing check passed.
- Queue capacity was 16, so the workload exceeded the historical 512-event
  condition while remaining bounded.

Artifact: `results/runtime_artifacts/phase5_profiling/p5_g3a_fix1_profiler_validation/cuda_microtest/`.

This validates profiler lifecycle and accounting, not SGS-SLAM numerical
equivalence or online performance.
