# SGS-SLAM Project Status

> **CURRENT PROJECT-STATE AUTHORITY.** Repository/source/config/runtime evidence has highest priority. This file defines the current phase; use `SESSION_HANDOFF.md` for the exact resume point.

Last reconciled: 2026-10-14.

## Project Identity

- Repository: SGS-SLAM — Semantic Gaussian Splatting for Neural Dense SLAM.
- Branch: `phase4-vb-001-cpu-keyframe-offload`.
- Experimental evidence / pre-closure-commit HEAD: `507aea652a5da15c92d358c19b8d6705c510242b`.
- Released baseline: `e4183986204242a8bb422624618af07780a49d26` (`main`).
- Dataset/config: Replica `room0`, `configs/replica/slam.py`, seed 0.

## Current Phase

- Phase 4 — CPU Keyframe Offload / Reproducible Memory Baseline Variant: **COMPLETE**.
- Variant `PHASE4-VB-001`: **COMPLETE / VALIDATED**.
- Closure status: `PASS_PHASE4_CLOSURE`.
- Next phase: **PLANNED / NOT STARTED**.
- Canonical closure package: `results/runtime_artifacts/phase4_closure/`.

Phase 4 changed memory ownership, not the SGS-SLAM objective: archived keyframe `color`, `depth`, `semantic_id`, and `semantic_color` payloads are CPU-authoritative and synchronously staged to GPU when selected. Archived `est_w2c` remains GPU-resident. The implementation adds no pinned memory, asynchronous copy, prefetch, persistent GPU cache, compression, or eviction and retains the released keyframe and optimization policies.

## Baseline Limitation and Variant Result

- Unchanged Phase 3 baseline: frames 0–1293 completed; CUDA OOM during mapping at frame 1294 on the tested RTX 5080. Peak allocated/reserved before termination: 13,602,712,064 / 15,843,983,360 B.
- PHASE4-VB-001 detailed full-scene run: frames 0–1999 completed without CUDA OOM; corrected classification `PASS_RUNTIME_VALIDATOR_BUG`. Peak allocated/reserved: 6,774,482,432 / 8,009,023,488 B. Final CPU archive: 10,497,024,000 B. Persistent GPU archived payload: 0 B. Runtime: 22,299.70758857 s under detailed instrumentation.
- Separate authoritative output-save run: `PASS_FULL_OUTPUT_SAVE_TELEMETRY`; 2,000 frames, 402 logical keyframes, 4,956,467 Gaussians, runtime 14,173.47515856901 s, peak allocated/reserved 5,817,509,888 / 7,189,037,056 B.
- Final checkpoint: `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`.

The two variant runs answer different questions and their memory/runtime values must not be merged: the detailed run is the authoritative offload-memory audit; the output-save run is the authoritative saved-state source.

## Validation and Evaluation Chain

- Runtime gates 1 and 2: PASS.
- Gate 3 (0–99), Gate 4 (0–499), Gate 5 (0–999): `PASS_FRAME_LIMIT`.
- Full-scene detailed runtime: corrected `PASS_RUNTIME_VALIDATOR_BUG` after auditing the terminal-keyframe validator.
- Full-scene saved output: `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.
- Evaluation E1–E4: complete; E4 status `PASS_EVAL_E4_FULL_RELEASED`.
- Visualization: `PASS_V1_VISUALIZATION_AUDIT`, `PASS_V2_CAMERA_ALIGNED_QUALITATIVE`, `PASS_V3A_FULL_SCENE_VISUALIZATION_PROOF`, `PASS_V3B_FINAL_PRESENTATION_PACKAGE`, and `PASS_V3C_PRESENTATION_REFINEMENT`.

## Final Released-Protocol Evidence

- Image/depth/semantic protocol: 401 sampled training views; no skipped frames.
- Trajectory: all 2,000 saved poses.
- PSNR: 33.313067015269745 dB.
- MS-SSIM: 0.9794702553689628 (released output calls this SSIM, but implementation computes MS-SSIM).
- LPIPS-Alex: 0.06755526393577642.
- Depth L1: 0.004951576771391114 m.
- Semantic-color mIoU: 0.9165854801076707 under the released GT-palette-assisted recoloring protocol.
- Released Horn-aligned mean relative-w2c translation error: 0.002740748680388891 m; this is not RMSE.
- Supplementary true RMSE over the same aligned errors: 0.003398270593244735 m.
- Canonical evaluation record: `docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md`.

## Scientific Interpretation

`RUNTIME VERIFIED`: CPU-authoritative keyframe observation storage removed the measured persistent GPU archive growth and allowed Replica `room0` frames 0–1999 to complete on the tested 16-GB GPU. The saved reconstruction is loadable, has finite released-protocol metrics, reproduces representative observed views, and has interpretable full-scene geometry, semantic-ID metadata, and trajectory context.

Not established: accuracy equivalence to a full-scene baseline (the baseline did not complete), benchmark-wide superiority, novel-view accuracy, cross-scene generalization, post-SLAM quality, or fixed semantic IDs as released per-pixel predictions.

## Known Limitations

- One Replica scene and one tested GPU configuration.
- CPU archive growth remains proportional to retained payloads; final detailed archive was 10.497 GB.
- Synchronous pageable host-to-device staging; no isolated transfer-time measurement.
- No pinned-memory, asynchronous overlap, prefetch, cache, eviction, compression, or reduced-precision archive.
- Direct full-scene baseline quality comparison is unavailable because the unchanged baseline OOMed.
- Virtual full-scene views are diagnostics, not novel-view accuracy evidence; Gaussian-center views are not continuous surfaces.

## Planned Next Phase

The next phase is planned but not started. First priority is controlled multi-scene validation of the unchanged PHASE4-VB-001 variant. Subsequent, separately gated systems hypotheses are transport optimization (pinned memory, non-blocking copies, streams/prefetch), a bounded reuse-aware GPU cache, and archive compaction. Keyframe eviction is an algorithmic experiment and must remain separate.

## STOPPED HERE

Phase 4 is closed at `PASS_PHASE4_CLOSURE`. Do not resume V3 gates, rerun SLAM/E4, or begin the next phase implicitly. Start a new named session and gate only after explicit authorization.
