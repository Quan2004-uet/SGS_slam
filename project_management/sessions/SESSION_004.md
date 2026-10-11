# SESSION_004 — Phase 4 Variant B Full-Scene Validation and State Preservation

## Metadata

- Session ID: SESSION_004.
- Status: CLOSED.
- Started: 2026-10-10.
- Last active: 2026-10-11.
- Closed: 2026-10-11.
- Phase: Phase 4 — Memory-management research variant.
- Variant: `PHASE4-VB-001` — CPU offload of resident keyframe payloads.

Objective: validate full-scene Variant-B memory behavior, resolve the original
full-scene validator contradiction, and preserve a reloadable full-scene final
state with lightweight telemetry, without evaluation or algorithm change.

## Starting State

Phase 3 was closed with the unchanged baseline OOM at frame 1294 and an
allocator-only OOM at frame 1333 on the RTX 5080. PHASE4-VB-001 had passed
bounded gates through frames 0–999. No paper-protocol evaluation had run.

## Work Completed

1. Ran the detailed PHASE4-VB-001 online full scene 0–1999. It completed all
   frames without OOM. The original harness reported `FAIL_RUNTIME` only
   because its expected keyframes omitted the released `num_frames-2` terminal
   condition. The corrected classification is `PASS_RUNTIME_VALIDATOR_BUG`.
2. Audited the validator and preserved the original evidence unchanged.
3. Audited the final save boundary and evaluator ordering.
4. Validated the minimal final-save path with a 0–49 smoke test:
   `PASS_MINIMAL_OUTPUT_SAVE_SMOKE`.
5. Validated lightweight timing/GPU/RSS telemetry with a separate 0–49 smoke:
   `PASS_TELEMETRY_OUTPUT_SAVE_SMOKE`.
6. Ran one authorized minimal full-scene output-save workload over frames
   0–1999 and verified final artifacts and telemetry:
   `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.
7. No evaluation, ATE, image-quality/depth/semantic metrics, post-SLAM
   optimization, or paper-metric reproduction was run.

## Historical Detailed Full-Scene Runtime

- Corrected status: `PASS_RUNTIME_VALIDATOR_BUG`.
- Runtime: 22,299.70758857 s (about 6 h 11 m 40 s).
- Final Gaussians: 4,983,660.
- Logical keyframes: 402.
- CPU archive / GPU archived payload: 10,497,024,000 / 0 B.
- Peak GPU allocated/reserved: 6,774,482,432 / 8,009,023,488 B.
- Detailed residency invariants: PASS.
- Final state from that historical run: not saved because its harness stopped
  before `save_params(...)`.

## Final Output-Saving Result

- Status: `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.
- Frame range: 0–1999; 2,000 frames completed; final frame 1999.
- Runtime: 14,173.47515856901 s (approximately 3 h 56 m 13 s).
- Final Gaussians: 4,956,467.
- Keyframes: 402; tail `[1989, 1994, 1998, 1999]`.
- Tracking/mapping/overall FPS: 0.3354664059815056 /
  0.25086898791330586 / 0.14110865384985266.
- Peak GPU allocated/reserved: 5,817,509,888 / 7,189,037,056 B.
- Process RSS/HWM: 17,960,493,056 B host RAM.
- Final serialization: 9.3924627660017 s.
- Save success / artifact completeness / telemetry completeness: true/true/true.

The minimal harness intentionally omitted heavy per-iteration residency
instrumentation. Its detailed archive/staging residency fields are `UNKNOWN`,
not failed. The historical detailed run remains the evidence for those
invariants.

## Saved State and Provenance

Stable output:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/`

Evidence:
`results/runtime_artifacts/phase4_vb001_minimal_output_save_full_0_1999/`

Result record:
`docs/experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md`

Verified artifacts:

- readable `params.npz`, 322,361,795 B;
- `params.ply`, 337,040,173 B;
- `seg_params.ply`, 337,040,173 B;
- readable `keyframe_time_indices.npy`, 3,344 B;
- timing, memory, run metadata, artifact manifest/checksums, system-state logs,
  runtime log, result JSON, and summary in the evidence directory.

`params.npz` contains Gaussian/map state, estimated camera trajectory, GT
trajectory, intrinsics, `w2c`, timestep, semantic state, keyframe indices, and
original image dimensions. Checksums are recorded in the result document and
runtime manifest.

## Scientific Conclusion

For Replica `room0` on the tested RTX 5080, PHASE4-VB-001 removes the
GPU-memory scalability failure observed in the unchanged Phase 3 baseline,
reaches frame 1999 without GPU OOM, and now preserves a reloadable final state.
The final minimal run peaked at approximately 5.82 GB allocated and 7.19 GB
reserved GPU memory, below the 16.61 GB physical capacity.

This does not establish reconstruction accuracy, paper metrics, or
generalization to other scenes/datasets.

## Evaluation Status

`NOT RUN`. PSNR, SSIM, LPIPS, DepthL1, ATE Mean/RMSE, mIoU, rendering metrics,
semantic metrics, post-SLAM optimization, and paper metrics remain uncomputed.

## STOPPED HERE

Phase 4 Variant B validation and full-scene state preservation are complete.
The next gate is **Evaluation / Export Audit** from the saved `params.npz`.
Do not rerun online SLAM if saved-state loading succeeds.

## Next Gate

Audit, without executing evaluation:

- saved-state loading and required reconstruction;
- RGB/depth/semantic renderer invocation;
- PSNR/SSIM/LPIPS, DepthL1, ATE, and mIoU implementations/protocols;
- frame sampling and GT alignment;
- evaluation/export output directories and provenance.

Stop after the audit for separate evaluation authorization. PHASE4-VB002
runtime optimization remains future work and was not started.

## Constraints Preserved

- No PHASE4-VB-001 source, algorithm, or experiment-config change.
- No pinned memory, non-blocking transfer, persistent GPU cache, or keyframe
  eviction.
- No evaluation, metrics, post-opt, or paper-result claim.
- No large runtime artifact added to regular Git.
