# Phase 3C-1 Bounded Online Reproduction: Frames 0-4

## Result

**Phase 3C-1 Status: PASS**

`RUNTIME VERIFIED` on 2026-10-02: the released online SGS-SLAM path processed
Replica `room0` frame indices 0, 1, 2, 3, and 4 at 680 x 1200 on the NVIDIA
GeForce GTX 1650 Ti. Tracking, pixel-driven Gaussian addition, keyframe logic,
mapping, Adam optimizer use, and configured pruning all executed with finite
losses. The guard intercepted index 5 before the underlying dataset loader was
called.

No source, checked-in config, algorithm, environment, or dataset change was
required. No evaluation, final save, tracking/mapping beyond frame 4, post-opt,
or benchmark was run.

## Pre-flight and regression checks

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
renderer import   PASS
```

Pre-existing untracked paths were `2402.03246v6.pdf`, `AGENTS.md`, and
`docs/`. The tracked source and configs were clean.

## Released online order

`VERIFIED FROM SOURCE` in `scripts/slam.py`:

```text
load current RGB/depth/pose/semantics
  -> initialize current camera pose
  -> tracking Adam + configured tracking iterations (frame > 0)
  -> pixel-driven Gaussian addition (frame > 0 when mapping is scheduled)
  -> geometric overlap keyframe selection
  -> mapping Adam + configured mapping iterations
       -> get_loss(mapping=True)
       -> backward
       -> configured pruning
       -> optional gradient densification
       -> optimizer step
  -> keyframe capture test
  -> checkpoint hook
  -> empty CUDA cache
```

Tracking precedes Gaussian addition. Addition precedes mapping optimizer
creation. Mapping selection occurs before the current frame can be appended to
the stored keyframe list; the current frame is included explicitly as `-1`.
The paper-described semantic-mIoU keyframe filter remains commented out and was
not restored.

The final evaluation/save path is after the online loop. It was never reached
because the dataset guard stopped execution before loading index 5.

## Active baseline configuration

The following values have both a checked-in definition and an active read-site
in the released online path:

| Setting | Value | Executed behavior |
|---|---:|---|
| Tracking iterations | 40 | frames 1-4 |
| Mapping iterations | 60 | frames 0-4 |
| `map_every` | 1 | mapping every frame, including frame 0 |
| `keyframe_every` | 5 | capture frame 0 and frame 4 |
| Mapping window | 24 | request up to 22 overlap keyframes, then latest + current |
| Tracking weights | depth 1.0, RGB 0.5, semantic 0.05 | all three active |
| Tracking silhouette | enabled, threshold 0.99 | active loss mask |
| Mapping weights | depth 1.0, RGB 0.5, semantic 0.1 | all three active |
| Pixel addition | enabled, silhouette threshold 0.5 | frames 1-4 |
| Pruning | enabled | called each mapping iteration; active checks at iterations 0 and 20 |
| Opacity threshold | 0.005 | active pruning threshold |
| Opacity reset | disabled | did not execute |
| Gradient clone/split densification | disabled | zero runtime calls |
| Checkpoint | enabled every 500 in source config | artifact-only hook disabled in harness |
| W&B | enabled with placeholder entity in source config | disabled through existing runtime flag |
| `eval_every` | 5 | consumed only by final evaluation, which was not reached |

The diagnostic copy changed only `use_wandb=False`,
`save_checkpoints=False`, and the output path under `/tmp`. These controls
prevented external logging and frame-0 checkpoint artifacts. Iterations,
resolution, losses, learning rates, mapping cadence, keyframe cadence, and
Gaussian behavior were unchanged. Two frame-0 `report_progress` calls were
suppressed because the task explicitly prohibited evaluation/metric reporting;
they are reporting hooks and do not update SLAM state.

## Bounded harness and frame guard

The temporary harness is `/tmp/sgs_phase3c1_bounded_online.py`. It calls
`rgbd_slam()` and the released stage functions. Wrappers only record stage
inputs/outputs, losses, optimizer state, timings, and memory.

The guarded dataset retained the real length of 2000 so that the source's
`time_idx == num_frames-2` keyframe condition was not changed. It loaded only:

```text
[0, 1, 2, 3, 4]
```

The next requested index was 5; the proxy raised before delegating to
`ReplicaDataset`. Thus no frame greater than 4 was loaded.

The authoritative machine-readable result and console log are:

```text
/tmp/sgs_phase3c1_results.json
/tmp/sgs_phase3c1_bounded_online.log
```

An initial instrumentation run created a reference cycle by binding a measured
`step()` closure directly to each optimizer. That retained obsolete optimizer
states and invalidated its cross-frame memory curve. Its results were preserved
as `/tmp/sgs_phase3c1_results_retention_artifact.json`. The harness was changed
to a non-cyclic forwarding proxy and the entire bounded run was repeated. Only
the second run reported below is accepted as memory evidence.

## Frames and tracking

Frame 0 uses the initialized identity camera and does not enter tracking.
Frame 1 copies the preceding pose as its initial estimate. Frames 2-4 use the
released component-wise constant-velocity extrapolation. All recorded raw
quaternions and translations remained finite.

Tracking component values below are already multiplied by the checked-in loss
weights, matching the dictionary returned by `get_loss()`.

| Frame | Iterations | Initial total (D / RGB / semantic) | Final total (D / RGB / semantic) | Stage time |
|---:|---:|---|---|---:|
| 1 | 40 | 76,677.94 (25,457.04 / 49,164.69 / 2,056.21) | 10,984.21 (2,508.23 / 8,245.13 / 230.84) | 8.780 s |
| 2 | 40 | 15,223.62 (2,934.72 / 11,965.72 / 323.18) | 8,236.51 (1,167.88 / 6,856.62 / 212.02) | 8.396 s |
| 3 | 40 | 16,833.41 (3,271.31 / 13,204.39 / 357.70) | 8,205.63 (1,149.16 / 6,838.35 / 218.12) | 8.345 s |
| 4 | 40 | 19,554.03 (4,022.05 / 15,124.60 / 407.37) | 7,970.64 (1,060.31 / 6,696.55 / 213.78) | 8.276 s |

Every total and component was finite for all 160 tracking iterations.

Final camera state after tracking:

| Frame | Raw quaternion `[w,x,y,z]` | Translation `[x,y,z]` |
|---:|---|---|
| 0 | `[1, 0, 0, 0]` | `[0, 0, 0]` |
| 1 | `[1.001542, 0.002471, -0.002951, -0.001450]` | `[-0.012927, -0.002618, 0.008007]` |
| 2 | `[1.000762, 0.004162, -0.005485, -0.002882]` | `[-0.025359, -0.006741, 0.015299]` |
| 3 | `[1.000668, 0.005211, -0.007545, -0.004052]` | `[-0.037373, -0.011790, 0.022422]` |
| 4 | `[1.000664, 0.005621, -0.009067, -0.004835]` | `[-0.048925, -0.016815, 0.028897]` |

## Gaussian addition and pruning

The addition mask is the released silhouette/new-foreground union intersected
with valid depth. Its final selected count exactly matched the new point-cloud
and appended-Gaussian count.

| Frame | N before | Valid depth | Added | N after addition | Pruned at iter 0 / 20 | N after frame |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 815,998 | 815,998 | 0 | 815,998 | 0 / 0 | 815,998 |
| 1 | 815,998 | 815,996 | 13,068 | 829,066 | 0 / 0 | 829,066 |
| 2 | 829,066 | 816,000 | 12,700 | 841,766 | 0 / 0 | 841,766 |
| 3 | 841,766 | 815,996 | 10,751 | 852,517 | 7 / 21 | 852,489 |
| 4 | 852,489 | 815,998 | 8,615 | 861,104 | 23 / 11 | 861,070 |

New semantic colors were trainable `(N_added,3)` parameters; new semantic IDs
were fixed `(N_added,)` metadata. Every appended timestep equaled its current
frame index. All per-Gaussian fields remained shape-consistent after addition
and pruning.

Configured gradient clone/split densification had zero runtime calls. Opacity
reset was disabled and did not run.

## Keyframes

| After frame | Stored keyframe IDs | Count | Unique referenced tensor storage |
|---:|---|---:|---:|
| 0 | `[0]` | 1 | 26,112,064 bytes |
| 1 | `[0]` | 1 | 26,112,064 bytes |
| 2 | `[0]` | 1 | 26,112,064 bytes |
| 3 | `[0]` | 1 | 26,112,064 bytes |
| 4 | `[0,4]` | 2 | 52,224,128 bytes |

Each stored keyframe contains `id`, estimated `w2c`, RGB `(3,680,1200)`, depth
`(1,680,1200)`, semantic ID `(1,680,1200)`, and semantic color
`(3,680,1200)` on `cuda:0`.

Before frame 4 was appended, the only stored keyframe was frame 0. The source
passes `keyframe_list[:-1]` to overlap selection, leaving no older overlap
candidates in this prefix. The effective mapping frame IDs were therefore:

```text
frame 0: [0]
frame 1: [0, 1]
frame 2: [0, 2]
frame 3: [0, 3]
frame 4: [0, 4]
```

This matches the released latest-keyframe-plus-current behavior.

## Mapping

The first mapping event was frame 0, not frame 1. Mapping ran for 60 iterations
on every processed frame.

Mapping component values are weighted values returned by `get_loss()`. Because
each iteration randomly samples from the selected mapping views, initial and
final losses need not represent the same view and are not treated as a
convergence metric.

| Frame | Initial total (D / RGB / semantic) | Final total (D / RGB / semantic) | Finite | Stage time |
|---:|---|---|---|---:|
| 0 | 0.039199 (0.023296 / 0.014700 / 0.001203) | 0.006248 (0.003037 / 0.002887 / 0.000324) | YES | 15.186 s |
| 1 | 0.008180 (0.004237 / 0.003543 / 0.000399) | 0.004989 (0.001606 / 0.003101 / 0.000282) | YES | 14.516 s |
| 2 | 0.011309 (0.004132 / 0.006693 / 0.000484) | 0.004554 (0.001530 / 0.002755 / 0.000268) | YES | 14.224 s |
| 3 | 0.010812 (0.003880 / 0.006472 / 0.000460) | 0.004722 (0.001400 / 0.003065 / 0.000257) | YES | 14.081 s |
| 4 | 0.010783 (0.003878 / 0.006443 / 0.000461) | 0.005020 (0.001423 / 0.003346 / 0.000250) | YES | 13.924 s |

All 300 mapping totals and components were finite.

## Optimizers

Tracking and mapping each created a fresh `torch.optim.Adam` with eight groups;
`semantic_ids` was excluded.

| Group | Tracking LR | Mapping LR |
|---|---:|---:|
| `means3D` | 0 | 0.0001 |
| `rgb_colors` | 0 | 0.0025 |
| `unnorm_rotations` | 0 | 0.001 |
| `logit_opacities` | 0 | 0.05 |
| `log_scales` | 0 | 0.001 |
| `semantic_colors` | 0 | 0.0025 |
| `cam_unnorm_rots` | 0.0004 | 0 |
| `cam_trans` | 0.002 | 0 |

At frame 1 tracking creation, the groups contained 12,253,970 elements.
Although Gaussian LRs were zero, the first step allocated Adam state for RGB,
rotation, opacity, scale, and semantic colors because those fields received
gradients. It also allocated camera Adam state. `means3D` was detached in
tracking and received no state. Total observed tracking Adam state was
78,447,836 bytes at frame 1, growing to 81,950,972 bytes by frame 4 as N grew.

At frame 0 mapping creation, the same eight groups contained 12,253,970
elements. Gaussian groups had nonzero LRs; camera groups had zero LR and no
Adam state because mapping detaches camera pose. Pruning at mapping iteration 0
replaces the just-backpropagated Parameters, so runtime state after mapping
step 1 was empty. State was lazily created on step 2 for all six trainable
Gaussian groups: 97,919,784 bytes at frame 0. Final frame-4 mapping state was
103,328,424 bytes. Optimizer creation, state migration during pruning, and
subsequent steps all completed.

## GPU memory

`RUNTIME MEASUREMENT`: peak stats were reset before each online frame. Values
below are bytes. A dash means that stage does not execute on frame 0.

| Frame | Before allocated/reserved | After load alloc. | After tracking alloc. | After addition alloc. | After mapping alloc./reserved | Per-frame peak |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 114,035,712 / 169,869,312 | 140,148,736 | — | — | 344,413,696 / 1,474,297,856 | 1,371,316,224 |
| 1 | 295,453,696 / 394,264,576 | 321,566,720 | 556,747,776 | 567,533,568 | 620,123,136 / 1,807,745,024 | 1,653,760,512 |
| 2 | 423,382,016 / 708,837,376 | 449,495,040 | 688,656,384 | 699,563,520 | 662,122,496 / 1,837,105,152 | **1,712,923,648** |
| 3 | 433,844,736 / 748,683,264 | 460,829,184 | 709,382,144 | 721,244,672 | 653,010,944 / 2,004,877,312 | 1,711,494,144 |
| 4 | 446,895,104 / 748,683,264 | 473,415,168 | 726,308,352 | 675,331,584 | 600,662,528 / 1,734,344,704 | 1,665,407,488 |

The maximum PyTorch allocated peak was **1,712,923,648 bytes (about 1,633.6
MiB / 1.60 GiB)**. The maximum sampled process memory from `nvidia-smi` at a
frame boundary was 978 MiB; this sampling did not attempt to capture the
short-lived allocator peak.

**4 GiB VRAM is sufficient for the released baseline through frame 4: YES.**
This statement is limited to the observed prefix and must not be extrapolated
to longer keyframe/map growth or the full sequence.

## Diagnostic timings

These are synchronized diagnostic stage timings, not benchmark FPS.

| Frame | Load | Tracking | Addition | Mapping | Total |
|---:|---:|---:|---:|---:|---:|
| 0 | 0.084 s | — | — | 15.186 s | 15.447 s |
| 1 | 0.093 s | 8.780 s | 0.029 s | 14.516 s | 23.532 s |
| 2 | 0.094 s | 8.396 s | 0.029 s | 14.224 s | 22.871 s |
| 3 | 0.107 s | 8.345 s | 0.030 s | 14.081 s | 22.698 s |
| 4 | 0.086 s | 8.276 s | 0.030 s | 13.924 s | 22.443 s |

## Integrity and stop boundary

```text
source changed             NO
config changed             NO
environment changed        NO
algorithm changed          NO
dataset changed            NO
temporary harness created  YES (/tmp only)
```

No tracked experiment output was created. The `/tmp` diagnostic output
directory contains only an empty `eval/` directory; final evaluation and save
were not entered.

The next authorized phase is **Phase 3C-2 — Bounded Online Reproduction:
10–20 Frames**. It was not started here.
