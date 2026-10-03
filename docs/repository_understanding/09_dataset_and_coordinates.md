# Dataset, configuration, coordinates, and evaluation

## Configuration hierarchy

There is no inherited base experiment config. A scene-specific Python file is dynamically imported; its `data.gradslam_data_cfg` YAML supplies dataset name and camera/depth metadata. Runtime code inserts a few missing defaults and derives dataset lengths/resolution flags. **[VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

Important keys and readers:

| Area | Keys | Read site |
|---|---|---|
| schedule | `map_every`, `keyframe_every`, `mapping_window_size` | `rgbd_slam` frame loop |
| tracking | `num_iters`, `forward_prop`, `use_gt_poses`, masks/threshold, weights, LRs | pose init/tracking loop/`get_loss` |
| mapping | `num_iters`, append/silhouette, weights/LRs, prune/densify dictionaries | mapping block and helpers |
| data | paths, start/end/stride, dimensions, semantic flags | dataset construction |
| evaluation | `eval_every`, progress interval | final `eval` and reporting |
| output | work/run names, checkpoint flags, W&B | startup/frame loop/save |

`use_uncertainty_for_loss`, `use_uncertainty_for_loss_mask`, and `use_chamfer` appear in ScanNet configs but have no read site in the main pipeline. **[VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

## Dataset sample path

```text
image/depth/semantic files + c2w pose
  → subclass get_filepaths/load_poses
  → GradSLAMDataset.__getitem__
  → resize RGB bilinear; depth/semantics nearest-neighbor
  → depth / png_depth_scale (meters)
  → scale intrinsics to requested resolution
  → pose relative to first pose
  → move tuple to configured GPU
  → slam permutes HWC→CHW and divides RGB/semantic RGB by 255
```

**[VERIFIED FROM SOURCE]** RGB is read as float in nominal `[0,255]`; depth becomes float meters; semantic ID remains integer; semantic color becomes float and is later normalized.

Replica uses `frames/frame*.jpg`, `depths/depth*.png`, semantic ID/color folders, and `traj.txt` c2w matrices. Its YAML specifies 1200×680, focal 600, and depth scale 6553.5. ScanNet uses color/depth/pose plus semantic folders, YAML native 1296×968 metadata and scale 1000, normally resized to 640×480. **[VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

ScanNet++ reads Nerfstudio JSON, undistorted DSLR images/depth/semantic directories, and conjugates each c2w by `diag(1,-1,-1,1)` to GradSLAM convention. For test/NVS split it prepends the first train frame as reference. **[VERIFIED FROM SOURCE]**

The abstraction supports several other datasets and optional saved embeddings, but the checked-in semantic experiments target Replica, ScanNet, and ScanNet++. **[VERIFIED FROM SOURCE; VERIFIED FROM README/DOCUMENTATION]**

## Coordinate model

Dataset subclasses load poses as camera-to-world. `GradSLAMDataset._preprocess_poses` returns `inverse(c2w_0) @ c2w_t`, so frame 0 is identity and map/world coordinates are the first-camera coordinate system. SLAM inverts each returned pose for relative w2c ground truth. **[VERIFIED FROM SOURCE]**

The complete point path is:

`(u,v,z) → p_cam=[(u-cx)z/fx,(v-cy)z/fy,z] → p_world=inverse(w2c_est)·[p_cam,1] → Gaussian mean → p_cam'=w2c_est·[mean,1] → K p_cam'/z → (u',v')`.

**[VERIFIED FROM SOURCE]** Positive camera z is depth. Intrinsics are a scaled 3×3 pinhole matrix. Camera quaternion convention is real-first `[w,x,y,z]` and normalized before matrix conversion.

`setup_camera` embeds the first-frame w2c into raster settings. Because Gaussian centers are explicitly transformed to each current camera frame before rendering, the fixed rasterizer view represents the canonical frame. **[VERIFIED FROM SOURCE]**

## Evaluation

Online completion calls `utils.eval_helpers.eval` at `eval_every`: it renders with estimated poses and reports Horn-aligned mean translation error (printed as ATE RMSE though implementation returns mean Euclidean translation error), RGB PSNR, CPU MS-SSIM, LPIPS-Alex, depth L1, a variable named RMSE whose formula is per-pixel absolute error followed by a mean, and color-based semantic mIoU. **[VERIFIED FROM SOURCE]** Metric naming discrepancies should be runtime/research reporting caveats.

`eval_novel_view.py` loads `params.npz`. Train split delegates to `eval`; test split delegates to `eval_nvs`, which uses GT test camera poses, rejects metric aggregation for views with more than 0.1% uncovered valid-depth pixels, and reports rendering/depth metrics. Semantic mIoU is not filtered by that valid-view mask. **[VERIFIED FROM SOURCE]**

Preprocessing `preprocess/scannet/run.py` extracts `.sens` RGB/depth/poses/intrinsics and converts filtered raw label IDs to NYU40-style semantic colors with extra named objects. **[VERIFIED FROM SOURCE]**
