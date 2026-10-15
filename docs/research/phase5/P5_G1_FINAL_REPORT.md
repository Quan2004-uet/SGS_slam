# SGS-SLAM Phase 5 — Gate P5-G1 Final Report

============================================================
SGS-SLAM PHASE 5 — GATE P5-G1 REPORT
============================================================

## 1. REPOSITORY STATE

Branch: `phase4-vb-001-cpu-keyframe-offload`
HEAD: `37522db553ff18b96592073f9de699db7fa48600`
Working tree before P5-G1: only untracked `vds`; read-only inspection identified it as a Phase 4 visualization JSON record and it was not touched.
Working tree after P5-G1: `vds` plus new documentation under `docs/research/phase5/`; no source/config/artifact change.
Phase 4 closure: `VERIFIED` — `PASS_PHASE4_CLOSURE`; closure evidence was synthesized at `507aea6` and committed by current HEAD `37522db`.
Phase 5 initial status: canonical state said `PLANNED / NOT STARTED`; this explicit task starts and completes design Gate P5-G1 only. P5-G2 has not started.

## 2. SGS-SLAM ARCHITECTURE

Tracking: 40 default render/loss/backward/Adam iterations per non-initial frame; new tracking optimizer per frame (`scripts/slam.py:798-887`).
Keyframe insertion: frame 0, every fifth frame, plus `num_frames-2`, valid-pose guarded (`scripts/slam.py:1059-1077`).
Keyframe mapping selection: GPU overlap scoring over archived poses, random candidate permutation, then last keyframe/current frame (`utils/keyframe_selection.py:40-110`; `scripts/slam.py:931-953`).
CPU archive: four observation payloads copied to persistent pageable CPU storage; `est_w2c` remains GPU (`scripts/slam.py:513-526`).
H2D staging: one selected archived payload synchronously copied with `non_blocking=False`, then references deleted after the iteration (`scripts/slam.py:529-541,967-1029`).
Gaussian representation: GPU trainable geometry/RGB/opacity/scale/semantic colors, fixed semantic IDs, pose arrays and auxiliaries (`scripts/slam.py:133-178`).
Optimizer: frame-local tracking and mapping Adam; mapping moments and gradients scale with Gaussian state.
Densification/pruning: pixel-driven append and active pruning; gradient clone/split densification exists but is disabled in the Replica online config.

## 3. EXISTING BASELINE EVIDENCE

Full-scene frames: V0 completed 0-1999; released baseline completed 0-1293 and OOMed mapping frame 1294.
CPU archive: 10,497,024,000 B at 402 keyframes (detailed V0 run).
GPU allocated/reserved: detailed V0 peaks 6,774,482,432 / 8,009,023,488 B.
Gaussians: 4,983,660 detailed run; 4,956,467 separate output-save run.
Runtime: 22,299.7076 s detailed run; 14,173.4752 s separate authoritative output-save online run. These are not combined or compared as like-for-like.
ATE Mean: 0.002740748680388891 m, released Horn-aligned mean.
ATE RMSE: 0.003398270593244735 m, supplementary true RMSE.
PSNR: 33.313067015269745 dB.
MS-SSIM: 0.9794702553689628.
LPIPS: 0.06755526393577642 (AlexNet).
Semantic mIoU: 0.9165854801076707, released GT-palette-assisted semantic-color protocol.
Depth L1: 0.004951576771391114 m.

## 4. BOTTLENECK VISIBILITY

Transfer instrumentation: bytes/events measured (114,404 events; 2.987 TB cumulative), latency `NOT INSTRUMENTED`.
Tracking instrumentation: aggregate source wall timers exist; component GPU time and reliable synchronized e2e split are `NOT INSTRUMENTED`.
Mapping instrumentation: aggregate timers exist; selection/H2D/render/backward/prune/step split is `NOT INSTRUMENTED`.
Gaussian memory attribution: count and static model exist; runtime field/gradient/aux allocation is `NOT INSTRUMENTED`.
Optimizer memory attribution: `NOT INSTRUMENTED`.
CPU memory attribution: logical archive and process RSS/HWM exist; metadata/field/RSS attribution is partial.

## 5. DATASET READINESS

Available scenes: room0, room1, room2, office0-office4.
Verified complete scenes: eight have structurally complete 2,000-frame RGB/depth/semantic-ID/semantic-color/pose layouts with continuous endpoints, nonzero modality files and valid pose field counts; only room0 is runtime validated.
Missing scenes: apartment_0/1/2, frl_apartment_0/4 listed by config; local ScanNet/ScanNet++ absent.
Large-scene readiness: `BLOCKED`; no 10k-50k-frame dataset. Repetition/concatenation is not valid evidence.
Dataset blockers: per-scene immutable profiling configs absent; seven scenes need bounded decode/runtime validation; long-horizon dataset absent.

## 6. PROPOSED VARIANTS

V0: validated unchanged Phase 4 CPU keyframe offload reference.
V1: V0 + bounded GPU keyframe cache; independently branched/tested.
V2: V0 + RAM/SSD hierarchical keyframe archive; independent of V1.
V3: V0 + spatial Gaussian submapping; initially excludes V1/V2.
V4: V3 + budgeted mapping, with equal-budget geometric-only and semantic-aware controls.
V5: integrate only independently passed V1/V2/V3/V4 modules.

## 7. RESEARCH HYPOTHESES

H1: synchronous repeated staging is a material critical-path cost; unconfirmed.
H2: linear CPU archive growth crosses practical RAM budgets at target horizons; unconfirmed.
H3: Gaussian/gradient/optimizer/render growth dominates GPU/mapping scalability; unconfirmed.
H4: mapping spends material time on redundant low-utility work; unconfirmed.
H5: independently validated modules form a better multi-resource/quality Pareto system; unconfirmed.

## 8. PHASE 5 GATES

P5-G1: source/evidence/dataset audit and design — complete.
P5-G2: implement measurement-only, disabled-by-default profiling and CPU/static tests — next, not started.
P5-G3: room0 0-99 then 0-499 equivalence, overhead and bounded profiles — not started.
P5-G4: fixed-protocol full/multi-scene profiles after bounded scene gates — not started.
P5-G5: calibrated bottleneck decision selecting exactly one first variant — not started.

## 9. DOCUMENTATION CREATED

Paths:

- `docs/research/phase5/SGS_SLAM_RUNTIME_ARCHITECTURE_AUDIT.md`
- `docs/research/phase5/PHASE5_MEMORY_RUNTIME_BASELINE_AUDIT.md`
- `docs/research/phase5/PHASE5_PROFILING_INSTRUMENTATION_PLAN.md`
- `docs/research/phase5/PHASE5_MULTI_SCENE_DATASET_AUDIT.md`
- `docs/research/phase5/PHASE5_RESEARCH_HYPOTHESES.md`
- `docs/research/phase5/PHASE5_VARIANT_ABLATION_MATRIX.md`
- `docs/research/phase5/PHASE5_EVALUATION_PROTOCOL.md`
- `docs/research/phase5/PHASE5_EXECUTION_PLAN.md`
- `docs/research/phase5/P5_G1_FINAL_REPORT.md`

## 10. OPEN RISKS

1. Current `time.time()` regions do not reliably isolate asynchronous GPU work; profiling overhead/synchronization can perturb results.
2. V0 trades VRAM for 10.497 GB host archive and 2.987 TB staged traffic on room0; dominance of either cost is not yet measured.
3. Multi-scene layouts exist but runtime generalization is untested, and no large-scene/10k-50k dataset exists locally.
4. External rasterizer workspace cannot be perfectly attributed with PyTorch tensor inventories alone.
5. Canonical project-management files still describe Phase 5 as planned because P5-G1 was instructed not to overwrite existing documents; reconcile them only in an authorized handoff/documentation update.

## 11. NEXT PRIMARY TASK

Task: **P5-G2 — implement profiling instrumentation only**, from a new approved branch based on `37522db`, with profiling disabled by default.
Files expected to change: a new telemetry utility/schema and tests; minimal hooks in `scripts/slam.py`; possibly loader timing hooks that preserve return behavior; new immutable profiling configs. No algorithm/default config mutation.
Measurement design: `off/light/detailed`; perf-counter CPU dispatch, sampled synchronized e2e, batched CUDA events, unique-storage memory attribution, RSS/HWM, archive/staging bytes and deterministic JSONL.
Validation: CPU unit/static tests in P5-G2; actual 0-99 CUDA equivalence/overhead belongs to separately authorized P5-G3.
Completion criteria: schema-valid telemetry, disabled path has no RNG/tensor/schedule changes, hooks cover the documented gaps, deterministic sampling, and bounded-run protocol is executable without design ambiguity.

## 12. FINAL GATE STATUS

`PASS_P5_G1_DESIGN_READY`

P5-G2 through P5-G5 were not executed. No CUDA workload, online SLAM, new experiment, source/config edit, checkout, commit, push, download, or artifact mutation occurred.

============================================================
