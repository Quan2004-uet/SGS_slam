# SGS-SLAM Project Status

> **CURRENT PROJECT-STATE AUTHORITY.** Repository/source/config/runtime evidence has highest priority. This file defines the current phase; use `SESSION_HANDOFF.md` for the exact resume point.

Last reconciled: 2026-10-22.

## Project Identity

- Repository: SGS-SLAM — Semantic Gaussian Splatting for Neural Dense SLAM.
- Branch: `phase5-profiling-instrumentation`.
- Phase 4 reference HEAD: `37522db553ff18b96592073f9de699db7fa48600`.
- Phase 5 P5-G1 checkpoint HEAD: `86ac4f990932563c721187a5cb458f3e07be9ce6`.
- Experimental evidence / pre-closure-commit HEAD: `507aea652a5da15c92d358c19b8d6705c510242b`.
- Profiler FIX1 implementation ancestor: `302e3e6bf46d50ea96b010eb5988dfd6616c2317`.
- P6-BAM-001 FIX1 implementation source: `a3aefc745b73da520fa2ae53e77b0349fd25fa00`; P6-BAM-003 execution HEAD: `bb830b1f6a0a31028f14fe390b8cb4e1a50c47fe` (P6-BAM-002 documentation-only descendant).
- P6-BAM-001 start HEAD: `c6742854b884495ece0cc18fbc9296c1d5e31371`; implementation checkpoint is the commit containing `docs/research/phase6_bam/P6_BAM_001_IMPLEMENTATION_REPORT.md`.
- Released baseline: `e4183986204242a8bb422624618af07780a49d26` (`main`).
- Dataset/config: Replica `room0`, `configs/replica/slam.py`, seed 0.

## Current Phase

- Phase 4 — CPU Keyframe Offload / Reproducible Memory Baseline Variant: **COMPLETE**.
- Variant `PHASE4-VB-001`: **COMPLETE / VALIDATED**.
- Closure status: `PASS_PHASE4_CLOSURE`.
- Phase 4 Replica full-scene inventory: closure/evaluation records exist for room0, room1, room2, and office0–office4 (eight scenes total). Optional 3D visualization remains `DEFERRED_OPTIONAL` where stated in the per-scene reports.
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
- Phase 7 BCGM: researcher-selected proposed direction; `PLANNED_NOT_IMPLEMENTED`. Source implementation and validation are `NOT_VERIFIED`; Phase 7 is not ACTIVE and no implementation or experiment is authorized by this status entry.
- P6-BAM-001: `PASS_P6_BAM_001_CPU_STATIC`; novelty-aware controller and dedicated controls are implemented but **NOT_RUNTIME_VALIDATED**.
- P6-BAM-001 FIX1: `PASS_P6_BAM_001_FIX1_CPU_STATIC`. Source audit found the reported cross-event budget leak absent at `e644df4`; configured/effective iteration names are now explicit, with a 38-test CPU regression gate. **NOT_RUNTIME_VALIDATED**.
- P6-BAM-002: `PASS_P6_BAM_002_SMOKE_INTEGRATION`, `ADAPTIVE_ACTIVATION_CONFIRMED` on two matched LIGHT Replica room0 runs, frames 0–10. This is bounded runtime integration only, not full-scene, speedup or quality validation.
- P6-BAM-003: `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME`. Both matched LIGHT room0 runs completed frames 0–49 with valid budgets, finite saved state and isolated artifacts. V-A executed 1,740 versus V0 3,000 mapping iterations, but preliminary matched evaluation showed PSNR −0.739 dB and Depth L1 +19.26%, exceeding provisional P5-LEAN quality targets. A single pair cannot establish causality or non-inferiority.
- P6-BAM-003-R1 V-A2: `PASS_P6_BAM_003_R1_QUALITY_CONSTRAINED_0_49` as candidate screening only. One matched-protocol V-A2 run completed frames 0–49 with 2,445/3,000 iterations (1 FULL/12 MID/37 LOW), finite state and isolated output. All seven researcher-defined 15% checks pass versus saved V0; whole-process wall decreased 11.33%. The historical 0.5 dB provisional P5 PSNR margin is narrowly exceeded (−0.50164 dB), online-wall target remains unmeasured, and no statistical/full-scene quality or speedup claim is made. Original P6-BAM-003 remains INCONCLUSIVE.
- P6-BAM-005: `PASS_P6_BAM_005_0_499_QUALITY_CONSTRAINED` for one matched LIGHT pair on room0 frames 0–499. V0/V-A2 completed all 500 frames; V-A2 executed 22,695 versus V0 30,000 mapping iterations (−24.35%), measured online-loop wall decreased 15.33%, and all seven researcher-defined 15% quality screens plus the historical P5 quality margins pass on matched final-map metrics. The older ≥20% online-wall target is missed. This remains a single-pair bounded result, not statistical non-inferiority or full-scene validation; details are in `docs/research/phase6_bam/P6_BAM_005_0_499_REPORT.md` and comparison.
- P6-BAM-006 full-scene V-A2: `PASS_P6_BAM_006_FULL_SCENE_QUALITY_CONSTRAINED` for one authorized Replica room0 frames 0–1999 run. All frames completed; checkpoint-first NPZ/PLY saving and CPU integrity checks passed; the same-source E4 evaluator completed 401 views and all-2000-pose ATE; all seven 15% quality screens pass against stored Phase 4 E4 values; RGB and learned-semantic-color 3D visualization passed. Online wall was 12,383.451 s, but full-scene runtime speedup remains unverified because no matched full-scene V0 exists and Phase 4 process timing has a different scope. This is single-run execution/quality screening, not statistical non-inferiority. See the P6-BAM-006 reports and isolated runtime evidence.
- Three-week execution window: 2026-10-15 through 2026-11-05; code/config freeze target 2026-10-28.
- Selected candidate: novelty-aware Budget-Aware Mapping using pre/post append Gaussian counts; V-A2 passed the 0–49 screen and the matched 0–499 bounded quality/runtime gate. Statistical non-inferiority and full-scene behavior remain unvalidated; the 20% historical online-wall target was not met in P6-BAM-005.
- P6-BAM-006 publication/closure: the original Phase 6 3D visualization, the Phase 4 V1 camera-matched package, and the Phase 4 V2/V3A extended camera-family package are inventoried and validated. The reviewed checkpoint is published on GitHub research branch `phase5-profiling-instrumentation` at `7454f170f3ece83b38f2429a43084ff550cf49a2`; the visualization-only backup is independently verified on the private Hugging Face dataset. Neither publication changes the experiment result.
- Phase 4 multi-scene extension — Replica `room1`: `CLOSED_EVALUATED` for run `p4_vb001_room1_full_0_1999_r01` at frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06`. Online 2,000/2,000 frames, process exit 0, 6,663,167 Gaussians, 402 keyframes; offline `PASS_OFFLINE_EVALUATION` with 401 E4 image views, 2,000-pose trajectory, and supplementary true Depth RMSE. Optional 3D visualization is `DEFERRED_OPTIONAL`. Exact metrics, SHA256 values, scope qualifications, and paths: `docs/research/phase4_multiscene/PHASE4_ROOM1_FINAL_RESULTS.md` and its linked runtime evidence. Phase 4 room0 remains a separate result.
- Phase 4 multi-scene extension — Replica `room2`: `CLOSED_EVALUATED` for run `p4_vb001_room2_full_0_1999_r01` at the same frozen source. Online exit 0, 2,000/2,000 validated frames, 5,587,273 Gaussians, 402 keyframes; offline `PASS_OFFLINE_EVALUATION` covers 401 E4 views, 2,000 trajectory poses, and supplementary standard Depth RMSE. Checkpoint SHA256 `d772e65a3c0bc163cf20960d30bd0b88f9182477462f9c1fe8dadd0a86155c3f`; CRC PASS. E4 process exit code was not retained. Optional 3D visualization is `DEFERRED_OPTIONAL`. Exact metrics and paths: `docs/research/phase4_multiscene/PHASE4_ROOM2_FINAL_RESULTS.md`. Subsequent entries below record closure of office0–office4; the eight-scene Replica inventory is complete.
- Phase 4 multi-scene extension — Replica `office0`: `CLOSED_EVALUATED` for run `p4_vb001_office0_full_0_1999_r01` at frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06`. Online exit 0, 2,000/2,000 frames; checkpoint `PASS_CHECKPOINT_VALIDATION`, CRC PASS, SHA256 `6d0f180d7677a38c29295ae9ffc10d745f726aac700f40338543a062a9bf7390`; 6,088,334 Gaussians and 402 keyframes. Offline `PASS_OFFLINE_EVALUATION` and final integrity `PASS_FINAL_INTEGRITY_VALIDATION`: 401 E4 views, 2,000 trajectory poses, 401 supplementary standard Depth RMSE records, and 1,612/1,612 original E4 manifest files unchanged. E4 exit code/stdout/stderr were not retained. Optional 3D visualization is `DEFERRED_OPTIONAL`. Exact metrics and evidence: `docs/research/phase4_multiscene/PHASE4_OFFICE0_FINAL_RESULTS.md`. Subsequent entries below record closure of office1–office4; the eight-scene Replica inventory is complete.
- Phase 4 multi-scene extension — Replica `office1`: `CLOSED_EVALUATED` for run `p4_vb001_office1_full_0_1999_r01`, frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06`. Online `CORE_ARTIFACTS_VALIDATED`, 2,000/2,000 frames, exit 0; checkpoint `PASS_CHECKPOINT_VALIDATION`, CRC PASS, SHA256 `f2bcf577a62655929b066ea0ce05148f64ded7509c27eba88002f5090490704b`; 5,549,520 Gaussians and 402 keyframes. Offline `PASS_OFFLINE_EVALUATION`; final integrity `PASS_FINAL_INTEGRITY_VALIDATION`, including 401 E4 views, 2,000 trajectory poses, 401 supplementary standard Depth RMSE records, and 1,612/1,612 original E4 manifest files unchanged. Optional 3D visualization is `DEFERRED_OPTIONAL`. Exact metrics and evidence: `docs/research/phase4_multiscene/PHASE4_OFFICE1_FINAL_RESULTS.md`. Subsequent entries below record closure of office2–office4; the eight-scene Replica inventory is complete.
- Phase 4 multi-scene extension — Replica `office2`: `CLOSED_EVALUATED` for run `p4_vb001_office2_full_0_1999_r01` at frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06` (`scripts/slam.py` SHA256 `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3`). Online `CORE_ARTIFACTS_VALIDATED`, 2,000/2,000 frames, exit 0; checkpoint `PASS_CHECKPOINT_VALIDATION`, CRC PASS, SHA256 `7508fc2a3fb6916dd6211221b75693ae868b97b3b830bb1fac9227a5e697726d`; offline `PASS_OFFLINE_EVALUATION`; final integrity `PASS_FINAL_INTEGRITY_VALIDATION`. Evidence covers 401 E4 views, 2,000 trajectory poses, 401 supplementary standard Depth RMSE records, and 1,612/1,612 original E4 manifest files unchanged. Optional visualization `DEFERRED_OPTIONAL`; see `docs/research/phase4_multiscene/PHASE4_OFFICE2_FINAL_RESULTS.md`. The subsequent Office4 entry records closure; the eight-scene Replica inventory is complete.
- Phase 4 multi-scene extension — Replica `office3`: `CLOSED_EVALUATED` for run `p4_vb001_office3_full_0_1999_r01` at frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06` (`scripts/slam.py` SHA256 `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3`). Online `CORE_ARTIFACTS_VALIDATED`, 2,000/2,000 frames, process exit 0; checkpoint `PASS_CHECKPOINT_VALIDATION`, CRC PASS, SHA256 `2c5c30a16ac179d4be37e2ca622945d72c8b16993f4378c331a566349b6ca26c`; 5,116,198 Gaussians and 402 keyframes. Offline evidence independently reconciled as `PASS_OFFLINE_EVALUATION`; final integrity `PASS_FINAL_INTEGRITY_VALIDATION`, with 401 E4 metric views, 2,000 trajectory poses, 401 supplementary standard Depth RMSE records, and 1,612/1,612 original E4 manifest files unchanged. E4 process exit code was not recorded. Optional 3D visualization is `DEFERRED_OPTIONAL`. Exact metrics/evidence: `docs/research/phase4_multiscene/PHASE4_OFFICE3_FINAL_RESULTS.md`. The subsequent Office4 entry records closure; the eight-scene Replica inventory is complete.
- Phase 4 multi-scene extension — Replica `office4`: `CLOSED_EVALUATED` for run `p4_vb001_office4_full_0_1999_r01` at frozen source `68f9060f7ff4d8d141be1d5f71339401327edd06` (`scripts/slam.py` SHA256 `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3`). Online `CORE_ARTIFACTS_VALIDATED`, 2,000/2,000 frames, process exit 0; checkpoint `PASS_CHECKPOINT_VALIDATION`, NPZ CRC PASS, SHA256 `5ad2f28b79a8e1868fcb3ab6dc234f867e8ceeba03e0a5a974e59383f7f9263c`; 5,244,062 Gaussians and 402 keyframes. Offline arrays, supplementary Depth RMSE, 2,000-pose trajectory, and final integrity pass; all 1,612 original E4 manifest entries match. Optional visualization is `DEFERRED_OPTIONAL`. See `docs/research/phase4_multiscene/PHASE4_OFFICE4_FINAL_RESULTS.md` and `PHASE4_OFFICE4_OFFLINE_EVALUATION_REPORT.md`. No Phase 4 Replica experiments remain in the eight-scene inventory (room0 was evaluated in the original Phase 4 record; Room1/Room2 and Office0–Office3 have prior records). This does not change Phase 5/6/7 state.
- Phase 4 versus Phase 6 qualitative comparison and thesis packaging was completed in SESSION_021. The independent P5-LEAN workstream remains `IN PROGRESS`; resume it from its canonical records. No additional SLAM, tracking, mapping, evaluation, visualization, variant, or scene is authorized automatically. P6-BAM-004 remains `PLANNED_NOT_STARTED` and requires separate researcher authorization.
- SESSION_021 closed after P6-BAM-007 Gate 5C final backup acceptance. Gate 0–3: PASS; Gate 4: PASS_WITH_LIMITATIONS; Gate 5A: PASS_TECHNICAL_FREEZE; Gate 5B: PASS_REMOTE_VERIFIED; Gate 5C: PASS_FINAL_CLOSURE. GitHub commit `f3f0e508c8feccd302c7ec5acede4f8935654829`; private Hugging Face revision `f5a53f74901dbe09329471009be92356c32fa901`. Laptop backup was researcher-reported at `/home/quan/research/SGS_slam_backups/P6-BAM-007/final_package/`, with 86 physical files, 84 inventory items, 47,535,429 payload bytes and 85/85 SHA256 checks passing. Final closure evidence: `results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate5c_final_closure/run_01/`. This closes SESSION_021 only; P5-LEAN remains an independent active workstream.
- Supplemental completed experiment record: Phase 6 V-A2 Replica/room1 run `p6_bam_ms_room1_gate3_0_1999_r01`, frozen source `002927f3b24dd69418c17da08bd4ae987bae9ee2`, frames 0–1999. Gate 4 **PASS**, Gate 5 **PASS**, overall `ROOM1_GATE5_CLOSED_QUALIFIED`. Official saved results: 2,000 frames; 6,682,135 final Gaussians; 402 keyframes; PSNR 34.096186264494705 dB; MS-SSIM 0.9714362002964924; LPIPS-Alex 0.09135246086410453; Depth L1 0.004393707946328413 m; semantic-color mIoU 0.9265354206849918; released ATE Mean 0.004655330867990601 m; supplementary true ATE RMSE 0.004802019103114381 m. Process wall 16,075.75 s / 0.124411 FPS; peak PyTorch allocated/reserved 9.521/11.654 GiB; peak process RSS 18.234 GiB. Device-wide NVML VRAM peak and separate Gate 5 runtime are NOT_MEASURED; CUDA-event timing is unvalidated. Saved “Depth RMSE” is MAE, semantic-color mIoU is GT-palette-assisted, and runtime effective config adds three frozen inactive/default fields absent from its pre-run serialization lock without changing approved V-A2 settings. Gate 4 checksums 7/7, artifact-manifest entries 1,623/1,623, Gate 5 checksums 1,614/1,614, frozen source checksums 17/17, and CPU artifact integrity PASS. Artifacts are retained locally on the GPU server at `results/runtime_artifacts/phase6_bam/`; no file was moved or removed. GitHub publication: `NOT_REQUESTED`; Hugging Face upload: `NOT_REQUESTED`. Full report: `docs/experiments/PHASE6_MULTISCENE_ROOM1_GATE5_FINAL_REPORT.md`; preserve the archive plan and local inventory for later review. Replica/room2 preparation is `PLANNED_NOT_STARTED`, pending separate researcher authorization and dataset/config/source-lock/resource/output-isolation preflight; no room2 run is authorized. This supplemental record does not change the independent active P5-LEAN workstream or close any session.
- Full-scene limitations remain: matched runtime speedup is unverified; the controller selected LOW/45 for 1,987/2,000 events, so superiority over fixed-45 mapping is unestablished. The quality result is a single-run 15% screen, not statistical non-inferiority. `seg_params.ply` is learned semantic-color visualization, not a categorical-ID PLY or per-pixel semantic predictor.
- Canonical closure package: `results/runtime_artifacts/phase4_closure/`.

## Local Phase 4 room1 closure addendum — 2026-10-21

Run `p4_vb001_room1_full_0_1999_r01`, Replica room1 frames 0–1999, is
`CLOSED_EVALUATED`. Online run metadata and the 11-entry artifact manifest
validate; checkpoint CRC and current SHA256 pass; offline E4 completed 401
sampled views and all 2,000 trajectory poses; the supplementary standard
Depth RMSE has 401 finite per-frame values. Final status is
`PASS_OFFLINE_EVALUATION`. Optional 3D visualization is
`DEFERRED_OPTIONAL`. This closes only the room1 experiment and does not claim
completion of all eight Replica scenes. See
`docs/research/phase4_multiscene/PHASE4_ROOM1_FINAL_RESULTS.md`.

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

No original Phase 5 optimization variant V1–V5 has been implemented. The original Phase 5 execution plan remains administratively retired and its historical gates are unchanged. P5-LEAN-001 completed the mapping-loop audit and design contracts. P6-BAM-001/FIX1 and P6-BAM-002 retain their historical PASS results. Original P6-BAM-003 remains historically inconclusive. The R1 0–49 screen passed the researcher-defined 15% checks but narrowly missed the historical PSNR margin. P6-BAM-005 completed one matched LIGHT 0–499 pair: V-A2 used 22,695 versus V0 30,000 mapping iterations, online wall decreased 15.33%, and all seven 15% quality checks and historical P5 quality margins passed. The ≥20% historical online-wall target was not met. This is a single-pair bounded observation, not statistical non-inferiority or full-scene evidence. Comprehensive DETAILED profiling remains deferred; further horizon/scene work requires researcher authorization.

## STOPPED HERE

P6-BAM-006 completed one authorized V-A2 run over Replica room0 frames 0–1999. The final model was saved and validated before evaluation; all 2,000 poses and 401 matched E4 views were evaluated, all seven 15% screens passed against stored Phase 4 E4 metrics, and the RGB/learned-semantic-color 3D package passed validation. Evidence is in `docs/research/phase6_bam/P6_BAM_006_FULL_SCENE_REPORT.md`, `P6_BAM_006_FULL_SCENE_COMPARISON.md`, `P6_BAM_006_3D_VISUALIZATION_INVENTORY.md`, and `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/`. Full-scene runtime speedup remains unverified: there is no matched 2000-frame V0, and historical Phase 4 process timing is not comparable to this run's online timer. This is single-run screening evidence, not statistical non-inferiority. Do not execute another SLAM run, P6-BAM-004, or push automatically.
