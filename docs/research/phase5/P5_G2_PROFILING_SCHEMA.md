# P5-G2 Profiling Telemetry Schema

Schema version: `p5g2.telemetry.v1`

## Output layout

Enabled profiling creates a new unique directory:

```text
<profiling.output_dir>/<profiling.run_id>/
  run_metadata.json
  telemetry.jsonl
  telemetry_summary.json
```

No directory or file is created in `off` mode. Existing run directories are never overwritten.

## Event record

Every JSONL record requires:

| Field | Meaning |
|---|---|
| `schema_version` | fixed schema identity |
| `run_id` | experiment-unique identifier |
| `frame_id` | online frame or null |
| `iteration_id` | tracking/mapping iteration or null |
| `component` | source/runtime component |
| `metric_name` | metric within the component |
| `value` | finite numeric value |
| `unit` | `ms`, `bytes`, `count`, etc. |
| `measurement_mode` | `light` or `detailed` |
| `timestamp_relative_s` | profiler-relative monotonic timestamp |

## Run metadata

Required core fields include schema, run ID, mode, sampling settings, Python/platform and `PENDING_P5_G3_CUDA_VALIDATION`. The SGS-SLAM integration additionally records scene, frame range, seed, primary device, canonical config SHA-256, Git commit/branch/status, PyTorch/CUDA build versions and GPU name when CUDA profiling is actually enabled.

## Summary

For every metric key `<component>.<metric_name>.<unit>`:

- `observed_sample_count`: all emitted observations;
- `percentile_sample_count`: bounded deterministic reservoir size;
- `total`, `mean`, `peak`;
- `p50`, `p90`, `p95`, `p99` from the bounded reservoir.

Global sections contain online profiler wall time, status, archive keyframe/logical-byte totals, staging event/cumulative-byte totals, pending CUDA events at close, dropped CUDA event spans and CUDA validation state.

## Metrics implemented

- CPU: preprocessing, tracking, mapping, overlap-keyframe selection, per-iteration observation choice, archive copy, sampled H2D wall, evaluation and serialization.
- CUDA events: RGB, depth/silhouette and semantic render; loss; backward; optimizer step; selection; append; prune/densify; H2D.
- GPU allocator: current/peak allocated and reserved. These are PyTorch allocator metrics, not total VRAM.
- State: Gaussian/keyframe counts; Gaussian parameters; semantic attributes; gradients; optimizer state; auxiliary tensors; keyframe pose and archived GPU payload bytes; unattributed allocator bound.
- CPU: archive logical bytes, approximate container metadata, RSS and HWM.
- Transport: exact staging event count and cumulative bytes; sampled event bytes/timing.

## Sampling and size controls

CPU, memory and CUDA-event intervals are deterministic functions of frame/iteration indices and do not consume RNG. JSONL is streamed with bounded buffering. Pending CUDA events, summary percentile samples and flush batches have independent hard caps. Exact aggregate staging/archive counters remain in memory as scalars even when individual events are sampled.

## Timing semantics

- CPU wall metrics use `perf_counter_ns`; they measure host-observed elapsed time.
- GPU elapsed metrics use paired CUDA events ordered on the active stream.
- `cuda_batch_synchronize` reports the explicit batch-resolution wait.
- `cuda_batch_end_to_end_wall` spans from creation of the first event in a deferred batch through its resolving synchronization. It is a batched synchronized wall interval, not a sum of component GPU events.
- Component event time and end-to-end wall time are separate and must not be summed blindly.
- Pageable synchronous H2D host cost and CUDA event time describe different aspects of the same transfer.

`PENDING_P5_G3_CUDA_VALIDATION`: event placement, stream behavior, deferred resolution, real file volume and overhead require a bounded GPU run.
