# Phase 4 Memory-Management Analysis Plan

Date: 2026-10-10  
Repository: `/home/robot/research/SGS_slam`  
Planning HEAD: `249e22f873e4ead32d4837cbccbcf38b3c3ff2fd` (`main`)  
Phase 3 closure tag: `phase3-runtime-closure-2026-10-10`

This is a design and analysis document. No Phase 4 source implementation,
configuration change, CUDA workload, experiment, evaluation, or paper
comparison was performed while preparing it.

## 1. Phase 3 conclusion summary

`RUNTIME VERIFIED`:

- Destination-host validation passed on the NVIDIA GeForce RTX 5080 16 GB
  server.
- Phase 3C-4 passed the bounded online prefix 0–99.
- Phase 3C-6 passed the bounded online prefix 0–499.
- The unchanged released full-scene baseline completed frames 0–1293 and
  raised CUDA OOM during mapping of frame 1294.
- The runtime-only allocator/low-overhead attempt completed frames 0–1332 and
  raised `CUDA_OOM_ALLOCATOR_OPT` during mapping of frame 1333.
- Allocator settings extended the completed horizon by 39 frames, reduced peak
  allocated memory by about 1.06 GB, and reduced peak reserved memory by only
  about 4 MB. They did not complete Replica `room0` 0–1999.
- Observed losses and captured trainable/non-trainable state remained finite.
  The characterized blocker was memory, not an observed numerical failure.

Phase 3 is closed with a documented memory limitation. It did not reproduce
paper metrics, complete full `room0`, run evaluation/ATE/rendering metrics, or
run post-SLAM optimization.

## 2. Memory bottleneck hypotheses

| ID | Hypothesis | Evidence status | Current assessment |
|---|---|---|---|
| H1 | The retained GPU keyframe payload is the largest directly measured frame-count-dependent resident allocation. | `RUNTIME VERIFIED` plus `VERIFIED FROM SOURCE` | High confidence. Payload grew from 2,637,318,464 bytes at 101 keyframes/frame 499 to 6,763,024,576 bytes at 259 keyframes/frame 1293. No eviction exists. |
| H2 | Gaussian parameters, auxiliaries, gradients, and Adam moments add an independent `O(N)` resident burden. | `RUNTIME VERIFIED` plus `VERIFIED FROM SOURCE` | High confidence for growth; exact total attribution remains unknown. Gaussian count reached about 2.26 million at frame 499 and 4.70 million at frame 1293. |
| H3 | Mapping peak is driven by renderer/autograd transients that scale with Gaussian count and overlap across RGB, depth/silhouette, and semantic passes until backward. | `RUNTIME VERIFIED` for the peak/failure boundary; overlap mechanism partly `INFERRED FROM SOURCE` | High confidence that renderer-stage transient pressure is material. Baseline OOM occurred on a semantic-render allocation during mapping of frame 1294. Exact extension-buffer attribution is unknown. |
| H4 | Allocator fragmentation contributes but is not the primary blocker. | `RUNTIME VERIFIED` and `INFERRED` | The allocator-only run gained 39 frames, but peak reserved changed by only 4,194,304 bytes and OOM still occurred with substantial reserved-but-unallocated memory. Live residency remained too large. |
| H5 | References surviving between tracking, Gaussian append, mapping optimizer creation, and backward may increase transient overlap beyond the semantically necessary lifetime. | `VERIFIED FROM SOURCE` for object creation; `UNKNOWN` for avoidable retained bytes | Requires a controlled lifetime audit. No claim is made that a leak exists. |
| H6 | Semantics materially increase both persistent keyframe residency and renderer pressure. | `RUNTIME VERIFIED` plus `VERIFIED FROM SOURCE` | At frame 1293, semantic ID and semantic color keyframe fields account for 3,381,504,000 of 6,763,024,576 keyframe bytes, approximately half. Semantic colors also add a trainable per-Gaussian field, Adam moments, and a third render pass. |

The hypotheses are not interchangeable. H1 is directly quantified and grows
with keyframe count; H2 grows with Gaussian count; H3 concerns stage peaks;
H4 concerns allocator behavior; H5 is an unverified lifetime opportunity.

## 3. Source-code memory ownership map

### 3.1 Resident keyframes

- `scripts/slam.py:658-660` creates `keyframe_list` and
  `keyframe_time_indices` for the full online run.
- `datasets/gradslam_datasets/basedataset.py:357-406` loads color, depth,
  intrinsics, pose, semantic ID, and semantic color and transfers them to the
  configured device before returning them.
- `scripts/slam.py:1022-1039` stores `est_w2c`, color, depth, semantic ID, and
  semantic color directly in `keyframe_list`. There is no `.cpu()` conversion,
  eviction, or bounded cache.
- `scripts/slam.py:899-921` scans prior keyframe poses for overlap selection.
  `utils/keyframe_selection.py:40-110` uses keyframe `est_w2c`; it does not use
  every archived RGB/depth/semantic payload during overlap ranking.
- `scripts/slam.py:930-960` randomly chooses current data or one selected
  keyframe per mapping iteration and reads that keyframe's image/depth/semantic
  tensors.

Ownership conclusion: the Python list is the long-lived owner of all keyframe
GPU payloads. The logical archive grows at the released cadence
`keyframe_every=5`, while the released mapping window is 24.

### 3.2 Gaussian tensors and auxiliary state

- `scripts/slam.py:133-178` initializes the persistent `params` dictionary:
  `means3D`, `rgb_colors`, `unnorm_rotations`, `logit_opacities`, `log_scales`,
  optional `semantic_ids`, optional trainable `semantic_colors`, and camera
  trajectory parameters. It also creates per-Gaussian `variables` arrays:
  `max_2D_radius`, `means2D_gradient_accum`, `denom`, and `timestep`.
- `scripts/slam.py:421-478` creates pixel-driven new Gaussians and concatenates
  every per-Gaussian field. The auxiliary arrays are resized or concatenated.
- `utils/slam_external.py:127-172` contains optimizer-aware concatenation and
  removal helpers for parameter and Adam-state migration.
- `utils/slam_external.py:179-200` prunes Gaussians. Released online config
  enables pruning, while gradient clone/split densification is disabled.

Ownership conclusion: `params` and `variables` are persistent GPU-resident map
state. Append/prune operations can temporarily coexist with replacement
tensors; exact peak overlap has not been isolated at runtime.

### 3.3 Optimizer states

- `scripts/slam.py:181-187` builds a new Adam optimizer over every parameter
  not in `params_opt_exclude`.
- `scripts/slam.py:772-800` creates the tracking optimizer each frame and runs
  backward/step/`zero_grad(set_to_none=True)`.
- `scripts/slam.py:923-981` replaces it with a mapping optimizer, then runs
  backward, pruning/densification hooks, step, and zero-grad.
- `utils/slam_external.py:109-172` explicitly migrates `exp_avg` and
  `exp_avg_sq` when parameters are replaced, appended, or pruned.

Tracking uses zero learning rates for map fields, but those fields remain in
the optimizer and graph, so Adam state was observed for several zero-LR groups.
The recorded tracking and mapping optimizer byte counts are stage snapshots;
the evidence does not prove that both complete state sets remain resident
simultaneously after optimizer replacement.

### 3.4 Renderer and autograd transients

- `scripts/slam.py:249-389` constructs transformed Gaussian state and invokes
  three renderer passes per semantic loss evaluation: RGB at lines 277–280,
  depth/silhouette at lines 282–289, and semantic color at lines 291–294.
- `utils/slam_helpers.py:131-162` creates per-pass normalized rotations,
  sigmoid opacities, tiled scales, and `means2D` tensors.
- `utils/slam_helpers.py:191-232` creates per-Gaussian depth/silhouette colors
  and another render-variable set.
- `utils/slam_helpers.py:235-270` creates homogeneous points and transformed
  Gaussian centers.
- `scripts/slam.py:964-981` retains the computation needed for a combined loss
  until backward and optimizer step.
- `scripts/slam.py:421-478` also invokes a depth/silhouette render for
  pixel-driven Gaussian addition.

The CUDA rasterizer implementation is an external compiled dependency, not
vendored in this repository. Its tile/sort/backward workspace ownership and
exact allocation formulas remain `UNKNOWN` without bounded runtime profiling.

### 3.5 Semantic tensors

- `datasets/gradslam_datasets/basedataset.py:368-406` loads semantic IDs and
  semantic colors and transfers them to the configured device.
- `scripts/slam.py:151-157` stores fixed `semantic_ids` and trainable
  `semantic_colors` per Gaussian. Semantic IDs are excluded from Adam;
  semantic colors are included.
- `scripts/slam.py:746-750` stores current-frame semantic tensors.
- `scripts/slam.py:1033-1038` retains semantic ID and color for every
  keyframe.
- `utils/slam_helpers.py:153-162` and `scripts/slam.py:291-294` create and
  execute the separate semantic-color render.

## 4. Evidence-based memory attribution

### 4.1 Growth measurements

| Boundary | Gaussians | Resident keyframes | Keyframe payload | Post-frame allocated | Peak allocated | Peak reserved |
|---:|---:|---:|---:|---:|---:|---:|
| Phase 3C-6 frame 0 | 815,998 | 1 | 26,112,064 B | 295,453,696 B | 1,337,694,720 B | 1,539,309,568 B |
| Phase 3C-6 frame 499 | 2,257,421 | 101 | 2,637,318,464 B | 3,675,821,056 B | 6,254,666,752 B | 8,025,800,704 B |
| Full baseline frame 999 | 4,414,351 | 201 | `UNKNOWN` in the summary table | 7,227,769,856 B | 11,668,789,760 B | 14,017,363,968 B |
| Full baseline frame 1293 | 4,698,647 | 259 | 6,763,024,576 B | 8,902,253,568 B | 13,446,667,264 B | 15,839,789,056 B |
| Full baseline frame 1294 in progress | 4,698,647 last stable | 259 last stable | 6,763,024,576 B last stable | 12,291,378,176 B | 13,602,712,064 B | 15,843,983,360 B |

Gaussian counts differ slightly between independently executed runs at the
same boundary; no bit-exact determinism claim is made.

### 4.2 Keyframe attribution

- Phase 3C-6 measured exactly 26,112,064 bytes per keyframe at 680×1200:
  RGB 9,792,000; depth 3,264,000; semantic ID 3,264,000; semantic color
  9,792,000; pose 64 bytes.
- Keyframes grew linearly to 101/2.64 GB at frame 499 and 259/6.76 GB at frame
  1293.
- At frame 1293, keyframe payload was about 76% of the measured post-frame
  allocated bytes. This ratio is a derived comparison, not a claim that all
  remaining allocation is Gaussian state.
- Semantic keyframe fields account for approximately half of the measured
  keyframe payload.

### 4.3 Gaussian and optimizer attribution

- Gaussian count grew from 815,998 at initialization to 2,257,421 at Phase
  3C-6 frame 499 and 4,698,647 at the last stable full-scene baseline frame.
- At frame 499, recorded Adam state was 216,678,332 bytes for the tracking
  stage snapshot and 270,890,544 bytes for mapping.
- At frame 1293, recorded Adam state was 451,135,100 bytes for tracking and
  563,837,664 bytes for mapping.
- Static tensor-shape accounting gives a mapping-time lower bound of roughly
  260 bytes per Gaussian when parameters, auxiliaries, gradients, and two Adam
  moments are materialized. It excludes allocator overhead, transformed/tiled
  tensors, replacement copies, and renderer buffers.
- Tracking and mapping optimizer snapshots must not be summed as guaranteed
  simultaneous residency without a new lifetime measurement.

### 4.4 Peak and failure attribution

- At Phase 3C-6 frame 499, peak allocated exceeded post-frame allocated by
  about 2.58 GB.
- At full-baseline frame 1293, peak allocated exceeded post-frame allocated by
  about 4.54 GB.
- The baseline OOM occurred during mapping frame 1294 after 41 mapping
  iterations, on the next semantic-render allocation.
- The allocator-only run failed at frame 1333. Peak allocated fell from
  13,602,712,064 to 12,547,390,464 bytes, while peak reserved stayed
  effectively unchanged near 15.84 GB.

These measurements support a combined live-residency plus transient-peak
model. They do not provide a complete byte-exact partition of CUDA memory.

## 5. Candidate variants

All savings below are expectations or bounds until measured by a controlled
Phase 4 run.

| Variant | Expected memory saving | Algorithm-behavior risk | Paper-metric comparability risk | Complexity | Required validation |
|---|---|---|---|---|---|
| **A. Tensor lifetime cleanup only** | `UNKNOWN`; expected to reduce avoidable stage overlap and possibly transient peaks, but not the 6.76 GB keyframe archive. | Low if limited to provably dead references/no-grad scopes; medium if backward order or graph construction changes. | Low to medium. Still a source variant even if mathematical operations are intended to match. | Low to medium; requires reference/lifetime audit around tracking optimizer replacement, append, mapping, and render temporaries. | Static ownership assertions; dataset[0]; first-frame; 0–99 equivalence; 0–499 memory comparison; longer gates only if a material saving is measured. |
| **B. CPU offload resident keyframes** | Largest quantified opportunity: up to 2.64 GB at frame 499 and 6.76 GB at frame 1293 before GPU staging/cache cost. One keyframe payload is 26.1 MB. | Low to medium if the complete logical archive, exact dtype/value, keyframe cadence, overlap selection, and random frame selection remain unchanged. Transfer timing can affect performance and potentially execution ordering. | Medium. It is no longer pure baseline, even if intended computations and selected frames are identical. | Medium. Requires CPU authoritative storage, explicit staging, transfer lifetime, and checkpoint/resume handling. | Dataset and dtype checks; exact keyframe IDs/selection trace; 0–99 and 0–499 state/memory comparison; 0–999; full scene; evaluation only after full PASS. |
| **C. Bounded GPU keyframe residency** | With a 24-keyframe GPU cap and a complete CPU archive, theoretical payload reduction at frame 1293 is about 6.14 GB versus retaining all 259 on GPU; actual saving depends on cache/staging. | Medium if only residency is bounded; high if logical keyframes are evicted or selection candidates change. | Medium to high. Any change to candidate set or sampling changes the algorithm. | Medium to high; needs deterministic cache semantics and separation of logical archive from physical residency. | All B gates plus proof that overlap candidates, selected IDs, random choices, and tensor values match the intended policy. |
| **D. Optimizer state offload** | Mapping Adam snapshot was 563.8 MB at frame 1293; tracking snapshot was 451.1 MB. Net saving is `UNKNOWN` because stage states are not proven co-resident and active moments must be staged for every step. | Medium to high. Device transfers, update ordering, precision, and optimizer replacement semantics are sensitive. | High until trajectory/map/metric equivalence is demonstrated. | High; optimizer-aware append/prune state migration must remain correct. | Unit checks for every parameter group and moment after append/prune; first-frame; 0–99/0–499; numerical-delta policy; long gates and full scene. |
| **E. Renderer transient memory reduction** | Potentially material: observed peak-minus-post-frame gap was about 4.54 GB near frame 1293. Exact reducible portion is `UNKNOWN`. | High. Reordering RGB/depth/semantic backward, recomputation, tiling, precision, or external rasterizer behavior can change gradients/results. | High. Renderer changes directly affect losses and optimization. | High to very high; external CUDA code is not vendored and may require dependency-level work. | Renderer forward/backward equivalence; gradient checks; first-frame; 0–99/0–499 with strict finite/delta checks; full scene; complete evaluation after PASS. |
| **F. Larger-VRAM pure-baseline reproduction** | Adds capacity without reducing model memory. Based on the 15.84 GB observed peak, a device materially larger than 16 GB is required; exact sufficient capacity is `UNKNOWN` because growth to frame 1999 was never observed. | None from source/config if environment compatibility is preserved; environment differences remain. | Lowest among options and remains the pure-baseline route. | Infrastructure-dependent, low source complexity. | Destination validation, dataset[0], first-frame, 0–99, then full 0–1999 with failure capture; evaluation only after full PASS. |

## 6. Recommended first variant

**Recommend Variant B: CPU offload of resident keyframe image/depth/semantic
payloads, with the complete logical keyframe archive and all selection policies
preserved.**

Rationale:

1. It targets the largest directly measured and source-confirmed resident
   allocation: 6.76 GB by frame 1293.
2. Keyframe payload grows predictably at 26,112,064 bytes per retained
   keyframe, whereas Variant A has no quantified saving and cannot address this
   linear archive by itself.
3. Overlap selection needs keyframe poses, not every archived image tensor.
   Mapping consumes one selected keyframe payload per iteration, so all image
   payloads do not need to be simultaneously GPU resident to preserve the
   logical candidate set.
4. It avoids changing resolution, keyframe cadence, mapping-window policy,
   tracking/mapping iterations, loss, Gaussian representation, pruning,
   renderer math, or semantic content.
5. It is less coupled to optimizer mutation and external renderer internals
   than Variants D and E.

Design constraints for a future implementation:

- Preserve every logical keyframe and its exact ID, pose, RGB, depth, semantic
  ID, and semantic color.
- Preserve dtypes and values; do not compress, quantize, resize, or discard.
- Preserve overlap-selection candidates, selected IDs, random-number usage,
  mapping-window size, and keyframe cadence.
- Stage only the payload needed for the active mapping iteration, then release
  it at a proven safe lifetime boundary.
- Treat any bounded cache as physical residency only. Logical eviction would
  be a different, higher-risk variant.
- Record transfer time separately from SLAM compute time.

Variant A remains a useful bounded audit before or alongside design review,
but it should not be assumed sufficient and should not be silently combined
with Variant B in the first controlled comparison.

## 7. Validation plan

Each Phase 4 variant requires a distinct modification ID, config snapshot,
command, commit, environment record, output directory, and failure policy.
Compare against the preserved Phase 3 evidence; do not overwrite it.

1. **Static integrity and unit checks**
   - Confirm the only changed ownership/lifetime path belongs to the named
     variant.
   - Verify source/config diffs, keyframe fields, devices, dtypes, shapes,
     logical IDs, optimizer groups, and serialization/resume behavior.
   - For Variant B, verify CPU round-trip equality for RGB, depth, semantic ID,
     semantic color, and pose before any online run.

2. **Dataset index 0**
   - Load Replica `room0` index 0 through the active dataset path.
   - Verify shapes, dtypes, device transitions, intrinsics, depth validity, and
     semantic tensors. Do not run evaluation.

3. **First-frame initialization**
   - Verify 815,998 initial Gaussians where reproducible, field shapes,
     optimizer inclusion/exclusion, finite state, and memory.
   - Compare the variant against the Phase 3 first-frame contract.

4. **Bounded 0–99 gate**
   - Guard index 100 before the real loader.
   - Verify completion, finite losses/state, logical keyframe IDs, selected
     keyframe traces, Gaussian counts, optimizer state, allocated/reserved
     memory, and no evaluation/post-opt entry.

5. **Bounded 0–499 gate**
   - Guard index 500 before the real loader.
   - Compare against Phase 3C-6: 101 logical keyframes, keyframe archive bytes,
     GPU-resident bytes, Gaussian growth, stage optimizer bytes, peak and
     post-frame memory, and runtime.
   - Require a material memory reduction before escalating.

6. **Bounded 0–999 gate, if needed**
   - Use when 0–499 does not establish a clear plateau/margin or when the
     variant introduces a cache/offload steady state that needs validation.
   - Stop on OOM/numerical/runtime failure; do not auto-retry or stack another
     change.

7. **Full Replica room0 0–1999**
   - Run only after prior gates pass and the researcher authorizes the cost.
   - Preserve released workload, dataset boundary, seed, iterations,
     resolution, loss, renderer, keyframe policy, and Gaussian policy except
     for the single declared memory variant.
   - Capture exact failure frame/stage and stop without retry if OOM occurs.

8. **Evaluation gate**
   - Evaluation, ATE, rendering metrics, semantic metrics, post-SLAM
     optimization, and paper comparison remain prohibited until a full-scene
     online run reaches frame 1999 and saves the required outputs.
   - Full-scene PASS authorizes only a separate evaluation decision; it does
     not itself establish paper comparability.

## 8. Classification and provenance boundary

**Phase 4 memory-management variants are not pure released baseline
reproduction. They must be tracked separately from the closed Phase 3
baseline, with distinct source/config provenance, outputs, and claims.**

Variant F is the exception in classification: running the unchanged released
baseline on larger-VRAM infrastructure remains a pure-baseline reproduction
attempt, provided source/config/algorithm and evaluation protocol remain
unchanged and the environment is documented.

No Phase 4 implementation is authorized by this plan alone.

## 9. Evidence and source files used

Runtime and closure evidence:

- `docs/experiments/PHASE3_BASELINE_CLOSURE_2026-10-10.md`
- `docs/experiments/PHASE3_RUNTIME_CONCLUSION_2026-10-10.md`
- `docs/experiments/FULL_SCENE_MEMORY_OPTIMIZATION_LOG.md`
- `results/runtime_artifacts/phase3c6/PHASE3C6_SUMMARY.md`
- `results/runtime_artifacts/phase3c6/phase3c6_results.json`
- `results/runtime_artifacts/full_scene_room0/FULL_SCENE_SUMMARY.md`
- `results/runtime_artifacts/full_scene_room0/full_scene_room0_results.json`
- `results/runtime_artifacts/full_scene_room0_allocator_opt_fast/FULL_SCENE_ALLOCATOR_OPT_FAST_SUMMARY.md`
- `results/runtime_artifacts/full_scene_room0_allocator_opt_fast/full_scene_room0_allocator_opt_fast_results.json`

Source/config and static architecture:

- `scripts/slam.py`
- `utils/slam_helpers.py`
- `utils/slam_external.py`
- `utils/keyframe_selection.py`
- `datasets/gradslam_datasets/basedataset.py`
- `configs/replica/slam.py`
- `docs/repository_understanding/07_keyframe_system.md`
- `docs/repository_understanding/08_loss_and_optimization.md`
- `docs/repository_understanding/10_memory_architecture.md`
- `docs/repository_understanding/13_unknowns_and_runtime_verification.md`
