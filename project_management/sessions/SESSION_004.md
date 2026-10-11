# SESSION_004 — Phase 4 Variant B Full-Scene Run

## Metadata

Session ID: SESSION_004\
Title: Phase 4 Variant B Full-Scene Run\
Status: CLOSED\
Started: 2026-10-10\
Last active: 2026-10-11\
Closed: 2026-10-11\
Phase: Phase 4 — Memory-management research variant\
Variant: `PHASE4-VB-001` — CPU offload of resident keyframe payloads\
Objective: run and audit the unchanged Variant B online pipeline on full
Replica `room0` frames 0–1999 without evaluation or post-SLAM work.

## Starting State

Phase 3 baseline runtime reproduction was closed with the documented RTX 5080
16 GB memory limitation. Phase 4 Variant B had passed Gate 5 frames 0–999 with
`PASS_FRAME_LIMIT`. The full-scene Variant B run and evaluation had not yet
been performed.

## Work Completed

- Ran one continuous online PHASE4-VB-001 Replica `room0` sequence covering
  frames 0–1999.
- Reached the natural post-online evaluation boundary after all 2,000 frames;
  the real loader was never called for index 2000.
- Blocked evaluation before execution. No ATE, rendering metrics, semantic
  metrics, post-SLAM optimization, or paper metrics were run.
- Preserved source/config integrity and the declared Variant B residency
  policy. No CUDA OOM, NaN/Inf failure, memory safety stop, or residency
  violation occurred.
- Audited the harness contradiction in
  `docs/experiments/PHASE4_VB001_FULL_SCENE_AUDIT.md`.

## Result and Corrected Classification

Corrected classification: `PASS_RUNTIME_VALIDATOR_BUG`.

The original generated harness summary remains `FAIL_RUNTIME`. Its only
validation error was `logical keyframe IDs/order mismatch`. The validator
constructed the expected IDs from the normal five-frame cadence but omitted
the released source condition `time_idx == num_frames-2`. For 2,000 frames,
frame 1998 is therefore a legitimate terminal keyframe and frame 1999 is also
legitimate through the normal cadence. Expected and observed final keyframe
counts are both 402.

The original evidence is preserved unchanged. The corrected classification is
an audit interpretation, not a silent rewrite from FAIL to PASS.

## Full-Scene Runtime Facts

- Completed frame range: 0–1999.
- Final completed frame: 1999.
- Online runtime completed: yes.
- Final Gaussians: 4,983,660.
- Final logical keyframes: 402.
- Final CPU keyframe archive: 10,497,024,000 B.
- Final GPU archived payload: 0 B.
- Peak GPU allocated/reserved: 6,774,482,432 / 8,009,023,488 B.
- Runtime: 22,299.70758857 s (about 6 h 11 m 39.708 s).
- PHASE4-VB-001 memory objective: succeeded at the measured runtime level.

Evidence:

- `results/runtime_artifacts/phase4_vb001_full_scene_0_1999/`
- `docs/experiments/PHASE4_VB001_FULL_SCENE_AUDIT.md`

## Output Availability

Final evaluation artifacts are not available. The run used
`save_checkpoints=False`, and the evaluation-blocking completion hook stopped
execution before the source's final `save_params(...)` path. It did not save:

- `params.npz`;
- a final map/Gaussian checkpoint;
- estimated trajectory/camera parameter arrays;
- final semantic/Gaussian numerical state;
- reloadable `keyframe_time_indices` checkpoint output;
- PLY output; or
- evaluation output.

The runtime JSON contains measurements and validation traces, not a
reconstructable final map. A rerun is not required to classify the existing
runtime or memory result. A separately authorized full-scene rerun is required
if future evaluation needs the final map and trajectory.

## STOPPED HERE

PHASE4-VB-001 online full-scene 0–1999 completed, but final evaluation
artifacts were not saved. The next session starts with output-save dry-run
inspection and a bounded 0–49 smoke test, not evaluation or a direct full-scene
rerun.

## Next Recommended Gate

`PHASE4-VB-001` output-saving dry-run inspection, followed—only if inspection
passes—by one output-save smoke test over frames 0–49.

Review the smoke artifacts for `params.npz`, keyframe indices, camera
trajectory, Gaussian state, semantic state, provenance, and proof that no
evaluation ran. Stop for explicit approval after this review. Do not authorize
the full-scene output-saving 0–1999 run until the smoke output is validated.
Evaluation remains prohibited until full-scene outputs are saved and reviewed.

## Next Session Start Prompt

Dry-run inspect the PHASE4-VB-001 output-saving harness and released
`save_params(...)` boundary. If it is correct, run exactly one bounded Replica
`room0` output-save smoke test for frames 0–49, verify `params.npz`, reloadable
`keyframe_time_indices`, trajectory, map, and semantic outputs, then stop for approval. Do not run
full-scene 0–1999 directly.

## Constraints Preserved

- No evaluation, ATE, rendering metrics, semantic metrics, post-SLAM
  optimization, or paper metrics were run.
- No source/config/algorithm modification was made during the full-scene run
  or audit.
- No automatic retry, commit, or push was performed.
