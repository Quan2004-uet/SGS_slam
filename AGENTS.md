# SGS-SLAM Agent Instructions

This repository is a research codebase for **SGS-SLAM: Semantic Gaussian Splatting for Neural Dense SLAM**, not a production application. Preserve the released baseline, reproduce it before proposing improvements, and keep every compatibility fix, algorithm change, and experiment traceable.

This file is based on the static repository audit in `docs/repository_understanding/`, produced against commit `e4183986204242a8bb422624618af07780a49d26`. If the current HEAD materially differs from that commit, verify affected execution paths before relying on the audit. For current behavior, use this evidence priority:

1. Active source execution path.
2. Active config read-sites.
3. Runtime observation from a controlled run.
4. README and paper descriptions.

Do not silently reconcile disagreements among these sources. Record the discrepancy and its provenance.

## Project Purpose

- Preserve and reproduce the released SGS-SLAM baseline before improving it.
- Treat the repository as research evidence: source, config, command, environment, output, and metric implementation must remain attributable.
- Do not refactor, modernize, upgrade, or repair code merely because it appears old or unusual.
- Do not change an algorithm to make a run succeed until the failure is classified as an environment issue, compatibility recovery, source bug, GPU-capacity issue, or intended research modification.

## Current Research Phase

The project workflow is:

1. **Research Documentation** — **PASS** from the static repository audit.
2. **Baseline Reproduction Audit** — **PASS** (static contract complete).
3. Baseline Recovery & Reproduction.
4. Mathematical / Algorithmic Verification.
5. Limitation Characterization.
6. Research Hypothesis.
7. Proposed Method.
8. Controlled Implementation.
9. Controlled Experiments.
10. Ablation Study.
11. Evaluation & Comparative Analysis.
12. Failure Analysis / Threats to Validity.
13. Thesis / Paper Results.

Some static Phase 4 work exists in the paper-to-code mapping, but runtime verification has not been performed. Do not start Phase 5 or later because an interesting limitation was found. Baseline reproduction must be established first.

## Read Before Editing

Start with `docs/repository_understanding/README.md`. Then read the documents relevant to the task:

| Task area | Required reading |
|---|---|
| Architecture and orchestration | `00_repository_overview.md`, `01_execution_flow.md` |
| State and Gaussian representation | `02_core_state.md`, `03_gaussian_representation.md` |
| Tracking | `04_tracking.md` |
| Mapping and Gaussian lifecycle | `05_mapping.md` |
| Semantic pipeline | `06_semantic_pipeline.md` |
| Keyframes | `07_keyframe_system.md` |
| Losses and optimizers | `08_loss_and_optimization.md` |
| Dataset, config, coordinates, metrics | `09_dataset_and_coordinates.md` |
| VRAM or runtime memory | `10_memory_architecture.md` |
| Paper-to-code claims | `11_paper_code_mapping.md` |
| Research changes | `12_research_modification_surface.md` |
| Runtime unknowns | `13_unknowns_and_runtime_verification.md` |

Do not re-audit the whole repository when the knowledge base already answers the question and relevant source has not changed. Verify only the affected path.

## Repository Architecture

The main online path is:

```text
experiment config
  -> dataset and relative camera poses
  -> first-frame Gaussian-map initialization
  -> per-frame tracking
  -> pixel-driven Gaussian addition
  -> keyframe selection
  -> mapping and optional prune/densify
  -> checkpoint/evaluation/save
```

`scripts/slam.py` is the main online semantic system. `scripts/post_slam_opt.py` is a separate offline optimization regime. `scripts/gaussian_splatting.py` is a separate older/non-semantic training path, not the README's main online entry point. The CUDA rasterizer is an external compiled dependency; its implementation is not vendored here.

## Critical Source Files

Tier A — understand before changing the corresponding subsystem:

- `scripts/slam.py`: dataset and map initialization, tracking, Gaussian addition, keyframe selection, online mapping, checkpoints, and evaluation calls.
- `utils/slam_helpers.py`: camera/Gaussian transforms, renderer argument construction, RGB/depth/semantic passes, and gradient detach boundaries.
- `utils/slam_external.py`: optimizer-aware parameter mutation, pruning, optional clone/split densification, Adam state migration, and LR helpers.
- `utils/keyframe_selection.py`: active geometric keyframe selection.
- `datasets/gradslam_datasets/basedataset.py`: image/depth/semantic preprocessing, intrinsics scaling, relative poses, and device placement.
- `utils/eval_helpers.py`: actual metric definitions and aggregation.
- `scripts/post_slam_opt.py`: offline post-SLAM refinement; do not conflate it with online mapping.

Also account for the duplicated `slam_*` and `gs_*` helper families: online SLAM and post-opt/legacy paths do not necessarily share the same helper implementation.

## Verified Current Implementation Facts

The following facts were verified by static source audit at the audit commit:

1. The online pipeline is concentrated in `scripts/slam.py`.
2. The semantic Gaussian representation uses trainable `semantic_colors` with shape `N x 3`; it is not class logits, one-hot vectors, CLIP/DINO features, or an open-vocabulary embedding.
3. `semantic_ids` are fixed labels/metadata and are excluded from optimizer parameters.
4. Semantic colors are rendered through the Gaussian rasterization pathway in a separate pass analogous to RGB.
5. The released online source does not actively execute the paper-described semantic-mIoU keyframe filter; the relevant block is commented out.
6. Paper-described uncertainty weighting has no verified active implementation/call in the online mapping path.
7. A `do_ba` support branch exists, but **no active online BA execution path has been verified in the audited source**.
8. Default online map growth is primarily pixel-driven Gaussian addition in low-silhouette or new-foreground regions.
9. Gradient clone/split densification is stage- and config-dependent. It is disabled in the shipped online configs and enabled in shipped post-opt configs; never describe it as globally enabled or disabled.
10. Post-SLAM optimization is a separate optimization regime, not online mapping.

These are implementation facts, not guarantees about runtime behavior on an unverified environment.

## Paper vs Released Source

Always distinguish:

- **Paper-described method**.
- **Released implementation**.
- **Runtime-observed behavior**.

Known discrepancies in the audited revision:

- Semantic-mIoU keyframe filtering is described by the paper but inactive/commented in the online source.
- Uncertainty-weighted mapping is described by the paper but has no verified online read/call path.
- BA-related helper logic exists, but no active online caller has been verified.

Do not restore these components during baseline reproduction unless the task explicitly requests a paper-faithful reimplementation. Such work is a separate, named modification, not a baseline fix.

## Baseline Preservation

- Do not modify released source without recording the reason and evidence.
- Keep **upstream baseline**, **reproduction/compatibility fixes**, and **research modifications** logically separable.
- Never mix baseline recovery fixes with a proposed method in one unexplained change.
- Do not refactor unrelated code, mass-format files, or perform broad naming/API cleanup.
- Do not update dependencies merely because the pinned stack is old.
- Do not change reproduction configs to improve results.
- Do not enable, disable, or reinterpret algorithm components without recording provenance.
- Never overwrite a baseline output with a modified or post-optimized output.
- Respect existing branch/commit structure. Do not create a branch or commit unless requested.

## Environment and Dependencies

README and `environment.yml` specify different Python/PyTorch/CUDA stacks. Do not arbitrarily select the newer stack. Phase 2 must identify the authoritative working environment.

The `diff-gaussian-rasterization-w-depth` fork and its CUDA/PyTorch ABI compatibility are critical. Do not replace the renderer or use another fork silently.

Classify every environment change as:

- **A — reproduction requirement**;
- **B — compatibility recovery**;
- **C — algorithm modification**;
- **D — convenience-only change**.

Only A and B belong in baseline recovery, and both require evidence. Record compiler, driver, CUDA, PyTorch, Python, and renderer revision when runtime work begins.

## Configuration Rules

A config key is not active until a source read-site is verified in the executed path.

Trace every behavioral claim as:

```text
config definition -> config load -> source read-site -> executed branch
```

For example, the presence of `use_uncertainty_for_loss` or `use_chamfer` in a config does not prove those features run. Do not infer behavior from option names, comments, or default values alone. Record config snapshots with experiment outputs; do not silently edit them in place.

## Dataset and Coordinate Conventions

Before changing a loader or camera path, verify all of the following at its actual source and runtime boundary:

- RGB shape, channel order, dtype, and range.
- Depth shape, invalid convention, and metric scale.
- Semantic ID and semantic-color formats.
- Intrinsics before and after resize.
- c2w versus w2c convention and first-frame-relative normalization.
- Resize interpolation for RGB, depth, IDs, and semantic colors.
- CPU/GPU placement and tensor lifetime.

The main research datasets in the checked-in experiments are Replica, ScanNet, and ScanNet++. Do not assume a legacy loader works merely because its class exists.

## Online SLAM vs Post-SLAM Optimization

- Online: `scripts/slam.py`.
- Post-opt: `scripts/post_slam_opt.py`.

Keep their output directories and provenance separate. Do not overwrite online results with post-optimized results. Every reported metric must identify whether it came from online SLAM, post-opt, or novel-view evaluation. Do not transfer conclusions between these regimes without evidence; they use different data residency, cameras, iteration schedules, helper families, and densification settings.

## Evaluation Rules

Do not trust a metric based on its variable or function name. Verify its formula and aggregation in `utils/eval_helpers.py` or the actual stage-specific evaluator.

Every reported result must include:

- dataset and scene;
- exact config and frame range;
- online, post-opt, or NVS stage;
- metric implementation;
- source commit and modification state;
- environment and GPU;
- random seed;
- output directory.

When comparing with the paper, report `Paper`, `Reproduced`, and `Delta`. A successful process exit is not a reproduction claim. Confirm expected artifacts and metric protocol first.

## Baseline Reproduction Workflow

Use the smallest bounded step that can answer the current question:

```text
environment audit
  -> dependency/import test
  -> dataset integrity test
  -> renderer smoke test
  -> first-frame initialization
  -> bounded 2-5 frame run
  -> bounded 10-20 frame run
  -> short sequence
  -> one full scene
  -> full evaluation
  -> optional post-opt
  -> paper comparison
```

Do not begin with the full benchmark suite. If a bounded run fails, do not immediately change the algorithm. First classify the failure as environment, dataset, CUDA/compiler, compatibility, source bug, GPU capacity, or expected algorithm behavior. Preserve the failing command and logs.

## Runtime and VRAM Verification

The current memory documentation is a static model, not a measurement. Label claims explicitly as **STATIC EVIDENCE** or **RUNTIME MEASUREMENT**.

Track memory along these independent axes:

- Gaussian parameters, gradients, and Adam moments;
- Gaussian auxiliary arrays;
- renderer forward/backward buffers;
- autograd graph lifetime;
- keyframe GPU tensors;
- current-frame and semantic tensors;
- append/prune/densify transient copies;
- post-opt all-frame preload.

For memory work, read `10_memory_architecture.md` and `13_unknowns_and_runtime_verification.md` first. Do not optimize memory until evidence identifies the allocation source. Prefer bounded instrumentation around one stage over a full-scene profiler run.

## Research Modification Rules

Research modifications begin only after the baseline gate is satisfied or the user explicitly changes scope. Assign identifiers such as `RF-001`, `METHOD-001`, or `EXP-001`.

For each modification record:

- Problem.
- Hypothesis.
- Source location.
- Change.
- Expected effect.
- Potential risk.
- Verification method.
- Observed result.

Prefer one hypothesis, one minimal implementation, and one controlled experiment. Do not simultaneously replace semantic representation, keyframes, losses, optimizer behavior, and memory architecture unless full integration is explicitly requested.

Any new per-Gaussian field must be traced through initialization, pixel-driven append, optimizer inclusion/exclusion, prune/densify resizing, serialization, evaluation, and visualization. Account for both online and post-opt helper families where applicable.

## Controlled Experiment Rules

Hold constant where possible: source baseline, dataset, scene, resolution, frame range, seed, GPU, config, environment, and evaluator. Change only the research variable under test.

Every experiment record must contain:

- Experiment ID and goal.
- Baseline and modification ID.
- Exact command and config snapshot.
- Environment and source commit.
- Output directory.
- Metrics and artifacts.
- Result and interpretation.
- Failure or run-selection policy.

Do not report only the best run unless the selection policy was defined and all attempted runs remain recorded.

## Ablation Rules

For a method with components A, B, and C, do not evaluate only `Baseline` versus `A+B+C`. Use a defensible subset such as:

```text
Baseline
Baseline + A
Baseline + B
Baseline + C
Baseline + A+B
Full
```

The exact matrix may be reduced for compute limits, but document which interactions remain untested and why.

## Documentation Policy

Do not rewrite `docs/repository_understanding/` wholesale. Update only the affected document when new evidence changes a conclusion.

Preserve provenance using forms such as:

```text
STATIC AUDIT: ...
RUNTIME VERIFIED: ...
```

If the knowledge base is wrong, correct the relevant file and include the source pointer, command, runtime evidence, commit, and date. Do not erase the earlier distinction between verified, inferred, and unknown claims.

## Source Modification Policy

Avoid all of the following unless explicitly required and justified:

- unrelated refactoring or mass formatting;
- broad API or symbol renaming;
- dependency upgrades;
- silent config edits;
- algorithm changes during baseline reproduction;
- repairs to dormant code outside the executed path;
- deletion of legacy/unused code;
- renaming `_init_.py` to `__init__.py` without evidence that it causes the scoped failure.

An observed oddity is not automatically a bug. Diagnose first; implement only when the task authorizes implementation.

## Git and Change Hygiene

Before editing:

- inspect `git status --short`;
- identify pre-existing tracked and untracked changes;
- do not overwrite user work;
- do not reset, revert, delete, commit, or push unless requested.

After the task, report:

- files changed and their purpose;
- whether source or config changed;
- tests, smoke checks, or experiments performed;
- checks intentionally not performed;
- unresolved issues and evidence status.

## Command Safety

Do not run a full dataset experiment, long post-opt, benchmark suite, destructive cleanup, environment reinstall, or broad CUDA rebuild unless the task explicitly requires it. Before a potentially expensive command, confirm that it is inside the requested phase and choose the smallest workload that can verify the hypothesis.

Read-only inspection and bounded diagnostics are preferred. Do not download datasets or replace system packages implicitly.

## Project State Source of Truth

Use this precedence for current research state:

1. Repository/source/config/runtime evidence.
2. `project_management/PROJECT_STATUS.md` for current project state.
3. `project_management/SESSION_HANDOFF.md` for the exact operational resume point.
4. `project_management/sessions/SESSION_NNN.md` for permanent session history.
5. `project_management/DECISIONS.md` and `project_management/CHANGELOG.md` for decisions and changes, not current state.
6. `docs/project_state/` documents, which are roadmap, migration, historical, or derived records unless explicitly promoted.

Repository/runtime evidence decides any conflict. Reconcile both canonical
project-management files during a handoff; never choose between conflicting
values arbitrarily. Keep stable Session IDs for coherent work objectives; a
new date or conversation does not create a new Session.

`docs/project_state/CURRENT_STATE.md` is a legacy migration snapshot,
`docs/project_state/state.yaml` is derived machine-readable state, and
`docs/project_state/ROADMAP.md` is planning context. Do not infer the current
Phase, Session, `STOPPED HERE`, or immediate `NEXT TASK` from them when the
canonical project-management files contain current evidence.

### Session Startup

At the beginning of a work period:

1. Read `AGENTS.md`.
2. Verify Git HEAD and inspect `git status --short`.
3. Read `project_management/PROJECT_STATUS.md`.
4. Read `project_management/SESSION_HANDOFF.md`.
5. Read the active or paused `project_management/sessions/SESSION_NNN.md`.
6. Read relevant entries in `project_management/DECISIONS.md`.
7. Read relevant technical documentation and runtime evidence required by the canonical next task.

Read `docs/project_state/CURRENT_STATE.md` only for migration/history or when
the canonical handoff explicitly references it. If the current Session is
paused and its objective continues, reuse its ID and update status only when
work actually resumes.

### Session Shutdown

When the researcher explicitly ends the current work period:

1. Inspect Git and runtime evidence.
2. Update the current `project_management/sessions/SESSION_NNN.md`.
3. Update `project_management/CHANGELOG.md` if needed.
4. Update `project_management/DECISIONS.md` only for durable new decisions.
5. Update `project_management/PROJECT_STATUS.md`.
6. Update `project_management/SESSION_HANDOFF.md` last.
7. Update derived `docs/project_state/state.yaml` only when the workflow explicitly requires it.
8. Do not update historical `docs/project_state/CURRENT_STATE.md` merely to mirror dynamic status.
9. Preserve important runtime evidence outside `/tmp`, verify the next action and blockers, then stop before the next gate.

For unfinished work, keep the Session ID and original start date; mark it
`PAUSED` at shutdown. Mark it `CLOSED` only when the objective is complete.

## Stop Conditions

Stop at the boundary of the requested phase:

- **Baseline Reproduction Audit:** stop after identifying environment candidates, dataset requirements, commands, expected outputs/metrics, blockers, and a reproduction plan. Do not fix code.
- **Environment recovery:** stop when dependency imports and the renderer smoke test pass. Do not run a full scene.
- **Bounded reproduction:** stop at the requested frame or scene limit. Do not expand into a benchmark suite.
- **Diagnosis:** report the verified cause and evidence. Do not implement unless requested.
- **Documentation:** stop after the requested documents and validation checks are complete.

## Reporting Requirements

Use explicit evidence labels when conclusions may be confused:

- `VERIFIED FROM SOURCE`
- `VERIFIED FROM CONFIG`
- `VERIFIED FROM DOCUMENTATION/PAPER`
- `RUNTIME VERIFIED`
- `INFERRED`
- `UNKNOWN / NEEDS RUNTIME VERIFICATION`

Lead with the outcome. Include precise file/function pointers for important behavior. State paper/source/config/runtime discrepancies rather than resolving them by assumption. End every implementation or experiment task with the changed files, validation performed, artifact locations, and remaining unknowns.
