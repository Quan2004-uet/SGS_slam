# Phase 5 Variant and Ablation Matrix

Status: `PROPOSED`. Only V0 exists. V1-V5 are conceptual variants and must receive separate identifiers/branches after approval.

## Frozen V0 contract

V0 is commit `37522db` on `phase4-vb-001-cpu-keyframe-offload` with algorithm source hash `a26aafe...32b3`, Replica settings, seed and evaluation protocol fixed per run. Profiling-only code from P5-G2 becomes a common measurement layer; comparisons must use the same instrumentation commit/mode.

| Variant | Parent / independence rule | Modified components | Frozen components | Hypothesis and expected effect | Failure modes | Metrics / controls | Gate and exit criterion |
|---|---|---|---|---|---|---|---|
| V0 | Validated PHASE4-VB-001 reference | Profiling only in P5-G2; no algorithm change | CPU-authoritative pageable archive, synchronous staging, selection, loss, map, schedule, evaluation | Reference | Existing CPU growth and staging cost | Full contract; `off/light/detailed` overhead control | P5-G2 equivalence then P5-G3/P5-G4 profiles |
| V1 | New branch directly from frozen V0; independent of V2 | Fixed-byte/count reuse-aware GPU cache for already-selected payloads only | Selection/RNG, archive, map, losses, keyframe policy | H1; fewer H2D bytes/events and lower mapping time; bounded VRAM increase | cache lifetime/staleness, budget overflow, no useful hit rate | Cache hit/miss, staged bytes/time, peak GPU, mapping wall; compare V0 and cache-disabled build | Unit equality + 0-99 + 0-499; exit if material speedup within GPU/quality gate, otherwise reject |
| V2 | New branch directly from V0; must not contain V1 | RAM/SSD hierarchy for archived payload, initially exact/lossless | Selection/RNG, no GPU cache, Gaussian path, losses/schedule | H2; bounded RAM, added disk I/O | stalls, corruption, cache confounding, SSD wear/capacity | RAM/RSS/HWM, SSD occupancy/read/write/latency, exact round-trip, H2D and wall | Offline round-trip then bounded runs; pass only under RAM budget and no trace/value divergence |
| V3 | New branch directly from V0; no V1/V2 | Spatial Gaussian partition/submap and bounded active optimization/render set | CPU archive/staging, keyframe policy initially, losses and semantic representation | H3; bounded GPU/optimizer active set and mapping scaling | seams, missed constraints, pose/map inconsistency, quality loss | active/total Gaussians, param/grad/Adam bytes, render/map time, cross-boundary quality | Synthetic/unit geometry then 0-99/0-499 and cross-scene; exit on stable boundaries and quality/resource gate |
| V4-G | Parent V3 after V3 passes | Geometry-only budgeted mapping scheduler | V3 submaps, semantics unused for scheduling | Control for generic budget effect | under-optimization, biased coverage | work saved, novelty, geometric/quality metrics | Must establish control frontier before semantic claim |
| V4-S | Same frozen V3 parent and budget as V4-G | Semantic-aware prioritization in addition to geometry | Total iteration/time budget, V3 and all else | H4; allocate same budget to higher utility/rare semantic content | semantic bias/error feedback, unequal actual compute | Same budget, semantic coverage/mIoU plus all geometric quality | Pass only if better than V4-G, not merely V0, with no geometry regression |
| V5 | Integration branch only after prerequisite approvals | V1+V2+V3+best validated V4 | Frozen module interfaces/budgets and evaluation | H5; Pareto improvement across GPU/RAM/storage/runtime | adverse interactions, nondeterminism, attribution loss | Full metrics plus component on/off interaction ablations | Multi-scene Pareto and stability gate; reject monolithic integration if interactions unresolved |

## Required ablations

1. V0 versus V1 and V0 versus V2 are separate experiments from the same parent.
2. V0 versus V3 excludes V1/V2.
3. Scheduler matrix: V3/no budget scheduler; V3+V4-G; V3+V4-S at the same budget.
4. V5 minimum integration controls: V0, V1, V2, V3, V3+V4-G, V3+V4-S, V1+V2, V3+selected V4, and full V5. If compute limits reduce this set, document untested interactions before claims.

## Comparison eligibility

A pair is eligible only when dataset/scene/frame range/seed, base algorithm/config, hardware/software, instrumentation mode, warm-up policy, evaluation scripts and output completeness match. V1/V2 require exact observation tensors and selected-ID traces. V3/V4 are algorithmic and require quality/failure gates. Failed/OOM runs remain in the table; no best-run-only selection.

## Branch and artifact convention

Proposed names (not created here): `phase5-p5g2-profiling`, then `phase5-v1-bounded-gpu-cache`, `phase5-v2-tiered-keyframe-archive`, `phase5-v3-spatial-submapping`, and `phase5-v4-semantic-budgeted-mapping`. Store artifacts under immutable run IDs such as `P5G3_V0_room0_f0000-0499_seed0_<commit>_<profile>`; never overwrite Phase 4 evidence.
