# Phase 5 Memory and Runtime Baseline Audit

Status: `VERIFIED` from saved Phase 4 artifacts; no metric was recomputed.
Reference: PHASE4-VB-001 on Replica `room0`, seed 0, 680x1200, frames 0-1999, RTX 5080.

## Provenance rule

The detailed residency run and the output-saving run are separate executions and must not be merged into a synthetic run:

- Detailed run: `results/runtime_artifacts/phase4_vb001_full_scene_0_1999/phase4_vb001_full_scene_0_1999_results.json` (source-run commit `ecb2ae6`).
- Output-saving run: `results/runtime_artifacts/phase4_vb001_minimal_output_save_full_0_1999/` (source-run commit recorded in its `run_metadata.json`).
- Quality evaluation E4: `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/` (saved-state evaluation, not online runtime).
- Canonical synthesis: `results/runtime_artifacts/phase4_closure/` at evidence/pre-closure HEAD `507aea6`; final closure commit is current HEAD `37522db`.

## Existing measurements and gaps

| Resource/component | Existing metric | Evidence | Measurement gap |
|---|---|---|---|
| Completion | Detailed and output-save runs both completed frames 0-1999 without OOM | Detailed JSON; output-save result JSON | No other scene/seed/hardware |
| GPU allocated | Detailed peak 6,774,482,432 B; output-save peak 5,817,509,888 B | Detailed `memory_final`; output-save `memory_summary.json` | No component-attributed curve; runs have different instrumentation |
| GPU reserved | Detailed peak 8,009,023,488 B; output-save peak 7,189,037,056 B | Same sources | Fragmentation/allocator segment history not captured |
| Archived GPU payload | Detailed persistent archived observation payload 0 B | Detailed `residency_summary` and invariants | `est_w2c` bytes are not separately reported in final summary |
| Temporary staging | 114,404 events; 2,987,317,248,000 B total; peak one group 26,112,000 B; max one live group | Detailed `residency_summary` | H2D latency, bandwidth, per-field timing and cache reuse are `NOT INSTRUMENTED` |
| Gaussian count | Final 4,983,660 in detailed run; 4,956,467 in output-save run | Detailed frame record/closure; output-save checkpoint metadata | Per-attribute bytes and time-series correlation with mapping time absent |
| Gaussian params/aux | Static lower-bound model exists in `docs/repository_understanding/10_memory_architecture.md` | Static audit | Direct runtime byte attribution by tensor/storage is `NOT INSTRUMENTED` |
| Gradients | Existence implied by backward and parameters | Active source | Allocated gradient bytes by stage are `NOT INSTRUMENTED` |
| Optimizer state | Adam active in tracking and mapping | `scripts/slam.py:181-187,806,956` | State bytes and lifecycle are `NOT INSTRUMENTED` |
| Renderer/autograd | Three renders per `get_loss` plus external buffers | `scripts/slam.py:273-295` | Workspace, saved tensors and kernel time are `NOT INSTRUMENTED` |
| CPU archive | Detailed final/peak 10,497,024,000 B across 402 keyframes | Detailed `residency_summary` | Metadata/storage allocator overhead and per-field distribution absent |
| Mean payload | 26,112,000 B per complete keyframe (= 10,497,024,000 / 402) | Exact detailed totals | Distribution is expected constant here but was not persisted per field/frame |
| Archive growth | 402 events; fixed cadence plus terminal frame | Detailed `archive_events`; source | Rate per wall time and projected capacity thresholds not formalized |
| Process RSS/HWM | Detailed max RSS 13,529,231,360 B; HWM 13,583,106,048 B. Output-save HWM 17,960,493,056 B | Detailed `process_memory_summary`; output-save memory summary | RSS attribution to archive vs Python/native/allocator is unavailable |
| Total runtime | Detailed 22,299.7076 s; output-save authoritative online wall 14,173.4752 s | Detailed `run_seconds`; output-save `timing_summary.json` | Instrumentation overhead prevents direct comparison between the two |
| Tracking | Output-save avg 74.5413 ms/iteration, 2.980924 s/frame, 79,960 iterations, 1,999 frames; reciprocal 0.335466 frame/s | Output-save `timing_summary.json` | Timers use `time.time()` without explicit CUDA synchronization; render/backward/step split absent |
| Mapping | Output-save avg 66.4294 ms/iteration, 3.986144 s/frame, 120,000 iterations, 2,000 frames; reciprocal 0.250869 frame/s | Same | Selection, staging, render, backward, prune and optimizer split absent |
| Overall throughput | 0.14110865 FPS for 2,000 frames / 14,173.4752 s | Same | Must not be compared with differently instrumented run |
| Serialization | 9.39246 s in output-save run | Same | Per-array copy/write bytes and storage throughput absent |
| Keyframe selection | Selected IDs/windows captured in detailed harness | Detailed JSON | Isolated latency and scaling with keyframe count are `NOT INSTRUMENTED` |
| Pruning | 120,000 hook calls, 4,000 active checks, 1,015,972 removed | Detailed `totals` | Active/no-op elapsed and transient allocation absent |
| Densification | 0 calls; disabled | Detailed `totals`; Replica config | No gap for V0; future variants must retain disabled state unless separately studied |

## Baseline failure context

The unchanged released baseline completed frames 0-1293, then failed with CUDA OOM during mapping frame 1294. Its observed peak was 13,602,712,064 B allocated and 15,843,983,360 B reserved, with 6,763,024,576 B of archived GPU payload at 259 keyframes. The run lasted 8,089.096 s to failure. These figures are capacity evidence, not a matched full-scene speed or final-memory comparison, because the baseline did not reach frame 1999.

## Quality baseline from E4

E4 evaluated the saved VB001 state with the released training-view protocol: 401 sampled image frames and all 2,000 trajectory poses.

| Metric | Saved result | Definition caveat |
|---|---:|---|
| ATE Mean | 0.002740748680388891 m | `evaluate_ate` returns mean Horn-aligned translation norm (`utils/eval_helpers.py:161-178`), though released output calls it RMSE |
| ATE RMSE | 0.003398270593244735 m | Supplementary true RMSE computed by the E4 harness over the same aligned errors; not implemented in released evaluator |
| PSNR | 33.313067015269745 dB | Released masked training-view protocol |
| MS-SSIM | 0.9794702553689628 | `pytorch_msssim.ms_ssim`; some released labels say SSIM |
| LPIPS-Alex | 0.06755526393577642 | Clamped [0,1] inputs |
| Depth L1 | 0.004951576771391114 m | Mean absolute error; source's separate `rmse` algebra reduces to absolute error before averaging and is not true depth RMSE |
| Semantic-color mIoU | 0.9165854801076707 | GT-frame-palette-assisted color snapping, not fixed-ID categorical accuracy |

There is no completed baseline checkpoint, so baseline full-scene quality and a baseline-vs-V0 quality delta are unavailable.

## Conclusions for Phase 5

`VERIFIED`: Phase 4 solved the observed persistent keyframe-payload VRAM failure on one scene. `VERIFIED`: it shifted 10.497 GB to host memory and caused nearly 2.987 TB of cumulative synchronous staging traffic in the detailed run. `NOT INSTRUMENTED`: transfer time, renderer time, backward time, optimizer time, component-level GPU memory, and archive-attributed RSS. These gaps define P5-G2; they do not confirm H1-H4.
