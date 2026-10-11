# PHASE4-VB-001 Full-Scene Result Audit

Date: 2026-10-11  
Repository: `/home/robot/research/SGS_slam`  
Branch: `phase4-vb-001-cpu-keyframe-offload`  
Audited HEAD: `ecb2ae67b073fe7002df6cda76999a18e603a901`  
Evidence: `results/runtime_artifacts/phase4_vb001_full_scene_0_1999/`

This is a source-, harness-, and existing-evidence-only audit. No CUDA workload, experiment, evaluation, or post-SLAM optimization was run. The original evidence files were not rewritten.

## 1. Runtime facts

`RUNTIME VERIFIED` from the existing full-scene log and structured result:

- The online loop captured all 2,000 frames, exactly `0-1999`.
- The final completed frame was 1999.
- `guard.natural_online_loop_completion` is `true`.
- The real dataset loader was not called for index 2000.
- The final evaluation call was intercepted before evaluation execution.
- No CUDA OOM, memory safety stop, NaN/Inf failure, or residency failure was recorded.
- Tracking iterations were 79,960: zero for frame 0 and 40 for each of frames 1-1999.
- Mapping iterations were 120,000: 60 for each of 2,000 frames.
- Final Gaussian count was 4,983,660.
- Runtime was 22,299.70758857 seconds (approximately 6 h 11 m 39.708 s).
- Maximum GPU allocated/reserved memory was 6,774,482,432 / 8,009,023,488 bytes.
- Maximum observed process RSS/high-water mark was 13,529,231,360 / 13,583,106,048 bytes.

The harness first classified the `FullSceneComplete` boundary exception as `PASS_FULL_SCENE`. A later validator step changed the status to `FAIL_RUNTIME` solely because of `logical keyframe IDs/order mismatch`.

## 2. Validator contradiction

The harness generated its expected keyframe IDs as:

```python
expected_keyframe_ids = [0, *range(4, MAX_FRAME + 1, 5)]
```

For `MAX_FRAME=1999`, this list contains frame 0 plus the regular five-frame cadence `4, 9, ..., 1999`. It contains 401 IDs and omits the released source's special penultimate-frame keyframe, frame 1998. The observed list contains 402 IDs and ends `..., 1989, 1994, 1998, 1999`; therefore the harness emitted the mismatch even though the observed list follows the released condition.

The later summary statement `Logical keyframe IDs match: True` answers a different question. Its implementation compares the full-scene run's frame-499 keyframe list with the Phase 3C-6 frame-499 keyframe list:

```python
comparison_variant = result["frames"]["499"]
final_baseline = baseline["frames"]["499"]
comparison_variant["keyframes"]["ids"] == final_baseline["keyframes"]["ids"]
```

It does not compare the final frame-1999 list with `expected_keyframe_ids`. The summary label is therefore ambiguous, but the frame-499 comparison itself is true.

The completion booleans were produced by status coupling rather than independent runtime evidence:

```python
full_scene_completed = result['status'] == 'PASS_FULL_SCENE' and last_completed == 1999
```

After the incorrect keyframe expectation changed `result['status']` to `FAIL_RUNTIME`, this expression made both `Full scene completed` and `Variant B reached frame 1999` false. This contradicts the independently recorded 2,000 processed frames, final frame 1999, natural online-loop completion, and `scope.online_full_scene_completed=true`. It is a summary/reporting bug downstream of the validator expectation bug.

## 3. Released keyframe terminal condition

`VERIFIED FROM SOURCE` in `scripts/slam.py`, function `rgbd_slam`, per-frame keyframe insertion region (current lines 1059-1061):

```python
if ((time_idx == 0) or ((time_idx+1) % config['keyframe_every'] == 0) or \
            (time_idx == num_frames-2)) and (not torch.isinf(curr_gt_w2c[-1]).any()) and (not torch.isnan(curr_gt_w2c[-1]).any()):
```

A frame is appended when its GT pose is finite and any of these is true:

1. `time_idx == 0`;
2. `(time_idx + 1) % keyframe_every == 0`; or
3. `time_idx == num_frames - 2`.

The checked-in Replica config sets `keyframe_every = 5` in `configs/replica/slam.py`.

The same boolean condition is present in the static-audit baseline commit `e4183986204242a8bb422624618af07780a49d26` and the pre-Variant-B commit `443d3d3`. The Variant B diff adds CPU archival immediately before append and synchronous staging after selection; it does not change the insertion condition.

## 4. Expected versus observed final keyframes

For `num_frames=2000`, assuming the recorded finite GT poses:

- frame 0 contributes one keyframe;
- `range(4, 2000, 5)` contributes 400 cadence keyframes, including frame 1999;
- frame `num_frames-2`, or 1998, contributes one additional terminal keyframe and is not already in the cadence set.

The released-source expectation is therefore:

```python
[0, *range(4, 2000, 5)[:-1], 1998, 1999]
```

Equivalently, it is frame 0, cadence frames `4, 9, ..., 1994`, then terminal frame 1998, then cadence frame 1999. Expected count: 402. Observed count: 402. The observed final tail `..., 1989, 1994, 1998, 1999` is correct.

## 5. Root-cause classification

Primary classification: **harness/validator expectation bug**.

Secondary classification: **summary/reporting bug**.

This is not evidence of a Variant B behavioral failure. The validator modeled only the regular cadence and omitted the released `num_frames-2` branch. The summary then derived runtime-completion claims from the already downgraded aggregate status instead of the independent completion guard and processed-frame evidence.

The summary also states that pre/post system-state logs were saved, but only `pre_run_system_state.log` exists. This is another output-reporting inaccuracy and does not alter online completion.

## 6. Online execution classification

- `ONLINE_RUNTIME_COMPLETED`: **YES**. The released online loop processed frames 0-1999 and reached its natural post-loop evaluation boundary.
- `VARIANT_INVARIANTS`: **PASS** for the recorded checks. All archived payloads were CPU-authoritative, archived `est_w2c` remained GPU-resident, persistent GPU archived-payload bytes were zero, at most one archived payload group was staged, no staged group remained after a frame or at run end, staging followed selection, and the observed staging count matched archived mapping selections.
- `VALIDATOR`: **FAIL**, caused solely by the incorrect expected-keyframe formula.

These are separate findings and must not be collapsed into one boolean.

## 7. PHASE4-VB-001 memory objective

`RUNTIME VERIFIED`: the memory objective succeeded at the measured runtime level.

- The run reached frame 1999, beyond the released Phase 3 OOM at frame 1294 and allocator-only OOM at frame 1333.
- Final persistent GPU archived keyframe payload was 0 bytes.
- Final CPU archive was 10,497,024,000 bytes.
- Maximum simultaneous staged payload groups was 1, with 0 live groups at end.
- Peak allocated/reserved GPU memory was 6,774,482,432 / 8,009,023,488 bytes, with no OOM.
- At frame 499, long-lived allocated memory was 2,783,630,848 bytes lower than Phase 3C-6 (75.728%), while the Gaussian-count delta was 1,081 (0.0479%).

This establishes the full-scene online memory result. It does not establish metric equivalence, bit-exact equivalence, or paper-result reproduction.

## 8. Final output availability

The evidence directory contains only:

- `phase4_vb001_full_scene_0_1999.log`;
- `phase4_vb001_full_scene_0_1999_results.json`;
- `PHASE4_VB001_FULL_SCENE_SUMMARY.md`; and
- `pre_run_system_state.log`.

The temporary work directory exists at `/tmp/sgs_phase4_vb001_full_scene_0_1999_output/room0_frames_0_1999_diagnostic/`, but its `eval/` directory is empty. No final or intermediate `.npz`, `.npy`, `.pt`, `.pth`, checkpoint, PLY, or CSV output exists there or in the evidence directory.

The run overrode `save_checkpoints=False`, so the periodic `save_params_ckpt(...)` and `keyframe_time_indices<frame>.npy` path did not execute. At natural completion, the harness replaced `slam.eval` with `blocked_final_eval`, which raised `FullSceneComplete`. This intentionally stopped execution before the subsequent source block that adds `timestep`, intrinsics, camera trajectory, GT trajectory, and keyframe indices to `params`, converts semantic IDs for saving, and calls `save_params(params, output_dir)`.

Consequently, the JSON preserves measurements, shapes, finiteness checks, keyframe IDs, selection traces, and memory data, but not the numerical final Gaussian/map tensors or camera trajectory arrays required to reconstruct and evaluate the final state.

Final output availability:

- final `params.npz`: **NO**;
- map/Gaussian checkpoint: **NO**;
- `keyframe_time_indices`: **recorded as IDs in JSON, but no reloadable checkpoint `.npy`**;
- estimated trajectory/camera parameter values: **NO**;
- Gaussian parameter values: **NO**;
- semantic parameter values: **NO**;
- PLY output: **NO**;
- evaluation output: **NO**.

A future evaluator cannot evaluate this completed run without reconstructing the final state. Since the process has ended and no checkpoint was saved, that requires repeating the 2,000-frame online SLAM run with an explicitly reviewed output-saving boundary. No rerun is required to classify the existing runtime and memory result.

## 9. Is a rerun required?

- To determine whether online frames 0-1999 completed and whether the PHASE4-VB-001 residency/memory objective succeeded: **NO**.
- To run future evaluation against this run's final map and trajectory: **YES**, because the required final numerical state was not saved.

Any such rerun is a separate authorized gate. It must not be treated as an automatic retry of a runtime failure, because the online runtime did not fail.

## 10. Recommended corrected status

Recommended classification: **PASS_RUNTIME_VALIDATOR_BUG**.

Justification:

- `PASS_FULL_SCENE` alone would conceal that the recorded harness validator did not pass and that original evidence still says `FAIL_RUNTIME`.
- `FAIL_RUNTIME` is not supported by the independent runtime evidence; all frames completed, the natural boundary was reached, and no runtime/invariant failure occurred.
- `UNKNOWN` is unnecessary because source semantics and recorded runtime evidence resolve the contradiction.
- `PASS_RUNTIME_VALIDATOR_BUG` accurately preserves both facts: the online full-scene runtime completed successfully, and the harness's final aggregate status was corrupted by an incorrect keyframe expectation. The original evidence must remain unchanged and should be interpreted together with this audit note.

No evaluation, ATE, rendering metrics, semantic metrics, post-SLAM optimization, or paper metrics were run or reproduced.
