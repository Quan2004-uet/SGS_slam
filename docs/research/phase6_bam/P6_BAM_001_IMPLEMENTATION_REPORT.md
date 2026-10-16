# P6-BAM-001 — Minimal Implementation and CPU Validation

Date: 2026-10-16. Status: `PASS_P6_BAM_001_CPU_STATIC`.
Evidence: `VERIFIED FROM SOURCE` and CPU/static tests only. `NOT_RUNTIME_VALIDATED`.
Base HEAD: `c6742854b884495ece0cc18fbc9296c1d5e31371`, a descendant of P5-LEAN-001 `c3a76c0`. Phase 4 tag resolves to `37522db553ff18b96592073f9de699db7fa48600`.

## Modification and exact files

- `utils/mapping_budget.py`: frozen CPU-only decision, pruning safety, scalar telemetry adapter and codebook.
- `scripts/slam.py`: host shape count around append, one decision before mapping optimizer iterations, actual iteration counter, one record per mapping event.
- `configs/replica/phase6_bam_base.py`: isolated Phase 6 output root and unique run-ID guard.
- `configs/replica/phase6_bam_v0.py`, `phase6_bam_va.py`, `phase6_bam_vfixed30.py`, `phase6_bam_vfixed45.py`: dedicated controls and candidate.
- `tests/test_mapping_budget.py`: CPU invariants and static integration checks.
- This report and the session, status, handoff, changelog, roadmap and derived state files: provenance only.

No released Replica config, tracking, keyframe policy, CPU archive, Gaussian append/prune/densify helper, optimizer/loss, or profiler implementation was edited.

## Source integration

`scripts/slam.py:rgbd_slam` enters mapping at frame 0 or `(time_idx+1) % map_every == 0`. It takes `pre_num_pts` from `params['means3D'].shape[0]` before the conditional append. Only when `add_new_gaussians` executes on a frame greater than zero does it take `post_num_pts`; equal counts mean zero append, while `None` means append did not execute. The decision follows keyframe selection and precedes the mapping optimizer loop. The original loop body remains intact. Frame 0 uses all 60 configured iterations. The controller is called once per mapping event.

V-A's sole novelty signal is `(post-pre)/pre`; count and fraction are host Python metadata from tensor shapes. Candidate thresholds are `<=0.01` for LOW 30, `<=0.05` for MID 45, and above that FULL 60. They are **experimental, not validated**. V-FIXED30/45 use the named budget after frame 0. OFF/missing control returns the configured count (60 in Replica), with no RNG, render, tensor transfer, or CUDA call. Invalid signal/config falls back to the configured count with a reason. Enabled gradient densification or opacity-reset pruning also falls back to the full count because shortening may skip their scheduled effects.

The active Replica prune schedule includes zero-based iterations 0 and 20. The helper derives the last scheduled prune within the configured horizon and refuses a reduced budget that would skip it; hence the candidate minimum is 21. It does not clip bad budgets silently. The mapping loop has no separate iteration scheduler; progress reporting and keyframe sampling remain inside the existing loop. Shorter ON runs deliberately perform fewer NumPy view-selection draws, a quality and subsequent-RNG risk requiring runtime measurement. OFF performs the same number of draws as before.

## Config and artifact isolation

Each wrapper keeps the released `tracking.num_iters=40`, `mapping.num_iters=60`, seed, mapping parameters, and Phase 4 CPU offload path. V0 is the **current Phase 6 source with the controller disabled**, not a historical Phase 4 reproduction. `P6_BAM_RUN_ID` must be a new `p6_bam_*` identifier. Config loading fails if the result or corresponding telemetry directory exists. Results are rooted at `results/runtime_artifacts/phase6_bam/`; LIGHT telemetry, when enabled for a separately approved run, is rooted below its `telemetry/` subdirectory. No P6 run was launched.

`VERIFIED FROM SOURCE`: `scripts/slam.py` builds save, checkpoint and eval paths from `workdir/run_name`, but its main entry point uses `os.makedirs(..., exist_ok=True)` and copies only the selected wrapper to `config.py`. Thus the wrapper's import-time existence guard is the current protection; a directory created between config import and the main-entry write would still be writable. For P6-BAM-002, freeze a unique ID, verify the target is absent immediately before execution, and preserve the effective config and the shared wrapper/base files with run metadata. A stronger atomic run-directory reservation would require an output-path change outside the authorized mapping hook and is deferred. The Phase 4 immutable checkpoint and all historical outputs were untouched.

## Telemetry

When the existing profiler is LIGHT/DETAILED, `mapping.budget` records once per mapping event: frame ID (record field), event ID (same as frame ID because at most one mapping event occurs per frame), enabled, signal valid, pre/post counts, added count/fraction, tier code, configured/effective/executed iterations, fallback code, pruning enabled, and required iteration count for the final scheduled prune. The existing bounded JSONL and summary paths are used. Missing counts are encoded as `-1` and missing fraction as `-1.0`; these are telemetry sentinels, not controller signals. Tier codes are `FULL=0`, `MID=1`, `LOW=2`, `FIXED=3`. Fallback codes are defined in `utils/mapping_budget.py`; enabled runs also print the literal fallback reason once per mapping event. OFF profiling mode writes no profiler records. No per-iteration logging, CUDA synchronization or persistent GPU allocation was added.

## CPU/static validation

Command: `PYTHONDONTWRITEBYTECODE=1 CUDA_VISIBLE_DEVICES='' /home/robot/miniconda3/envs/sgs_slam_5080/bin/python -m unittest tests.test_mapping_budget tests.test_performance_profiler -v` — **37 passed, 0 failed** (14 controller, 23 existing profiler).

AST parse of `scripts/slam.py`, helper, four wrappers, shared base and test: **8 passed**. `git diff --check`: **passed**. Static diff audit found only the mapping hook in `scripts/slam.py`; released config and helper paths were untouched. No online frames, CUDA kernels, GPU profiler, dataset access, package install, or quality/speed measurement ran.

## Remaining risks and next gate

`UNKNOWN / NEEDS RUNTIME VERIFICATION`: OFF equivalence in a fresh controlled run, actual append distributions, proportion of LOW/MID/FULL selections, telemetry schema in a live run, pruning coverage, reconstruction and tracking quality, speedup, and RNG-related run variability. Historical R2 OFF/OFF final Gaussian counts differed by 644 over frames 0–10; CPU tests cannot resolve that variability.

Next proposed task: `P6-BAM-002 — Matched LIGHT 0–10 Smoke Validation`, with separate authorization. Use new immutable P6 directories and effective config snapshots. Do not infer speedup or quality equivalence from this gate.

## FIX1 clarification (2026-10-16)

The original 37-test CPU/static PASS is preserved. A follow-up source review raised a possible cross-event budget leak. The source actually reloaded `mapping.num_iters` inside each frame before its mapping event, so that leak did not occur in `e644df4`. FIX1 renamed and separated configured and effective event budgets explicitly, and added a source-AST event-sequence regression. See `P6_BAM_001_FIX1_REPORT.md`. Runtime status remains `NOT_RUNTIME_VALIDATED`.
