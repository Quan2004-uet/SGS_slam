# Mapping, Gaussian lifecycle, BA, and post-SLAM optimization

## Online mapping

Mapping runs on frame 0 and whenever `(time_idx+1) % map_every == 0`; shipped configs set `map_every=1`. It uses `mapping.num_iters` iterations and independently samples one view each iteration from the selected overlap keyframes, always-added last keyframe, and current frame. **[VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

`get_loss(mapping=True)` enables center gradients and detaches the selected camera pose. Config camera LRs are also zero. Map geometry, RGB, quaternion, opacity, isotropic scale, and semantic RGB are optimized; fixed semantic IDs are excluded. **[VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

The mapping Adam is recreated at each mapping event. Online pixel-based appending occurs before this creation, so the new tensors are naturally registered. Pruning and optional gradient densification later resize parameters and migrate Adam `exp_avg`/`exp_avg_sq`. **[VERIFIED FROM SOURCE]**

## Pixel-driven addition

`add_new_gaussians` renders `[depth,silhouette,z²]` with the tracked pose and selects pixels satisfying either:

- rendered silhouette `< mapping.sil_thres`, or
- rendered depth is behind GT depth and absolute error exceeds `50 × median(depth_error)`.

It intersects this union with valid GT depth, back-projects selected pixels using estimated current w2c, initializes attributes, concatenates them into every per-Gaussian field, resets radius/gradient/denominator arrays for all Gaussians, and appends creation time. **[VERIFIED FROM SOURCE]** Gaussian count increases here in normal online configs.

The append function directly replaces Parameters rather than migrating the then-live tracking optimizer. This is safe for subsequent mapping because a new optimizer is immediately built; however, the old tracking optimizer may transiently retain old tensors/moments until reassignment. **[INFERRED]**

## Pruning and gradient densification

Online pruning is enabled in shipped configs. At configured iterations it removes opacity below threshold and, after `remove_big_after`, scales greater than `0.1×scene_radius`. Tensor fields, auxiliary arrays, and existing Adam moments are filtered together. **[VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

Optional 3DGS densification accumulates screen-gradient norms. Small high-gradient Gaussians are cloned; large high-gradient ones are split into `n` samples transformed by their quaternion and shrunk by `0.8n`; originals are removed, then low-opacity/oversized points are pruned. It is disabled online in shipped configs. **[VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

## Bundle adjustment

`get_loss` contains a `do_ba` branch that enables gradients for both camera transform and Gaussian centers. No source call sets it, no BA optimizer/window/trigger exists, and mapping camera LR is zero. **[VERIFIED FROM SOURCE]** Result: **NO EXECUTED BUNDLE ADJUSTMENT IN CURRENT SOURCE AUDIT**.

## Post-SLAM optimization

`scripts/post_slam_opt.py` loads online `params.npz`, removes saved metadata, reconstructs tensors and a mapping Adam, then loads all selected mapping frames, GT w2c poses, raster cameras, RGB/depth, and semantics into GPU lists. Only at the final outer frame does it run 15,000 configured iterations, uniformly sampling any loaded frame, using GT camera settings and optimizing the fixed existing map. Pixel addition is commented out. **[VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

Post loss is `0.5 RGB(0.8 L1+0.2 DSSIM) + 1.0 depth mean-L1 + 0.1 semantic(0.8 L1+0.2 DSSIM)` in shipped configs. It uses exponential position-LR decay and enables gradient densification. Camera groups have LR zero. It evaluates at iteration 7000 and after completion, then saves a new NPZ/PLY pair. **[VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

Post-opt differs from online mapping: GT rather than tracked poses, all frames pre-resident, global random-frame sampling, long single optimization, position LR schedule, enabled clone/split densification, and no new RGB-D pixel append. **[VERIFIED FROM SOURCE]**

Static anomaly: line 87 assigns `semantic_id = color.permute(...)` during post-opt initialization; this local value is not used to rebuild saved IDs. It is recorded only as source evidence, not fixed. **[VERIFIED FROM SOURCE]**
