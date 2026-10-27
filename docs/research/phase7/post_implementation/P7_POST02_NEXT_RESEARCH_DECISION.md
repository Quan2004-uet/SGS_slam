# P7-POST-02 — Next Research Decision: P7-B

**Status:** decision analysis only. No P7-B roadmap was found or approved. No implementation or experiment is authorized by this report.

| Option | Scientific value | Effort / GPU cost | Risk | Evidence needed | Thesis fit |
|---|---|---|---|---|---|
| A — stop algorithm development; finalize thesis | Honest, bounded conclusion: BCGM admission works and bounds map growth, with material quality trade-offs | Lowest; CPU/reporting only if needed | Low engineering risk; thesis must clearly discuss >10% LPIPS/Depth L1/ATE deltas and timing limits | Complete current evidence, figures/tables, limitations | Best if deadline is near; strongest scope control |
| B — Quality-Aware Gaussian Admission | Potential contribution if utility-aware selection improves depth/pose/semantic coverage at the same caps | High: new score/payload logic, CPU tests, repeated full-scene runs and careful memory/runtime profiling | High regression/attribution risk; requires design, implementation, ablations and time | First a separate approved hypothesis/design; then paired same-scene baseline/BCGM/quality-aware runs, multiple seeds if feasible, per-event quality attribution | Valuable only with sufficient thesis/GPU time and advisor approval |
| C — controlled BCGM ablation (Event Cap, Global Cap, ranking) | Best causal decomposition of current method before adding a new heuristic | High GPU cost: factorial arms on at least one full scene; careful run selection and repeated trials | Could reveal that current combined method is not attributable to one component; may delay completion | Baseline, Event-only, Global-only, both/ranking variants; same configs/seed/harness; confidence/variance where feasible | Scientifically clean, but expensive and does not itself repair quality regressions |

## Recommendation

**Recommend Option A for the near-complete thesis unless the researcher/advisor explicitly allocates additional compute and time.** P7-A is complete with limitations; evidence already demonstrates runtime activation of both caps and a visible resource/quality trade-off. Current results do not justify claiming a general improvement. A new quality-aware selector (B) before ablation (C) would make attribution harder. If extra research time is granted, do C first as a diagnostic, then propose B only from measured failure evidence.

Required thesis framing: describe BCGM as bounded admission preserving deterministic payload alignment; report the room1 resource reductions as historical observations with timing/memory scope caveats; state LPIPS, Depth L1, and ATE regressions beyond ~10%; distinguish correlation from causality. Do not claim speedup significance, quality retention, or P7-B approval.
