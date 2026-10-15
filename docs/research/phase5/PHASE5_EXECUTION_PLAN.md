# Phase 5 Execution Plan

Status: `PROPOSED`; P5-G1 only is executed in this session.
Reference implementation: PHASE4-VB-001 at `37522db`.

## P5-G1 — Audit and design

**Scope:** reconstruct Phase 4 reference, inspect active runtime path and saved measurements, audit local datasets, define instrumentation/hypotheses/variants/evaluation. No GPU work.

**Outputs:** the nine documents in `docs/research/phase5/`.

**Pass criteria:** reference state verified; source hooks and measurement gaps explicit; dataset inventory evidence; controlled variants and decision rules; P5-G2 has no major design ambiguity.

**Result:** `PASS_P5_G1_DESIGN_READY`. The absence of a >2,000-frame dataset blocks a later large-scene claim, not instrumentation implementation.

## P5-G2 — Profiling instrumentation implementation

**Authorized only after a new task.** Create a new profiling branch from the validated reference. Add disabled-by-default telemetry without algorithm/config-default changes.

Deliverables:

1. Versioned telemetry schema/writer and exact storage-accounting helpers.
2. Hooks listed in `PHASE5_PROFILING_INSTRUMENTATION_PLAN.md` with `off/light/detailed` modes.
3. Immutable profiling experiment configs for room0 0-99 and 0-499; do not edit the released config in place.
4. CPU-only unit tests for storage de-duplication, RSS parsing, schema, aggregation and deterministic sampling.
5. Static/source checks showing profiling-disabled control does not alter RNG calls, keyframe selection, schedules, tensor operations or output logic.

Validation in P5-G2 itself should remain CPU/static unless separately authorized. Telemetry CUDA-event functionality can be code-reviewed/mocked; actual CUDA verification belongs to P5-G3 under explicit permission.

Exit: instrumentation is reviewable, disabled-by-default and ready for bounded validation; no performance claim.

## P5-G3 — Bounded performance profiling

**Not executed here.** After explicit CUDA authorization:

1. room0 0-99: `off`, `light`, `detailed`, seed 0; establish telemetry validity, algorithmic trace equivalence and overhead.
2. Repeat eligible modes enough to estimate timing variance; calibrate provisional 5% light-overhead gate.
3. room0 0-499 only after 0-99 passes; collect component shares and growth curves.
4. Optionally office0 0-99 as an early loader/scene sanity gate before P5-G4.

Numerical equivalence: selected keyframe IDs, insertion indices, iteration counts, Gaussian counts and final tensor shapes must match; define exact/toleranced tensor comparison before running. Stop on divergence, OOM, NaN/Inf, missing telemetry or excessive measurement overhead.

Exit: trustworthy bounded profiles and calibrated measurement overhead; hypotheses remain provisional.

## P5-G4 — Full-scene and multi-scene profiling

**Not executed here.** Freeze instrumentation commit/configs/seeds and run only scenes that pass bounded gates. Minimum characterization set: V0 room0 0-1999 reference plus office0 0-1999 and room1 0-1999 candidates, each with separate artifact provenance. Use `light` mode for full scenes; detailed sampling only at declared milestones.

Collect online runtime, component timing, GPU/CPU/storage growth and released/supplementary quality metrics. Do not merge detailed and output-saving executions. Preserve failures and last completed frames.

Exit: at least two additional structurally compatible scenes characterized or a documented dataset/runtime blocker. This gate cannot establish 10k-50k scalability with current data.

## P5-G5 — Bottleneck decision and phase closure

**Not executed here.** Apply the preregistered H1-H4 rules after overhead calibration and multi-scene review. Produce a ranked bottleneck table, confounder analysis, selected first variant and rejected/deferred alternatives.

Decision:

- approve V1 first only if H2D is a material critical-path contributor and bounded VRAM is feasible;
- approve V2 first if host budget crossing is dominant;
- approve V3 first if Gaussian/optimizer/render growth dominates across scenes;
- defer V4 until redundant mapping utility is directly evidenced and geometric control is specified.

Exit: one new branch/modification ID and experiment ID approved. No V5 integration approval before independent prerequisites pass.

## Dependencies

```text
P5-G1 PASS
  -> P5-G2 instrumentation + CPU/static tests
  -> P5-G3 room0 0-99 equivalence/overhead
  -> P5-G3 room0 0-499 component profile
  -> P5-G4 bounded-new-scene gate, then distinct full-scene runs
  -> P5-G5 bottleneck decision
  -> exactly one of V1/V2/V3 first
```

Large-scene data acquisition/adaptation is a parallel future data gate; it is not satisfied by concatenating Replica scenes or repeating frames.

## Stop conditions

- Any source/config default or RNG-order change beyond instrumentation: stop and reclassify.
- Instrumentation changes outputs/traces: fail equivalence before longer horizon.
- `light` overhead exceeds calibrated acceptance: redesign telemetry before profiling.
- New scene fails structural/decode gate: preserve evidence; do not repair loader algorithmically in the profiling run.
- Never overwrite Phase 4 artifacts, reuse a run ID, or begin a variant before P5-G5 authorization.
