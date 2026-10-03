# Scope and Baseline

## Immutable baseline identity

- Repository: SGS-SLAM released source. `VERIFIED FROM SOURCE`
- Branch at audit: `main`. `VERIFIED FROM SOURCE` (Git metadata)
- Commit: `e4183986204242a8bb422624618af07780a49d26`.
  `VERIFIED FROM SOURCE` (Git metadata)
- The current HEAD equals the commit recorded by the repository-understanding
  audit and root `AGENTS.md`. No commit substitution or fork is authorized.
- Pre-audit worktree entries were untracked: `2402.03246v6.pdf`, `AGENTS.md`, and
  `docs/`. No tracked source/config diff was present. `VERIFIED FROM SOURCE`
  (pre-flight Git inspection)

Phase 3 must record the full commit and working-tree state with every result.
It must not reset these untracked research artifacts.

## Canonical first reproduction

| Dimension | Definition | Evidence |
|---|---|---|
| Dataset | Replica semantic dataset expected by the repository | README + source |
| Scene | `room0` | Both checked-in Replica configs; README command defaults |
| Seed | `0` | Both checked-in Replica configs |
| Resolution | 1200x680 (width x height) | `configs/replica/slam.py`, `configs/data/replica.yaml` |
| Online stage | `scripts/slam.py` with `configs/replica/slam.py` | README + source |
| Post-opt stage | `scripts/post_slam_opt.py` with `configs/replica/post_slam_opt.py` | README + source |
| Semantic inputs | Precomputed semantic ID and semantic-color PNGs | Dataset source |
| Online output | `experiments/Replica/room0_0/` | Config + source |
| Post-opt output | `experiments/Replica_postopt/postopt_room0_0/` | Config + source |

`room0` is recommended because it is the exact default of both configs, the
README commands require no experiment-file substitution, and Tables 1, 3, and 6
of the paper report room0 targets. This is a provenance-based choice, not a claim
that room0 is the easiest scene. `INFERRED`

Risks are full-resolution cost, unmeasured Gaussian growth, W&B being enabled in
the online config, and the absence of a local dataset. `UNKNOWN / NEEDS RUNTIME
VERIFICATION` for actual compute and memory.

## Baseline stages must remain separate

1. **Online released baseline:** tracked poses plus incrementally built map from
   `scripts/slam.py`.
2. **Post-SLAM released baseline:** offline Gaussian refinement using the online
   `params.npz`, ground-truth cameras, frame stride 20, and 15,000 iterations.
3. **Standalone evaluation:** reloads a saved map and evaluates either training
   or NVS split according to `data.use_train_split`.

Post-opt does not establish online SLAM reproduction. Online and post-opt outputs
must have separate result records and metric labels.

## Acceptance definitions

### Environment reproduced

Exact expectations: selected versions and provenance are recorded; Python imports
PyTorch and dependencies; `torch.cuda` sees the intended GPU; the pinned renderer
imports and completes a minimal forward/backward smoke test. Runtime success is
not established by this audit.

### Dataset verified

Exact expectations: required modality counts agree; trajectory covers all selected
frames; frame 0 loads with expected tensor shapes/types; depth conversion,
intrinsics scaling, semantic files, and relative pose are checked.

### Online SLAM reproduced

Exact expectations: the released online path completes one full `room0` run at
the checked-in settings, creates all required online artifacts, performs final
evaluation, and preserves logs/config/commit/environment provenance. Merely
starting or completing a bounded run is not full online reproduction.

### Paper-level approximately reproduced

The correct code metric implementation and evaluation stage must first be
identified. Results must be reported as `Paper`, `Reproduced`, and `Delta`, with
hardware, seed, environment, stage, and protocol. Exact numerical equality is not
expected across GPU/dependency/seed differences. The paper specifies no acceptance
tolerance, so this contract deliberately defines none. Any later numerical band
must be labeled `PROPOSED TOLERANCE — NOT PAPER-SPECIFIED` and justified before
examining favorable runs.
