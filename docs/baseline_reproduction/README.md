# SGS-SLAM Baseline Reproduction Contract

## Phase status

**Phase 2 — Baseline Reproduction Audit: PASS (static contract complete).**

This status means the released baseline, required inputs, candidate environment,
commands, artifacts, evaluator behavior, paper targets, blockers, and bounded
Phase 3 gates have been identified. It does **not** mean that the environment,
dataset, renderer, SLAM run, or paper numbers have been runtime-verified.

Evidence labels used throughout this directory are:

- `VERIFIED FROM SOURCE`
- `VERIFIED FROM CONFIG`
- `VERIFIED FROM README`
- `VERIFIED FROM PAPER`
- `INFERRED`
- `UNKNOWN / NEEDS RUNTIME VERIFICATION`

## Quick contract

| Question | Contract answer |
|---|---|
| Baseline | Repository `main` at `e4183986204242a8bb422624618af07780a49d26`; current HEAD exactly matches. |
| First dataset | Replica semantic release expected by this repository. |
| First scene | `room0`, seed `0`, full 680x1200 resolution. |
| Online config | `configs/replica/slam.py` |
| Online command | `python scripts/slam.py configs/replica/slam.py` |
| Post-opt config | `configs/replica/post_slam_opt.py` |
| Post-opt command | `python scripts/post_slam_opt.py configs/replica/post_slam_opt.py` |
| Standalone train-view evaluation | `python scripts/eval_novel_view.py configs/replica/slam.py` |
| Preferred environment candidate | README stack: Python 3.9, PyTorch 2.0.1, torchvision 0.15.2, torchaudio 2.0.2, CUDA 11.8, plus `requirements.txt`. |
| Alternative candidate | `environment.yml`: Python 3.10, PyTorch 1.12.1, torchvision 0.13.1, torchaudio 0.12.1, CUDA toolkit 11.6. |
| Renderer | `diff-gaussian-rasterization-w-depth`, commit `cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110`, imported as `diff_gaussian_rasterization`. |
| Primary room0 paper targets | PSNR 32.50 dB, SSIM 0.976, LPIPS 0.070, semantic mIoU 92.95%, ATE RMSE 0.46 cm. |
| Phase 3 next gate | Gate 0: record host/GPU/driver/toolkit/compiler capability without changing the host. |

The environment preference is based on the repository's current explicit README
installation recipe, not runtime proof. The paper does not identify its Python,
PyTorch, or CUDA software versions. Treat both candidates as unverified until the
bounded import and renderer gates pass.

## Immediate blockers and ambiguities

- No `data/` directory exists in the audited worktree; Replica must be obtained
  before dataset gates. `VERIFIED FROM SOURCE` (repository-tree inspection)
- README and `environment.yml` specify incompatible software stacks.
  `VERIFIED FROM README`; `VERIFIED FROM CONFIG`
- The CUDA rasterizer is a pinned external extension and is sensitive to the
  selected PyTorch/CUDA/compiler ABI. `INFERRED`; build/import must be verified.
- The default online config enables W&B with placeholder entity `my-project`.
  Phase 3 must either supply valid W&B provenance or use an explicitly recorded
  reproduction-config copy; never silently edit the checked-in baseline config.
  `VERIFIED FROM CONFIG`
- The paper does not state unambiguously whether its training-view rendering and
  semantic tables are from the final online map or post-SLAM optimization.
  `UNKNOWN / NEEDS RUNTIME VERIFICATION`
- The released ATE and depth “RMSE” implementations do not implement conventional
  RMS reductions. Direct comparison with paper labels requires protocol care.
  `VERIFIED FROM SOURCE`

## Documents

1. [Scope and baseline](00_scope_and_baseline.md)
2. [Environment audit](01_environment_audit.md)
3. [Dataset requirements](02_dataset_requirements.md)
4. [Configuration and execution](03_config_and_execution.md)
5. [Outputs and artifacts](04_outputs_and_artifacts.md)
6. [Evaluation protocol](05_evaluation_protocol.md)
7. [Paper target metrics](06_paper_target_metrics.md)
8. [Paper/source discrepancies](07_paper_source_discrepancies.md)
9. [Known blockers](08_known_blockers.md)
10. [Phase 3 bounded test plan](09_phase3_bounded_test_plan.md)

The deeper static implementation audit remains in
[`docs/repository_understanding/`](../repository_understanding/README.md). Do not
re-audit the repository before Phase 3 unless source paths materially change.
