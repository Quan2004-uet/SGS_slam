# Tracking subsystem

## Verified flow

```text
previous relative w2c pose(s)
  → constant-velocity quaternion/translation extrapolation (or previous-pose copy)
  → freeze center transform from map; enable camera transform gradient
  → RGB + [depth,silhouette,z²] + semantic render
  → valid-depth ∩ finite ∩ silhouette mask
  → weighted summed L1 losses
  → Adam step
  → retain lowest-loss pose candidate
  → commit candidate into camera arrays
```

**[VERIFIED FROM SOURCE]** Camera pose is relative world-to-camera: quaternion `[w,x,y,z]` plus translation, stored per frame in `params`. Frame 0 is identity because dataset poses are made relative to frame 0.

`initialize_camera_pose` uses component-wise constant-velocity extrapolation for both translation and the unnormalized quaternion, then normalizes quaternion. For frame 1 or with `forward_prop=False`, it copies the preceding pose. This is not SE(3) exponential-map extrapolation. **[VERIFIED FROM SOURCE]**

## Optimization

`initialize_optimizer(...tracking=True)` creates one Adam param group for every optimizable `params` entry. Config LRs set only current camera arrays effectively nonzero (`cam_unnorm_rots`, `cam_trans`); all Gaussian LRs are zero. `transform_to_frame` detaches `means3D` but other rendered Gaussian attributes are not detached, so they can receive gradients and Adam moment state even though LR=0. **[VERIFIED FROM SOURCE]** This is a material distinction between “not numerically updated” and “excluded from the graph.”

The entire camera arrays `1×4×T` and `1×3×T` are optimizer parameters, but slicing by `time_idx` means only the current columns receive nonzero gradients. **[VERIFIED FROM SOURCE]**

Tracking loss for the usual semantic/silhouette path is:

`L_track = λD Σ_M |Dgt-D| + λC Σ_tile(M) |Cgt-C| + λS Σ_tile(M) |Sgt-S|`,

where `M = valid_gt_depth ∩ finite_render ∩ (silhouette > threshold)` and default threshold is 0.99. If outlier masking is enabled, it also requires depth error below ten times the median. Loss uses sums, so magnitude scales with valid pixel count/resolution. **[VERIFIED FROM SOURCE]**

Replica uses 40 iterations and LRs rotation `4e-4`, translation `2e-3`; ScanNet config uses 100 and `5e-4` each; ScanNet++ uses 200, rotation `1e-3`, translation `4e-3`. Semantic weights are 0.05 except ScanNet sets tracking semantic weight to zero. **[VERIFIED FROM CONFIG]** Paper appendix iteration counts (ScanNet 120/40, ScanNet++ 220/50) do not match checked-in configs (100/30 and 200/60). **[VERIFIED FROM README/DOCUMENTATION; VERIFIED FROM CONFIG]**

If `use_depth_loss_thres=True`, failure to beat the configured raw depth-loss threshold at the original iteration limit doubles the total limit once. The lowest total-loss pose, not necessarily the last iterate, is committed. With `use_gt_poses=True`, the relative GT w2c is derived from `gt_w2c @ inverse(first_frame_w2c)` and written directly. **[VERIFIED FROM SOURCE]**

There is no convergence tolerance, pose prior, robust kernel beyond optional median mask, loop closure, relocalization, or covariance estimate in the executed tracking path. **[VERIFIED FROM SOURCE]**
