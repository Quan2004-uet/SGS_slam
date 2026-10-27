# Phase 7 Gate 4 — BCGM Contribution and Limitations

## Implemented contribution

BCGM (`utils/bcgm.py`, online integration in `scripts/slam.py`) bounds pixel-driven Gaussian insertion. Candidate filtering occurs before pointcloud construction; valid candidates are selected deterministically under per-event and total-count admission budgets. The selected RGB, depth and semantic payloads remain index-aligned. Gate 3 retained Phase 4 CPU Keyframe Offload and the baseline tracking/mapping objectives; no Phase 6 BAM was combined, and online gradient clone/split densification remained disabled.

Run configuration: Event Cap `9,000`; Global Cap `4,500,000`; pixel-driven insertion preserved. Source/config identities are pinned in the Gate 4 evidence manifest.

## Full-scene runtime validation

1,999 insertion events satisfy the actual admission equation and all counter transitions. Aggregate valid/admitted/rejected candidates are `8,698,235 / 4,363,012 / 4,335,223`. Event Cap activated 104 times; Global Cap activated 789 times. The `global_saturated` field—not the combined `budget_saturated` field—was used for Global Cap accounting. The summary validates BCGM admission and runtime Global Cap activation.

The Global Cap bounds admissions when points are appended. Existing pruning may reduce the live map after an insertion, so cap activation and final checkpoint count are distinct concepts. Final checkpoint count is `4,499,583`; this does not imply every intermediate map state remained exactly at the cap.

## Runtime and memory interpretation

Gate 3 process wall is `14,165.030217954074 s`, E2E `0.1411927803 FPS`; tracking and mapping stage rates are `0.3470693` and `0.2567926 FPS`. CUDA peak allocated/reserved are `5,442,630,656 / 6,784,286,720 B`; sampled device-wide NVML peak is `7,684 MiB` from 13,941 valid samples.

Historical Phase 4 output-save reference is `14,173.475159 s`, `5,817,509,888 / 7,189,037,056 B` CUDA allocated/reserved, and `4,956,467` final Gaussians. Since harness, evaluation/save boundaries and timing scope are not fully matched, differences are descriptive context only. They do not prove statistically significant acceleration or memory reduction attributable to BCGM. There is no full-scene Phase 4 matched quality, trajectory or NVML result. No matched Phase 6 quantitative result for this exact scene/config/evaluator was identified.

## Scientific and evidence limitations

- One BCGM-on full-scene run; no repeat-run confidence interval or statistical inference.
- Quality arrays are training-view evaluation with 401 samples; no held-out novel-view claim.
- `ssim.txt` means MS-SSIM; `rmse.txt` reproduces Depth L1, not Depth RMSE.
- Original console ATE RMSE label is arithmetic aligned mean; true ATE RMSE is the separately calculated offline value. Alignment is Horn SE(3) on W2C translation columns, no scale, all poses.
- NVML peak is sampled, device-wide and distinct from CUDA allocator peaks; no unsampled absolute peak.
- Selection/sorting time is not isolated by the recorded insertion host-call sum.
- Visualization has V3A clipping/frustum limitations. Fixed semantic-ID Gaussian-center plots are sampled diagnostics, not pixel-wise semantic prediction. Qualitative trajectory plots are not ATE plots. Learned semantic colors are not categorical semantic IDs.
- Gate 0 has no standalone design report in the current Phase 7 worktree; its `PASS_PHASE7_GATE0_DESIGN_READY` status is carried forward from Gate 1A/1B and management records.
- Researcher reports laptop transfer complete; no independent laptop SHA256 verification is available.
- The Phase 7 worktree changes remain uncommitted by design at this closure.

## Final scientific interpretation

Gate 3 establishes that the configured Event Cap and Global Cap admission controls were exercised and internally consistent over the saved full-scene trace, with a readable final checkpoint, complete saved trajectory and evaluator artifacts. It does not isolate the causal effect of BCGM against a matched Phase 4 full-scene quality/performance arm. Report the outcome as `COMPLETE_WITH_LIMITATIONS`; do not claim matched speedup, quality retention, or statistical significance.
