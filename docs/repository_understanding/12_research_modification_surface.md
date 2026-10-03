# Research modification surface

This file identifies likely touch points only; it proposes no implementation.

| Research direction | Primary touch points | Coupled surfaces |
|---|---|---|
| A Replace semantic representation | `initialize_params/new_params`, `get_pointcloud`, semantic render helpers, `get_loss` | save/PLY, eval recoloring/mIoU, viz loaders, prune/densify field handling, configs |
| B DINOv2 features | dataset embedding path or new preprocessor; semantic/feature renderer and loss | high-D renderer support, keyframe storage, checkpoints, memory model, evaluation |
| C CLIP/open vocabulary | same as B plus text/class association layer | object editing/filtering, metrics/palette assumptions |
| D Keyframe strategy | `keyframe_selection.py`, capture condition and selected-list construction in `slam.py` | new config keys, keyframe state/residency, post-opt if reused |
| E Tracking loss | `scripts/slam.py:get_loss` tracking branches | masks, stage detach boundaries, config weights, reporting |
| F Mapping loss | same function mapping branches; post-opt `get_loss_gs` | online/post-opt parity, eval interpretation |
| G Semantic uncertainty | representation fields, semantic render/loss, keyframe selection | append/init, optimizer migration, save/viz/eval |
| H Reduce VRAM | keyframe storage policy, dataset device behavior, optimizer group inclusion, render-pass lifetime | append transient copies, post-opt preloading, external renderer profiling |
| I Object-level representation | semantic IDs/colors and initialization, grouping/data association | renderer/loss, object pose state, prune/densify, editing UI/checkpoint schema |
| J Scene graph/topology | new state beside Gaussian map; semantic/object association | keyframes, serialization, visualization/evaluation; core rasterizer may remain unchanged |

## Minimal dependency chains

Changing semantic dimensionality is cross-cutting because the rasterizer currently accepts three-channel `colors_precomp`; verify extension support before designing a high-dimensional feature field. **[VERIFIED FROM SOURCE; UNKNOWN / NEEDS RUNTIME VERIFICATION]**

Changing only online `slam_helpers.py` will not change post-opt, which imports `gs_helpers.py`; changing only `scripts/slam.py:get_loss` will not change `post_slam_opt.py:get_loss_gs`. **[VERIFIED FROM SOURCE]**

Any new per-Gaussian field must be initialized in both first-frame and append paths, included/excluded from optimizer deliberately, resized by prune/densify helpers, serialized, and handled by visualization/evaluation loaders. **[INFERRED FROM VERIFIED STATE LIFECYCLE]**

For VRAM work, the highest-priority measurement points are external rasterizer peak allocation, tracking zero-LR Adam states, GPU keyframe image residency, append-time duplicate tensors, and post-opt all-frame preload. **[INFERRED]**

For paper-faithful keyframes, the relevant surface is unusually small but behaviorally important: activate/define semantic comparison in `keyframe_selection_overlap`, introduce verified thresholds, and pass a mapping weight if implementing uncertainty. The current code lacks those active paths. **[VERIFIED FROM SOURCE]**
