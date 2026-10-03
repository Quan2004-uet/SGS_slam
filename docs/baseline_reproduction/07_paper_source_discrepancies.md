# Paper vs Released Source: Reproduction Impact

The Phase 3 baseline is the released source at the audited commit, not a
paper-faithful reconstruction. Paper-only behavior must not be restored while
measuring the released baseline.

| Paper component | Released source status | Effect on reproduction | Action now |
|---|---|---|---|
| Semantic-mIoU keyframe filtering | Paper describes semantic filtering; corresponding online logic is commented/inactive. Active selection is geometric overlap plus periodic insertion. | Released baseline may use a different mapping window than the paper-described method. | Reproduce released source as-is; document discrepancy; defer reconstruction to Phase 4+. |
| Uncertainty-weighted mapping | Paper describes uncertainty weighting; no active implementation/caller was located in the audited online path. | Paper loss behavior may not match released online optimization. | Reproduce released source as-is; runtime verify only if new evidence appears; do not invent the term. |
| Bundle adjustment | Helper/loss support has a `do_ba` branch, but no active online caller was verified. | Do not describe online results as using BA. | Document discrepancy and defer to Phase 4. |
| Semantic representation | Released source trains per-Gaussian RGB semantic colors, with fixed semantic IDs; it does not train class logits/one-hot/features. | Evaluation depends on palette recoloring; cannot substitute class-logit metrics. | Reproduce representation and evaluator unchanged. |
| Online densification | Checked-in online config disables gradient clone/split but enables pixel-driven append and pruning. Post-opt enables clone/split. | “Densification” is stage-dependent; Gaussian count evolution differs online/post-opt. | Preserve config and label growth mechanism by stage. |
| Paper metric names | Released ATE “RMSE” is mean aligned translation distance; depth “RMSE” reduces to L1; code uses MS-SSIM. | A naive table comparison may compare different formulas. | Run released evaluator unchanged; document protocol; defer mathematical resolution to Phase 4. |
| Published rendering/semantic stage | Paper tables do not explicitly identify online vs post-opt output. | Could select the wrong artifact for target comparison. | Preserve both stages separately; report stage as unknown until behavioral/provenance evidence resolves it. |

Statuses are `VERIFIED FROM SOURCE` and `VERIFIED FROM PAPER` except the stated stage ambiguity, which
is `UNKNOWN / NEEDS RUNTIME VERIFICATION`.

## Reproduction rule

If a released-source result differs from the paper, first classify the difference
as environment, dataset, evaluator protocol, released-source discrepancy,
stochastic/hardware variation, or genuine algorithm failure. Do not enable BA,
semantic keyframe filtering, or uncertainty weighting to “improve” a Phase 3
number. Such work belongs to a separately identified paper-faithful or research
method branch after baseline recovery.
