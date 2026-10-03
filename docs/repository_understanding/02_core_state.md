# Core state and data structures

## `params`: persistent GPU model state

Let `N` be Gaussian count and `T` configured frame count. Unless noted, tensors are float32 CUDA and initially `torch.nn.Parameter(requires_grad=True)`. **[VERIFIED FROM SOURCE]**

| Key | Shape | Meaning | Grows with N | Main writers |
|---|---:|---|---|---|
| `means3D` | `N×3` | centers in first-frame world coordinates | yes | init, append, mapping, densify/prune |
| `rgb_colors` | `N×3` | precomputed RGB values | yes | init, append, mapping |
| `unnorm_rotations` | `N×4` | real-first quaternion, normalized at use | yes | init, mapping; rotation is immaterial for exactly isotropic scale **[INFERRED]** |
| `logit_opacities` | `N×1` | sigmoid parameterization of opacity | yes | init zero, mapping, pruning/reset |
| `log_scales` | `N×1` | isotropic log radius; tiled to 3 axes | yes | projective init, mapping/densify |
| `semantic_ids` | `N` | fixed source class ID, used for editing/export filtering | yes | init/append/prune; excluded from optimizer |
| `semantic_colors` | `N×3` | trainable semantic RGB channel | yes | init/append/mapping |
| `cam_unnorm_rots` | `1×4×T` | relative w2c quaternions | no | init, tracking/GT branch |
| `cam_trans` | `1×3×T` | relative w2c translations | no | init, tracking/GT branch |

Although `semantic_ids` originate as integer images, concatenation with float point data promotes them to float in memory; final save casts them to `uint8`. **[VERIFIED FROM SOURCE]**

## `variables`: persistent auxiliary state

| Key | Shape/lifetime | Meaning |
|---|---|---|
| `max_2D_radius` | `N`; whole run, reset on pixel append | largest observed raster radius |
| `means2D_gradient_accum` | `N`; whole run/reset/resize | accumulated screen-space gradient norm for optional densification |
| `denom` | `N` | observation count for the above |
| `timestep` | `N` | frame of Gaussian creation; resized with map |
| `scene_radius` | scalar | max first depth / config ratio |
| `means2D` | temporary reference replaced each loss call | synthetic screen-space leaf used for densification gradient |
| `seen` | `N`, replaced each call | `radius > 0` visibility mask |

**[VERIFIED FROM SOURCE]** `means2D` can retain the most recent computation graph until overwritten or the surrounding references are released; its exact allocator impact needs profiling.

## Per-frame and per-iteration structures

`curr_data`/`tracking_curr_data`/`iter_data` contain raster settings `cam`, normalized RGB `3×H×W`, metric depth `1×H×W`, ID, `3×3 K`, constant first-frame w2c, a GT-pose list (diagnostics), and optionally semantic ID/color images. They live on the configured device. **[VERIFIED FROM SOURCE]**

`keyframe_list` is a Python list of dictionaries `{id, est_w2c, color, depth, semantic_id?, semantic_color?}`. All tensor values remain on GPU because dataset outputs are moved to the device and no `.cpu()` is applied. Its image tensors scale with keyframe count and resolution. **[VERIFIED FROM SOURCE]**

`gt_w2c_all_frames` is a growing Python list of GPU `4×4` tensors. `timestamp_keyframes` is CPU/Python metadata. Raster output images, masks, `transformed_pts`, render dictionaries, losses, and autograd nodes are per iteration. **[VERIFIED FROM SOURCE]**

## Lifetimes

- Whole run: `params`, most `variables`, datasets/path metadata, camera settings, keyframes, GT poses.
- One frame: input images, current dictionaries, tracking optimizer, candidate pose copies, selected keyframe indices.
- One mapping event: mapping Adam and its moments, mapping loop temporaries.
- One loss iteration: transformed points, three render passes, masks, rendered images, autograd graph.
- Save-only metadata (`intrinsics`, `w2c`, GT poses, dimensions, keyframe indices) is inserted into `params` after evaluation.
