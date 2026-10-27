# Phase 7 Gate 1A — Minimal BCGM Implementation Report

**Status:** `PASS_PHASE7_GATE1A_CPU_READY`<br>
**Base commit:** `68f9060f7ff4d8d141be1d5f71339401327edd06`<br>
**Worktree/branch:** `/home/robot/research/SGS_slam_phase7_bcgm`, `phase7-bcgm`<br>
**Scope:** bounded pixel-driven Gaussian admission only. No SLAM or CUDA workload was run.

## Changed files

| File | Purpose |
|---|---|
| `scripts/slam.py` | Optional BCGM switch at the online entry, bounded selection within `add_new_gaussians`, early masked pointcloud construction, and one lightweight JSON record per enabled insertion event. |
| `utils/bcgm.py` | Strict config validation and deterministic candidate selection with event/global count budgets. |
| `tests/test_bcgm_cpu.py` | CPU-only policy tests and function-level comparison with the frozen Phase 4 source. |
| This report | Gate 1A implementation, validation and limitations. |

No Phase 4 source worktree, Phase 5 source/config, tracking, keyframe selection, CPU archive/staging, mapping schedule, loss, optimizer policy, prune/densify implementation, default experiment config, checkpoint, dataset or existing result was edited.

## Switch and configuration contract

`config.get('bcgm')` absent or `{'enabled': False}` selects the original Phase 4 insertion behavior. The on form requires both integer controls:

```text
bcgm.enabled = true
bcgm.max_new_gaussians_per_event = <nonnegative integer>
bcgm.max_gaussians = <nonnegative integer>
```

The event cap is the maximum number of new Gaussians admitted at one pixel-insertion event. The global cap is the maximum total Gaussian count after insertion. Both are inclusive. Zero is valid and skips insertion. Booleans, negative values, floats, unknown keys and missing enabled-mode limits raise `ValueError` before the online SLAM call; direct `rgbd_slam(config)` callers receive the same validation before output creation or device setup. When BCGM is on, online gradient clone/split densification is rejected because that separate growth path is outside this Gate 1A bound. If the initial or resumed map already exceeds the global cap, execution stops before the online frame loop. Numeric cap values are not frozen by Gate 1A; they require the Gate 1B run contract and baseline count evidence.

## Admission algorithm

The existing silhouette/depth-residual candidate detection remains unchanged. BCGM intersects that mask with positive GT depth *before* materializing a new pointcloud. For over-budget candidates, depth-foreground evidence is ranked ahead of silhouette-only evidence. Within each group, larger existing depth residual or lower silhouette is preferred. Equal scores retain ascending flattened pixel index using stable ordering. This ranking is a proposed Phase 7 policy, not a Phase 4 behavior.

```text
if BCGM is disabled:
    execute the frozen Phase 4 candidate, pointcloud and append path
else:
    candidates = existing_nonpresence_mask AND (GT_depth > 0)
    available = min(event_cap, global_cap - current_gaussian_count)
    if candidate_count > available:
        rank candidates deterministically from existing depth/silhouette evidence
        admit the first available candidates
    else:
        admit all valid candidates
    if admitted == 0: skip pointcloud creation and parameter mutation
    otherwise: project only admitted pixel indices, keeping RGB/depth/semantic rows aligned
               initialize and append only admitted Gaussian rows
    emit one BCGM_INSERTION JSON line with counts, caps, saturation and reason
```

The enabled projection uses selected pixel indices before constructing camera/world points, per-pixel Gaussian scale, or semantic/color pointcloud rows. The original full-image projection remains the disabled path. Pixel insertion still precedes per-event Adam construction. No optimizer state is mutated by the admission selector. The Gaussian parameter schema and checkpoint writer are unchanged.

## Instrumentation

Each enabled insertion event prints `BCGM_INSERTION` followed by one JSON object with frame ID, `before`, `after`, `valid_candidates`, `admitted`, `rejected`, `event_cap`, `global_cap`, `event_saturated`, `global_saturated`, `budget_saturated`, and `reason`. Reasons include `no_valid_candidates`, `global_cap_reached`, `event_cap_zero`, `budget_limited`, and `all_candidates_admitted`. The off path prints no BCGM event line and adds no BCGM config key to the base config.

## CPU validation

- Command: `CUDA_VISIBLE_DEVICES='' PYTHONDONTWRITEBYTECODE=1 /home/robot/miniconda3/envs/sgs_slam_5080/bin/python -m unittest discover -s tests -p test_bcgm_cpu.py -v`.
- Result: **9/9 PASS**. Coverage: disabled-path parameter/auxiliary tensor equality against the function extracted from frozen commit `68f9060…`; event/global arithmetic; deterministic priority/ties; zero budget and over-cap handling; strict invalid config and incompatible gradient densification; early selected pointcloud equality and RGB/depth/semantic row alignment; Gaussian schema; and no mutation of a pre-existing Adam state object.
- Source/test syntax compile: **PASS** for `scripts/slam.py`, `utils/bcgm.py`, `tests/test_bcgm_cpu.py` using `compile()` without creating bytecode files.
- `git diff --check`: **PASS** after removing one trailing whitespace introduced by indentation of the unchanged meshgrid branch.

These CPU tests use a deterministic fake renderer to exercise the actual insertion functions without importing the CUDA renderer module. They establish function-level compatibility, not a runtime parity claim for full online SLAM.

## Safety and remaining Gate 1B requirements

The Phase 7 worktree began clean at the frozen source. The Phase 4 multiscene worktree's tracked status remained clean. The Phase 5 worktree remained at HEAD `809d5ea2fd93ce8a97f8082840b44b134bc86519`; its 65 pre-existing untracked paths (expanded Git status) remained present. Only the four Phase 7 paths above changed. No commit or publication was made.

Before GPU Gate 1B, freeze an exact effective config and numeric caps from baseline count evidence, select a bounded frame interval and run IDs, audit dataset/output paths and GPU occupancy, then run a matched Phase 4 versus BCGM-off parity check followed by one BCGM-on bounded run. Measure runtime, Gaussian count and CUDA/NVML memory under the agreed scope. Full-scene quality, speedup, peak VRAM reduction and the approximately 10% quality target remain **NOT VERIFIED**. Candidate ranking may reject thin/new geometry or semantic boundaries; GPU stable-sort cost and actual renderer savings remain unmeasured.
