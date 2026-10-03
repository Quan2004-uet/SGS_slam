# Known Blockers and Phase 3 Checks

“Do not fix yet” means classify and gather evidence at the relevant gate before
changing environment, source, config, dataset, or method.

## Environment

| Blocker | Evidence | Impact | Phase 3 verification | Do not fix yet |
|---|---|---|---|---|
| README and Conda YAML disagree on Python/PyTorch/CUDA | Explicit version records conflict | Wrong stack may fail imports/build or change numerics | Try preferred README candidate through bounded import/renderer gates; retain full lock record | Do not upgrade/downgrade ad hoc |
| Pinned external CUDA rasterizer | Git commit in requirements; imported on core paths | Build/import failure blocks all rendering | Verify VCS checkout, compile log, import, minimal forward/backward | Do not replace with another rasterizer/fork |
| Environment YAML renderer URL uses `/tree/<commit>` | Static file inspection | Conda pip phase may reject URL | Validate without modifying baseline; if necessary use the same commit via requirements URL and record compatibility recovery | Do not change renderer revision |
| Unpinned transitive dependencies | Requirements inspection | Modern resolver results may be incompatible | Capture resolved versions and imports | Do not choose “latest” as an algorithm fix |
| W&B enabled with placeholder entity | Replica online config | Startup/auth failure or untraceable logging | Verify credentials/entity or use a documented derived config with W&B disabled | Do not silently edit checked-in config |

## Dataset

| Blocker | Evidence | Impact | Phase 3 verification | Do not fix yet |
|---|---|---|---|---|
| No local `data/` directory | Worktree inspection | No loader or run can start | Acquire documented semantic Replica dataset, then run integrity checklist | Do not substitute a standard non-semantic Replica layout |
| Semantic files are mandatory for config | Loader/config source | Missing folders/count mismatch raises or invalidates semantics | Compare all four modality counts and indices | Do not disable semantics to get a run |
| Exact frame count/content unavailable | Dataset absent | Cannot precompute runtime/storage or validate table protocol | Record after dataset acquisition | Do not invent counts |
| Trajectory provenance is separate in README | README | Missing/misaligned `traj.txt` blocks valid poses | Validate line count, matrices, frame pairing | Do not synthesize trajectories |

## Source/config behavior

| Blocker | Evidence | Impact | Phase 3 verification | Do not fix yet |
|---|---|---|---|---|
| No CLI frame-limit override | Script parser | Bounded tests need a derived config | Create a recorded test-only config diff with only frame limit/W&B changes | Do not alter canonical config in place |
| Tracking may double iterations on failure criterion | `scripts/slam.py` | Bounded runtime may exceed 40 iterations/frame | Capture log and iteration counts | Do not disable retry before classifying failure |
| Dormant config/helper branches | Static audit | Names can falsely imply uncertainty/BA/densification is active | Trace each read-site before claims | Do not “activate” dormant behavior |
| Paper/source keyframe, uncertainty, BA discrepancies | Paper-code audit | Published/released results may diverge | Preserve source behavior and annotate result | Do not implement paper components in Phase 3 |

## GPU and runtime

| Blocker | Evidence | Impact | Phase 3 verification | Do not fix yet |
|---|---|---|---|---|
| Full 680x1200 frames and renderer buffers | Config/static memory audit | Peak VRAM can block first full scene | Measure allocated/reserved/peak at bounded gates | Do not lower resolution for claimed full baseline |
| Gaussian count grows by pixel append | Online source | Persistent parameters, gradients, Adam state, renderer buffers grow | Record count and peak memory by frame gate | Do not prune/add thresholds beyond baseline |
| Keyframes retain GPU tensors | Source/static audit | Memory grows with keyframe count/window | Record residency and memory at 5/20/short run | Do not move them to CPU as a reproduction fix |
| Post-opt preloads selected frames and densifies | Post-opt source | Large persistent frame storage and map growth | Measure only after online acceptance | Do not begin with 15k post-opt |
| Paper's “<12 GB typical” is not a guarantee | Paper | Underprovisioned GPU may OOM | Record GPU and bounded peak before full run | Do not claim a source bug from OOM alone |

## Evaluation

| Blocker | Evidence | Impact | Phase 3 verification | Do not fix yet |
|---|---|---|---|---|
| ATE code/label mismatch | Evaluator audit | Paper ATE RMSE comparison may be invalid | Capture code output and independently characterize formula in Phase 4 | Do not change evaluator during baseline run |
| Depth RMSE equals L1 algebraically | Evaluator audit | `rmse.txt` label is misleading | Confirm arrays during bounded evaluation | Do not silently replace formula |
| MS-SSIM vs paper SSIM label | Source/paper | Potential metric delta | Record exact package/version/function | Do not swap evaluator |
| Post-opt evaluator does not save metric arrays | `utils/gs_helpers.py` | Weak artifact reproducibility | Preserve stdout/W&B and plots; later add external measurement harness if authorized | Do not mix with online metric files |
| Paper table stage is ambiguous | Paper/source audit | Online/post-opt target selection unresolved | Preserve and compare both labeled stages after online baseline | Do not overwrite online outputs |
