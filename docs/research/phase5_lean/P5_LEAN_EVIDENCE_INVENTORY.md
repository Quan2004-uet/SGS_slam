# P5-LEAN Evidence Inventory

Evidence inspected at commit `1fbde976d9bb534cfc6b19f1bbde758521b24601` on 2026-10-15.

| Evidence | Classification | What it establishes | Limitation |
|---|---|---|---|
| Phase 4 `room0` full-scene detailed run | `VALIDATED_REFERENCE` | 0–1999 complete; no OOM; peak allocated/reserved 6.774/8.009 GB; CPU archive 10.497 GB; 402 keyframes | Detailed runtime 22,299.71 s belongs only to this run |
| Phase 4 output-save run | `VALIDATED_REFERENCE` | 0–1999 complete; 4,956,467 Gaussians; 14,173.48 s; saved checkpoint | Its 5.818/7.189 GB peak must not be merged with the detailed run |
| Phase 4 E4 saved-state evaluation | `VALIDATED_REFERENCE` | ATE mean 0.002741 m, true RMSE 0.003398 m, PSNR 33.313 dB, MS-SSIM 0.97947, LPIPS 0.06756, Depth L1 0.004952 m, semantic mIoU 0.91659 | One scene; released semantic-color protocol; no completed original-baseline comparator |
| P5-G3A initial | `NOT_EXECUTED` | CUDA context failure occurred before C0 | No runtime evidence |
| P5-G3A Retry1 OFF/LIGHT | `COMPLETED_WITH_LIMITATIONS` | 0–99 completed; about 386/385 s; matching logged keyframes; LIGHT had zero event drops | Single run/mode; numerical equality not established |
| P5-G3A Retry1 DETAILED | `INSTRUMENTATION_INVALID` | 0–99 completed and supplied diagnostic wall/resource counters | 1,958 CUDA spans dropped; component GPU totals are incomplete |
| FIX1 | `COMPLETED_WITH_LIMITATIONS` | 23/23 CPU tests; 648 synthetic CUDA spans resolved with zero drops/pending | Preflight only; no online post-FIX1 validation |
| P5-G3A R2 OFF-A/OFF-B | `NUMERICAL_INCONCLUSIVE` | Both 0–10 runs completed with matching structural traces | Final Gaussians differed 879,862 vs 879,218; first divergence unavailable |
| R3, G3B, multi-scene profiling | `NOT_EXECUTED` | No evidence found | No cross-scene or medium-horizon profiling conclusion |

Primary paths: `results/runtime_artifacts/phase4_closure/`, `results/runtime_artifacts/phase5_profiling/p5_g3a_retry1_room0_0_99/comparison/`, and `results/runtime_artifacts/phase5_profiling/p5_g3a_r2_precheck_room0_0_10/comparison/`.
