# Phase 5 Profiling Instrumentation Plan

Status: `PROPOSED` for P5-G2; no instrumentation is implemented by this document.
Invariant: profiling must preserve PHASE4-VB-001 values, dtypes, devices, selection/RNG order, schedules, losses and output state.

## Timing model

CUDA work is asynchronous. Three distinct clocks are required and must not be substituted for one another:

1. **CPU dispatch time**: `time.perf_counter_ns()` around Python/API regions, with no synchronization. It measures host work and launch overhead, not completion of GPU work.
2. **GPU elapsed time**: paired `torch.cuda.Event(enable_timing=True)` recorded on the active stream. Read after a batched synchronization at a frame/mapping boundary. It measures ordered GPU work between events.
3. **End-to-end synchronized wall time**: `perf_counter_ns()` with one explicit synchronization at a predefined boundary. It includes host work, transfers, GPU work and waiting; use sparingly for ground-truth frame latency and overhead calibration.

Do not synchronize around every renderer call or mapping iteration. Record events per component and resolve them once per frame (or every N profiling frames). H2D from pageable memory with `non_blocking=False` may block the host, but both wall and event timing are still recorded. Sum mutually exclusive spans only; renderer/loss/backward/step event spans are sequential on the current stream, while frame end-to-end is reported separately and never added to their sum.

## Telemetry schema

Each JSONL record includes `schema_version`, `run_id`, `frame_idx`, `mapping_iter` (nullable), `stage`, `metric`, `value`, `unit`, `clock_kind`, and `sampled`. A compact per-frame record should also contain keyframe count, Gaussian count, selection IDs, staged bytes, CUDA memory snapshots, RSS/HWM and exception/status. A final summary records percentiles and peaks; raw records remain authoritative.

## Measurement points

### CPU and end-to-end wall time

| Metric name | Source file/function | Mechanism / frequency | Synchronization | Expected overhead / limitations | Output field |
|---|---|---|---|---|---|
| `frame_load_cpu_ms`, `frame_load_e2e_ms` | `scripts/slam.py:759-782`; `GradSLAMDataset.__getitem__` | perf counter every frame; optionally split decode/preprocess and `.to` inside loader | CPU timer none; e2e profile samples synchronize before/after only every N frames | Low normally; sampled e2e sync medium. Loader currently combines CPU and GPU transfer | `timing.frame_load.*` |
| `tracking_cpu_dispatch_ms` | `scripts/slam.py:802-887` | perf counter every frame | None | Low; not GPU elapsed | `timing.tracking.cpu_dispatch_ms` |
| `tracking_e2e_ms` | same | synchronized wall every profiling frame; retain released unsynchronized timer as legacy | One sync before/after region on sampled frames | Medium; may perturb overlap (none explicit in V0) | `timing.tracking.e2e_ms` |
| `keyframe_insert_ms` | `scripts/slam.py:1059-1077` | perf counter on insertion | Copy is synchronous; no extra sync initially | Low; includes dict/copy, not allocator attribution | `timing.keyframe_insert.wall_ms` |
| `selection_wall_ms` | `scripts/slam.py:931-953`, `keyframe_selection_overlap` | perf counter every mapping frame | One event pair for GPU work; resolve at frame boundary | Low-to-medium; function mixes Python loop and GPU ops | `timing.selection.wall_ms` |
| `archive_copy_ms` | `archive_keyframe_payload_on_cpu` | per field and total on insertion | Event pair plus boundary resolution; D2H pageable copy semantics noted | Low event overhead; Python timer may include wait | `timing.archive_copy.{field}_ms` |
| `h2d_wall_ms` | `stage_keyframe_payload` | total and per field for every staged selection | No added per-copy sync; event pair, resolved at boundary | Event creation at 114k events is material; default aggregate fields into one span, detailed sampling 1/N | `timing.h2d.wall_ms` |
| `mapping_cpu_dispatch_ms`, `mapping_e2e_ms` | `scripts/slam.py:958-1040` | dispatch every mapping frame; synchronized e2e sampled | One boundary sync for sampled e2e | Medium for e2e; do not sum with component spans | `timing.mapping.*` |
| `serialization_wall_ms` | `scripts/slam.py:1134-1150`, save helper | perf counter once; bytes written from file stats | Synchronize once before timing serialization to exclude pending CUDA | Low and required for clean phase boundary | `timing.serialization.wall_ms` |

### GPU operation timing

| Metric name | Source | Mechanism / frequency | Synchronization | Overhead / attribution limit | Output field |
|---|---|---|---|---|---|
| `render_rgb_gpu_ms` | `get_loss`, lines 273-280 | CUDA events; sample configured iterations | Resolve at frame boundary | Renderer launches external kernels; event span is inclusive | `gpu_time.render_rgb_ms` |
| `render_depth_sil_gpu_ms` | lines 275, 282-289 | CUDA events; sampled | Boundary | Same | `gpu_time.render_depth_sil_ms` |
| `render_semantic_gpu_ms` | lines 291-295 | CUDA events when semantics enabled | Boundary | Same | `gpu_time.render_semantic_ms` |
| `loss_gpu_ms` | lines 296-332 | Events after renders through scalar loss assembly | Boundary | Some reductions may induce host sync elsewhere; label inclusive | `gpu_time.loss_ms` |
| `backward_gpu_ms` | calls at 829 and 1000 | Events around `loss.backward()` | Boundary | Includes autograd and renderer backward | `gpu_time.backward_ms` |
| `optimizer_step_gpu_ms` | calls at 831 and 1015 | Events around step | Boundary | Includes lazy Adam state initialization on first step | `gpu_time.optimizer_step_ms` |
| `gaussian_append_gpu_ms` | `add_new_gaussians`, call 923 | Events around function; optional nested silhouette/concat samples | Boundary | Inclusive span; nested spans not added to parent | `gpu_time.gaussian_append_ms` |
| `prune_gpu_ms` | call 1004 | Events only when active prune condition is true; count no-op calls separately | Boundary | Avoid 120k useless event pairs | `gpu_time.prune_active_ms` |
| `densify_gpu_ms` | call 1010 | Events only if enabled/executed | Boundary | Expected absent in V0 | `gpu_time.densify_ms` |
| `h2d_gpu_ms` | staging helper | Events around grouped copies; sample per-field detail | Boundary | Pageable synchronous behavior limits overlap; event duration does not include all host paging cost | `gpu_time.h2d_ms` |

### GPU memory attribution

Use exact tensor storage accounting (`untyped_storage().nbytes()` with storage-pointer de-duplication), separated from CUDA allocator snapshots. Never sum aliased views twice.

| Metric | Point / frequency | Mechanism | Limitation | Output field |
|---|---|---|---|---|
| Gaussian parameter bytes by field | after initialization, append, prune, mapping end; periodic frame milestones | de-duplicated tensor storage bytes | Logical storage, not allocator fragmentation | `gpu_bytes.gaussian_params.<field>` |
| Semantic attribute bytes | same | semantic IDs separate from trainable semantic colors | IDs excluded from Adam but remain GPU map state | `gpu_bytes.semantic.*` |
| Gaussian auxiliary bytes | same | variables dict storage inventory | Temporary `means2D` may vary by iteration | `gpu_bytes.gaussian_aux.*` |
| Gradient bytes | after backward before zeroing, sampled | `param.grad` storage inventory | `set_to_none=True` changes lifetime; snapshot phase matters | `gpu_bytes.gradients.*` |
| Tracking/mapping optimizer bytes | after optimizer creation and after first step | recursively inventory Adam tensor states and param groups | Parameters referenced by optimizer must not be counted as state | `gpu_bytes.optimizer.{stage}` |
| Camera parameter bytes | milestones | exact storage | Small but separate from Gaussian state | `gpu_bytes.camera_params` |
| Archived pose bytes | milestones | unique `est_w2c` storage across keyframes | Does not include Python metadata | `gpu_bytes.keyframe_pose` |
| Staged keyframe bytes | every staged iteration | exact per-field storage | Logical bytes; allocator may retain freed blocks | `gpu_bytes.staged_payload.*` |
| Allocated/reserved/current peaks | frame boundaries; reset local peak only under explicitly documented scoped mode | `memory_allocated`, `memory_reserved`, `max_*` | Allocator totals cannot uniquely attribute renderer/autograd; resetting peaks alters observation semantics, not algorithm | `cuda_allocator.*` |
| Unattributed allocated bytes | milestones | allocator allocated minus unique known live storages | Residual is a bound, not proof of renderer workspace ownership | `gpu_bytes.unattributed_bound` |

### CPU and storage

| Metric | Source/point | Mechanism / frequency | Limit | Output field |
|---|---|---|---|---|
| Archive logical bytes and per-field bytes | archive helper, every insertion | exact CPU tensor storage with de-duplication | Excludes Python/allocator metadata | `cpu_bytes.archive.*` |
| Payload distribution | every insertion | payload total and field histogram/quantiles | Fixed resolution makes it near-constant but preserve evidence | `keyframes.payload_bytes` |
| RSS | frame boundary, every frame or every 5 frames | `/proc/self/status` `VmRSS` | Includes all native/Python memory | `process.rss_bytes` |
| HWM | same | `/proc/self/status` `VmHWM` | Process-wide, monotonic | `process.hwm_bytes` |
| Metadata estimate | sparse milestones | `sys.getsizeof` recursively for keyframe containers only | Incomplete for allocator overhead; report as estimate | `cpu_bytes.keyframe_metadata_estimate` |
| Disk read/write bytes | run start/end and sampled boundaries | `/proc/self/io` deltas plus artifact file sizes | Process-wide; page cache and shared I/O confound | `process_io.*` |
| SSD occupancy/latency | V2 only, not V0 | exact archive files plus timed operations | Filesystem cache must be declared | `archive_io.*` |

### Growth indicators

Every per-frame record contains `frame_idx`, `keyframe_count`, `gaussian_count`, logical bytes/Gaussian, logical bytes/keyframe, tracking and mapping e2e milliseconds, H2D bytes/time, cumulative H2D bytes, online elapsed seconds and effective FPS. Report milestone slopes over predefined windows (0-99, 100-499, etc.); do not fit/extrapolate beyond observed horizon without confidence bounds and an `INFERRED` label.

## Sampling modes

- `profile=off`: byte-for-byte control path with no telemetry hooks executed beyond one disabled branch.
- `profile=light`: frame-level clocks/memory, exact counters, selected-ID trace; intended for full scene.
- `profile=detailed`: component CUDA events on a deterministic sampling schedule; intended for 0-99/0-499.
- Sampling decisions must depend only on frame/iteration index, never RNG, timing or memory values.

## Overhead and equivalence validation

For each horizon run paired `off`, `light`, and `detailed` modes with identical source/config/seed and isolated output directories. Compare selected keyframe traces, keyframe insertion indices, Gaussian counts at every frame, finite-state checks, final tensor keys/shapes and numerical hashes/tolerances. Instrumentation overhead is `(profile wall - off wall) / off wall`; runtime claims compare only identical profiling modes. A provisional acceptance threshold is <=5% median wall overhead for `light` at 0-499 and no algorithmic trace divergence. This is a design threshold to calibrate with repeated bounded runs, not a confirmed property.

## Known attribution limits

PyTorch allocator counters do not reveal external rasterizer internal buffers by semantic component; event boundaries are inclusive, and peak deltas are order-dependent. RSS cannot isolate pageable tensor payload from interpreter/native allocations. CUDA events on one stream do not measure host preprocessing. These limitations must travel with every result rather than being “corrected” by subtraction.
