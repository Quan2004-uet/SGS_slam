# Budget-Aware Mapping Design

## Candidate comparison

| Candidate | Mechanism | Effort / overhead | Risk | Three-week suitability |
|---|---|---|---|---|
| Fixed budget | Replace 60 with a fixed lower count | Very low; no new signal | Uniform under-optimization; ablation only | Essential control, not contribution |
| Residual-aware | Stop from mapping loss convergence | Medium; needs smoothing, normalization and GPU scalar synchronization | Random-view losses are not directly comparable | Reject initially |
| Novelty-aware | Allocate iterations from newly appended Gaussian fraction/count | Low; append already occurs and tensor shapes are host metadata | Append count is an imperfect proxy for optimization difficulty | **Selected** |
| Hybrid | Combine novelty and residual | Higher effort and hyperparameters | Harder attribution and tuning | Defer |

## Selected method: novelty-aware tiered budget

**HYPOTHESIS:** frames that append little new geometry need fewer map-optimization steps, while high-novelty frames retain the full V0 budget.

- Controller input: `pre_append_gaussians`, `post_append_gaussians`, and derived `added_count` / `added_fraction`. Frame 0 and any unavailable signal use the full budget.
- Controller output: an effective mapping-iteration count for the current mapping event.
- Scope: one decision per mapping event, before optimizer iteration.
- Budget: discrete low/mid/full tiers `30/45/60`. The V0 full budget remains 60. Candidate low/mid values and novelty thresholds are experimental hyperparameters frozen before each run; a small predefined search should compare fixed 30, fixed 45, and one novelty tiering using `{30,45,60}`.
- Safety invariant: effective budget must be at least 21 while Replica pruning is enabled so iteration 20 still executes. If config validation fails or append data are unavailable, fall back to 60.
- OFF mode: absent/disabled `mapping.budget_control` yields exactly `mapping.num_iters` and V0 behavior.
- Gaussian append, pruning conditions, learning rates, keyframe selection, tracking, loss and transfer behavior remain unchanged.

The thresholds are **NOT_VALIDATED**. Freeze them from the short predefined search; do not tune them from final-scene results. The controller records signal, selected tier, configured and executed iteration counts.

Expected implementation surface: a small CPU-pure controller helper plus one hook around `scripts/slam.py:847` and `975-1038`, configuration in a new experiment wrapper, telemetry counters, and CPU tests. No profiler repair is required.
