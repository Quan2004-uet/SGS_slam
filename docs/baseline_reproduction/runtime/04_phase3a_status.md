# Phase 3A Status

## Result

**Phase 3A Status: PASS**

The environment now qualifies as a `RUNTIME VERIFIED BASELINE ENVIRONMENT` for
the narrow Phase 3A contract.

| Criterion | Evidence | Status |
|---|---|---|
| Host inventory recorded | `00_host_inventory.md` | PASS |
| Isolated environment exists | `sgs_slam_baseline` | PASS |
| Exact PyTorch import | 2.0.1 | PASS |
| CUDA available | `True`, one GTX 1650 Ti | PASS |
| CUDA allocation/backward | finite tensor and gradient | PASS |
| Core dependencies import | `pip check` clean and import log | PASS |
| Exact renderer built | pinned `cb65e4b...` | PASS |
| Exact renderer imports | required symbols present | PASS |
| Minimal renderer forward | finite 16x16 output/depth, positive radius | PASS |
| Minimal renderer backward | finite nonzero gradients | PASS |
| Algorithm/source/config untouched | final Git checks | PASS |
| Environment snapshot | `sgs_slam_baseline_environment.yml` | PASS |

## Static audit updated by runtime evidence

```text
STATIC AUDIT:
README Python 3.9 / PyTorch 2.0.1 / CUDA 11.8 was the preferred but unverified
candidate; renderer ABI compatibility was unknown.

RUNTIME VERIFIED:
That candidate works on this host after documented NumPy/OpenCV/MKL/SciPy and
build-dependency compatibility pins. The exact renderer commit builds, imports,
and executes differentiable CUDA forward/backward on SM 7.5.
```

## Boundaries and remaining risks

- The GPU has only 4 GiB VRAM, below the paper's stated typical `<12 GB` envelope;
  full-resolution baseline feasibility remains unknown and is not implied by the
  8.55 MB smoke test.
- No dataset is present or was downloaded.
- W&B config/credentials remain a later-stage blocker; W&B was only imported.
- No SLAM entry point, evaluator, or post-opt was run.
- The environment export is a runtime snapshot, not a proposal to replace the
  repository's `environment.yml`.

## Stop condition

The requested stop condition is met. Next gate:

**Phase 3B — Dataset Integrity & First-Frame Initialization**

Do not start it without a separate task/authorization.
