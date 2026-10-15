# P5-G3 Bounded Profiling Readiness

Status: `READY_FOR_RESEARCHER_REVIEW`; P5-G3 is not authorized or executed.

## Prerequisites before any GPU run

1. Review and commit P5-G2 separately if accepted.
2. Create immutable run configs with unique run IDs/output directories; never edit the released Replica config.
3. Confirm clean implementation branch except known `vds` and record the exact commit/config hashes.
4. Confirm telemetry disk budget and set time/memory stop policies.
5. Preserve Phase 4 artifacts; use only `results/runtime_artifacts/phase5_profiling/` or another approved unique root.

## First bounded matrix: room0 frames 0-99

| Condition | Mode | Repetitions | Purpose |
|---|---|---:|---|
| C0 | missing profiling section or `off` | 1 equivalence reference, then timing repeats if approved | prove legacy/default path |
| C1 | `light` | same seed/repetition policy | low-overhead telemetry and trace equivalence |
| C2 | `detailed` | same seed/repetition policy | validate component CUDA events and attribution |

Hold scene, inclusive frame range, seed 0, hardware, environment, algorithm config, progress/evaluation/output controls constant. Use separate run directories. Do not compare against Phase 4 full-scene timing as a matched performance result.

## Required 0-99 checks

- Exact insertion indices, selected keyframe IDs and mapping iteration counts.
- Per-frame Gaussian counts and final parameter keys/shapes.
- Finite losses/parameters/optimizer state and no new failure.
- Archive/staging event and byte invariants.
- JSONL/metadata/summary schema and completeness.
- CUDA event durations finite/nonnegative and plausible relative to synchronized boundaries.
- Explicit synchronization count/time, pending events zero at close and dropped CUDA event spans zero.
- OFF/light/detailed wall overhead; calibrate, do not assume, the provisional <=5% light threshold.
- No profiling output in OFF.

If any trace or numerical invariant diverges, stop before 0-499 and classify instrumentation perturbation. If detailed event resolution or file volume is excessive, adjust only profiling cadence/buffer policy and repeat 0-99 with a new run ID.

## Conditional 0-499 gate

Proceed only after 0-99 passes. Repeat eligible conditions with the same instrumentation commit and declared repetitions. Measure component shares, archive/Gaussian/optimizer growth, H2D traffic/time and RSS/GPU curves. Do not begin multi-scene/full-scene work in P5-G3 unless separately authorized.

## Outstanding label

All GPU-facing functionality remains `PENDING_P5_G3_CUDA_VALIDATION`. Current P5-G2 evidence supports implementation readiness only, not runtime equivalence or performance accuracy.
