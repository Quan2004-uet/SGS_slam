# Paper/code mapping, dependencies, and critical files

## Paper ↔ implementation

| Paper concept | Source/function/config | Audit result |
|---|---|---|
| isotropic Gaussian | `initialize_params`, `transformed_params2rendervar` | implemented as one log scale tiled to 3 axes |
| RGB/depth/silhouette rendering | `get_loss`, depth pseudo-colors `[z,1,z²]` | implemented via external rasterizer |
| semantic color channel | `semantic_colors`, `transformed_semantics2rendervar` | implemented as trainable RGB |
| semantic tracking supervision | `get_loss(tracking=True)`; `tracking.loss_weights.seg` | implemented, ScanNet weight is zero |
| fixed-map pose tracking | `transform_to_frame`; tracking LRs | numerical map update frozen, but map attributes remain partly in graph |
| constant velocity | `initialize_camera_pose` | implemented component-wise |
| low-silhouette/new-foreground addition | `add_new_gaussians` | implemented |
| joint multi-channel mapping | `get_loss(mapping=True)` | implemented |
| geometric keyframe overlap | `keyframe_selection_overlap` | implemented, threshold is `>0`, not paper 0.05 |
| semantic mIoU keyframe filter | commented block in `keyframe_selection.py` | **NOT ACTIVE / NOT LOCATED IN EXECUTION PATH** |
| uncertainty keyframe loss weight `exp(-τt)` | no read/call/config | **NOT LOCATED IN CURRENT SOURCE AUDIT** |
| BA/joint pose-map optimization | dormant `do_ba` branch | **NOT ACTIVE** |
| object edit by semantic ID | `viz_scripts/tk_recon.py`, eval filter helper | supporting visualization/filter capability |

**[VERIFIED FROM SOURCE; VERIFIED FROM README/DOCUMENTATION]** The paper describes semantic keyframe filtering and uncertainty weighting as core contributions, but this released revision does not execute them.

## External dependencies

| Group | Dependencies/use |
|---|---|
| core/GPU | PyTorch, torchvision, CUDA; differentiable Gaussian rasterizer Git package |
| image/data | OpenCV, imageio, Pillow, PyYAML, natsort, Kornia |
| metrics | torchmetrics LPIPS, `pytorch-msssim`, NumPy/Matplotlib |
| visualization/export | Open3D 0.16, plyfile, Tkinter system module |
| logging | W&B, pandas |
| capture | CycloneDDS |
| optional/legacy | faiss-gpu in `environment.yml`; neighbor helpers are not in main flow |

`environment.yml` specifies Python 3.10, PyTorch 1.12.1 and CUDA toolkit 11.6, while README installation specifies Python 3.9, PyTorch 2.0.1 and CUDA 11.8. Requirements do not pin PyTorch. This environment discrepancy requires reproduction testing. **[VERIFIED FROM CONFIG; VERIFIED FROM README/DOCUMENTATION]**

The only direct compiled-extension import in core/render/evaluation/visualization modules is `diff_gaussian_rasterization` (`GaussianRasterizer`, and settings in `recon_helpers`). No `simple-knn` dependency is present. **[VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

## Critical file ranking

### Tier A — must understand

1. `scripts/slam.py`: owns orchestration, both optimizations, state construction, append, keyframes, save/eval calls.
2. `utils/slam_helpers.py`: defines the actual renderer inputs and gradient detach boundaries.
3. `utils/slam_external.py`: owns Gaussian/Adam resize semantics, pruning, optional densification.
4. `utils/keyframe_selection.py`: determines mapping views and exposes the paper/code semantic-selection gap.
5. `datasets/gradslam_datasets/basedataset.py`: fixes tensor formats, device residency, depth units, intrinsics, and pose relativity.
6. `utils/eval_helpers.py`: defines what reported metrics actually compute.

### Tier B — important

`configs/*/slam.py`, dataset-specific loaders, `utils/recon_helpers.py`, `scripts/post_slam_opt.py`, `utils/gs_helpers.py`, `utils/gs_external.py`, `scripts/eval_novel_view.py`, `utils/common_utils.py`.

### Tier C — supporting

Visualization scripts, ScanNet preprocessing, capture converter, `neighbor_search.py`, `graphics_utils.py`, and legacy `scripts/gaussian_splatting.py`.

The duplicated `slam_*` and `gs_*` helper families are stage-specific in current callers; a researcher must avoid modifying only one family when online and post-opt behavior should both change. **[VERIFIED FROM SOURCE]**
