# PHASE4-VB-001 Full-Scene Output-Saving Dry-Run Plan

Date: 2026-10-11  
Repository: `/home/robot/research/SGS_slam`  
Branch: `phase4-vb-001-cpu-keyframe-offload`  
HEAD: `ecb2ae67b073fe7002df6cda76999a18e603a901`

## Scope and gate

This is a `DRY-RUN / INSPECT ONLY` plan. No CUDA workload, SLAM frame,
smoke test, full-scene run, evaluation, metric computation, ATE, rendering,
semantic evaluation, post-SLAM optimization, commit, or push was performed.

The current workflow is intentionally stopped before execution. Full-scene
0-1999 may only start after explicit user approval in a later prompt.

## Preconditions

### Repository and working tree

- Expected branch: `phase4-vb-001-cpu-keyframe-offload` — verified.
- Current HEAD: `ecb2ae67b073fe7002df6cda76999a18e603a901` — verified.
- Existing working-tree changes are documentation/state files only:

  ```text
   M docs/project_state/CURRENT_STATE.md
   M docs/project_state/state.yaml
   M project_management/CHANGELOG.md
   M project_management/PROJECT_STATUS.md
   M project_management/SESSION_HANDOFF.md
   M project_management/sessions/SESSION_004.md
  ?? docs/experiments/PHASE4_VB001_FULL_SCENE_AUDIT.md
  ?? docs/experiments/PHASE4_VB002_RUNTIME_OPTIMIZATION_PLAN.md
  ```

- No unapproved changes were found in `scripts/slam.py`, `configs/`, renderer
  code, dataset loaders, losses, semantic code, or the PHASE4-VB-001 source
  implementation.
- `git diff --stat`: 6 files changed, 427 insertions(+), 252 deletions(+).
- No source/config changes are proposed by this plan.

### Evidence availability

All required evidence files were found:

- `docs/experiments/PHASE4_VB001_FULL_SCENE_AUDIT.md`
- `docs/experiments/PHASE4_VB002_RUNTIME_OPTIMIZATION_PLAN.md`
- `results/runtime_artifacts/phase4_vb001_full_scene_0_1999/PHASE4_VB001_FULL_SCENE_SUMMARY.md`
- `project_management/SESSION_HANDOFF.md`
- `project_management/PROJECT_STATUS.md`
- `docs/project_state/state.yaml`

The smoke-test summary
`results/runtime_artifacts/phase4_vb001_output_save_smoke_0_49/PHASE4_VB001_OUTPUT_SAVE_SMOKE_SUMMARY.md`
does not exist. No 0-49 output-saving smoke test is recorded, and no smoke
artifacts were found at that path.

Therefore the normal workflow is: run/review the smoke test first. A
full-scene output-saving run must not be treated as authorized unless the user
explicitly approves skipping that gate.

The dataset expectation is Replica `room0`, 2,000 frames, with RGB, depth,
semantic IDs, semantic colors, instance IDs, and instance colors present.
This was verified by read-only file counts. No dataset workload was run.

### CUDA/GPU precondition for Step 2

No CUDA workload is part of this dry run. At the beginning of Step 2, the
harness must first record Python/PyTorch/CUDA/device identity, confirm exactly
one expected RTX 5080 device, confirm CUDA availability, and record a
pre-run `nvidia-smi` snapshot. If that preflight fails, stop without loading a
SLAM frame and preserve the preflight evidence.

## Proposed Step 2 command

The proposed full-scene harness is a temporary harness-only file, not a source
or config change:

```text
/tmp/phase4_vb001_full_scene_output_save_0_1999.py
```

Proposed exact command:

```bash
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python \
  /tmp/phase4_vb001_full_scene_output_save_0_1999.py
```

The harness will use:

- dataset: `Replica`, scene `room0`;
- source config: `configs/replica/slam.py` loaded without changing its
  algorithmic values;
- frame range: `0-1999`, with an explicit guard against dataset index `2000`;
- seed policy: released config seed unchanged (`0`);
- tracking/mapping iterations, resolution, dtype, renderer, losses,
  keyframe cadence, mapping window, pruning, densification, semantics, and
  Variant B residency behavior unchanged;
- environment: `/home/robot/miniconda3/envs/sgs_slam_5080`.

The prior Variant B full-scene runtime was approximately 22,299.7 seconds
(6 h 11 m 39.7 s). The output-saving run should be budgeted for roughly
6-7 hours, with additional final serialization time and no guarantee of an
identical runtime.

## Proposed output paths

Evidence directory:

```text
results/runtime_artifacts/phase4_vb001_full_scene_output_save_0_1999/
```

Stable final-state output directory:

```text
experiments/Replica/room0_phase4_vb001_output_save_0_1999/
```

The stable output directory must be unique and must not overwrite the prior
online run or any baseline/post-opt result.

## Save strategy

The released source final boundary is understood from `scripts/slam.py` and
`utils/common_utils.py`:

1. The online loop completes frame 1999 and appends logical keyframes.
2. The source calls `eval(...)`.
3. The source adds `timestep`, `intrinsics`, `w2c`, image dimensions,
   `gt_w2c_all_frames`, and `keyframe_time_indices` to `params`.
4. When semantics are enabled, semantic IDs are converted to `uint8` for
   saving; trainable `semantic_colors` remain part of the parameter state.
5. The source calls `save_params(params, output_dir)`.
6. `save_params` writes `params.npz`, `params.ply`, and `seg_params.ply`.

The Step 2 harness will preserve this released final save path and wrap it
only for output verification. The wrapper will call the original
`save_params(...)` first, then write a standalone
`keyframe_time_indices.npy` from the final saved field and record file sizes.
This wrapper is output control, not an algorithm change. It also records the
source/config/harness hashes, command, environment, frame range, seed, and
timestamps in the evidence directory.

Expected final state includes:

- `params.npz` with Gaussian/map parameters (`means3D`, colors, rotations,
  opacities, scales, and optimizer-independent saved state);
- `params.ply` and `seg_params.ply` as final map/semantic exports from the
  released save helper;
- estimated camera parameters and trajectory fields (`cam_unnorm_rots`,
  `cam_trans`, `timestep`, `intrinsics`, and `w2c`);
- `gt_w2c_all_frames` where normally assembled by the source;
- `keyframe_time_indices` in `params.npz` and standalone
  `keyframe_time_indices.npy`;
- semantic IDs and semantic colors;
- config/provenance metadata and timing/memory summaries in the evidence
  directory.

Periodic checkpoints remain disabled unless separately required by the
approved harness. The final `params.npz` and standalone keyframe index are the
authoritative final artifacts; no baseline output is overwritten.

## Evaluation and metrics blocking strategy

The source calls `eval(...)` before final parameter assembly and saving. The
Step 2 harness will replace only the module-level evaluator reference with a
no-op recorder that returns without loading evaluation frames, rendering
outputs, or computing metrics. It will also suppress progress-render hooks as
the existing runtime harness did.

This allows execution to continue to the source's final parameter assembly
and `save_params(...)` call while guaranteeing that the following are not
run:

- evaluation;
- ATE;
- PSNR, SSIM, LPIPS, or DepthL1;
- mIoU or any semantic metric;
- rendering metrics or semantic rendering evaluation;
- post-SLAM optimization;
- paper-metric reproduction.

No evaluation directory contents will be interpreted as metrics. The harness
will explicitly record `evaluation_executed: false` and equivalent false
flags for all prohibited metric families.

## Visual export strategy

Full RGB/depth/semantic rendered-image export for all frames is deferred to a
separate evaluation/export gate and is not part of Step 2.

No optional sanity renders for frames 0, 999, or 1999 are proposed here. If a
future sanity export would enter the evaluator or renderer-metric path, it
must be skipped and recorded as deferred. The final PLY files created by the
released `save_params` helper are state exports, not per-frame rendered-image
metrics.

## Timing and FPS logging strategy

The harness will preserve the existing timing instrumentation around tracking,
mapping, and the complete online run. It will record:

- tracking iteration/frame timing and derived tracking FPS, if available;
- mapping iteration/frame timing and derived mapping FPS, if available;
- overall online SLAM runtime and derived overall FPS;
- final serialization duration separately;
- peak GPU allocated/reserved memory and process RSS/HWM.

If any timing cannot be obtained without changing the algorithm or source
execution path, it will be reported as `UNKNOWN`; no intrusive source change
will be made.

## Memory logging strategy

The harness will record, without changing allocation policy:

- maximum GPU allocated bytes;
- maximum GPU reserved bytes;
- maximum process RSS and HWM;
- CPU keyframe archive bytes;
- persistent GPU archived payload bytes;
- GPU-resident `est_w2c` bytes;
- peak staged payload bytes and simultaneous staged groups, if available;
- sampled memory at frames `0, 49, 99, 199, 299, 399, 499, 699, 899,
  999, 1199, 1399, 1599, 1799, 1999`.

No pinned memory, non-blocking transfer, persistent GPU cache, keyframe
eviction, precision change, or new memory optimization will be introduced.

## Expected keyframe logic

The released source condition in `scripts/slam.py` is:

```python
(time_idx == 0) or ((time_idx + 1) % keyframe_every == 0) \
    or (time_idx == num_frames - 2)
```

With `num_frames=2000` and `keyframe_every=5`, the expected final tail is:

```text
..., 1989, 1994, 1998, 1999
```

The expected final logical keyframe count is 402, assuming finite GT poses.
The Step 2 validator must include the `num_frames-2` condition and must not
reuse the old cadence-only formula `[0, *range(4, MAX_FRAME + 1, 5)]`.

## Step 2 acceptance criteria

The run is acceptable only if all of the following are true:

- frames `0-1999` completed and frame `1999` completed;
- final logical keyframe count is 402;
- terminal keyframes include 1998 and 1999;
- `params.npz` exists and is readable;
- `keyframe_time_indices.npy` or an equivalent reloadable field exists;
- trajectory/camera parameters exist;
- Gaussian/map parameters exist;
- semantic parameters exist;
- config/provenance metadata exists;
- final state is sufficient for later evaluation without rerunning online
  SLAM;
- no evaluation metrics were computed;
- no paper metrics were reproduced;
- memory remains within the observed safe envelope, with no OOM or safety
  violation;
- no source/config drift occurred;
- Variant B residency invariants remain valid.

## Step 2 failure policy

Stop immediately on OOM, NaN/Inf, residency invariant violation, output-save
failure, source/config drift, or unexpected runtime error. Preserve partial
evidence and logs. Do not retry, stack an optimization, run evaluation, or
convert the failure into a metric run.

## Proposed final Step 2 summary fields

The final evidence summary will include:

- final status;
- completed frame range and final frame;
- runtime and human-readable duration;
- final Gaussian count;
- logical keyframe count and terminal IDs;
- peak GPU allocated/reserved memory;
- max RSS/HWM;
- timing/FPS availability and values;
- CPU archive/GPU archived payload/GPU `est_w2c`/staged payload values;
- artifact manifest with paths and byte sizes;
- `params.npz`: yes/no;
- `keyframe_time_indices`: yes/no;
- final-state sufficiency: yes/no;
- explicit no-evaluation/no-metrics/no-paper-reproduction statement;
- source/config drift result;
- recommended later evaluation/export gate.

## Approval gate

STEP 2 is not authorized by this document. The smoke-test gate is also not
present in the current evidence. Any later execution requires explicit user
approval and a fresh CUDA preflight.

STOPPED HERE — DRY-RUN/INSPECT ONLY COMPLETE. DO NOT RUN FULL-SCENE 0–1999 UNTIL USER EXPLICITLY APPROVES STEP 2.
