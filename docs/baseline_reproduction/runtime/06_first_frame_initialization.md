# First-Frame Initialization Boundary

## Runtime status

**BLOCKED — NOT EXECUTED.**

The Phase 3B contract requires Gate 3 dataset integrity to pass before any
first-frame initialization. The authoritative dataset is unavailable, so the
actual loader was not instantiated, frame 0 was not loaded, and no Gaussian
state or initialization VRAM measurement exists. This is deliberately not a
runtime PASS claim.

## Released source path prepared for the resumed gate

`VERIFIED FROM SOURCE`:

```text
configs/replica/slam.py data settings
  -> scripts/slam.py:get_dataset()                         lines 47-71
  -> ReplicaDataset / GradSLAMDataset
     -> file discovery and c2w trajectory parsing
     -> RGB/depth/semantic preprocessing
     -> relative-to-frame-0 c2w pose and CUDA transfer
  -> scripts/slam.py:initialize_first_timestep()           lines 190-246
     -> dataset[0]
     -> HWC-to-CHW conversion and color scaling
     -> pose inversion c2w -> w2c
     -> setup_camera()
     -> valid-depth mask
     -> get_pointcloud()                                  lines 74-131
     -> initialize_params()                               lines 133-178
     -> scene_radius = max(depth) / scene_radius_depth_ratio
```

The online caller is `scripts/slam.py:584-633`. The canonical config uses the
same resolution for the base and densification paths, so the caller takes the
non-separate branch at lines 628-633.

## State that must be runtime-checked after acquisition

The source prepares these fields, but none was runtime-verified in Phase 3B:

- trainable Gaussian tensors: `means3D`, `rgb_colors`,
  `unnorm_rotations`, `logit_opacities`, `log_scales`, and
  `semantic_colors`;
- non-Parameter semantic metadata: `semantic_ids`, listed in
  `params_opt_exclude`;
- trainable per-frame camera arrays: `cam_unnorm_rots`, `cam_trans`;
- auxiliary tensors: `max_2D_radius`, `means2D_gradient_accum`, `denom`,
  `timestep`, plus scalar `scene_radius`.

`initialize_first_timestep()` does not create an optimizer. Optimizers are
created later by `initialize_optimizer()` at the tracking and mapping call sites
(`scripts/slam.py:774` and `scripts/slam.py:924`), so Phase 3B must not force
optimizer creation merely for inspection.

## Deferred runtime evidence

| Required evidence | Status |
|---|---|
| Frame-0 RGB/depth/semantic tensors | BLOCKED |
| Runtime intrinsics and relative c2w pose | BLOCKED |
| Initial valid-depth pixel / Gaussian count | BLOCKED |
| Parameter shapes, dtypes, devices, finiteness | BLOCKED |
| Semantic trainability and optimizer exclusion | BLOCKED |
| CUDA allocated/reserved/peak boundaries | BLOCKED |
| 4 GiB first-frame sufficiency | UNKNOWN |
| Optional bounded first render | DEFERRED |

No diagnostic harness was created because it could not be executed against the
required dataset. No SLAM, tracking, mapping, renderer-on-dataset, evaluation,
or post-opt path was run.
