# Repository architecture

## Selected topology

```text
scripts/
  slam.py                 main online semantic RGB-D SLAM
  post_slam_opt.py        offline refinement of saved map
  eval_novel_view.py      train/NVS evaluation of params.npz
  gaussian_splatting.py   separate older Gaussian-only trainer
  nerfcapture2dataset.py  DDS capture/conversion utility
configs/
  replica|scannet|scannetpp/slam.py
  replica|scannetpp/post_slam_opt.py
  data/*.yaml             camera/depth metadata
datasets/gradslam_datasets/
  basedataset.py          shared loading, resize, depth scaling, relative poses
  replica.py, scannet.py, scannetpp.py
  ...                     additional inherited loaders
utils/
  slam_helpers.py         render dictionaries and pose transform
  slam_external.py        SSIM, Adam-aware prune/densify
  keyframe_selection.py   geometric-overlap selection
  recon_helpers.py        rasterizer camera construction
  eval_helpers.py         ATE/render/depth/semantic metrics
  common_utils.py         checkpoint/NPZ/PLY saving
  convert_ply.py          RGB and semantic PLY export
  gs_helpers.py, gs_external.py  parallel helpers used by post-opt/legacy script
preprocess/scannet/       .sens extraction and semantic color creation
viz_scripts/              Open3D/Tk online/final visualization and object masking
2402.03246v6.pdf          local paper
```

No CUDA/C++ source or git submodule is vendored. The compiled renderer is installed from the external `diff-gaussian-rasterization-w-depth` Git dependency. **[VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

Generated outputs are under `experiments/<group>/<run>/`: copied `config.py`, `params<N>.npz`, `keyframe_time_indices<N>.npy`, final `params.npz`, `params.ply`, `seg_params.ply`, evaluation images/metric text, and optionally `timestamp_keyframes.csv`. **[VERIFIED FROM SOURCE]**

## Responsibility map

| Area | Core files | Role |
|---|---|---|
| Entry/config | `scripts/slam.py`, `configs/*/slam.py` | executable orchestration and experiment values |
| Dataset | `basedataset.py`, dataset subclasses | disk paths → GPU tensors; relative c2w poses |
| Tracking/mapping | `scripts/slam.py` | both stages and persistent state live in one file |
| Rendering | `slam_helpers.py`, `recon_helpers.py`, external rasterizer | camera-frame conversion; RGB/depth/silhouette/semantic passes |
| Gaussian lifecycle | `slam.py:add_new_gaussians`, `slam_external.py` | pixel-based append; prune; optional gradient densification |
| Keyframes | `keyframe_selection.py`, `slam.py` | fixed-interval capture and overlap-based mapping-window choice |
| Evaluation | `eval_helpers.py`, `eval_novel_view.py` | ATE, PSNR, MS-SSIM, LPIPS, depth, mIoU, NVS |
| Post optimization | `post_slam_opt.py`, `gs_helpers.py`, `gs_external.py` | offline all-map refinement with GT cameras |
| Supporting | `viz_scripts`, `preprocess`, `nerfcapture2dataset.py` | UI, conversion, capture; not online algorithm core |

## Architecture map after source tracing

```text
config.py loaded as Python module
  ↓
GradSLAMDataset (RGB, depth, semantic ID/color, intrinsics, relative c2w)
  ↓
first valid-depth pixels → world points → initial Gaussian map + camera arrays
  ↓
for each frame
  ├─ load per-frame tensors and initialize pose (constant velocity/copy)
  ├─ TRACK: render 3 passes → masked RGB/depth/semantic loss → Adam pose update
  ├─ if map interval:
  │    ├─ append Gaussians at low silhouette/new foreground pixels
  │    ├─ select overlap keyframes + always last keyframe + current frame
  │    └─ MAP: sample one view/iteration → render/loss → prune/densify → Adam
  ├─ capture keyframe at fixed interval
  ├─ optional checkpoint
  └─ empty CUDA cache
  ↓
final evaluation → augment state metadata → NPZ + RGB/semantic PLY
```

**[VERIFIED FROM SOURCE]** This is a single-process, sequential frame loop. There is no frontend/backend thread split, loop closure, pose graph, or active BA call in the audited source.
