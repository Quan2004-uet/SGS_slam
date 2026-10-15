# Budget-Aware Mapping Source Audit

Evidence label: `VERIFIED_FROM_SOURCE`. Current source is `scripts/slam.py` at `1fbde97`; line references below were verified against this commit. Design consequences are labeled separately as risks or opportunities, not runtime observations.

| Point | Source and behavior | Residency/frequency | Reducible? / risk |
|---|---|---|---|
| Tracking completion | `rgbd_slam`, `scripts/slam.py:853-954`; commits the lowest-loss pose at 937–939 | GPU; every frame except frame 0 optimization | Do not reduce; pose errors affect append, selection and mapping |
| Mapping trigger | `scripts/slam.py:974-975`; frame 0 or `(time_idx+1)%map_every==0` | `map_every=1` in `configs/replica/slam.py:12,26` | Frequency is reducible but changes observation cadence; not selected initially |
| Gaussian append | `add_new_gaussians`, `scripts/slam.py:440-497`, called 989–994 | GPU; before mapping on frames >0 | Keep unchanged; appended-count is a free novelty signal after work already occurs |
| Keyframe selection | `keyframe_selection_overlap`, `utils/keyframe_selection.py:40-110`, called `slam.py:1000-1028` | GPU geometry plus NumPy permutation; once per map event | Keep semantics/RNG unchanged |
| Current-frame inclusion | `scripts/slam.py:1017-1023` appends latest keyframe then `-1` current frame | Python list; every map event | Required for current observation; keep |
| CPU archive | `archive_keyframe_payload_on_cpu`, `scripts/slam.py:535-550`; capture at 1157–1175 | CPU authoritative payload; every fifth frame plus frame 0/penultimate | Keep unchanged |
| H2D staging/release | `stage_keyframe_payload`, `scripts/slam.py:553-573`; use/delete at 1053–1058 and 1125–1126 | Synchronous pageable CPU→GPU per selected archived iteration | Iteration reduction proportionally reduces events; do not change transfer semantics |
| Mapping optimizer | `initialize_optimizer`, `scripts/slam.py:182-188`; initialized at 1030–1031 | GPU Adam recreated per mapping event | Required; fewer steps reduce compute, but state initialization remains |
| Iteration loop | `scripts/slam.py:1033-1137`; `range(num_iters_mapping)` | Default 60 at `configs/replica/slam.py:16,86` | Primary control point: choose effective budget before loop |
| Observation choice | `scripts/slam.py:1040-1044` | One NumPy random draw per iteration | Variable budget changes number of later draws, but not selection policy inside executed iterations |
| RGB/depth/semantic render | `get_loss`, `scripts/slam.py:250-408`; render calls 279–309 | Three GPU rasterizations per mapping iteration when semantics enabled | Dominant repeated work; reduced only by fewer iterations |
| Loss | `get_loss:311-400`; mapping depth mean L1, RGB/semantic 0.8 L1 + 0.2 DSSIM | GPU per iteration | Required for each executed step; raw losses vary by randomly selected view |
| Backward | `scripts/slam.py:1080-1088` | GPU per iteration | Required for optimizer update; reduced with iteration count |
| Optimizer step | `scripts/slam.py:1106-1113` | GPU per iteration | Required for executed iterations |
| Pruning | `scripts/slam.py:1090-1094`; `utils/slam_external.py:179-200` | GPU at iterations 0 and 20 under Replica config (`stop_after=20`, `prune_every=20`) | Any budget must include iteration 20; minimum effective budget is at least 21 |
| Gradient densification | `scripts/slam.py:1098-1102`; `utils/slam_external.py:203-255` | Disabled in Replica config `slam.py:118` | Preserve disabled state |
| Pose dependency | `transform_to_frame`, `utils/slam_helpers.py:235-270`; mapping detaches camera pose at `get_loss:267-269` | Gaussian gradients on GPU, fixed estimated pose | Mapping cannot repair tracking pose in active path |
| Checkpoint/evaluation | `scripts/slam.py:1177-1181`, final eval/save 1227–1254 | Periodic/final GPU and disk work | Keep separate from online timing and matched across variants |

## Coupling

The iteration budget controls how often a randomly selected current/keyframe view performs three render passes, loss, backward and Adam update. Gaussian append happens before the budgeted loop, while pruning happens inside it at fixed iteration indices. Keyframe capture happens after mapping. Reducing iterations can save render/backward/H2D work but can under-optimize newly appended Gaussians, affect opacity pruning, and propagate map-quality changes into later tracking.

Residual early stopping is not the preferred first method: successive losses usually refer to different randomly selected views and converting CUDA loss tensors into Python decisions introduces synchronization. Novelty from `post_num_pts - pre_num_pts` is available as host-visible shape metadata without an extra render.
