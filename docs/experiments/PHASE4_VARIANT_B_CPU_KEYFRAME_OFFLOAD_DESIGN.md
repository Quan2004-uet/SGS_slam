# Phase 4 Variant B — CPU Keyframe Offload Implementation Design

Date: 2026-10-10

Variant ID proposed for implementation: `PHASE4-VB-001`

Repository: `/home/robot/research/SGS_slam`

Design HEAD: `249e22f873e4ead32d4837cbccbcf38b3c3ff2fd` (`main`)

Phase 3 rollback tag: `phase3-runtime-closure-2026-10-10`

This document specifies a future implementation. It does not authorize or
contain a source/config change, CUDA workload, experiment, evaluation, commit,
or push.

## 1. Current keyframe ownership

### 1.1 `keyframe_list` structure

`scripts/slam.py:658-660` initializes three process-lifetime Python lists:
`keyframe_list`, `keyframe_time_indices`, and `timestamp_keyframes`.
Each normal keyframe dictionary contains:

| Field | Current value | Current residency/lifetime |
|---|---|---|
| `id` | Python frame index | Host metadata; retained for the run |
| `est_w2c` | Estimated 4×4 world-to-camera tensor | GPU; retained for the run |
| `color` | RGB tensor, shape 3×H×W | GPU; retained for the run |
| `depth` | Depth tensor, shape 1×H×W | GPU; retained for the run |
| `semantic_id` | Semantic-ID tensor, shape 1×H×W when semantics are enabled | GPU; retained for the run |
| `semantic_color` | Semantic-color tensor, shape 3×H×W when semantics are enabled | GPU; retained for the run |

The dataset transfers all returned tensors to its configured device at
`datasets/gradslam_datasets/basedataset.py:357-406`. The online path then
permutes/normalizes them at `scripts/slam.py:726-750` without moving archived
payloads back to CPU.

### 1.2 Insertion sites

- Checkpoint resume reconstructs prior keyframe dictionaries from dataset
  frames at `scripts/slam.py:674-723`.
- Normal online insertion occurs at `scripts/slam.py:1022-1039` after the
  released cadence condition. The dictionary stores direct references to the
  current GPU color/depth/semantic tensors.
- The cadence is controlled by `keyframe_every=5` in
  `configs/replica/slam.py:12-16`; the final pre-terminal insertion condition
  is part of the existing source and must remain unchanged.

No current path evicts a keyframe or converts its payload to CPU. The whole
logical archive is therefore also the whole GPU-resident archive.

### 1.3 Overlap-selection reads

`scripts/slam.py:899-921` passes `keyframe_list[:-1]` to
`keyframe_selection_overlap`. `utils/keyframe_selection.py:40-110` iterates
the candidate dictionaries and reads only `keyframe['est_w2c']`; archived
color, depth, semantic ID, and semantic color are not read for the active
overlap ranking. The source then appends the latest logical keyframe and the
current-frame sentinel `-1` to the selected mapping list.

### 1.4 Mapping payload reads

At `scripts/slam.py:930-960`, each mapping iteration:

1. calls `np.random.randint` over the existing `selected_keyframes` list;
2. resolves either current frame `-1` or one selected keyframe index;
3. reads that keyframe's `color` and `depth`;
4. when semantics are enabled, reads `semantic_id` and `semantic_color`;
5. sends the resulting `iter_data` through the unchanged mapping loss,
   renderer, backward, prune/densify hooks, and optimizer update.

## 2. Variant B invariant

Variant B changes only physical residency. It must preserve:

- the complete logical keyframe archive and insertion order;
- exact keyframe IDs;
- released keyframe cadence and terminal-frame condition;
- the overlap candidate set and list slicing behavior;
- overlap projection, ranking, filtering, permutation, and returned indices;
- the number and order of random-number-generator calls;
- random keyframe selection and current-frame sentinel behavior;
- `mapping_window_size=24` and every other mapping-window operation;
- exact RGB, depth, semantic-ID, and semantic-color values;
- tensor dtype, shape, layout required by consumers, and 680×1200 resolution;
- tracking iterations, mapping iterations, learning rates, losses, renderer
  calls, Gaussian addition/pruning/densification behavior, and seed;
- checkpoint keyframe IDs and reconstruction semantics.

The only intended difference is:

- archived keyframe image/depth/semantic payloads are authoritative on CPU;
- after random selection, one archived payload is staged synchronously to the
  configured GPU only for the mapping iteration that consumes it;
- the staged GPU references are released after all iteration consumers have
  finished and before the next iteration where safe.

`est_w2c` remains GPU-resident in the first implementation. It is 64 bytes per
keyframe in Phase 3 evidence and is actively consumed by GPU overlap
projection. Keeping it unchanged avoids introducing per-candidate pose copies,
device changes, or ranking-order differences.

This is a Phase 4 source variant, not pure released baseline reproduction.

## 3. Exact source modification surface

The minimal proposed implementation changes only `scripts/slam.py`.

| Current region | Function/scope | Proposed change |
|---|---|---|
| Near `scripts/slam.py:47-73` or immediately before `rgbd_slam` | New local helper(s) | Add one helper that builds a keyframe dictionary with CPU-authoritative payload and one helper that synchronously stages an archived payload to `device`. Helpers must not call RNG, cast, resize, compress, pin, or modify values. |
| `scripts/slam.py:674-723` | `rgbd_slam`, checkpoint reconstruction | Reconstruct prior payload fields into CPU-authoritative storage while leaving `id`, keyframe ordering, `keyframe_time_indices`, and GPU `est_w2c` unchanged. |
| `scripts/slam.py:930-960` | `rgbd_slam`, mapping iteration data selection | Preserve `np.random.randint` and selected index resolution exactly; only after selection, synchronously stage the selected archived payload and build the same `iter_data`. Current-frame `-1` continues to use existing GPU tensors directly. |
| After all per-iteration consumers, currently around `scripts/slam.py:982-996` | `rgbd_slam`, end of mapping iteration | Drop references to the staged dictionary and its `iter_data` after optional progress reporting and optimizer work. Do not add `torch.cuda.synchronize()`, `empty_cache()`, or `gc.collect()` per iteration. |
| `scripts/slam.py:1022-1039` | `rgbd_slam`, normal keyframe insertion | Store detached CPU copies for color/depth/semantic payload fields; preserve GPU `est_w2c`, ID, insertion condition, and append order. |

Explicitly out of scope:

- `configs/replica/slam.py` and every other experiment config;
- `utils/keyframe_selection.py` selection/ranking code;
- `datasets/gradslam_datasets/basedataset.py` dataset placement behavior;
- `get_loss`, renderer wrappers, Gaussian state, pruning/densification,
  optimizers, losses, seeds, resolution, and iteration counts;
- pinned-memory pools, non-blocking transfers, prefetch, persistent GPU cache,
  keyframe eviction, payload compression, quantization, or reduced precision;
- Variant A, D, or E changes.

No feature flag is proposed for `PHASE4-VB-001`. The variant should be isolated
by its own branch/commit and provenance record rather than editing the released
Replica config. A future configurable implementation would be a separate
design decision.

## 4. Data movement design

The first implementation uses pageable CPU memory and blocking host-to-device
semantics (`non_blocking=False`, explicitly or by default).
No dtype argument is passed during `.to(device)` staging, so PyTorch preserves
the source dtype.

| Field | Authoritative storage | Staging device | Copy semantics | Lifetime and release |
|---|---|---|---|---|
| `est_w2c` | Existing GPU tensor | None | No change and no copy in Variant B | Retained for logical keyframe lifetime; overlap selection reads the same tensor. |
| `color` | Detached CPU tensor | Configured GPU | Exact CPU copy at insertion/resume; synchronous `.to(device)` after keyframe selection; no cast or normalization | CPU copy lives for archive lifetime. One GPU copy lives through loss/render/backward/optional progress reporting for that mapping iteration, then its references are dropped. |
| `depth` | Detached CPU tensor | Configured GPU | Same as color; no resize, scale, or cast during offload/stage | Same lifetime as staged color. |
| `semantic_id` | Detached CPU tensor | Configured GPU | Preserve the runtime dtype exactly; never call `.float()`, `.long()`, or another conversion in the offload helper | CPU archive lifetime; staged only when semantics are enabled and an archived keyframe is selected; released with the iteration payload. |
| `semantic_color` | Detached CPU tensor | Configured GPU | Exact synchronous transfer with no renormalization or cast | CPU archive lifetime; staged/released with the iteration payload. |

The source asks the loader for integer semantic IDs, while the Phase 3 memory
record attributes 3,264,000 bytes per semantic-ID frame. The implementation
must not resolve this by assumption. Static and dataset[0] validation must
record the actual runtime dtype/element size and require exact preservation.

Copy requirements:

- CPU archive tensors must not share mutable GPU storage.
- Offload happens only after preprocessing/normalization already performed by
  the released path.
- `torch.equal` must pass for CPU source versus a CPU round-trip of the staged
  GPU tensor; dtype, shape, stride/contiguity expected by mapping, and values
  must be checked separately.
- No host-to-device transfer occurs in the current-frame `-1` branch.
- The staging helper must not make any RNG call.

Safe release point:

- not before `get_loss`, renderer execution, `loss.backward()`, prune/densify,
  optimizer step, zero-grad, and optional `report_progress` have completed;
- after those consumers, remove Python references to the staged container and
  iteration data. PyTorch's allocator/stream lifetime rules handle outstanding
  work; do not synchronize merely to reclaim/log memory;
- verify during bounded tests that no staged tensor is retained by `loss`,
  `losses`, progress hooks, or another dictionary into the next iteration.

## 5. Keyframe-selection correctness

Variant B leaves `utils/keyframe_selection.py` unchanged and retains the same:

- `keyframe_list` length, order, dictionaries, and IDs;
- `keyframe_list[:-1]` candidate slice;
- GPU `est_w2c` tensors and their dtype/values;
- current depth, intrinsics, and current pose inputs;
- sampled pixel count and all Torch/NumPy RNG calls;
- sort, positive-overlap filter, permutation, and truncation to
  `mapping_window_size - 2`;
- append of the latest keyframe and current-frame sentinel.

Because overlap selection reads only `est_w2c` from each archived keyframe,
moving image/depth/semantic payloads to CPU does not change the data consumed
by ranking. The implementation must stage payload only after
`selected_rand_keyframe_idx` has been produced. Doing so prevents transfer
logic from changing random selection or candidate behavior.

Validation must compare the ordered selected keyframe-ID trace at every
mapping frame against a preserved Phase 3 trace where available. If the
baseline trace is unavailable for a gate, a fresh unchanged control trace must
be captured under the same environment before claiming selection equivalence.

## 6. Mapping correctness

For each mapping iteration:

1. Execute the unchanged `np.random.randint` call.
2. Resolve the same selected list entry.
3. If it is `-1`, use current GPU tensors exactly as released code does.
4. Otherwise, read the selected logical dictionary and synchronously stage its
   four payload fields to the configured GPU, preserving values, dtype, shape,
   and field names.
5. Build the same `iter_data` dictionary with unchanged camera, intrinsics,
   pose history, ID, and staged payload references.
6. Execute unchanged loss, three semantic-mode renderer passes, backward,
   prune/densify hooks, Adam step, zero-grad, and optional progress reporting.
7. Drop staged payload references only after the last consumer.

No staging cache is included in `PHASE4-VB-001`. At most one archived
keyframe payload should be staged by the mapping loop at a time. A persistent
or mapping-window GPU cache would introduce Variant C residency semantics and
must not be silently combined with this implementation.

The variant may be slower because it can transfer the same keyframe repeatedly
across 60 mapping iterations. Runtime is a measured tradeoff, not permission
to alter selection, iterations, or mapping behavior.

## 7. Expected memory saving

Phase 3 evidence measured 26,112,064 bytes per keyframe:

- `est_w2c`: 64 bytes;
- color: 9,792,000 bytes;
- depth: 3,264,000 bytes;
- semantic ID: 3,264,000 bytes;
- semantic color: 9,792,000 bytes.

Variant B retains the 64-byte pose and removes 26,112,000 bytes per keyframe
from long-lived GPU residency.

| Boundary | Logical keyframes | Baseline resident keyframe bytes | Long-lived GPU bytes removed | Pose bytes retained | Maximum one-keyframe staging | Expected keyframe-related GPU bytes during archived-keyframe use | Expected net reduction at that moment |
|---:|---:|---:|---:|---:|---:|---:|---:|
| Frame 499 | 101 | 2,637,318,464 | 2,637,312,000 | 6,464 | 26,112,000 | 26,118,464 | 2,611,200,000 |
| Frame 1293 | 259 | 6,763,024,576 | 6,763,008,000 | 16,576 | 26,112,000 | 26,128,576 | 6,736,896,000 |

Outside an archived-keyframe mapping iteration, expected long-lived GPU
keyframe storage is only the pose total. Current-frame tensors remain on GPU
as in the released path and are not counted as an offload saving.

Expected temporary staging overhead is 26,112,000 bytes for one payload, plus
small Python/container and allocator overhead. Actual allocated/reserved
effects are `UNKNOWN` until measured. The design must detect accidental
double-staging or references surviving into the next iteration.

Worst-case transfer volume is up to 1,566,720,000 payload bytes per mapped
frame if all 60 mapping iterations select archived keyframes. Actual transfer
volume depends on the unchanged random choices. At 401 logical keyframes, the
CPU archive would be about 10,470,912,000 payload bytes plus poses/metadata, so
host-RAM capacity must be checked before a full-scene run.

## 8. Main risks

### Transfer overhead

Repeated synchronous H2D copies can substantially increase runtime. Do not
reduce iterations or add a cache to hide this cost in the first controlled
variant.

### Synchronization and ordering

Pageable synchronous transfers can block the host, but make readiness explicit
for the first implementation. Do not add explicit CUDA synchronization unless
required for correctness and separately justified.

### Deterministic random selection

Any added Torch/NumPy/Python RNG call, changed list order, or staging before
selection can alter the keyframe sequence. Helpers must be RNG-free and the
existing RNG calls must remain in the same order.

### Accidental dtype/value/layout conversion

Calling `.float()`, changing semantic-ID dtype, renormalizing semantic color,
or rebuilding tensors from NumPy would violate the invariant. Use tensor
device copies and validate exact equality.

### `non_blocking` and pinned memory

Pinned CPU memory and `non_blocking=True` are excluded from the minimal
implementation. They require explicit source-buffer lifetime and stream/event
reasoning. Adding them later is a separate controlled performance variant.

### Reference lifetime bugs

`iter_data`, loss objects, progress hooks, or local aliases may retain staged
tensors longer than intended. Conversely, releasing/reusing a source buffer
too early can corrupt asynchronous work. Validate one-stage-at-a-time
residency without per-iteration `empty_cache()` or `gc.collect()`.

### CPU memory pressure

GPU savings become host-RAM residency. The full-scene logical archive may
exceed 10 GB, excluding dataset/runtime state. Pre-run host-memory and disk
checks remain required.

### Checkpoint/resume

The released checkpoint stores parameters and `keyframe_time_indices`, not
keyframe payloads (`scripts/slam.py:1041-1045`). Resume reloads historical
frames from the dataset. Variant B must rebuild CPU-authoritative payloads at
`scripts/slam.py:674-723` without changing checkpoint format, IDs, order,
normalization, or pose reconstruction. Resume equivalence requires its own
bounded test before relying on checkpoints.

## 9. Minimal implementation strategy

Proposed implementation sequence for a future authorized task:

1. Work on a dedicated Variant B branch/commit derived from the Phase 3
   closure, leaving the closure tag immutable.
2. Add two small local helpers in `scripts/slam.py`:
   - archive an already-preprocessed keyframe payload as detached CPU tensors;
   - stage one archived payload synchronously to the configured device.
3. Route both insertion paths—checkpoint reconstruction and live insertion—
   through the same archive helper.
4. Modify only the archived-keyframe branch of mapping payload retrieval.
5. Add scoped reference release after all iteration consumers.
6. Keep current-frame handling, poses, selection, RNG, mapping, optimizer,
   renderer, Gaussian logic, configs, and checkpoint format unchanged.
7. Add only lightweight validation counters/equality assertions in the test
   harness or variant-specific evidence layer; do not add per-frame production
   logging or profiling.

Do not combine tensor-lifetime restructuring beyond the staged payload
(Variant A), optimizer offload (Variant D), renderer changes (Variant E),
pinned memory, prefetch, or a bounded persistent cache with `PHASE4-VB-001`.

## 10. Validation gates

Each gate stops on mismatch, OOM, numerical failure, or unexpected source
surface. Do not auto-retry or stack another optimization.

1. **Static CPU round-trip equality**
   - For every payload field, check CPU archive → GPU stage → CPU round trip
     with `torch.equal`, identical dtype, shape, element size, and required
     layout.
   - Verify helper calls do not consume RNG state.
   - Verify only the declared `scripts/slam.py` regions changed.

2. **Dataset index 0**
   - Record source and archived devices, values, dtype, shape, and semantic-ID
     element size.
   - Confirm intrinsics, pose, resolution, depth validity, and semantic content
     are unchanged.

3. **First-frame initialization**
   - Verify the released first-frame Gaussian count contract, parameter fields,
     semantic optimizer exclusion/inclusion, finite state, and initial memory.
   - Verify the first keyframe payload becomes CPU-authoritative while its pose
     remains unchanged on GPU.

4. **Bounded frames 0–99**
   - Guard index 100 before the real loader.
   - Compare logical keyframe IDs and ordered selected keyframe-ID traces with
     the unchanged control under the same seed/environment.
   - Compare Gaussian-count trajectory, tracking/mapping losses within a
     predefined numerical policy, finite state, pruning events, and iteration
     counts.
   - Confirm at most one archived payload is staged at a time.

5. **Bounded frames 0–499**
   - Guard index 500 before the real loader.
   - Require 101 logical keyframes at the Phase 3 boundary where reproducible.
   - Measure CPU archive bytes, long-lived/staged GPU keyframe bytes,
     post-frame allocated/reserved, peaks, runtime, and transfer volume.
   - Compare against Phase 3C-6 without claiming bit-exact Gaussian counts
     where independent baseline runs already differed slightly.

6. **Bounded frames 0–999, if needed**
   - Use if frame 499 does not establish stable offload residency, adequate
     memory margin, or acceptable correctness/runtime behavior.

7. **Full Replica room0 frames 0–1999**
   - Run only after explicit researcher authorization and all prior gates pass.
   - Keep the released workload unchanged except for declared residency.
   - Stop without retry on OOM, numerical failure, selection mismatch, or
     runtime failure; preserve evidence.

8. **Evaluation gate**
   - Do not run ATE, rendering metrics, semantic metrics, post-SLAM
     optimization, or paper comparison before full-scene online PASS and a
     separate evaluation authorization.

## 11. Acceptance criteria

Variant B is `PASS` only if all applicable conditions hold:

- the logical keyframe archive, IDs, order, cadence, and count are identical to
  the intended released behavior;
- overlap candidate sets and ordered selected keyframe-ID behavior are
  preserved under the controlled seed/environment;
- random mapping selection has no added RNG calls and preserves the intended
  selected-index trace;
- staged RGB/depth/semantic values, dtypes, shapes, and resolution are exact;
- tracking/mapping iterations, loss definitions, renderer calls, Gaussian
  behavior, optimizer behavior, pruning, and seed remain unchanged;
- observed losses and trainable/non-trainable numerical state remain finite;
- no source/config changes exist outside the declared Variant B surface;
- a material reduction in long-lived GPU memory is measured at 0–499;
- no more than one archived keyframe payload is staged at once in the minimal
  implementation;
- failure handling preserves evidence and does not retry automatically;
- no evaluation or post-SLAM stage runs before full-scene PASS and separate
  authorization.

Completion of frames 0–1999 is required before Variant B can claim full-scene
runtime PASS. It does not by itself prove metric equivalence or reproduce paper
results.

## 12. Rollback plan

If Variant B changes logical behavior, selected-keyframe traces, tensor
values/dtypes/shapes, numerical stability, checkpoint semantics, or produces
an abnormal metric/runtime trace:

1. Stop the current gate immediately; do not retry with another optimization.
2. Preserve the exact branch/commit, command, environment, logs, JSON,
   selected-ID trace, memory evidence, and failure point.
3. Classify the failure before editing again.
4. Return the working baseline to immutable tag
   `phase3-runtime-closure-2026-10-10` in a clean branch/worktree; do not
   rewrite or overwrite Phase 3 evidence.
5. Mark `PHASE4-VB-001` failed or paused as appropriate.
6. Do not automatically add Variant A, C, D, E, pinned memory, reduced
   workload, or another policy. A new hypothesis requires explicit researcher
   authorization and separate provenance.

## 13. Evidence and source basis

- `docs/experiments/PHASE4_MEMORY_MANAGEMENT_PLAN.md`
- `docs/experiments/PHASE3_BASELINE_CLOSURE_2026-10-10.md`
- `docs/experiments/PHASE3_RUNTIME_CONCLUSION_2026-10-10.md`
- `results/runtime_artifacts/phase3c6/phase3c6_results.json`
- `results/runtime_artifacts/full_scene_room0/full_scene_room0_results.json`
- `scripts/slam.py`
- `utils/keyframe_selection.py`
- `datasets/gradslam_datasets/basedataset.py`
- `configs/replica/slam.py`
