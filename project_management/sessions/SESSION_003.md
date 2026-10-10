# SESSION_003 — Phase 4 Variant B Bounded Validation

> **CLOSED SESSION.** Gate 5 bounded validation completed and evidence was
> recorded. Use `../PROJECT_STATUS.md` and `../SESSION_HANDOFF.md` for the
> next operational authority.

## Metadata

Session ID: SESSION_003\
Title: Phase 4 Variant B Bounded Validation\
Status: CLOSED\
Started: 2026-10-10\
Last active: 2026-10-10\
Closed: 2026-10-10\
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

## Gate 5 Checkpoint — 2026-10-10

`RUNTIME VERIFIED`: Gate 5 completed with `PASS_FRAME_LIMIT` on branch
`phase4-vb-001-cpu-keyframe-offload`, HEAD
`8061093b79be1cc643f3d8180ece8574fa51b5c5`.

- Dataset/scene: Replica `room0`, continuous frames `0–999`; 1000 frames
  completed, final frame `999`.
- Boundary: dataset index `1000` was intercepted before the real loader;
  `real_loader_called_for_blocked_index: false`; full scene did not complete.
- Runtime/environment: PyTorch `2.7.1+cu128`, CUDA `12.8`, NVIDIA GeForce RTX
  5080; runtime `7183.993467400001 s` (approximately 1 h 59 m 44 s).
- Final state: `4,411,916` Gaussians, `201` logical keyframes,
  `5,248,512,000 B` CPU archive, `0 B` GPU archived payload, and `12,864 B`
  GPU `est_w2c`.
- Memory: max allocated/reserved `5,958,148,096 / 6,949,961,728 B`;
  max RSS/high-water `7,905,923,072 / 7,957,504,000 B`.
- Iterations/lifecycle: `39,960` tracking iterations, `60,000` mapping
  iterations, `250,265` pruning removals, `0` densification calls, opacity
  reset `False`.
- Numerical state: all weighted losses, captured tensors, optimizer state,
  semantic colors, and semantic IDs finite.
- Residency: CPU-authoritative archived payloads `True`; GPU-resident
  `est_w2c` `True`; zero GPU archived payload; one maximum staged payload;
  no persistent staged payload; staging count matched archived selections;
  no added RNG calls.
- Phase 3C-6 comparison at frame 499: Gaussian count
  `2,257,421 / 2,247,988 / -9,433` (relative `-0.4178662287628227%`),
  cumulative pruning `100,571 / 112,354 / +11,783`, allocated reduction
  `2,787,247,616 B` (about `75.83%`), reserved reduction `4,777,312,256 B`.
- Gate 4 comparison at frame 499: Gate 4/Gate 5 Gaussian count
  `2,255,038 / 2,247,988 / -7,050` (about `-0.3126%`).
- Sampled Gaussian deltas through frame 499 remained under `1%`; online
  behavior was preserved at the Gate-5 observation level. Bit-exact
  equivalence is not claimed because the historical ordered Phase 3 trace is
  unavailable. Selected-view counts did not exact-match the independent Phase
  3 run, but causation by CPU staging is unresolved.

Evidence:
`results/runtime_artifacts/phase4_vb001_gate5_0_999/`.

## STOPPED HERE

PHASE4-VB-001 Gate 5 completed bounded Replica `room0` frames `0–999` with
`PASS_FRAME_LIMIT`. Dataset index `1000` was intercepted before the real
loader. Full scene `0–1999` was not run in this session.

## Unresolved and intentionally untested

- Full-scene `0–1999` completion, CPU-RAM growth, transfer overhead, and
  end-to-end runtime.
- Checkpoint/resume archive reconstruction.
- Evaluation, ATE, rendering metrics, semantic metrics, post-SLAM
  optimization, and paper-metric equivalence.
- Ordered selection-trace equivalence to historical Phase 3.

## Next session plan

Prepare `SESSION_004` (`PLANNED / READY`) for the separately authorized
full-scene Variant B online run `room0` frames `0–1999`. Evaluation remains
prohibited until full-scene online PASS and required outputs are saved.

## DO NOT

- Do not treat Variant B as released-baseline reproduction.
- Do not alter `scripts/slam.py`, configs, dataset code, renderer, keyframe
  selection, or any Variant B policy for Gate 5.
- Do not run 0–1999, evaluation, or post-SLAM optimization from this closed
  session.
- Do not commit or push.
