# Phase 7 Gate 3 — NVML parser fix and validation

**Status:** CPU parser regressions passed; Gate 3 GPU run not started.

## Fix location and preserved history

The Gate 2 collector writes CSV rows with four fields after `utc`, while its
runner aggregator checked for three fields and read the wrong column. That
executed runner and all Gate 2 experiment artifacts are unchanged.

Gate 3 uses new helper `tools/phase7/nvml_telemetry.py` from
`tools/phase7/gate3_on_runner.py`. The parser validates the four-column header,
timezone-aware timestamp, expected GPU index, nonnegative memory, and
utilization in [0,100]. Malformed and wrong-GPU samples count as invalid;
two-column `NVML_ERROR` records are counted separately. It computes the peak
memory/timestamp/device and maximum utilization only from valid samples for
the configured GPU.

After a future execution, Gate 3 `run_summary.json` records valid/invalid
sample counts, collector error rows, sampled peak MiB/time/GPU, maximum
sampled utilization and explicit device-wide scope. CUDA allocator allocated
and reserved peaks are separate worker fields and remain process allocator
measurements.

## CPU validation

The regression suite uses both a representative CSV containing ordinary,
malformed, wrong-GPU and `NVML_ERROR` rows, and the untouched Gate 2 CSV. The
real Gate 2 file parses to 2,334 valid samples, zero invalid, zero error rows,
4,877 MiB peak at `2026-10-27T04:16:03.322036+00:00` on GPU 0, and maximum
sampled utilization 98%.

Command and result: Gate 3 CPU suite plus existing Phase 7 CPU suite,
**20 tests passed**. The runner's ordinary invocation also ran its read-only
checks and stopped at `CODEX_GPU_NOT_VERIFIED` before any execution path; it
created no Gate 3 output directory. No CUDA workload, SLAM run, or rerun was
performed.
