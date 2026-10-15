# Remaining Phase 5 Validation Obligations

Planning these obligations does not satisfy them. They are separated by thesis priority.

## REQUIRED_FOR_CORE_THESIS_CLAIMS

- Matched online V0-versus-variant wall time, frame horizon, source/config hashes, seed, hardware, and environment.
- Tracking and mapping timing, with repeated-run reporting where affordable.
- Peak GPU allocated/reserved, CPU keyframe archive bytes, RSS/HWM, and OOM status.
- ATE Mean and true ATE RMSE under the documented evaluator, plus tracking failures and complete frame horizon.
- PSNR, MS-SSIM, LPIPS, Depth L1, Gaussian count, and qualitative reconstruction evidence.
- Semantic mIoU under the documented evaluation contract.
- Immutable run IDs, preserved failed runs, provenance, comparability rules, and explicit numerical-variability disclosures.

## HIGH_PRIORITY_GENERALIZATION

- Run at least one additional compatible scene beyond `room0` when resources permit.
- State clearly if additional-scene execution remains unavailable; do not present dataset readiness as generalization evidence.

## OPTIONAL_DIAGNOSTICS

- Lightweight transfer counters and bounded memory-growth traces.
- Detailed component timing only where its synchronization and overhead are justified.
- Qualitative trajectory, semantic, and map diagnostics beyond the core evaluation contract.

## DEFERRED_FUTURE_WORK

- Comprehensive original P5-G3B/G4/G5 profiling acceptance.
- Broad multi-scene scaling study.
- GPU keyframe cache, RAM/SSD hierarchy, Gaussian submapping, and semantic-aware scheduling variants unless separately authorized.

The next planned research task is P5-LEAN-001; no obligation above is claimed complete by this administrative transition.
