# P6-BAM-003 — Matched LIGHT Replica room0 frames 0–49

Date: 2026-10-16. Gate: `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME` (quality concern; structural/runtime integration passed). Exactly one V0 and one V-A run were executed sequentially, with no retry, threshold change, extra variant, additional scene or horizon expansion.

## Frozen provenance and protocol

- Branch `phase5-profiling-instrumentation`; execution HEAD `bb830b1f6a0a31028f14fe390b8cb4e1a50c47fe`, a documentation-only descendant of implementation/FIX1 `a3aefc745b73da520fa2ae53e77b0349fd25fa00`. Tracked algorithm/config/profiler files were unchanged before, between and after runs. The Phase 4 tag peeled to `37522db553ff18b96592073f9de699db7fa48600`.
- Validated interpreter `/home/robot/miniconda3/envs/sgs_slam_5080/bin/python`: Python 3.10.22, PyTorch 2.7.1+cu128, CUDA 12.8, NVIDIA GeForce RTX 5080, driver 580.167.08. Before execution, 15,370/16,303 MiB GPU memory was free, host available RAM was 117 GiB and filesystem free space 103 GiB. No environment changes.
- Replica `room0`; source loader slices `[start:end:stride]`, so `start=0,end=50,stride=1,num_frames=50` guarantees frame IDs 0–49. All RGB, depth, semantic-ID and semantic-color files for these 50 IDs and 2,000 trajectory lines were present. Resolution 680×1200; seed 0; tracking 40; mapping maximum 60; `map_every=1`; `keyframe_every=5`; mapping window 24; Phase 4 CPU keyframe offload active. The output/evaluator policy and LIGHT profiler settings matched P6-BAM-002. Released Phase 4 config was not edited.
- Dedicated, frozen launch wrappers and full effective-config JSONs are under `results/runtime_artifacts/phase6_bam/p6_bam_003_comparison/`. CPU preflight compared the complete effective configurations after removing only run/variant identity and `mapping.budget_control`; all other values matched. V0 had `enabled=False`; V-A kept 30/45/60 iterations and unvalidated thresholds `low_max=0.01,mid_max=0.05`. The preflight manifest records source, wrapper, launcher and effective-config SHA256 hashes.
- Exact launch commands, in order: `bash results/runtime_artifacts/phase6_bam/p6_bam_003_comparison/launch_v0.sh`; after V0 validation, `bash results/runtime_artifacts/phase6_bam/p6_bam_003_comparison/launch_va.sh`. The scripts preserve the full environment/entrypoint invocation and `/usr/bin/time` results. Both exited 0.

## Structural runtime result

| Check | V0 | V-A |
|---|---:|---:|
| Run ID suffix | `v0_r01` | `va_r01` |
| Completed frames / mapping events | 50 / 50 | 50 / 50 |
| Configured / executed mapping iterations | 3,000 / 3,000 | 3,000 / 1,740 |
| FULL / MID / LOW | 50 / 0 / 0 | 1 / 14 / 35 |
| Valid novelty signals | OFF-mode sentinel | 49 |
| Fallbacks | disabled ×50 | initial frame ×1; no other fallback |
| Initial / final Gaussians | 815,998 / 1,122,223 | 815,998 / 1,122,614 |
| Archived keyframes / logical bytes | 12 / 313,344,000 B | 12 / 313,344,000 B |
| H2D staging events / bytes | 2,371 / 61,911,552,000 B | 1,341 / 35,016,192,000 B |
| LIGHT dropped CUDA spans | 0 | 0 |
| Saved numeric state / OOM | finite / none | finite / none |

The CPU validator independently reapplied the frozen controller to every telemetry event's current pre/post append counts and checked added count/fraction, tier, configured/effective/executed counts, fallback and pruning floor. All V-A frames 1–49 had valid signals; append fractions ranged from 0.001452 to 0.016930. The initial event used FULL 60; all later decisions were LOW or MID, with no stale configured maximum. Each executed budget was at least 30, so the active zero-based prune call at iteration 20 was reachable for all 50 events. LIGHT does not directly count individual prune calls; this is source-call-site plus completed-loop evidence. The original Gaussian append/prune algorithms were not changed.

Both `params.npz` files were readable, all numeric saved arrays finite, and each contained 50 estimated/GT pose entries. Final keyframe IDs were identical and valid: `[0,4,9,14,19,24,29,34,39,44,48,49]`. CPU offload and H2D staging remained active. The existing final evaluator produced 11 matched RGB/depth/semantic rendered-image samples and metric arrays at `[0,4,9,14,19,24,29,34,39,44,49]`; no independent GPU evaluator or post-opt was launched.

## Preliminary quality and interpretation

The evaluator implementation is the same `utils/eval_helpers.py` at execution HEAD for both variants. It reports RGB PSNR, CPU MS-SSIM (the output filename is `ssim.txt`), LPIPS-Alex, valid-depth Depth L1 and GT-palette-assisted semantic-color mIoU. These are final-map renders of the 11 sampled training views, **not** novel-view or full-scene quality. Saved-trajectory ATE Mean and supplementary true ATE RMSE were computed read-only on all 50 relative-w2c translations with the same Horn rigid-alignment formula as Phase 4. The released printed “ATE RMSE” is a mean Euclidean error, not true RMSE.

| Metric | V0 | V-A | V-A − V0 |
|---|---:|---:|---:|
| Horn-aligned ATE Mean (m), 50 poses | 0.000369742 | 0.000332316 | −0.000037426 |
| Supplementary ATE RMSE (m), 50 poses | 0.000408083 | 0.000378266 | −0.000029817 |
| PSNR (dB), 11 renders | 40.611350 | 39.872295 | **−0.739055** |
| MS-SSIM, 11 renders | 0.995780 | 0.995552 | −0.000228 |
| LPIPS-Alex, 11 renders | 0.025973 | 0.026240 | +0.000267 |
| Depth L1 (m), 11 renders | 0.001892723 | 0.002257197 | **+0.000364475 (+19.26%)** |
| Semantic-color mIoU, 11 renders | 0.937575 | 0.935289 | −0.002285 |

The pre-existing P5-LEAN protocol's *provisional design targets* permit at most 0.5 dB PSNR decrease and 10% Depth L1 increase; both were exceeded here. PSNR was lower for V-A on 9/11 evaluated views, and Depth L1 was higher on 11/11. ATE, MS-SSIM, LPIPS and semantic mIoU did not show comparably large degradation under those provisional targets. This is a concrete quality warning, but one run pair with documented prior OFF-vs-OFF numerical divergence cannot establish causal deterioration or non-inferiority. Final Gaussian counts differed by only 391; that similarity is not quality evidence. No threshold was tuned after seeing results.

## Evidence and artifact integrity

- V0 saved state/eval: `results/runtime_artifacts/phase6_bam/p6_bam_003_room0_0_49_v0_r01/`; LIGHT JSONL/summary/metadata: `results/runtime_artifacts/phase6_bam/telemetry/p6_bam_003_room0_0_49_v0_r01/`. `params.npz` SHA256: `a634473ad6597a28cefeda26c8a4f2b7d829ab21039502baf64127dd805e3ed3`.
- V-A saved state/eval: `results/runtime_artifacts/phase6_bam/p6_bam_003_room0_0_49_va_r01/`; LIGHT JSONL/summary/metadata: `results/runtime_artifacts/phase6_bam/telemetry/p6_bam_003_room0_0_49_va_r01/`. `params.npz` SHA256: `7c1d7828d4fe0b20436f69d281039b65d46a62561c39c1ac4a83103ea5e7103d`.
- Comparison root: `results/runtime_artifacts/phase6_bam/p6_bam_003_comparison/` contains frozen configs, launcher scripts, preflight manifest, complete run logs, process-time records, CPU-only validator and per-run validation JSON. These runtime artifacts are intentionally Git-ignored; only this report and reviewed project-state documents enter the documentation checkpoint.
- Both destination result and telemetry directories were absent before launch, resolved strictly inside the Phase 6 root, and did not overlap P6-BAM-002. Runs were sequential; the wrapper's existence check remains non-atomic. No old output was overwritten.
- The immutable Phase 4 checkpoint `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz` retained SHA256 `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`. Both P6-BAM-002 checkpoint SHA256 values and LIGHT summary hashes were identical before/after; historical untracked reports, sessions 007–010 and `vds` were untouched.

## Gate decision and next action

Structural integration, artifact isolation, bounded execution and resource telemetry passed. Actual mapping iterations fell 42%, and observed timing improved in this one pair, but **the quality signal prevents a PASS classification**. Gate: `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME` because PSNR and Depth L1 exceed pre-registered provisional degradation targets. A single pair is not statistically reliable and does not establish full-scene feasibility or a validated speedup. Before authorizing 0–99 or fixed-budget GPU ablation, the researcher should review per-frame evaluation differences, baseline variability and the provisional margins; any follow-up run needs separate authorization. P6-BAM-004 was not started.
