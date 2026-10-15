# P6-BAM-001 — Minimal Implementation Contract

## Authorized modification boundary

- Add one CPU-pure helper (preferred: `utils/mapping_budget.py`) implementing and validating the controller.
- Modify only the mapping-budget hook in `scripts/slam.py` around append count (`989–995`) and loop setup (`1033–1038`), plus passive executed-budget telemetry.
- Add a new experiment config wrapper; do not edit released `configs/replica/slam.py` defaults.
- Add focused CPU tests. Do not modify tracking, loss, keyframe selection, Gaussian append/prune/densify helpers, CPU offload, or profiler internals.

## Controller API

`select_mapping_budget(config, configured_iters, pre_gaussians, post_gaussians, frame_id, pruning_config) -> decision`

The returned immutable decision contains `enabled`, `signal_valid`, `added_count`, `added_fraction`, `tier`, `configured_iters`, `effective_iters`, and `fallback_reason`.

Missing/disabled config returns `effective_iters == configured_iters`. Invalid values fail before an online run or safely fall back to the configured budget, with explicit telemetry. When pruning is enabled as in Replica, validate `effective_iters >= stop_after + 1` for the required iteration-20 prune.

## Tests and invariants

- OFF/missing config reproduces 60 and consumes no RNG.
- Zero/low/mid/high novelty selects the predefined tier deterministically.
- Frame 0/invalid signal uses full budget.
- Bounds and pruning-floor validation; no post-hoc threshold mutation.
- No tensor retention, CUDA calls, `.item()`, synchronization, or data transfer in the controller.
- Existing tracking iterations, mapping sampling logic, keyframe sequence, append/prune rules, optimizer/loss and seed remain unchanged.
- Telemetry records budget and signal using scalar host metadata only.

## Bounded validation

After CPU/static PASS and researcher approval, use matched LIGHT mode for 0–10 V0 and V-A. Check exact horizon, finite state, keyframes, configured/executed iterations, prune iteration coverage, archive/H2D counters and output provenance. Stop on any invariant failure. Proceed to 0–49 only by separate approval.

A short LIGHT integration validation can occur in the same bounded implementation-validation gate; another comprehensive profiler gate is unnecessary. P6-BAM-001 must not run automatically from P5-LEAN-001.
