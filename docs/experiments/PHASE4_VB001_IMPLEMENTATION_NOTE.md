# Phase 4 VB-001 Implementation Note

Date: 2026-10-10

Variant: `PHASE4-VB-001` — CPU offload of resident keyframe payloads

Branch: `phase4-vb-001-cpu-keyframe-offload`

Implementation base HEAD: `443d3d3251f0ac8d3e0e5489507fe13b506110a4`

Design:
`docs/experiments/PHASE4_VARIANT_B_CPU_KEYFRAME_OFFLOAD_DESIGN.md`

## Status

Implementation complete for static review. No online SLAM experiment, CUDA
workload, dataset gate, evaluation, full-scene run, commit, or push was
performed in this task.

## Files changed

- `scripts/slam.py`: Variant B implementation only.
- `docs/experiments/PHASE4_VB001_IMPLEMENTATION_NOTE.md`: this evidence note.

No config, dataset loader, keyframe-selection utility, renderer helper,
Gaussian helper, optimizer helper, loss, or evaluation file was changed.

## Exact functions and regions changed

Current post-change line regions:

- `scripts/slam.py:513-541`
  - `KEYFRAME_PAYLOAD_FIELDS`
  - `archive_keyframe_payload_on_cpu(keyframe)`
  - `stage_keyframe_payload(keyframe, device)`
- `scripts/slam.py:705-754`, inside `rgbd_slam`
  - checkpoint-resume keyframe reconstruction now archives payload fields as
    detached CPU copies before appending the logical keyframe.
- `scripts/slam.py:962-1033`, inside the mapping loop
  - the existing `np.random.randint` and selected-index resolution remain
    first;
  - only an already-selected archived keyframe is synchronously staged;
  - current-frame `-1` handling is unchanged;
  - staged references are dropped after backward, optimizer work, and optional
    progress reporting.
- `scripts/slam.py:1059-1077`, inside normal keyframe insertion
  - payload fields are archived as detached CPU copies before list insertion.

## Invariants preserved by construction

- Logical `keyframe_list` entries, IDs, order, append points, and cadence are
  unchanged.
- `est_w2c` is not copied or moved by the archive helper and remains on the
  configured GPU for unchanged overlap selection.
- `utils/keyframe_selection.py` is unchanged; candidate slicing, overlap
  ranking, permutation, and selected IDs use the existing path.
- `np.random.randint` remains in its original position and executes before
  any staging call. Neither helper calls Torch, NumPy, or Python RNG.
- Mapping window size, current-frame sentinel behavior, tracking/mapping
  iterations, loss, renderer, Gaussian addition/pruning/densification,
  optimizer behavior, resolution, precision, and seed are unchanged.
- Payload transfers pass no dtype argument and perform no cast, resize,
  normalization, compression, or quantization.
- Staging explicitly uses `non_blocking=False`.
- No pinned memory, prefetch, persistent GPU cache, or keyframe eviction was
  introduced.
- Only one local `staged_keyframe_payload` can exist in the mapping branch;
  references are deleted before the next iteration.
- Checkpoint format and `keyframe_time_indices` are unchanged. Resume rebuilds
  the same logical archive with CPU-authoritative payload fields.

## Implementation behavior

The CPU archive fields are:

- `color`
- `depth`
- `semantic_id`, when present
- `semantic_color`, when present

At archive time, each field is detached and copied to pageable CPU memory with
`copy=True`. The source dictionary is shallow-copied, so `id` and GPU
`est_w2c` retain their existing objects and semantics.

After the mapping RNG selects an archived keyframe, the staging helper verifies
that each archived payload tensor is CPU-resident and performs a synchronous
`.to(device=device, non_blocking=False)`. The staged tensors feed the unchanged
`iter_data` path. Their references are removed only after all consumers,
including optional progress reporting, have completed.

## Assumptions

- Real online execution uses the configured CUDA device; CUDA staging has not
  yet been exercised.
- The selected payload tensors do not require gradients; detaching archive
  copies therefore does not remove an algorithmically used gradient path.
- Dropping `loss`, `losses`, `iter_data`, and staged payload aliases after
  backward/step/reporting is after their last consumer and is required to
  prevent overlap with the next staged keyframe.
- PyTorch caching-allocator stream safety is sufficient after Python
  references are dropped; no explicit synchronize or per-iteration
  `empty_cache()` was added.
- Semantic fields are conditional. Their actual runtime dtype must be observed
  at dataset[0]; the implementation preserves rather than assumes it.
- Existing checkpoint reconstruction from the dataset remains authoritative;
  no keyframe payload is added to the checkpoint format.

## Static and CPU-only checks performed

- `git diff --check`: PASS before note creation.
- Python syntax compilation with the project environment and pycache redirected
  to `/tmp`: PASS.
- AST-extracted helper test without importing `scripts.slam`: PASS.
- Independent CPU archive copy: PASS.
- CPU archive is unpinned: PASS.
- Payload value equality: PASS.
- Payload dtype and shape preservation across archive/stage helper calls: PASS.
- Mixed test dtypes, including integer semantic IDs: PASS.
- Torch RNG state unchanged across helper calls: PASS.
- Optional no-semantics RGB-D keyframe path: PASS.
- Static diff inspection confirms no config, selection, renderer, loss,
  Gaussian, optimizer, or dataset source modification.

The AST helper test deliberately avoided importing `scripts.slam`, because a
normal import loads the external CUDA rasterizer module. This task prohibited
CUDA work and did not need that import to validate helper semantics.

## Checks not yet performed

- Actual module import with the compiled renderer.
- CPU→CUDA staging and allocator behavior.
- Real dataset index 0 dtype/shape/value checks.
- First-frame initialization.
- Checkpoint/resume runtime equivalence.
- Selected keyframe-ID trace comparison against an unchanged control.
- Tracking/mapping loss or Gaussian-count comparison.
- Finite-state checks on an online run.
- Frames 0–99, 0–499, 0–999, or full 0–1999.
- GPU memory reduction measurement.
- Runtime/transfer-overhead measurement.
- Evaluation, ATE, rendering metrics, semantic metrics, post-SLAM
  optimization, or paper comparison.

## Known risks

- Synchronous pageable-memory transfer can substantially increase mapping
  runtime, with up to one full payload transfer for each mapping iteration.
- Actual CUDA reference lifetime and peak reserved-memory behavior remain
  unverified.
- A retained reference in autograd or reporting could delay staged allocation
  release despite local alias deletion.
- The real semantic-ID dtype/element size must be verified rather than inferred
  from static source or prior byte attribution.
- CPU RAM grows with the complete logical archive and may exceed 10 GB for a
  full scene.
- Checkpoint reconstruction performs historical dataset loads and CPU copies;
  its time and host-memory behavior remain unmeasured.
- Independent runs were not previously bit-exact in Gaussian counts, so the
  numerical comparison policy must distinguish expected runtime variation
  from a Variant B behavior change.

## Next gate

The static CPU round-trip/helper validation is complete. The next separately
authorized gate is dataset index 0, followed by first-frame initialization.
Do not start frames 0–99 until the researcher explicitly authorizes it.
