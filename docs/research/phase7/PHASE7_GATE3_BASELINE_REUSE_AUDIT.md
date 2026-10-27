# Phase 7 Gate 3 — Phase 4 full-scene baseline reuse audit

**Audit scope:** existing Replica `room0`, frames 0–1999 evidence only. No
Phase 4 rerun, checkpoint copy or evaluation was performed.

## Historical runs found

### PHASE4-VB-001 detailed full-scene runtime

Evidence: `/home/robot/research/SGS_slam/results/runtime_artifacts/phase4_vb001_full_scene_0_1999/`
and `docs/experiments/PHASE4_VB001_FULL_SCENE_AUDIT.md`.

The recorded online loop processed exactly 0–1999 and reached the post-loop
evaluation boundary. The original harness aggregate says `FAIL_RUNTIME`,
because a validator omitted the released `num_frames-2` keyframe. The audit
classifies this specifically as `PASS_RUNTIME_VALIDATOR_BUG`; do not restate
it as an unqualified harness PASS. Effective source was a Phase 4 Variant B
uncommitted diff with recorded source-file SHA
`f02697323d9f07beb52fc10efeb413121271295cd4341881313063ca2ed80e1a` in its
result JSON. It did not save final NPZ/PLY/trajectory or evaluate metrics.

### PHASE4-VB-001 full-scene output-save telemetry

Evidence:

- `/home/robot/research/SGS_slam/docs/experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md`
- `/home/robot/research/SGS_slam/results/runtime_artifacts/phase4_vb001_minimal_output_save_full_0_1999/`
- `/home/robot/research/SGS_slam/experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/`

The run reports `PASS_FULL_OUTPUT_SAVE_TELEMETRY`, exact frames 0–1999,
14,173.475159 s wall/runtime, 4,956,467 final Gaussians, 402 keyframes and a
valid saved `params.npz` with camera/GT poses, Gaussian parameters and
semantic state. Its source SHA is exactly the frozen Phase 4
`scripts/slam.py` SHA `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3`
at HEAD `68f9060f7ff4d8d141be1d5f71339401327edd06`. The run used a temporary
output-save harness, disabled evaluation with a no-op evaluator, and added
the final-state save boundary. The artifact manifest's four checkpoint/PLY/
keyframe hashes were independently rechecked and match.

## Comparison classifications

| Metric/evidence | Available Phase 4 evidence | Gate 3 reuse classification | Limit |
|---|---|---|---|
| Dataset, scene, frame IDs | Replica `room0`, 0–1999 in output-save telemetry; source dataset length 2,000 | `COMPARABLE_WITH_LIMITATIONS` | Frame identity is recorded; source image/depth/semantic files were not individually hashed in that run |
| Frozen source | Output-save metadata records exact frozen source SHA; earlier detailed runtime used a Variant B diff | `COMPARABLE_WITH_LIMITATIONS` | Gate 3 adds BCGM and has a different active source/config path |
| Scientific config | Seed 0, 1200×680, tracking 40, mapping 60, map every frame, keyframe every 5, window 24, semantics and pixel insertion on, prune on, clone/split off | `COMPARABLE_WITH_LIMITATIONS` | Output-save run's frame count/evaluator were harness-overridden; no complete effective config hash |
| Completion | Output-save record covers exactly 2,000 frames and final frame 1999; earlier run retains validator-bug finding | `VERIFIED_COMPARABLE` for processed frame interval only | Earlier `FAIL_RUNTIME` is interpreted only as `PASS_RUNTIME_VALIDATOR_BUG`, not silently rewritten |
| Runtime | Output-save 14,173.475159 s; detailed run 22,299.707589 s | `COMPARABLE_WITH_LIMITATIONS` | Different harness, evaluator/no-op, save and timer scopes; no matched speedup claim |
| CUDA allocated/reserved | Output-save 5,817,509,888 / 7,189,037,056 B; detailed run 6,774,482,432 / 8,009,023,488 B | `COMPARABLE_WITH_LIMITATIONS` | Allocator scopes/harnesses differ; Gate 3 adds BCGM admission and evaluation cost |
| NVML peak | No sampled NVML peak in either full-scene result | `NOT_MEASURED` | No device-wide comparison |
| Final Gaussian count | 4,956,467 output-save; 4,983,660 detailed runtime | `COMPARABLE_WITH_LIMITATIONS` | BCGM changes admission; pruning can subsequently reduce count |
| Checkpoint/trajectory | Output-save `params.npz` and keyframes exist; earlier detailed runtime has no saved final checkpoint | `COMPARABLE_WITH_LIMITATIONS` | Output-save checkpoint supplies trajectories but no matched evaluator outputs |
| RGB PSNR / MS-SSIM / LPIPS | Not evaluated | `NOT_MEASURED` | No Phase 4 full-scene quality reference |
| Depth L1 | Not evaluated | `NOT_MEASURED` | No matched depth quality reference |
| ATE | Estimated/GT poses saved in output-save checkpoint, but no ATE was calculated | `NOT_MEASURED` | Pose availability is not an ATE result; preserve evaluator definition |
| Semantic mIoU | Not evaluated | `NOT_MEASURED` | Saved semantic colors are not an mIoU score |

## Reuse decision

Reuse the output-save run for full-scene completion, checkpoint schema,
Gaussian-count scale, runtime context and allocator-memory context only, with
the limitations above. Reuse the detailed runtime audit for the historical
keyframe validator contradiction and additional memory/runtime context. Do
not claim matched speedup, quality retention, NVML improvement, or paper
reproduction. No Phase 4 rerun is currently essential or scheduled; Gate 3's
single BCGM-on run is the only planned new full-scene arm.
