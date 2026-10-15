# Phase 5 Research Hypotheses and Decision Rules

Status: `PROPOSED`; none of H1-H5 is confirmed. V0 means unchanged validated PHASE4-VB-001.

Thresholds below are provisional design thresholds. P5-G3 must calibrate run-to-run variance and instrumentation overhead before P5-G5 applies them. Quality tolerances are gates against obvious regression, not claims of statistical equivalence.

## H1 — Transfer bottleneck

**Hypothesis.** Repeated synchronous CPU-to-GPU staging contributes materially to mapping/runtime.

- Evidence required: per-selection bytes, H2D wall and CUDA-event time, mapping component times, selected-ID reuse distances, transfer bandwidth, and matched `profile=off/light/detailed` overhead.
- Supporting observation: H2D critical-path time is >=10% of mapping end-to-end time or repeated staged bytes are high with substantial reuse and a cache simulation predicts meaningful avoidable traffic.
- Falsifying observation: upper confidence bound is <5% of mapping time and transfer reduction cannot improve end-to-end time materially.
- Expected benefit: V1 bounded GPU keyframe cache reduces staged events/bytes and stalls without changing selection.
- Potential regression: added VRAM, stale/lifetime bugs, cache-management overhead; no quality regression is expected if values are bit-identical.
- Confounders: pageable-copy host cost not fully represented by CUDA events; instrumentation synchronization; OS paging; current-vs-archived selection ratio; allocator reuse.
- Priority rule: prioritize V1 only if calibrated transfer share is material and a fixed cache budget remains below a prespecified GPU safety margin. Otherwise move to H2/H3.

## H2 — CPU archive scalability bottleneck

**Hypothesis.** Retained payload growth will exhaust practical host-memory budgets on longer runs.

- Evidence required: exact archive bytes/keyframe, keyframe growth, RSS/HWM, available-memory budget, per-field compressibility/round-trip tests, and projected crossing horizon with uncertainty.
- Supporting observation: measured archive+process memory reaches >=70% of a declared run RAM budget, or conservative projection crosses that budget within target horizon.
- Falsifying observation: archive growth is bounded by the actual policy or remains below 40% of budget over the declared target horizon with stable RSS.
- Expected benefit: V2 RAM/SSD hierarchy bounds RAM while preserving logical keyframes.
- Potential regression: I/O latency, page-cache pressure, serialization complexity, data corruption/precision changes.
- Confounders: RSS includes non-archive allocations; OS cache; constant-resolution room0 payloads may not generalize; target hardware RAM varies.
- Priority rule: prioritize V2 when budget crossing precedes GPU/map bottlenecks and exact/lossless round-trip is feasible. A 70% trigger is provisional and must be set per deployment RAM budget.

## H3 — Gaussian/optimizer scalability bottleneck

**Hypothesis.** Gaussian parameters, gradients, Adam state and rendering complexity dominate GPU growth and mapping cost after keyframe offload.

- Evidence required: unique-storage bytes by param/gradient/optimizer/auxiliary category, Gaussian count, renderer residual/peaks, mapping times and growth slopes across frames/scenes.
- Supporting observation: attributable Gaussian+optimizer+gradient bytes are the largest live GPU category and/or Gaussian count explains mapping-time growth across milestones/scenes; provisional dominance >=50% of allocated bytes or time-growth model materially exceeds H1.
- Falsifying observation: these categories remain bounded/minor while staging, renderer workspace independent of N, or another component dominates.
- Expected benefit: V3 spatial submapping bounds active Gaussian/optimizer working set and render candidates.
- Potential regression: seams, missed cross-submap constraints, trajectory/map inconsistency, quality loss, added orchestration.
- Confounders: renderer internal buffers correlate with Gaussian count but cannot be perfectly attributed; pruning and scene geometry; optimizer lazy state; resolution.
- Priority rule: choose V3 before V1/V2 only after multi-scene evidence identifies active-map growth as dominant and defines a quality-preserving submap boundary protocol.

## H4 — Mapping utility bottleneck

**Hypothesis.** Mapping performs substantial redundant work on low-utility observations or regions.

- Evidence required: per-iteration selected frame/region, loss improvement, visibility/novelty, semantic distribution, Gaussian updates, time and quality response under fixed-budget geometric-only controls.
- Supporting observation: a large fraction of mapping iterations has negligible prespecified loss/map change while consuming material time, and a geometry-only budgeted control retains quality.
- Falsifying observation: removing/downweighting candidate work causes quality/tracking/reconstruction regression or redundant fraction is small.
- Expected benefit: V4 semantic-aware budgeted mapping reduces work while preserving important/rare content.
- Potential regression: semantic bias, rare geometry loss, feedback from imperfect semantic colors, changed optimization distribution.
- Confounders: current semantic output is learned color and GT-palette-assisted evaluation, not an independent class predictor; loss scale changes; scene class imbalance; random keyframe sampling.
- Priority rule: first pass a geometric-only scheduling control. Semantic-aware V4 is justified only if it beats that control on prespecified semantic and geometric quality without hidden compute increases.

## H5 — Integrated system hypothesis

**Hypothesis.** Independently validated V1-V4 modules can jointly improve memory/runtime trade-offs without unacceptable quality loss.

- Evidence required: complete component gates, interaction ablations, fixed budgets, matched profiling/evaluation, failure analysis and multi-scene results.
- Supporting observation: V5 improves a prespecified Pareto objective (runtime, peak GPU, peak RAM/storage) on multiple scenes while meeting all quality/failure gates.
- Falsifying observation: integration loses individual gains, violates budgets, creates instability, or quality regression exceeds thresholds.
- Expected benefit: bounded multi-tier observation storage plus bounded active map and useful mapping work.
- Potential regression: compounded complexity, nondeterminism, interacting caches/submaps/scheduler, difficult attribution.
- Confounders: hardware/storage dependence; interactions; instrumentation mode; scene mix; survivor bias from only successful runs.
- Priority rule: V5 is forbidden until V1/V2/V3 pass independently and V4 passes geometric and semantic controls. Integration requires a frozen interface and full factorial subset sufficient to identify interactions.

## Shared provisional quality/failure gates

- Zero new tracking failures, NaN/Inf, OOM, residency invariant failures, or incomplete artifacts.
- Identical selected-keyframe/insertion traces for transport/storage-only V1/V2.
- For algorithmic V3/V4/V5, compare ATE Mean, true ATE RMSE, PSNR, MS-SSIM, LPIPS, depth L1 and semantic-color mIoU under the exact frozen protocol.
- Initial tolerance candidates: <=2% relative degradation for error metrics, <=0.5 dB PSNR loss, <=0.005 MS-SSIM loss, <=0.01 absolute semantic mIoU loss. These are `PROPOSED`, must be calibrated against repeated V0 variance, and are not universal scientific equivalence bounds.

## P5-G5 prioritization

Rank bottlenecks by (a) measured critical-path share, (b) projected resource-budget crossing, (c) multi-scene consistency, (d) intervention risk, and (e) expected quality impact. Choose exactly one first implementation: V1 if transfer dominates, V2 if host budget dominates, or V3 if active Gaussian/optimizer/map complexity dominates. H4 remains a later algorithmic study unless mapping redundancy is directly measured.
