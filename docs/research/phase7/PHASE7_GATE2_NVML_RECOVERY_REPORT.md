# Phase 7 Gate 2 — NVML telemetry recovery

**Run:** `p7_bcgm_g2_room0_on_0_499_r01`<br>
**Session:** `SESSION_005` — ACTIVE<br>
**Recovery:** `RECOVERED_FROM_ORIGINAL_CSV`

## Recovered values

The original `nvml_samples.csv` was parsed independently with Python's CSV
reader. Its header is
`utc,gpu_index,memory_used_mib,utilization_gpu_percent`; all 2,334 data rows
have four fields, parse successfully, and report GPU index 0.

| Quantity | Verified value |
|---|---:|
| Valid samples | 2,334 (`2334`) |
| Invalid samples | 0 |
| Sampled device-wide peak memory used | 4,877 MiB (`4877 MiB`) |
| Peak timestamp (UTC) | `2026-10-27T04:16:03.322036+00:00` |
| GPU index at peak | 0 |
| Utilization at peak-memory sample | 95% |
| Maximum sampled GPU utilization | 98% |

The original
`results/runtime_artifacts/phase7_gate2/p7_bcgm_g2_room0_on_0_499_r01/run_summary.json`
records `nvml_valid_samples: 0` and
`nvml_peak_device_used_mib: null`. These are runner aggregation errors, not
the CSV's telemetry result. The independently recovered values are saved in
`results/runtime_artifacts/phase7_gate2/p7_bcgm_g2_room0_on_0_499_r01/nvml_recovered_summary.json`.
The original summary and CSV remain unchanged.

## Verified parser cause

In `tools/phase7/gate2_on_runner.py`, the sampler writes four fields for each
valid line: timestamp followed by the three `nvidia-smi` values. The summary
aggregation later iterates past the header but accepts only `len(row) == 3`
and appends `row[1]` as memory. Actual valid records have length four, so the
predicate rejects every row before conversion. This directly explains the
zero count; no further root cause is needed or inferred.

Minimal future correction: accept four fields, parse `row[2]` for memory,
`row[1]` for device index, and `row[3]` for utilization; separately recognize
the two-field `NVML_ERROR` records. This report does not modify the executed
runner and no rerun was performed.

NVML here is sampled **device-wide** usage. It is distinct from the
process-wide PyTorch CUDA allocator's allocated and reserved peaks.
