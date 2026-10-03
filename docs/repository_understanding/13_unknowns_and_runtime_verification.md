# Unknowns and runtime verification plan

No instrumentation was run during this audit.

| Item | Static evidence | Unknown | Minimal instrumentation |
|---|---|---|---|
| actual field dtypes/shapes | constructors and loaders imply values | backend-specific semantic ID dtype; extension output shapes | log key/shape/dtype/device/grad once after init |
| Gaussian growth | two growth mechanisms identified | count curve and scene dependence | record N before/after append/densify/prune per map event |
| peak VRAM | allocation owners traced | real peak and fragmentation | reset/read CUDA peak stats around tracking, append, mapping, eval |
| Adam state | lazy allocation behavior inferred | exact zero-LR groups receiving state | print state keys/numel after first tracking and mapping step |
| renderer buffers | package external | tile/sort/backward sizes and scaling | profiler memory events for one pass at controlled N/H/W |
| graph lifetime | `variables['means2D']` retains latest leaf | whether references delay graph release materially | memory snapshots before/after overwrite/backward/zero-grad |
| keyframe residency | tensors stored without `.cpu()` | actual K and bytes for each dataset | sum tensor storage by keyframe after capture |
| mapping frequencies | config/control flow known | realized counts with checkpoint/resolution variants | lightweight counters only |
| semantic evaluation cost | nearest palette computes pixel×palette distances | peak for high class/color counts | time/peak around recolor function |
| post-opt feasibility | all frames preloaded to GPU | peak for full scene | log list storage and peak before optimizer |
| metric correctness | formulas statically inspected | intended comparison protocol compatibility | small synthetic metric unit cases, no full dataset |
| rasterizer gradient targets | Python graph inputs known | exact CUDA backward behavior | hooks on each param group for one iteration |

## Top 10 things a researcher must understand before modifying SGS-SLAM

1. `params` mixes an `O(N)` Gaussian map and `O(T)` camera trajectory.
2. Semantic state is trainable RGB plus a separate fixed class ID, not logits/features.
3. Tracking and mapping share `get_loss` but differ through detach flags, reductions, masks, and LRs.
4. Tracking zero LR does not fully detach Gaussian appearance/shape fields from autograd.
5. New geometry is mainly pixel-driven append before mapping, not gradient clone/split in default online configs.
6. Prune/densify must resize Adam moments and every per-Gaussian auxiliary consistently.
7. Keyframe capture is fixed-interval; selection is geometric-only in active source.
8. Paper semantic keyframe filtering and uncertainty weighting are absent from execution.
9. Online and post-opt use duplicated helper/loss families and different camera/data regimes.
10. GPU memory scales independently with Gaussian count, keyframe count×resolution, and renderer/autograd temporaries.

## Top 10 questions not proven by static analysis

1. What is peak allocated/reserved VRAM in each stage for each dataset?
2. How quickly does Gaussian count grow, and which growth/prune trigger dominates?
3. Which zero-LR tracking groups actually acquire gradients and Adam moments with the installed extension?
4. What memory does the external rasterizer allocate as a function of visible splats and resolution?
5. Does the installed rasterizer/version exactly match the assumed three-output Python API?
6. How much memory remains live because of `variables['means2D']` and optimizer replacement timing?
7. What is the exact semantic-ID dtype and storage footprint in every dataset environment?
8. Are reported “ATE RMSE” and “depth RMSE” intended to use the implemented mean-error formulas?
9. Do dependency combinations in README versus `environment.yml` reproduce identical results?
10. Were paper semantic-keyframe/uncertainty results produced from unreleased code, another commit, or external patches?

## Stop-condition answers

1. Main flow: config/dataset/init → per-frame track → append/select/map → keyframe/checkpoint → final eval/save.
2. Main state: `params`, `variables`, GPU keyframe list, GT-pose list, transient data dictionaries, stage Adam.
3. Gaussian: center/RGB/quaternion/opacity/isotropic scale/semantic RGB plus fixed ID and timestamp.
4. Tracking numerically updates current camera pose; map LRs are zero.
5. Mapping updates Gaussian geometry/appearance/opacity/scale/semantic RGB with fixed pose.
6. Semantics enter from precomputed ID/color images and a separate semantic-color render/loss.
7. New Gaussians are appended in `scripts/slam.py:add_new_gaussians`; optional clone/split is in `slam_external.py:densify`.
8. Keyframes are captured at fixed intervals and selected by reprojection overlap; semantics do not actively filter them.
9. Tracking and mapping Adam instances are recreated per stage/event; post-opt has a long final mapping Adam.
10. Gaussian parameters, gradients, Adam moments, auxiliaries, transform/render buffers all scale with N.
11. Paper mapping is documented in `11_paper_code_mapping.md`, including missing released features.
12. Replacing semantics touches dataset/init/append/render/loss/optimizer-resize/save/eval/viz in both online and post-opt families.
