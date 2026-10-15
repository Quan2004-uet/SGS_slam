# P5-G3A-FIX1 — Implementation

## Modified source

- `utils/performance_profiler.py`: detailed queue drain and event accounting.
- `tests/test_performance_profiler.py`: fake-event queue/accounting tests.
- `tests/cuda_microtest_profiler.py`: bounded real-CUDA lifecycle test.

No `scripts/slam.py`, keyframe selection, released configuration, optimizer,
loss, Gaussian lifecycle, archive, staging, or mapping policy was modified.

## Repair strategy

When the pending queue reaches `max_pending_cuda_events`, the profiler now
forces one bounded batch resolution before creating the next event pair. This
amortizes synchronization over a full queue rather than synchronizing every
operation. The old defensive drop counter remains for a broken backend, but the
supported CUDA path no longer overflows under the tested load.

The summary now includes `cuda_event_accounting` with requested, sampled,
accepted, resolved, pending, dropped, and intentionally-unsampled counts. Event
handles are moved out of the queue before resolution and no tensor references
are retained by the profiler.

## Timing semantics

`gpu_elapsed` is CUDA-event elapsed time for the marked interval. The profiler's
`cuda_batch_synchronize` is host wait time for a batch. `cuda_batch_end_to_end_wall`
includes the wall interval from batch start through synchronization and therefore
can overlap component event ranges. These fields must not be summed as a wall
clock decomposition. H2D timing is the marked device event interval around the
existing transfer call; it is not a claim of pinned/asynchronous transfer.

## Static integrity

`git diff --check` passed. The source diff contains no algorithmic branch,
iteration, RNG, keyframe, optimizer, Gaussian, archive, or staging changes.
