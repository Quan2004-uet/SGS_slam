# P6-BAM-006 PREFLIGHT FIX — CPU/Static Preparation

**Status: `PASS_P6_BAM_006_PREFLIGHT_FIX_CPU_STATIC_READY`.** This resolves the
preparation blockers only. No SLAM frame, CUDA mapping, GPU evaluator, rendering,
PLY conversion, or full-scene experiment was run. A separate researcher request
is still required before launching P6-BAM-006-FULL.

## Provenance and integrity

- Branch: `phase5-profiling-instrumentation`.
- Previous HEAD: `36284a2cbccd3e148a628c44f6fbcba139ac3ceb`.
- Phase 4 tag peels to `37522db553ff18b96592073f9de699db7fa48600`.
- Phase 4 checkpoint SHA256 remains
  `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`.
- `/tmp/phase4_vb001_eval_e4_full_released.py` was available; SHA256
  `8c31b131e1b294fb0a089589c4f934e1c9912a4969573169f2abe333c847d5e6`.
- The matched 500-frame V-A2 snapshot used for parity is
  `results/runtime_artifacts/phase6_bam/p6_bam_005_comparison/va2_effective_config.json`.
- No Phase 4 or previous Phase 6 artifact was modified. Pre-existing untracked
  historical reports, sessions 007–010, QA-001 report, and `vds` were preserved.

Machine-readable preparation evidence and hashes are in
`results/runtime_artifacts/phase6_bam/p6_bam_006_preflight_fix_20261016/preflight_fix_manifest.json`.

## Changed files

- `configs/replica/phase6_bam_va2_full_0_1999.py` — isolated full-scene V-A2
  wrapper; old Phase 4/V0/V-A/V-A2 wrappers are unchanged.
- `scripts/slam.py` — exclusive effective-config snapshot and checkpoint-first
  post-loop finalization; no online algorithm logic changed.
- `utils/common_utils.py` — CPU ZIP/schema/horizon and non-empty PLY validator
  for the just-saved final state.
- `scripts/evaluate_saved_phase6.py` — saved-checkpoint-only E4 evaluator and
  strict Phase 6 input/output path guards.
- `tests/test_p6_bam_006_preparation.py` — CPU/static config, protocol, output,
  checkpoint, and source-order regression tests.
- This report, dated follow-up appended to the historical preflight report, and
  project/session state records.

## Frozen effective full-scene configuration

The CPU-loaded wrapper resolves to:

| Setting | Value |
|---|---|
| Variant / run ID | `V-A2-FULL-0-1999` / `p6_bam_006_room0_0_1999_va2_r01` |
| Dataset / scene | Replica / room0 |
| Horizon | start `0`, end `2000` exclusive, stride `1`, `num_frames=2000` |
| Resolution / semantic input | 680×1200; semantics enabled; 101 configured classes |
| Seed | 0 |
| Tracking / mapping maximum | 40 / 60 |
| Mapping controller | adaptive LOW/MID/FULL `45/60/60` |
| Novelty thresholds | `low_max=0.01`, `mid_max=0.05` (unchanged) |
| Keyframe/offload and pruning | inherited unchanged from validated Phase 6 source; prune iteration 20 remains reachable at 45+ iterations |
| Evaluation | `eval_every=5`, 401 views `[0,4,9,...,1994,1999]` |
| Checkpointing | enabled; interval 1999, saving frame 0 and frame 1999 snapshots |
| Profiler / WandB | LIGHT / disabled |

The parity test compares the complete wrapper dictionary against the stored
P6-BAM-005 V-A2 effective config. Differences are the intended full-scene
horizon, `eval_every`, frame-1999 checkpoint interval, run identity/variant
label, plus the new explicit `checkpoint_first_finalization=true` output-safety
flag. WandB remains disabled, matching P6-BAM-005; this was explicitly set
because the shared base otherwise inherited it enabled. All other resolved
settings match. The wrapper invokes the existing run-ID regex and
output-existence guard, then additionally canonicalizes and rejects run or
telemetry symlinks that escape the Phase 6 root.

The bounded-loop proof is source/config based: `scripts/slam.py` uses
`config['data']['num_frames']` for its frame loop after the dataset is loaded;
the wrapper sets this to 2000 and the dataset constructor uses start/end/stride
`0/2000/1`. No run was executed to observe frame completion.

## Checkpoint-first save and recovery

The previous ordering ran final evaluation before assembling final metadata and
calling `save_params`, so an evaluator exception could leave only the periodic
snapshot. The post-loop order now is:

1. Existing online loop completes; the frame-1999 interval checkpoint and
   `keyframe_time_indices1999.npy` are written by the existing in-loop branch.
2. The existing final metadata is assembled: timestep, intrinsics, first-frame
   `w2c`, dimensions, all GT relative-w2c poses, final keyframe indices, and
   semantic IDs converted to `uint8`.
3. Existing `save_params` writes `params.npz`, `params.ply`, and
   `seg_params.ply`.
4. `validate_final_checkpoint` verifies NPZ ZIP CRCs, required model/semantic/
   camera/keyframe fields, 2000-pose horizon, Gaussian/semantic alignment,
   terminal keyframe 1999, and non-empty RGB/semantic PLY files.
5. Only after validation does the existing in-process final evaluator start.

The evaluator cannot modify or overwrite the saved model. If evaluation fails,
recovery is from `params.npz` and `effective_config.json`; no SLAM rerun is
needed. If the online evaluator aborts, use a fresh evaluation attempt
directory. If a derived PLY export alone is absent, the authoritative NPZ still
contains Gaussian and semantic arrays; export repair is a separate derived
artifact operation and must use a new path. The frame-1999 interval checkpoint
is a fallback, but does not contain all final metadata; the complete
`params.npz` is the preferred recovery input.

The source diff adds an exclusive startup config snapshot and gates
serialize/validate-before-evaluate behavior on the new wrapper-only
`checkpoint_first_finalization` flag. Configurations without the flag retain
the pre-existing evaluation-before-final-save order. The per-frame loop, RNG,
tracking, keyframe selection, mapping, optimizer/loss, Gaussian append/prune,
CPU keyframe staging/offload, and profiler implementation are untouched. No new
CUDA sync was added. Checkpoint CRC/schema validation is CPU-side and occurs
after the online loop.

## Saved-state evaluation contract

Entrypoint: `scripts/evaluate_saved_phase6.py`. Its module import is CPU-pure;
renderer/evaluator imports occur inside `main`. At execution it:

- accepts only `params.npz` directly under a Phase 6 run directory and the
  adjacent `effective_config.json`;
- verifies the frozen full-scene variant, horizon and E4 cadence;
- refuses output outside `results/runtime_artifacts/phase6_bam/`, inside the
  immutable run directory, or at an already existing destination;
- loads the saved model and calls the unchanged `utils.eval_helpers.eval`
  implementation exposed by `scripts/slam.py`, with `eval_every=5` and
  `save_frames=True`; it never calls tracking/mapping;
- validates that each of PSNR, MS-SSIM (`ssim.txt`), LPIPS-Alex, depth RMSE,
  depth L1 and semantic-color mIoU has 401 finite values and that RGB/depth/
  semantic render IDs exactly match `[0,4,9,...,1994,1999]`;
- computes all-2000-pose Horn-aligned mean translation error and supplementary
  true RMSE with the same `align` helper; it labels the former as ATE Mean
  rather than the released helper's misleading “ATE RMSE” print label.

Protocol provenance is the Phase 4 E4 harness/report and unchanged
`utils/eval_helpers.py` (current SHA256
`e94366ca256ec2b51b5d0264a5daba2a895cc0375d7b91e976e4ea0e9e28194e`). The
image sampler, GT-depth RGB mask, `calc_psnr`, `pytorch_msssim.ms_ssim`,
TorchMetrics AlexNet LPIPS, Replica depth scale/mask, GT-palette semantic
recoloring, and relative-w2c Horn alignment remain the released implementations.
This is a static equivalence review; the prepared 401-view evaluator was not
run here.

Suggested post-run invocation (not executed):

```bash
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python \
  scripts/evaluate_saved_phase6.py \
  --checkpoint results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/params.npz \
  --config results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/effective_config.json \
  --output-dir results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/evaluation/va2_attempt01
```

For an evaluation retry, choose a new unused `va2_attemptNN` path; never reuse
partial output. The saved-state evaluation requires GPU rendering and is not
authorized by this preparation task.

## 3D deliverables

- Authoritative model: `<run>/params.npz`, including `means3D`, RGB attributes,
  rotation/scale/opacity, `semantic_colors`, `semantic_ids`, both camera
  trajectories, intrinsics, and final keyframe metadata.
- Existing `save_params` RGB Gaussian export: `<run>/params.ply`.
- Existing learned semantic-color Gaussian export:
  `<run>/seg_params.ply`. It preserves the learned color rendering attributes,
  not explicit class-ID PLY properties. `semantic_ids` remain aligned metadata
  in NPZ; do not present the PLY as a categorical-ID point cloud.
- Phase 4 V1/V3A source audit has established `scripts/visualization/render_final_maps.py`
  as an existing derived RGB/semantic 3D map visualization route. Proposed
  output: `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2/`.
  It consumes both PLYs and optional `--params-npz`; its render is a derived
  free-view 3D map visualization, not the 401-view metric evaluation.
- A separate semantic-ID/class-label 3D exporter is `NOT_IMPLEMENTED`. If
  categorical labels are needed, a derived visualization would require an
  explicitly audited mapping from saved `semantic_ids` and palette provenance;
  no exporter or conversion was run or added.

## Artifact isolation and intended paths

Read-only canonical-path checks confirmed these destinations did not exist,
had no symlink escape, and resolve below the Phase 6 root:

- Run: `results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/`
- Telemetry: `results/runtime_artifacts/phase6_bam/telemetry/p6_bam_006_room0_0_1999_va2_r01/`
- Comparison: `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/`
- Saved-state evaluation attempt: `.../evaluation/va2_attempt01/`
- Derived 3D visualization: `.../visualization/va2/`

Expected artifacts after a separately authorized run: `params1999.npz`,
`keyframe_time_indices1999.npy`, `params.npz`, `params.ply`, `seg_params.ply`,
`effective_config.json`, and profiler telemetry at the Phase 6 telemetry path.
The interval checkpoint and keyframe sidecar are created by the existing
checkpoint branch. Evaluation metrics and 401 rendered RGB/depth/semantic
images go under its unique evaluation attempt path. `render_final_maps.py`
would write its metadata/images only under the unique visualization path.
No destination was created during validation except this preparation evidence
directory; the final run/telemetry/comparison/evaluation/visualization paths
remain absent.

## CPU/static validation and remaining risks

Executed with `/home/robot/miniconda3/envs/sgs_slam_5080/bin/python`:

- `python -m unittest tests.test_p6_bam_006_preparation tests.test_mapping_budget tests.test_performance_profiler` — **45 passed, 0 failed**.
- `python -m py_compile` on the new wrapper, `scripts/slam.py`, saved-state evaluator, `utils/common_utils.py`, and the new tests — **PASS**.
- `git diff --check` — **PASS**.

The tests check the resolved config against P6-BAM-005, strict frame horizon,
controller and profiler fields, 401 IDs, path isolation, a small CPU NPZ
fixture, save/validate/evaluate source ordering, and evaluator's lazy CUDA
imports. No CUDA API, device health probe, renderer, evaluator, SLAM frame,
tracking, mapping, or 3D export was invoked.

Remaining runtime risks: a full 2000-frame run can still OOM or exhaust host
memory/disk; a CPU ZIP CRC scan adds post-run time; the generated PLYs and
401-view render outputs consume substantial disk; evaluation GPU compatibility
is statically reviewed, not runtime-verified on this new entrypoint; a failed
PLY exporter may leave the valid NPZ and frame-1999 checkpoint but stop the
normal evaluator; semantic PLY is learned semantic color, not direct class IDs.
Recheck GPU/RAM/disk, path absence, dataset integrity, Phase 4 hash, and source
provenance immediately before any separately authorized launch.

### Safe launch command (example only; not executed)

Run only after separate researcher authorization and a fresh output-path check:

```bash
env P6_BAM_RUN_ID=p6_bam_006_room0_0_1999_va2_r01 PYTHONDONTWRITEBYTECODE=1 \
  /usr/bin/time -f 'elapsed_seconds=%e peak_rss_kb=%M exit_status=%x' \
  -o results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/process_time.txt \
  /home/robot/miniconda3/envs/sgs_slam_5080/bin/python \
  scripts/slam.py configs/replica/phase6_bam_va2_full_0_1999.py \
  > results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/run.log 2>&1
```

The comparison directory must first be created only after authorization and
verified absent. This report does **not** authorize execution.
