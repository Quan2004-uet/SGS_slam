# SESSION_003 — Phase 4 Variant B Bounded Validation

> **PLANNED SESSION.** This file records the next authorized operational
> objective. It is not ACTIVE until work begins. Use
> `../PROJECT_STATUS.md` and `../SESSION_HANDOFF.md` for current authority.

## Metadata

Session ID: SESSION_003\
Title: Phase 4 Variant B Bounded Validation\
Status: PLANNED / READY\
Started: —\
Last active: 2026-10-10 (planned)\
Closed: —\
Phase: Phase 4 — Memory-management research variant\
Variant: `PHASE4-VB-001` — CPU offload of resident keyframe payloads\
Objective: validate the unchanged Variant B implementation on bounded Replica
`room0` frames 0–999 while preserving online behavior and measuring CPU/GPU
residency.

## Starting State

Phase 3 baseline closure remains immutable and is classified as closed with a
documented RTX 5080 memory limitation. Variant B passed Gates 1–4 through
frames 0–499. It remains a research variant, not released-baseline
reproduction.

## First Authorized Task

Run Gate 5 only:

- bounded Replica `room0` frames 0–999 continuously;
- intercept dataset index 1000 before the real loader;
- preserve resolution, seed/RNG policy, renderer, losses, iterations,
  keyframe cadence/selection, Gaussian lifecycle, semantics, and optimizer;
- preserve Variant B residency invariants;
- do not run full scene, evaluation, ATE, rendering/semantic metrics, or
  post-SLAM optimization;
- do not modify implementation, config, renderer, dataset, or algorithm;
- stop immediately on CUDA OOM, NaN/Inf, boundary violation, residency
  violation, source/config drift, or unexpected runtime behavior.

## Preconditions and Evidence

- Gate 1: `results/runtime_artifacts/phase4_vb001_gate1/` — `PASS`.
- Gate 2: `results/runtime_artifacts/phase4_vb001_gate2/` — `PASS`.
- Gate 3: `results/runtime_artifacts/phase4_vb001_gate3_0_99/` —
  `PASS_FRAME_LIMIT`.
- Gate 4: `results/runtime_artifacts/phase4_vb001_gate4_0_499/` —
  `PASS_FRAME_LIMIT`.
- Phase 3 closure boundary: `docs/experiments/PHASE3_BASELINE_CLOSURE_2026-10-10.md`.

## Conditional Follow-on

Only after Gate 5 passes and its memory, CPU-RAM, runtime, Gaussian-divergence,
residency, and finite-state evidence is reviewed may a researcher authorize a
full Replica `room0` 0–1999 online run. Evaluation remains prohibited until
full-scene online success and required outputs are saved. Full scene is not
currently authorized by creating this planned session.

## STOPPED HERE

Phase 4 Variant B passed bounded validation through frames 0–499. Resume at
Gate 5 with the index-1000 pre-loader guard.

## DO NOT

- Do not treat Variant B as released-baseline reproduction.
- Do not alter `scripts/slam.py`, configs, dataset code, renderer, keyframe
  selection, or any Variant B policy for Gate 5.
- Do not run 0–1999, evaluation, or post-SLAM optimization before the stated
  review and explicit authorization.
- Do not commit or push.
