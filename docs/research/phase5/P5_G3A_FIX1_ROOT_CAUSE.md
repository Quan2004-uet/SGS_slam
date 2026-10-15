# P5-G3A-FIX1 — Profiler root-cause audit

Status: `VERIFIED_FROM_SOURCE` for the queue overflow cause; repair validated by
CPU fake-event tests and a bounded synthetic CUDA microtest. No Replica run was
executed in this fix.

## Failure lifecycle

1. `scripts/slam.py` calls `cuda_start()`/`cuda_stop()` around rendering, loss,
   backward, optimizer, pruning, H2D, and selection hooks.
2. In detailed mode, `cuda_start()` samples when the selected iteration is a
   multiple of `cuda_event_interval` (10), records two CUDA events, and appends
   the pair to `_pending_cuda`.
3. `resolve_cuda_events()` was called from the online loop only at frame
   boundaries satisfying `frame_id % cuda_resolve_interval == 0` (10), plus
   forced close.
4. Before this fix, when `_pending_cuda` reached 512, `cuda_start()` incremented
   `_dropped_cuda_event_spans` and returned `None`. The operation still ran, but
   no timing span existed.

## Verified cause

`max_pending_cuda_events=512` bounded the queue, but production between two
resolution boundaries exceeded that capacity. Retry1 detailed telemetry shows
5,163 resolved `gpu_elapsed` records and 1,958 explicit drops. The source had
no chunked drain and no accepted/resolved accounting. This is a profiler queue
policy failure, not a CUDA OOM or SGS-SLAM algorithm change.

## Accounting semantics

For detailed mode after the fix:

```text
requested = sampled + intentionally_unsampled
sampled = accepted + dropped
accepted = resolved + pending
```

At normal close `pending=0`. Sampling exclusions are counted as
`intentionally_unsampled`; they are not event loss.

## Hypotheses not treated as causes

- CUDA nondeterminism and pruning thresholds remain possible explanations for
  Retry1 Gaussian-count divergence, but are independent of the verified queue
  overflow.
- Event timing overlap and synchronization cost affect performance semantics,
  but do not explain the explicit drop counter by themselves.
