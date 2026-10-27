# Phase 7 Gate 3 — BCGM Global Cap CPU test report

**Status:** CPU policy/integration tests passed; no CUDA test or workload ran.

## Source behavior

`utils/bcgm.py:select_bounded_candidates` validates flattened candidate/evidence
alignment and computes:

```text
global_available = max_gaussians - N_current
N_admitted = min(N_valid_candidates, max_new_gaussians_per_event,
                 global_available)
```

For valid states `N_current <= max_gaussians`, this equals the configured
admission invariant with `max(0, max_gaussians - N_current)`. For
`N_current > max_gaussians`, the implementation fails closed with `ValueError`
before admission; the CPU tests explicitly cover this behavior rather than
pretending the source clamps an already-invalid map. Gate 3 config and tests
use the actual configured limits: Event Cap 9,000 and Global Cap 4,500,000.

Flag meanings from source:

- `event_saturated`: valid candidates were rejected and the admitted count
  reached the Event Cap.
- `global_saturated`: `N_current + N_admitted >= max_gaussians`; this is the
  Global Cap signal.
- `budget_saturated`: logical OR of `event_saturated` and
  `global_saturated`; it is not a Global Cap-only signal.

Insertion happens through `add_new_gaussians` in `scripts/slam.py`; online
mapping pruning may subsequently remove Gaussians. A lower post-prune count
does not mean the Global Cap failed. The cap governs additions, not pruning.

## CPU test matrix

| Case | Input/expected result | Result |
|---|---|---|
| Below Global Cap | 4,499,990 current, 3 candidates → admit 3 | PASS |
| At Global Cap | 4,500,000 current → admit 0; global saturated | PASS |
| Above Global Cap | 4,500,001 current → fail closed with `ValueError` | PASS |
| Candidates exceed remaining capacity | 7 slots, 20 candidates → admit 7/reject 13 | PASS |
| Both caps bind at same boundary | 9,000 slots, 12,000 candidates → admit 9,000; both flags true | PASS |
| Event Cap only | 9,005 candidates at low map count → admit 9,000; only event flag true | PASS |
| Zero valid candidates | admit 0, reason `no_valid_candidates` | PASS |
| Zero remaining slots | admit 0; no negative count or append | PASS |
| Deterministic ranking/ties | repeated ranking selects identical priority/tie indices | PASS |
| Aligned payload selection | RGB, depth, semantic ID and semantic color indices remain aligned | PASS |

Command:

```bash
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B -m unittest discover -s tests -p 'test_*cpu.py' -v
```

**Result:** 20 tests passed, including 9 existing Phase 7 CPU insertion
regressions and 11 new Gate 3 cap/NVML/config checks. PyTorch tensors in these
tests are CPU tensors; no CUDA API or experiment was invoked. The current
implementation does not enable clone/split densification in Gate 3 config.

Gate 3 full-scene runtime validation of Global Cap remains `NOT_STARTED`.
If no event reaches `global_saturated` during a future run, report the Global
Cap behavior as not runtime-verified. This preparation does not force
activation or tune either limit.
