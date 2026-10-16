# P6-BAM-001 FIX1 — Mapping Budget Lifecycle Audit and Explicit Per-Event Budget

Date: 2026-10-16. Base commit: `e644df43a2ddc6ecd28f1e3c58d663117dcb8e1e`.
Gate: `PASS_P6_BAM_001_FIX1_CPU_STATIC`. The historical `PASS_P6_BAM_001_CPU_STATIC` is preserved. Runtime status remains `NOT_RUNTIME_VALIDATED`.

## Source finding and cause

`VERIFIED FROM SOURCE`: the reported cross-event budget leak does **not** occur in base commit `e644df4`. The statement `num_iters_mapping = config['mapping']['num_iters']` was inside `for time_idx in ...` at `scripts/slam.py:848`, and there is at most one mapping event per frame. It therefore restored 60 before each later event. No GPU run was made, and no runtime equivalence is claimed.

The integration still reused one mutable local name for the configured maximum and the current effective count. That obscured the invariant and allowed a plausible but incorrect source reading. FIX1 makes the relationship explicit: `configured_mapping_iters` is read from `mapping.num_iters` inside each mapping event and passed unchanged to `select_mapping_budget`; `effective_mapping_iters` controls only that event's progress bar, loop and close condition. There is no remaining assignment that replaces the configured count with a selected tier.

## Before and after

| Event sequence | Base `e644df4` static behavior | FIX1 static behavior |
|---|---|---|
| frame 0 / low / high / mid / missing / low | 60 / 30 / 60 / 45 / 60 / 30 | 60 / 30 / 60 / 45 / 60 / 30 |

The expected numerical behavior is unchanged. In V-FIXED30/45, each later event with an available append signal remains at 30/45. The existing controller deliberately falls back to 60 if append data are unavailable; FIX1 does not alter that separate policy. V0/OFF remains 60 for every event. All budgets reach Replica prune iteration 20.

## Changes and CPU validation

- `scripts/slam.py`: separate configured and per-event effective names and move the config read directly into the mapping event.
- `tests/test_mapping_budget.py`: execute the assignment expressions and loop range extracted from the real `rgbd_slam` mapping branch as AST. Assert the six-event adaptive sequence, fixed controls, OFF sequence, 60 passed to every controller call, and inclusion of iteration 20.
- `docs/research/phase6_bam/P6_BAM_001_IMPLEMENTATION_REPORT.md` and project-state files: record this clarification and FIX1 gate.

Command: `PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' /home/robot/miniconda3/envs/sgs_slam_5080/bin/python -m unittest tests.test_mapping_budget tests.test_performance_profiler -q` — **38 passed, 0 failed** (15 mapping-budget, 23 profiler). AST parse of changed Python source/tests and `git diff --check` passed. No CUDA initialization, SLAM frame, profiler-source edit, config edit, output-directory write or artifact mutation occurred.

`VERIFIED FROM SOURCE`: the diff touches only the mapping budget setup/loop-count references and its test; tracking, sampling, loss, optimizer, prune/append, keyframe offload, profiler and Phase 6 output guards remain unchanged. Phase 4 checkpoint SHA-256 remains `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`.

## Remaining risk

The AST test exercises the live source expressions without importing or running the CUDA SLAM pipeline. It does not establish numerical equivalence, speedup, reconstruction quality, or GPU telemetry correctness. P6-BAM-002 matched LIGHT 0–10 V0/V-A remains a separately authorized next task.
