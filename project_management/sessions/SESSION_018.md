# SESSION_018 — P6-BAM-006 CPU/Static Preflight Fix

- Started: 2026-10-16.
- Completed: 2026-10-16.
- Status: `CLOSED`.
- Objective: prepare a safe 0–1999 V-A2 wrapper, checkpoint-first final saving,
  and saved-state Phase 4 E4-compatible evaluation without launching SLAM or
  CUDA work.
- Starting HEAD: `36284a2cbccd3e148a628c44f6fbcba139ac3ceb`.
- Branch: `phase5-profiling-instrumentation`.
- Phase 4 tag: `37522db553ff18b96592073f9de699db7fa48600`.
- Phase 4 checkpoint SHA256 verified unchanged:
  `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`.

## Result

`PASS_P6_BAM_006_PREFLIGHT_FIX_CPU_STATIC_READY`. The isolated full-scene
wrapper fixes the frame bound, LIGHT settings, E4 sampling cadence and
frame-1999 checkpoint interval; parity tests match the 0–499 V-A2 effective
config except intended horizon/run/evaluation/checkpoint identity changes and
the opt-in checkpoint-first flag. WandB remains disabled. For the new wrapper
only, final metadata, `params.npz`, RGB/semantic Gaussian PLYs, and CPU
checkpoint validation now precede in-process evaluation; existing configs
retain their previous order. A separate
saved-state evaluator uses the unchanged repository metric implementation,
enforces Phase 6-only output paths, and validates exactly 401 image metrics and
render IDs plus all-2000-pose Horn ATE mean/true RMSE.

## Validation and scope

- 45 CPU unit tests passed: P6-BAM-006 preparation, mapping budget, and profiler
  CPU suites.
- `py_compile` passed on new/changed Python files; `git diff --check` passed.
- No SLAM frame, CUDA API/device workload, evaluation, renderer, PLY export, or
  full-scene run was executed.
- Phase 4 and previous Phase 6 artifacts were not modified. Existing untracked
  historical reports, SESSION_007–010 and `vds` were preserved.

## Changed files

- `configs/replica/phase6_bam_va2_full_0_1999.py`
- `scripts/slam.py`
- `utils/common_utils.py`
- `scripts/evaluate_saved_phase6.py`
- `tests/test_p6_bam_006_preparation.py`
- `docs/research/phase6_bam/P6_BAM_006_PREFLIGHT_FIX_REPORT.md`
- `docs/research/phase6_bam/P6_BAM_006_PREFLIGHT_REPORT.md` (dated follow-up
  appended; historical blocker preserved)
- Project status, handoff, changelog, derived state, and this session record.
- Machine manifest:
  `results/runtime_artifacts/phase6_bam/p6_bam_006_preflight_fix_20261016/preflight_fix_manifest.json`.

## STOPPED HERE / next action

Researcher review of the preflight-fix report and separate explicit
authorization are required before P6-BAM-006-FULL. The new evaluator and
visualization commands are prepared but unexecuted. Recheck source/config
provenance, Phase 4 checksum, dataset, host/GPU/disk capacity, and unique output
paths immediately before any authorized run. No P6-BAM-006 full-scene run is
authorized by this session.
