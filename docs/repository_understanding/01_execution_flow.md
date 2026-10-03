# Execution flow and call graph

## Startup to termination

1. `scripts/slam.py:1118-1140` parses one positional experiment path, dynamically loads its Python `config`, seeds Python/NumPy/PyTorch, creates the result directory, copies the config unless resuming, then calls `rgbd_slam(config)`. **[VERIFIED FROM SOURCE]**
2. `rgbd_slam:513-633` fills two tracking defaults, initializes W&B/device, resolves YAML camera config, constructs the dataset(s), and calls `initialize_first_timestep`. Separate tracking/densification datasets exist only if corresponding resolution keys differ. **[VERIFIED FROM SOURCE]**
3. `initialize_first_timestep:190-246` reads frame 0, scales RGB to `[0,1]`, keeps depth in meters, inverts c2w to w2c, builds fixed rasterizer camera settings, back-projects every valid depth pixel, initializes one Gaussian per valid pixel, camera-pose arrays for all frames, and scene radius. **[VERIFIED FROM SOURCE]**
4. `rgbd_slam:674-724` optionally restores map/camera arrays and reconstructs keyframe tensors by rereading prior frames. **[VERIFIED FROM SOURCE]**
5. For every frame (`726-1051`), it loads data, forms `curr_data`, initializes pose, tracks, conditionally appends/maps, conditionally stores a keyframe/checkpoint, and calls `torch.cuda.empty_cache()`. **[VERIFIED FROM SOURCE]**
6. It writes optional keyframe selections, reports average timings, runs final `eval`, adds metadata to `params`, casts saved semantic IDs to `uint8`, and saves NPZ plus two PLY files. **[VERIFIED FROM SOURCE]**

## Core call graph

```text
slam.py::__main__
└─ rgbd_slam(config)
   ├─ load_dataset_config → get_dataset → GradSLAMDataset.__getitem__
   ├─ initialize_first_timestep
   │  ├─ setup_camera
   │  ├─ get_pointcloud
   │  └─ initialize_params
   └─ frame loop
      ├─ initialize_camera_pose
      ├─ initialize_optimizer(tracking=True)
      ├─ get_loss(tracking=True)
      │  ├─ transform_to_frame
      │  ├─ transformed_params2rendervar → Renderer
      │  ├─ transformed_params2depthplussilhouette → Renderer
      │  └─ transformed_semantics2rendervar → Renderer
      ├─ add_new_gaussians
      │  ├─ depth/silhouette Renderer
      │  ├─ get_pointcloud
      │  └─ initialize_new_params + tensor concatenation
      ├─ keyframe_selection_overlap
      ├─ initialize_optimizer(tracking=False)
      ├─ repeated get_loss(mapping=True)
      │  ├─ optional prune_gaussians
      │  ├─ optional densify
      │  └─ optimizer.step
      ├─ keyframe append / save_params_ckpt
      └─ eval → render and metrics
```

## Important function contracts

| Function | Inputs → outputs | State/side effects |
|---|---|---|
| `get_pointcloud` | `C×H×W`, `1×H×W`, `K`, w2c, mask → `N×(6 or 10)`, optional `N` scale² | allocates image grid and world points |
| `initialize_params` | point cloud, `T` → `params`, `variables`, exclusion set | creates all persistent trainable tensors |
| `get_loss` | state + one view + stage flags → scalar loss, mutated variables, components | 2 or 3 rasterizations; records means2D/radii/seen |
| `add_new_gaussians` | map + current view → enlarged map/state | replaces map tensors; resets three accumulators; extends timestep |
| `keyframe_selection_overlap` | current depth/pose/K + old keyframes → list indices | random samples; no map mutation |
| `prune_gaussians` / `densify` | map/state/Adam → resized map/state/Adam | migrates Adam moments when enabled |
| `eval` | dataset + final state → files/printed metrics | reads frames and renders under `no_grad` |

## Why the ordering matters

Tracking happens before Gaussian addition, so a new frame pose is estimated against the pre-existing map. Addition then uses that estimated pose to lift missing pixels into world space. Mapping starts only after append and rebuilds an optimizer for the resized map. Keyframe capture happens after mapping, therefore the current frame cannot be an already-stored keyframe during its own selection; it is injected explicitly as index `-1`. **[VERIFIED FROM SOURCE]**

`get_loss(..., do_ba=True)` could expose gradients to both camera centers and Gaussian centers, but no call passes `do_ba=True`. Therefore there is no executed bundle adjustment in this revision. **[VERIFIED FROM SOURCE]**
