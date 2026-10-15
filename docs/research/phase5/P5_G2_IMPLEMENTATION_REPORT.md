# P5-G2 Profiling Instrumentation Implementation Report

Gate result: `PASS_P5_G2_CPU_STATIC`

## Git provenance

- Phase 4 reference: `37522db553ff18b96592073f9de699db7fa48600`.
- P5-G1 checkpoint: `86ac4f990932563c721187a5cb458f3e07be9ce6`, containing exactly the nine P5-G1 documents.
- Implementation branch: `phase5-profiling-instrumentation`.
- P5-G2 implementation is intentionally uncommitted pending researcher review.
- Pre-existing untracked `vds` remains unmodified and untracked.

## Implementation

`utils/performance_profiler.py` implements a standalone opt-in profiler:

- `off`: singleton null profiler; no files, buffers, timers, CUDA queries/events or synchronization.
- `light`: CPU wall spans, archive/staging counters, Gaussian/keyframe counts, RSS/HWM and allocator milestones.
- `detailed`: light metrics plus deferred/batched CUDA events, sampled component timings, gradient/optimizer state bytes and de-duplicated tensor-storage attribution.
- Streaming JSONL with bounded in-memory write buffer and bounded percentile sample reservoir.
- Unique `<output_dir>/<run_id>` creation with refusal to overwrite.
- JSONL record, run-metadata and summary validators.
- Exception/process-exit cleanup and a final status summary.

`scripts/slam.py` receives minimal optional hooks at the existing operations. The tracking/mapping iteration counts, RNG calls, keyframe candidate selection, staging `.to(..., non_blocking=False)`, archive fields, optimizer operations, Gaussian append, pruning and densification conditions are unchanged.

## Hook map

| Runtime region | Hook |
|---|---|
| Dataset fetch and frame transforms | CPU `frame_preprocessing` |
| RGB/depth-silhouette/semantic renders | sampled CUDA events in `get_loss` |
| Loss construction | sampled CUDA event span |
| Tracking/mapping backward | sampled CUDA events plus pre-zero gradient storage bytes |
| Adam step | sampled CUDA events plus post-step state bytes |
| Keyframe overlap selection | CPU wall, sampled CUDA events and overlap candidate count |
| Per-iteration mapping observation choice | sampled CPU wall around the unchanged single RNG draw/index lookup |
| Archive copy | CPU wall, per-field/logical bytes, keyframe count |
| Synchronous H2D staging | sampled CPU wall/CUDA events, exact events/cumulative bytes |
| Gaussian append, pruning, densification | sampled CUDA events, respecting existing gates |
| Frame boundary | Gaussian/keyframe counts, RSS/HWM, allocated/reserved/peaks, storage attribution |
| Evaluation and serialization | separate CPU wall spans |

CUDA events are accumulated and resolved in one synchronization every configured frame interval, not one synchronization per operation. Pending events are capped; dropped event spans are counted. Each resolved batch records both synchronization wait and a batched end-to-end synchronized wall interval. Event correctness and actual overhead are not CPU-validated.

## Memory attribution

Storage-pointer de-duplication prevents counting aliased tensors twice. Detailed categories are Gaussian parameters, semantic attributes, gradients, optimizer state, auxiliary tensors, GPU keyframe poses and any GPU-resident archived payload. PyTorch allocated memory minus attributable live storage is emitted as `unattributed_allocator_bound_bytes`; it is not labeled renderer memory or total process VRAM. CPU archive logical bytes, approximate Python metadata bytes, RSS and HWM remain separate quantities.

## Configuration

`configs/replica/phase5_profile.py` deep-copies the unchanged released Replica config and adds only a `profiling` section. Its default is `mode="off"`. The base config hash remains `08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3`; the active keyframe-selection source hash remains `1dc1711b017884a3f04b8932e2bfd78fbb72704d48bea7f5d6e86bf81679ef87`.

Missing `profiling` configuration maps directly to the null profiler. Enabled modes require explicit non-empty `run_id` and `output_dir`; an existing output path is rejected.

## Integrity conclusion

`VERIFIED FROM SOURCE/STATIC TESTS`: no released config or keyframe-selection file changed; instrumentation surrounds existing calls and does not add caches, paging, submaps, semantic scheduling, tensor copies or optimizer changes. `UNKNOWN / NEEDS RUNTIME VERIFICATION`: numerical equivalence, CUDA timing validity, synchronization overhead and tensor lifetime effects in an actual GPU execution.
