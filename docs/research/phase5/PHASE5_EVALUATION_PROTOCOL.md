# Phase 5 Evaluation and Reproducibility Contract

Status: `PROPOSED` protocol for P5-G2 through P5-G5.

## Run identity and eligibility

Every run records: run ID, variant/modification ID, dataset and scene, exact inclusive frame range, seed, complete config snapshot and SHA-256, Git branch/commit and dirty diff inventory, GPU model/VRAM/driver, Python/PyTorch/CUDA/renderer revision, instrumentation commit and mode, evaluator script/hash, checkpoint path/hash, artifact directory, start/end timestamps, exit status and stop reason.

Comparisons are eligible only with equal scene/range/seed/config/hardware/software/instrumentation mode and complete required artifacts. Runtime results from `profile=off`, `light`, and `detailed` are separate strata. Never extrapolate a partial run as completed or compare an OOM horizon as a full-scene runtime.

## Runtime metrics

- End-to-end online wall time: synchronized start after initialization and end before evaluation/serialization; also record initialization separately.
- Frames processed and effective FPS = completed frames / online wall seconds.
- Tracking and mapping: per-frame and per-iteration distributions (mean, median, p90, p95, p99), CPU dispatch, GPU elapsed and synchronized e2e where sampled.
- H2D: events, bytes, bytes/frame, wall/event time, effective bandwidth, per-field detail and archived/current selection count.
- Component GPU time: RGB/depth-semantic rendering, loss, backward, optimizer, append, active prune/densify.
- CUDA synchronization overhead: paired mode delta and explicit count/time of profiling synchronizations.
- Output serialization and evaluation are separate phases and excluded from online FPS.

## Memory and storage metrics

- CUDA current/peak allocated and reserved, with timestamps/frame index.
- Exact unique-storage logical bytes for Gaussian params, semantic fields, auxiliaries, gradients, camera state, optimizer state, keyframe poses/cache and staged payload.
- “Unattributed” memory is a bound, not named renderer memory.
- CPU archive logical bytes by field/keyframe, process RSS and HWM, declared RAM budget and projected crossing horizon.
- V2: SSD occupancy, read/write bytes, operation latency, throughput, cache policy and filesystem/page-cache state.
- Growth: Gaussians/keyframes, bytes/Gaussian and bytes/keyframe, slopes by predefined frame window.

## Quality metrics and provenance

Use the released saved-state training-view evaluator behavior unless a new supplementary metric is explicitly named. E4 reference is 401 images (`{0} union {5k-1}`) and all 2,000 poses.

| Metric | Required definition |
|---|---|
| ATE Mean | Released Horn-aligned mean Euclidean translation error. `utils/eval_helpers.py:161-178` returns `trans_error.mean()` despite “ATE RMSE” labels |
| ATE RMSE | Supplementary true `sqrt(mean(trans_error^2))` over the same aligned pose errors; save separately, never overwrite/relabel released mean |
| PSNR | Released `calc_psnr` with its valid-depth-weighted rendered/GT inputs (`eval_helpers.py:664-680`) |
| Released MS-SSIM | `pytorch_msssim.ms_ssim`, data range 1.0 (`eval_helpers.py:673-674`); do not call plain SSIM in result schema |
| LPIPS | AlexNet LPIPS on clamped [0,1] inputs (`eval_helpers.py:675-681`) |
| Depth L1 | GT-valid masked mean absolute error (`eval_helpers.py:683-699`). Released “Depth RMSE” expression is also mean absolute error algebraically and is not accepted as true RMSE |
| Semantic mIoU | Released semantic-color output snapped to unique current GT-frame palette, black ignored (`eval_helpers.py:59-158,701-710`); label `semantic_color_miou_gt_palette_assisted` |
| Tracking failures | count extra-iteration events, invalid poses/losses, exceptions, NaN/Inf and early stops |
| Reconstruction stability | finite tensors, Gaussian/keyframe growth, checkpoint readability, render success and no catastrophic artifact loss |

For each metric save aggregate, per-frame/per-pose inputs or errors, frame IDs, evaluator hash and protocol label. Online, post-opt and NVS results remain distinct. Phase 5 does not silently redefine released metrics.

## Artifact contract

Each run directory contains `run_metadata.json`, copied config, `telemetry.jsonl`, `timing_summary.json`, `memory_summary.json`, `selection_trace.json`, `status.json`, stdout/stderr log, and checksums. Runs that reach save/evaluation gates also contain checkpoint/manifest and quality metrics. A top-level experiment index records all attempts and eligibility/exclusion reasons.

## Repetition and statistics

P5-G3 first uses seed 0 to prove equivalence. Runtime claims require at least three eligible repetitions per compared bounded condition unless wall cost is explicitly waived; report all runs, median and spread. Full-scene P5-G4 may use one prespecified run per scene for characterization, but must not support a significance claim. Scene aggregation reports per-scene values and macro summaries, not only the best scene.

## Failure and run-selection policy

Keep OOM, timeout, invalid-state and incomplete runs with last completed frame. No retry replaces an attempt; retries receive new IDs and reasons. Stop thresholds are declared before execution. Quality/runtime conclusions exclude ineligible pairs but still disclose them.

## Baseline reference

V0 Phase 4 room0 values are context, not automatic comparison results: 0-1999 complete; detailed 6.774 GB allocated/8.009 GB reserved/10.497 GB CPU archive; output-save 14,173.475 s; E4 metrics in `phase4_closure/FINAL_METRICS_SUMMARY.md`. New Phase 5 comparisons must rerun V0 under the common P5 instrumentation layer at bounded horizons before performance claims.
