# Phase 3B First-Frame Gaussian Initialization

## Result

**Phase 3B Status: PASS**

`RUNTIME VERIFIED` on 2026-10-02: the released SGS-SLAM first-frame path
completed for Replica `room0` frame 0 at 680 x 1200 on the NVIDIA GeForce GTX
1650 Ti (4096 MiB). It created 815,998 initial Gaussians with finite,
shape-consistent state. No source, config, algorithm, environment, or dataset
change was required.

Only index 0 was accessed. Tracking, mapping, optimizer construction/steps,
Gaussian addition, pruning, densification, rendering, evaluation, and frame 1+
were not run.

## Pre-flight and environment

```text
environment       /home/quan/miniconda3/envs/sgs_slam_baseline
python            /home/quan/miniconda3/envs/sgs_slam_baseline/bin/python
version           Python 3.9.25
branch            main
HEAD              e4183986204242a8bb422624618af07780a49d26
PyTorch           2.0.1
PyTorch CUDA      11.8
CUDA available    True
OpenCV            4.9.0
NumPy             1.26.4
```

Pre-existing untracked paths were `2402.03246v6.pdf`, `AGENTS.md`, and
`docs/`. No reset, revert, commit, or push was performed.

## Bounded diagnostic method

The temporary harness is `/tmp/sgs_phase3b_first_frame_init.py`. It loaded the
released config and called the released functions; it did not reimplement
point-cloud or Gaussian initialization. A dataset proxy rejected every index
other than 0. Measurement wrappers around the existing `get_pointcloud()` and
`initialize_params()` functions captured intermediate state while
`initialize_first_timestep()` remained the caller.

Exact execution command:

```bash
source /home/quan/miniconda3/etc/profile.d/conda.sh
conda activate sgs_slam_baseline
python /tmp/sgs_phase3b_first_frame_init.py
```

`RUNTIME VERIFIED`: the recorded access list was exactly `[0]`, the dataset
class was `ReplicaDataset`, and both `len(dataset)` and the configured
`num_frames` were 2000.

## Released initialization path

`VERIFIED FROM SOURCE` in `scripts/slam.py`:

```text
config
  -> get_dataset(... relative_pose=True, load_semantics=True)
  -> ReplicaDataset
  -> initialize_first_timestep(dataset, 2000, 3, "projective", cuda:0)
       -> dataset[0]
       -> RGB HWC -> CHW and divide by 255
       -> depth HWC -> CHW
       -> semantic ID HWC -> CHW
       -> semantic color HWC -> CHW and divide by 255
       -> intrinsics 4x4 -> 3x3
       -> w2c = inverse(relative c2w pose)
       -> setup_camera(...)
       -> mask = (depth > 0).reshape(-1)
       -> get_pointcloud(..., compute_mean_sq_dist=True,
                         mean_sq_dist_method="projective")
       -> initialize_params(..., num_frames=2000, load_semantics=True)
       -> variables["scene_radius"] = max(depth) / 3
```

The canonical config has no separate densification resolution, so
`densify_dataset=None` and the canonical intrinsics are passed to
`get_pointcloud()`.

`setup_camera()` creates `GaussianRasterizationSettings`; it does not render.
`initialize_optimizer()` is a separate function and is not called by this
path.

## Frame 0 and point cloud

The loader again returned the six previously verified tensors:

| Item | Shape | Dtype | Device | Finite |
|---|---:|---|---|---|
| RGB | `(680, 1200, 3)` | `float32` | `cuda:0` | YES |
| Depth | `(680, 1200, 1)` | `float32` | `cuda:0` | YES |
| Intrinsics | `(4, 4)` | `float32` | `cuda:0` | YES |
| Relative c2w pose | `(4, 4)` | `float32` | `cuda:0` | YES |
| Semantic ID | `(680, 1200, 1)` | `int32` | `cuda:0` | YES |
| Semantic color | `(680, 1200, 3)` | `float32` | `cuda:0` | YES |

The frame has 816,000 pixels. The source depth mask selected 815,998 positive
depth values and rejected 2 zero-depth pixels. There is no subsampling: the
selected pixel count, point count, and initial Gaussian count are all 815,998.

`RUNTIME VERIFIED` point-cloud state:

```text
shape       (815998, 10)
dtype       torch.float32
device      cuda:0
finite      YES
schema      XYZ | normalized RGB | semantic ID | normalized semantic RGB
columns     x y z r g b semantic_id semantic_r semantic_g semantic_b
```

The RGB, semantic-ID, and semantic-color columns were exactly equal to their
masked frame-0 inputs after the released normalization/conversion. Concatenating
the `int32` semantic IDs with floating-point columns promotes the stored IDs to
`float32`. The point cloud contains 18 unique semantic IDs:

```text
[0, 13, 18, 19, 29, 37, 40, 47, 59, 64, 76, 78, 79, 80, 91, 93, 97, 98]
```

Projective `mean3_sq_dist` has shape `(815998,)`, is finite `float32` on
`cuda:0`, and ranges from `4.0375226e-06` to `6.9641676e-05`.

## Gaussian parameter inventory

All per-Gaussian tensors have leading dimension N = 815,998. Every tensor is
finite.

| Runtime key | Shape | Dtype/device | `requires_grad` | Runtime range |
|---|---:|---|---:|---:|
| `means3D` | `(815998, 3)` | `float32/cuda:0` | YES | -2.264542 to 5.007095 |
| `rgb_colors` | `(815998, 3)` | `float32/cuda:0` | YES | 0.011765 to 1.0 |
| `unnorm_rotations` | `(815998, 4)` | `float32/cuda:0` | YES | 0 to 1 |
| `logit_opacities` | `(815998, 1)` | `float32/cuda:0` | YES | 0 to 0 |
| `log_scales` | `(815998, 1)` | `float32/cuda:0` | YES | -6.209939 to -4.786074 |
| `semantic_ids` | `(815998,)` | `float32/cuda:0` | NO | 0 to 98 |
| `semantic_colors` | `(815998, 3)` | `float32/cuda:0` | YES | 0 to 0.878431 |
| `cam_unnorm_rots` | `(1, 4, 2000)` | `float32/cuda:0` | YES | 0 to 1 |
| `cam_trans` | `(1, 3, 2000)` | `float32/cuda:0` | YES | 0 to 0 |

`cam_unnorm_rots` is initialized to identity quaternions and `cam_trans` to
zero for all 2000 camera slots. The returned first-frame `w2c` is identity
within approximately `1.2e-7`; it is not bit-exact identity because of
floating-point inversion of the relative c2w matrix.

### Rotation, scale, and opacity

- Every raw rotation begins as `[1, 0, 0, 0]`; measured quaternion norms are
  exactly 1.0.
- The scale is isotropic with one stored value per Gaussian. The source computes
  `log(sqrt(mean3_sq_dist))`, where projective
  `mean3_sq_dist = (depth / ((fx + fy) / 2))^2`. Runtime `log_scales` min/mean/max
  are -6.209939 / -5.469156 / -4.786074.
- Raw opacity logits are all 0. Applying the sigmoid gives 0.5 for every
  Gaussian.

## Semantic state

`RUNTIME VERIFIED`:

- `semantic_colors` is a `torch.nn.Parameter`, has shape `(815998, 3)`, is
  `float32` on `cuda:0`, requires gradients, and exactly equals point-cloud
  columns 7:10 at initialization. It is trainable state.
- `semantic_ids` is a plain tensor, has shape `(815998,)`, is `float32` on
  `cuda:0`, does not require gradients, exactly equals point-cloud column 6,
  and is the sole member of `params_opt_exclude`. It is fixed metadata and is
  not an optimizer parameter.

This runtime result confirms the corresponding static audit claims.

## Auxiliary state

| Runtime key | Shape | Dtype/device | Initial value |
|---|---:|---|---:|
| `max_2D_radius` | `(815998,)` | `float32/cuda:0` | all 0 |
| `means2D_gradient_accum` | `(815998,)` | `float32/cuda:0` | all 0 |
| `denom` | `(815998,)` | `float32/cuda:0` | all 0 |
| `timestep` | `(815998,)` | `float32/cuda:0` | all 0 |
| `scene_radius` | scalar | `float32/cuda:0` | 1.6690318584 |

All auxiliary values are finite and all per-Gaussian arrays have leading
dimension N.

## Optimizer and optional render

**Optimizer: NOT CREATED AT FIRST-FRAME INITIALIZATION.** No optimizer groups
exist at this boundary and no `optimizer.step()` was run.

**Optional first-frame render: DEFERRED.** Rendering is not part of
`initialize_first_timestep()`, and it was unnecessary for the required PASS
criteria. `setup_camera()` completed and returned
`GaussianRasterizationSettings`; the renderer was not invoked.

## GPU memory

These are `RUNTIME MEASUREMENT` values from a fresh bounded process after
`empty_cache()`, synchronization, and peak-stat reset. Dataset construction
precedes the baseline measurement.

| Boundary | Allocated bytes | Reserved bytes | Peak allocated bytes |
|---|---:|---:|---:|
| Before frame load | 9,885,696 | 23,068,672 | 9,885,696 |
| After frame load | 35,998,720 | 67,108,864 | 55,582,720 |
| After `get_pointcloud()` | 105,003,520 | 205,520,896 | 171,206,656 |
| After `initialize_params()` | 147,491,840 | 205,520,896 | 171,206,656 |
| After `initialize_first_timestep()` returned | 114,035,712 | 205,520,896 | 171,206,656 |

Peak PyTorch allocation was **171,206,656 bytes (about 163.3 MiB)**. The
largest sampled process value reported by `nvidia-smi` was **302 MiB**. These
measurements establish that 4 GiB VRAM is sufficient for the released baseline
first-frame initialization at 680 x 1200 on this host. They do not predict
renderer, tracking, mapping, optimizer-state, keyframe, or full-sequence memory.

## Integrity and stop boundary

```text
source changed             NO
config changed             NO
environment changed        NO
algorithm changed          NO
dataset changed            NO
temporary harness created  YES (/tmp only)
```

All Phase 3B dataset and initialization criteria now pass. The next authorized
phase is **Phase 3C — Bounded Online Reproduction, starting with 2–5 frames
only**; it was not started here.
