# Full-Scene Memory Optimization Log

Dataset/scene: Replica `room0` 2000-frame online run  
GPU: NVIDIA GeForce RTX 5080, 16 GB class device  
Released baseline HEAD: `dd8caa772bd9511c018d298e38c081a679de2c72`

This log records full-scene memory attempts separately from baseline source,
configuration, and algorithm changes. No evaluation or post-SLAM optimization
is included in these attempts.

## Attempt 0 — baseline full-scene run

`RUNTIME VERIFIED` from `results/runtime_artifacts/full_scene_room0/`.

- Status: `CUDA_OOM`.
- Completed frames: `0–1293`.
- OOM frame: `1294`.
- Stage: mapping.
- Runtime: `8089.096434480045` seconds as recorded by the runtime summary.
- Maximum allocated: `13,602,712,064` bytes.
- Maximum reserved: `15,843,983,360` bytes.
- Resident keyframes at the last stable frame: 259.
- Unique keyframe tensor payload: `6,763,024,576` bytes.
- Evaluation, ATE, rendering metrics, paper comparison, and post-opt were not run.
- Released source/config remained unchanged.

Evidence: `results/runtime_artifacts/full_scene_room0/`.

## Attempt 1 — runtime allocator + low-overhead instrumentation

`RUNTIME VERIFIED` from `results/runtime_artifacts/full_scene_room0_allocator_opt_fast/`.

- Status: `CUDA_OOM_ALLOCATOR_OPT`.
- Allocator settings: `PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True,garbage_collection_threshold:0.8` and `CUDA_MODULE_LOADING=LAZY`.
- Completed frames: `0–1332`.
- OOM frame: `1333`.
- Stage: mapping.
- Runtime: `8318.3` seconds.
- Maximum allocated: `12,547,390,464` bytes.
- Maximum reserved: `15,839,789,056` bytes.
- Source/config/algorithm unchanged.
- Evaluation/post-opt not run.
- Evidence path: `results/runtime_artifacts/full_scene_room0_allocator_opt_fast/`.

### Comparison with Attempt 0

- Attempt 0 completed `0–1293`.
- Attempt 1 completed `0–1332`.
- Improvement: `+39` completed frames.
- Allocated memory decreased by approximately `1.06 GB`.
- Reserved memory decreased by only approximately `4 MB`.
- Conclusion: fragmentation reduction was not enough; live memory residency remains the main blocker.

### Interpretation

- `RUNTIME VERIFIED`: the allocator-optimized attempt extended the run by 39 frames but still reached CUDA OOM.
- `INFERRED`: full 2000-frame Replica `room0` is unlikely to complete on 16 GB using only runtime allocator settings.
- `UNKNOWN`: whether source-level memory-policy changes can complete 2000 frames while preserving acceptable metrics.

### Decision

- Do not retry an identical allocator-only full-scene run.
- The next step is either:
  - **A.** Close baseline reproduction with the documented memory limit; or
  - **B.** Start a new memory-policy research variant, explicitly marked as non-baseline.

No new experiment was run while creating or updating this log.
