# SESSION_004 — Phase 4 Variant B Full-Scene Run

> **PLANNED SESSION.** This file records the next separately authorized
> operational objective. It is not ACTIVE until the full-scene run begins.
> Use `../PROJECT_STATUS.md` and `../SESSION_HANDOFF.md` for current
> authority.

## Metadata

Session ID: SESSION_004\
Title: Phase 4 Variant B Full-Scene Run\
Status: PLANNED / READY\
Started: —\
Last active: 2026-10-10 (planned)\
Closed: —\
Phase: Phase 4 — Memory-management research variant\
Variant: `PHASE4-VB-001` — CPU offload of resident keyframe payloads\
Objective: run the unchanged Variant B online pipeline on full Replica
`room0` frames 0–1999 after Gate 5 PASS and separate researcher
authorization.

## Starting State

Phase 3 baseline runtime reproduction remains closed with the documented
RTX 5080 16 GB memory limitation. Phase 4 Variant B passed bounded Gate 5
frames 0–999 with `PASS_FRAME_LIMIT`; index 1000 was intercepted before the
real loader. Gate 5 evidence is in:

`results/runtime_artifacts/phase4_vb001_gate5_0_999/`

The variant remains a research variant, not released-baseline reproduction.

## First Task

Full-scene online Variant B run only:

- Dataset: Replica `room0`.
- Frames: continuous `0–1999`.
- Preserve the released online workload and the declared Variant B residency
  policy.
- Save full-scene evidence separately from bounded-gate artifacts.
- Do not run evaluation or any post-SLAM stage in this session.

## Hard Constraints

- Do not run evaluation, ATE, rendering metrics, semantic metrics, or
  post-SLAM optimization.
- Do not modify source, config, renderer, dataset, losses, iteration counts,
  keyframe policy, Gaussian lifecycle, optimizer behavior, or algorithm.
- Preserve CPU-authoritative archived `color`, `depth`, `semantic_id`, and
  `semantic_color` payloads.
- Preserve GPU-resident `est_w2c`.
- Use synchronous CPU→GPU staging only after archived-keyframe selection.
- No pinned memory, no `non_blocking` transfer, no persistent GPU cache, no
  keyframe eviction, and no precision change.
- Stop immediately on CUDA OOM, NaN/Inf, residency violation, source/config
  drift, loader or frame-boundary violation, or unexpected runtime behavior.
- Do not overwrite Gate 1–5 evidence.
- Do not commit or push automatically.

## Required Evidence

Record the exact branch, HEAD, source/config integrity, environment, GPU,
command, output directory, and runtime. Capture CPU/GPU residency, CPU RSS,
GPU allocated/reserved memory, Gaussian trajectory, logical keyframe IDs,
tracking/mapping iterations, pruning/densification, opacity reset, finite
loss/state/optimizer checks, and stop/failure provenance.

Required outcome distinction:

- `PASS_FULL_SCENE` only if frames 0–1999 complete with required artifacts.
- `CUDA_OOM`, `FAIL_NUMERICAL`, `FAIL_RESIDENCY`, or `FAIL_RUNTIME` otherwise;
  preserve the failing boundary and do not retry with an unrecorded change.

## Evaluation Gate

Evaluation remains prohibited until full-scene online PASS and required
outputs are saved, followed by explicit separate authorization for evaluation.

## STOPPED HERE

Gate 5 bounded validation is complete. Begin only after separate researcher
authorization for this full-scene gate.
