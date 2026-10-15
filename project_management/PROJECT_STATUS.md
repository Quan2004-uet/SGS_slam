# SGS-SLAM Project Status

> **CURRENT PROJECT-STATE AUTHORITY.** Repository/source/config/runtime evidence has highest priority. This file defines the current phase; use `SESSION_HANDOFF.md` for the exact resume point.

Last reconciled: 2026-10-16.

## Project Identity

- Repository: SGS-SLAM — Semantic Gaussian Splatting for Neural Dense SLAM.
- Branch: `phase5-profiling-instrumentation`.
- Phase 4 reference HEAD: `37522db553ff18b96592073f9de699db7fa48600`.
- Phase 5 P5-G1 checkpoint HEAD: `86ac4f990932563c721187a5cb458f3e07be9ce6`.
- Experimental evidence / pre-closure-commit HEAD: `507aea652a5da15c92d358c19b8d6705c510242b`.
- Current implementation HEAD: `302e3e6bf46d50ea96b010eb5988dfd6616c2317` (`fix(profiler): prevent CUDA event queue overflow`).
- Latest session handoff checkpoint: `b30d5a622152e66d14ed2fd94b0a6f86a073eb1d` (P5-LEAN session handoff checkpoint).
- Released baseline: `e4183986204242a8bb422624618af07780a49d26` (`main`).
- Dataset/config: Replica `room0`, `configs/replica/slam.py`, seed 0.

## Current Phase

- Phase 4 — CPU Keyframe Offload / Reproducible Memory Baseline Variant: **COMPLETE**.
- Variant `PHASE4-VB-001`: **COMPLETE / VALIDATED**.
- Closure status: `PASS_PHASE4_CLOSURE`.
- Original Phase 5 — Multi-Scene Validation & Performance Profiling: **SUPERSEDED_BY_P5_LEAN_INCOMPLETE** (technical completion `NOT_ACHIEVED`).
- P5-G1: `PASS_P5_G1_DESIGN_READY`.
- P5-G2: `PASS_P5_G2_CPU_STATIC`; implementation is committed at `0118d2cf` and FIX1 at `302e3e6`.
- P5-G3A retry 1 (room0 0–99): `BLOCKED_P5_G3A_RETRY1`; CUDA environment recovery is `PASS_P5_G3A_CUDA_ENV_RECOVERED`. C0/C1/C2 completed the horizon, but detailed telemetry dropped 1,958 CUDA event spans, so the zero-drop gate failed.
- P5-G3A-FIX1 profiler preflight: `PASS_P5_G3A_FIX1_PREFLIGHT`; queue overflow repair passed CPU tests and bounded synthetic CUDA validation. No new SLAM run was authorized.
- P5-G3A-R2 precheck (room0 0–10): `BLOCKED_P5_G3A_R2`; OFF-A/OFF-B differed by 644 final Gaussians, so LIGHT/DETAILED were not run.
- P5-G3A-R3: **NOT_EXECUTED**.
- P5-G3B (0–499): **NOT_EXECUTED**.
- Multi-scene profiling and final bottleneck decision: **NOT_EXECUTED / INCONCLUSIVE**.
- P5-LEAN: **IN PROGRESS**; `P5-LEAN-001` is `PASS_P5_LEAN_001_21DAY_DESIGN_READY`.
- Three-week execution window: 2026-10-15 through 2026-11-05; code/config freeze target 2026-10-28.
- Selected candidate: novelty-aware Budget-Aware Mapping using pre/post append Gaussian counts; **DESIGNED, NOT IMPLEMENTED OR VALIDATED**.
- Next task: `P6-BAM-001 — Novelty-Aware Budgeted Mapping Minimal Implementation & CPU Validation`, `PLANNED_NOT_STARTED` pending researcher review.
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

## P5-LEAN Status

P5-G1 established the audit, dataset-readiness, instrumentation, hypothesis, ablation, evaluation, and execution contracts in `docs/research/phase5/`. P5-G2 added disabled-by-default `off`, `light`, and `detailed` profiling, bounded JSONL/summary telemetry, CPU/GPU-memory attribution helpers, and minimal hooks around the existing online path. Twenty CPU-only tests pass with CUDA hidden and uninitialized. Direct-host recovery using `/home/robot/miniconda3/envs/sgs_slam_5080` passed the CUDA smoke test. Retry 1 completed C0/C1/C2 on room0 frames 0–99; C1 had zero dropped spans, while C2 had zero pending events but 1,958 dropped CUDA event spans. Logged keyframe traces matched, but final Gaussian counts were not bit-exact. Detailed timing is therefore diagnostic, not gate-valid.

No optimization variant V1–V5 has been implemented. The original Phase 5 execution plan remains administratively retired and its historical gates are unchanged. P5-LEAN-001 completed the mapping-loop audit, selected a novelty-aware tiered mapping-budget hypothesis, and defined lean profiling, evaluation, ablation, schedule and implementation contracts. Comprehensive DETAILED profiling remains deferred. Core quality obligations and the additional-scene priority remain in force.

## STOPPED HERE

Stop at `PASS_P5_LEAN_001_21DAY_DESIGN_READY`. Budget-Aware Mapping is not implemented or validated. P6-BAM-001 must use the dedicated `results/runtime_artifacts/phase6_bam/` root and immutable run IDs. Do not reopen G3A retry loops, run any horizon, start P6-BAM-001, implement keyframe reuse, or push without separate researcher authorization.
