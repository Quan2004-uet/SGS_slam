# SGS-SLAM Runtime Architecture Audit — Phase 5 Gate P5-G1

Status: `VERIFIED` source audit, documentation only
Audit date: 2026-10-15
Branch / HEAD: `phase4-vb-001-cpu-keyframe-offload` / `37522db553ff18b96592073f9de699db7fa48600`
Scope: active online semantic path in `scripts/slam.py`; no CUDA workload was run.

## Evidence boundary

The active source path has precedence over the older static audit. The only online algorithm delta from upstream commit `e4183986204242a8bb422624618af07780a49d26` is the 48-line PHASE4-VB-001 residency change committed in `8061093`: CPU archive helpers, their two insertion call sites, per-selection synchronous staging, and explicit staged-payload release. Visualization scripts and documentation added later are not part of online SLAM.

## Runtime flow

```text
ReplicaDataset.__getitem__ (disk decode, preprocessing, then .to(primary_device))
  -> initialize/current-frame tensors on GPU
  -> tracking: render/loss/backward/Adam camera update
  -> pixel-driven Gaussian addition on mapping frames
  -> overlap-based mapping-window selection using GPU depth/poses
  -> one selected archived payload synchronously CPU -> GPU, or current frame
  -> mapping: three renders/loss/backward/prune/Adam
  -> release staged payload references
  -> fixed-cadence keyframe insertion: copy payload GPU -> pageable CPU
  -> optional evaluation, checkpoint, serialization
```

This path is sequential in one Python process. There is no explicit transfer stream, prefetch worker, persistent GPU keyframe cache, archive eviction, or submap scheduler.

## Component map

| Component | Source location / call site | Runtime behavior and I/O | Device, owner, lifetime | Bottleneck and profiling opportunity |
|---|---|---|---|---|
| Dataset load and preprocessing | `datasets/gradslam_datasets/basedataset.py:357-409`; called by `scripts/slam.py:759-782` | Reads RGB/depth and, when enabled, semantic ID/color; resizes, scales depth/intrinsics, returns relative pose | NumPy during decode; all returned tensors are moved to configured device at lines 397-406. Current-frame GPU tensors live through the frame and may become an archived copy | CPU decode/resize and H2D are currently conflated in `dataset[index]`; time decode/preprocess and device transfer separately in P5-G2 |
| First-frame initialization | `scripts/slam.py:190-246`, called at 652-664 | Loads frame 0, builds point cloud, Gaussian params, camera and auxiliary arrays | GPU-authoritative params/variables; scene lifetime | One-time cost and initial Gaussian/memory baseline; record separately from steady-state FPS |
| Tracking / pose estimation | `scripts/slam.py:798-887`; `get_loss` at 249-389; transform at `utils/slam_helpers.py:235-268` | Constant-velocity pose initialization; 40 default iterations; RGB/depth/semantic render/loss; backward; Adam step; best pose retained | Current observation, Gaussian map and pose arrays on GPU. A new Adam is constructed per frame; tracking graph/gradients are iteration-lived | Renderer/backward/optimizer dominate candidates. Existing `time.time()` timers do not establish GPU elapsed time. Add CPU dispatch, CUDA-event elapsed, iteration count and failure/extra-iteration telemetry |
| Keyframe insertion decision | `scripts/slam.py:1059-1077` (checkpoint recovery: 725-754) | Inserts frame 0, every `keyframe_every=5`, and terminal `num_frames-2`, subject to valid GT pose | Decision metadata is Python/host; constructed `est_w2c` is GPU-resident | Decision itself is cheap but insertion copy may stall. Record decision reason, payload bytes and archive-copy wall time |
| CPU keyframe archive | `KEYFRAME_PAYLOAD_FIELDS` and `archive_keyframe_payload_on_cpu`, `scripts/slam.py:513-526`; calls at 752 and 1074 | Detach and copy color/depth/semantic ID/semantic color to CPU with `copy=True` | CPU-authoritative pageable tensors persist until process exit; no eviction/compression. `est_w2c` remains in the GPU-resident keyframe dict | Linear host-memory growth; measure exact tensor storage bytes, RSS/HWM, per-field distribution and archive-copy latency |
| Mapping keyframe selection | `utils/keyframe_selection.py:10-110`; call at `scripts/slam.py:931-953` | Samples 1,600 valid current-depth pixels, back-projects, scores all eligible keyframe poses by overlap, then randomly permutes positive-overlap candidates; last keyframe and current frame are appended | Current depth/intrinsics/poses and archived `est_w2c` are GPU-resident; output indices are Python/NumPy | Work grows with retained keyframe count and includes GPU tensor operations plus Python loop. Time end-to-end and record candidate count, selected IDs and keyframe count; preserve RNG order |
| CPU-to-GPU staging | `stage_keyframe_payload`, `scripts/slam.py:529-541`; call/use at 967-990 | On archived selection, copies all four payload fields via `.to(device, non_blocking=False)` | Source pageable CPU persists; one temporary staged GPU payload group is iteration-lived and references are deleted at 1028-1029. Copy is synchronous by design | Repeated H2D volume is visible but latency is not. Record bytes/field, CPU synchronized wall time and CUDA-event transfer time; do not change transport behavior in measurement-only gate |
| Gaussian representation | `scripts/slam.py:133-178`, 392-478; renderer packing in `utils/slam_helpers.py:119-233` | Trainable means3D, RGB, rotations, opacity, scale, semantic colors; fixed semantic IDs; camera pose arrays; pixel-driven append | GPU-authoritative for full run; per-Gaussian arrays grow, are concatenated/pruned and serialized at end | Attribute and auxiliary bytes are directly attributable; gradients/Adam are state-dependent. Snapshot by tensor/storage category at bounded milestones |
| Rendering and loss | `scripts/slam.py:249-389`; calls at 819 and 992 | Three external rasterizer passes: RGB, depth/silhouette, semantic color; computes RGB/depth/semantic losses | Inputs, outputs, autograd graphs and external CUDA buffers on GPU; outputs/graph iteration-lived | External renderer buffers are not separately exposed. CUDA events around each pass and memory deltas/peaks can bound, not perfectly attribute, renderer workspace |
| Tracking optimizer | creation `scripts/slam.py:181-187`, call 806; step 829-832 | Adam over all non-excluded parameter groups, although Gaussian LRs are zero during tracking | GPU; optimizer is frame-lived. Adam/gradient materialization for zero-LR groups remains possible | Measure instantiated state bytes after first step, gradients and step GPU time; report zero-LR state rather than assuming it is absent |
| Mapping optimizer | creation at 956; step 1015-1016 | New Adam per mapping frame over map and camera params; map LRs active, camera LRs zero | GPU; mapping-frame lifetime; moments are created after step and resize-aware helpers migrate them during prune/densify | Likely large transient/persistent-within-frame memory. Attribute params, grads and optimizer state before/after first step and before destruction |
| Gaussian append | `add_new_gaussians`, `scripts/slam.py:421-478`; call 923-925 | Renders silhouette/depth, generates new points for unseen/new-foreground pixels, concatenates fields and rebuilds auxiliaries | GPU; output becomes scene-lifetime map; concatenation creates transient copies | Measure render, point generation, concatenation, Gaussian delta and peak allocation delta |
| Pruning | `utils/slam_external.py:147-200`; called `scripts/slam.py:1003-1004` | At configured iterations, masks opacity/large Gaussians and rebuilds params plus Adam state | GPU; temporary masks/copies iteration-lived, retained tensors survive | Time only active prune checks separately from no-op calls; count removed Gaussians and transient peak |
| Gradient densification | `utils/slam_external.py:203-255`; gated at `scripts/slam.py:1008-1013` | Clone/split path exists | GPU if enabled; **disabled** in checked-in Replica online config (`configs/replica/slam.py:118`) | Record configured/executed state. Do not assign runtime cost to this inactive branch |
| Mapping scheduling | `scripts/slam.py:907-1040`; config `configs/replica/slam.py:12-16,85-130` | Mapping every frame, 60 iterations, random choice among overlap window + last + current | Sequential; frame/iteration temporaries on GPU; chosen archived payload staged per iteration when applicable | Record mapping-trigger reason, iterations, frame vs archived selection, H2D reuse, end-to-end mapping time |
| Evaluation/save | `scripts/slam.py:1100-1150`; evaluator `utils/eval_helpers.py:583-839` | Prints aggregate runtime, evaluates sampled frames, enriches and serializes final params | Evaluation is a distinct GPU workload; serialization copies arrays to host/disk | Keep online, evaluation and serialization clocks separate; Phase 5 profiling comparisons use online interval only unless explicitly stated |

## Memory ownership invariants

- `VERIFIED`: archived `color`, `depth`, `semantic_id`, `semantic_color` are CPU-authoritative (`scripts/slam.py:513-526`).
- `VERIFIED`: `est_w2c` is not offloaded and is used directly by overlap selection (`utils/keyframe_selection.py:65-83`).
- `VERIFIED`: staging is pageable, synchronous and `non_blocking=False` (`scripts/slam.py:529-540`).
- `VERIFIED`: at most the active selected archived payload is intentionally staged; it is deleted after the mapping iteration (`scripts/slam.py:967-1029`).
- `VERIFIED`: no eviction or persistent GPU cache exists in the active path.
- `INFERRED`: allocator reuse may keep reserved CUDA memory after references are deleted; deletion is not equivalent to immediate physical release.
- `NOT VERIFIED`: exact external rasterizer workspace and kernel-level overlap, because the CUDA implementation is an external compiled dependency.

## P5-G2 source surface

Instrumentation should be isolated behind a disabled-by-default profiling option and a small telemetry module. The minimum active-path hooks are: dataset access (759), tracking region/iteration (802/817), Gaussian append (910), selection (931), optimizer construction (955), staging (977), render/loss (992), backward (1000), prune/densify (1003/1009), optimizer step (1015), keyframe archive (1059), frame boundary (1089), evaluation (1122), and serialization (1149). No loss, scheduling, selection, residency, dtype, or RNG behavior may change.
