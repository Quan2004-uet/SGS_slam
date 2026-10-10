# SGS-SLAM Project Status

> **CURRENT PROJECT-STATE AUTHORITY.** This file is the canonical
> human-readable source for the current Phase, phase status, latest Session,
> project-wide gate status, baseline status, next milestone, and highest-priority
> next task. Verify it against repository/runtime evidence, then use
> `SESSION_HANDOFF.md` for the exact operational resume point.

Last reconciled: 2026-10-10. Phase 3 baseline runtime reproduction remains
closed with a documented RTX 5080 16 GB memory limitation. Phase 4 Variant B
Gate 5 passed bounded validation through frames 0–999; `SESSION_003` is
closed and `SESSION_004` is planned for the full-scene gate.

## State Authority

1. Repository/source/config/runtime evidence.
2. This file for current project state.
3. `project_management/SESSION_HANDOFF.md` for operational handoff.
4. `project_management/sessions/SESSION_NNN.md` for permanent history.
5. `project_management/DECISIONS.md` and `CHANGELOG.md` for decisions/changes.
6. `docs/project_state/` for roadmap, migration, historical, or derived records.

If this file and `SESSION_HANDOFF.md` conflict, repository/runtime evidence
decides and both canonical files must be reconciled together.

## Project Identity

Repository: SGS-SLAM — Semantic Gaussian Splatting for Neural Dense SLAM\
Current documentation HEAD: `108d73e7367059a85010e2c19f48419cb3a2741f` (`main`)\
Released source/config baseline and audited commit: `e4183986204242a8bb422624618af07780a49d26` (`main`)\
Research objective: establish and characterize the released SGS-SLAM baseline before proposing changes.\
Dataset: author-distributed semantic Replica package at `data/Replica`\
Canonical scene/config: Replica `room0`, `configs/replica/slam.py`, seed 0

The later HEAD contains documentation/migration commits; a scoped diff verifies
no change from the released baseline in `scripts/`, `utils/`, `datasets/`, or
`configs/`. Runtime evidence remains under Git-ignored `results/` paths.

## Current Phase

Phase: Phase 4 — Memory-management research variant\
Status: IN PROGRESS\
Objective: validate `PHASE4-VB-001` CPU offload of resident keyframe payloads while preserving released online behavior and documenting memory/runtime tradeoffs.\
Entry condition: Phase 3 baseline closure with memory limitation; Phase 4 design and implementation note recorded.\
Exit / stop condition: stop at each bounded gate; full scene and evaluation require separate authorization.

## Latest Session

Session ID: SESSION_003\
Status: CLOSED\
Started: 2026-10-10\
Last active: 2026-10-10\
Closed: 2026-10-10

## COMPLETE

- Phase 1 — Research Documentation: PASS. Static repository understanding is recorded under `docs/repository_understanding/`.
- Phase 2 — Baseline Reproduction Audit: PASS. Static contract and reproduction plan are recorded under `docs/baseline_reproduction/`.
- Phase 3A — Environment and CUDA renderer recovery: PASS. Runtime evidence is in `docs/baseline_reproduction/runtime/00_host_inventory.md` through `04_phase3a_status.md`.
- Phase 3B-R — Dataset recovery: PASS. Author-distributed semantic Replica data is documented in `docs/baseline_reproduction/runtime/08_dataset_recovery.md`.
- Phase 3B-C — OpenCV/NumPy compatibility recovery: PASS. NumPy 1.26.4 was preserved with the documented OpenCV compatibility pin; see `09_opencv_numpy_recovery.md`.
- Phase 3B — Dataset and first-frame initialization: PASS. `room0` frame 0 loaded and 815,998 initial Gaussians were created; see `10_first_frame_gaussian_initialization.md`.
- Phase 3C-1 — bounded online frames 0–4: PASS; see `11_bounded_online_2_5_frames.md`.
- Phase 3C-2 — bounded online frames 0–19: PASS; see `12_bounded_online_20_frames.md`.
- Phase 3C-3 — bounded online frames 0–49: PASS; guard intercepted frame 50; see `13_bounded_online_50_frames.md` and ignored runtime evidence under `results/runtime_artifacts/phase3c3/`.
- Destination-host validation / migration regression: PASS on RTX 5080; see `results/runtime_artifacts/server_validation_2026-10-09/`.
- Phase 3C-4 — bounded online frames 0–99: PASS; guard intercepted index 100; see `results/runtime_artifacts/phase3c4/`.
- Phase 3C-6 — bounded online frames 0–499: PASS; guard intercepted index 500; see `results/runtime_artifacts/phase3c6/`.
- Full-scene runtime characterization: baseline OOM during mapping around frame 1294; allocator-opt runtime-only attempt OOM during mapping at frame 1333; see `docs/experiments/PHASE3_RUNTIME_CONCLUSION_2026-10-10.md`.
- Phase 3 baseline runtime reproduction: CLOSED / COMPLETE WITH MEMORY LIMITATION; see `docs/experiments/PHASE3_BASELINE_CLOSURE_2026-10-10.md`.

## PHASE 4 — VARIANT B CHECKPOINT

- Active research variant: `PHASE4-VB-001` — CPU offload of resident keyframe
  payloads.
- Branch: `phase4-vb-001-cpu-keyframe-offload`; implementation change is
  limited to `scripts/slam.py` for Variant B, with no config change.
- Gate 1: `PASS`; Gate 2: `PASS`; Gate 3 frames 0–99:
  `PASS_FRAME_LIMIT`; Gate 4 frames 0–499: `PASS_FRAME_LIMIT`; Gate 5 frames
  0–999: `PASS_FRAME_LIMIT`.
- Latest completed gate: Gate 5 0–999 `PASS_FRAME_LIMIT`.
- Gate 5 runtime: `7183.993467400001 s`; final Gaussians `4,411,916`;
  resident keyframes `201`; CPU archive `5,248,512,000 B`; GPU archived
  payload `0 B`.
- Gate 5 max allocated/reserved: `5,958,148,096 / 6,949,961,728 B`;
  max RSS/high-water: `7,905,923,072 / 7,957,504,000 B`.
- Latest measured frame-499 long-lived allocated reduction: `2,787,247,616 B`
  (about `75.83%`) versus Phase 3C-6.
- Next gate: full-scene online Variant B frames 0–1999 in `SESSION_004`.
- Full-scene Variant B: `NOT YET RUN`.
- Evaluation and paper metrics: `NOT STARTED` / `NOT REPRODUCED`.
- Variant B is a research variant, not pure released-baseline reproduction;
  Phase 3 baseline closure remains immutable.

Historical snapshot note: `07_phase3b_status.md` records the original dataset-blocked attempt, and the Phase 2 contract records the then-unverified runtime state. Later recovery and runtime reports supersede those earlier statuses; the historical documents are retained as provenance.

## PHASE 3 CLOSURE

- Latest completed bounded gate: Phase 3C-6, frames 0–499, PASS.
- Full Replica `room0` frames 0–1999 did not complete: the released baseline
  OOMed around frame 1294 and the allocator-only retry OOMed around frame 1333.
- Phase 3 baseline runtime reproduction is closed with this documented memory
  limitation. Full-scene PASS and paper-metric reproduction were not achieved.
- No evaluation, ATE, rendering metrics, post-SLAM optimization, or paper
  comparison was run.

## NOT STARTED

- Paper-protocol evaluation and paper-metric reproduction.
- Later research phases, including limitation characterization and method changes.

## BLOCKED

- Research/runtime limitation: full-scene `room0` did not fit the RTX 5080
  16 GB device under the unchanged released online path; runtime-only
  allocator settings were insufficient.
- No dataset, renderer, or numerical-stability blocker is known from the
  recorded bounded runs.
- Paper metrics remain unverified because evaluation and post-opt were not run.

## UNKNOWN / REQUIRES VERIFICATION

- Whether a larger-VRAM released-baseline run completes full `room0`.
- Whether a source-level memory-policy variant can complete 2,000 frames while preserving acceptable metrics.
- Full `room0` baseline completion and paper-protocol metric reproduction.
- Whether reported paper targets can be compared directly to this repository's evaluator and online/post-optimization outputs.

## Current Baseline

Released source/config baseline: commit
`e4183986204242a8bb422624618af07780a49d26`, branch `main`; source and
experiment config have not been modified. The destination runtime evidence was
recorded at HEAD `dd8caa772bd9511c018d298e38c081a679de2c72` using
`/home/robot/miniconda3/envs/sgs_slam_5080`, Python 3.10.22, PyTorch
2.7.1+cu128, CUDA runtime 12.8, NumPy 1.26.4, OpenCV 4.9.0.80, and an NVIDIA
GeForce RTX 5080 16 GB class GPU. Dataset is author-distributed `data/Replica`,
scene `room0`, 680×1200, 2,000 frames. The renderer is
`diff-gaussian-rasterization-w-depth` at revision
`cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110`.

The released online pipeline is runtime-verified through bounded frame 499 on
the RTX 5080. Full-scene `room0` did not complete: baseline OOM occurred around
frame 1294, and allocator-opt runtime-only OOM occurred at frame 1333. Phase 3
is closed with this memory limitation. This does not establish full-scene
metrics or reproduce SGS-SLAM paper results.

## Current Research Question

Whether the next authorized work should use larger-VRAM infrastructure for the
unchanged baseline or begin a separately identified Phase 4 memory-management
research variant.

## NEXT MILESTONE

Review Gate 5 and run the separately authorized full-scene Variant B online
gate frames 0–1999 in `SESSION_004`. Evaluation remains prohibited until
full-scene online PASS and required outputs are saved. Larger-VRAM
infrastructure remains the alternative for pure-baseline full-scene execution.

## IMMEDIATE OPERATIONAL NEXT TASK

Prepare `SESSION_004` for full-scene Variant B online Replica `room0` frames
0–1999. Preserve implementation/config and stop for review at the full-scene
boundary or any required failure condition.

## NEXT RESEARCH GATE

Full-scene Variant B online frames 0–1999. Evaluation status remains
`NOT STARTED`; paper metrics reproduced remains `false`. Evaluation remains
prohibited until full-scene online PASS and required outputs are saved.

## Phase 4 Gate 5 Reconciliation — 2026-10-10

The current runtime evidence supersedes the earlier Phase 4 checkpoint above:
Gate 5 completed Replica `room0` frames 0–999 with `PASS_FRAME_LIMIT`,
intercepting dataset index 1000 before the real loader. The run recorded
4,411,916 final Gaussians, 201 logical keyframes, 5,248,512,000 B CPU archive,
0 B GPU archived payload, maximum allocated/reserved
5,958,148,096 / 6,949,961,728 B, maximum RSS/high-water
7,905,923,072 / 7,957,504,000 B, and runtime 7,183.993467400001 s.
`SESSION_003` is closed; `SESSION_004` is planned for the full-scene Variant B
online gate. Evaluation, paper metrics, ATE, rendering/semantic metrics, and
post-SLAM optimization remain unstarted and prohibited.

## Historical Consistency Reconciliation — 2026-10-05

The table below is retained as historical provenance. The 2026-10-10 runtime
conclusion reconciliation at the end of this file supersedes its field values.

| State source | Classification before reconciliation | Reconciled role |
|---|---|---|
| Repository/Git/runtime artifacts | CONSISTENT | Highest-priority ground truth |
| `project_management/PROJECT_STATUS.md` | STALE header/HEAD/NEXT TASK | Canonical current project state |
| `project_management/SESSION_HANDOFF.md` | HISTORICAL label but newer migration handoff | Canonical operational handoff |
| `project_management/sessions/SESSION_002.md` | CONSISTENT historical research record | Permanent Session history; not current task authority |
| `project_management/DECISIONS.md` | STALE authority note | Durable decision log; not current state |
| `docs/project_state/CURRENT_STATE.md` | CONFLICTING independent authority | Historical/legacy migration snapshot |
| `docs/project_state/state.yaml` | DERIVED values presented without authority metadata | Derived machine-readable snapshot |
| `docs/project_state/ROADMAP.md` | CONSISTENT planning snapshot | Roadmap only; not current Session/NEXT TASK authority |

### Field-level consistency table

| Field | Evidence across prior state files | Classification | Canonical value |
|---|---|---|---|
| Current Phase | All state sources name Phase 3 | CONSISTENT | Phase 3 — Baseline Recovery & Reproduction |
| Phase status | Historical records said objective remained open | SUPERSEDED | CLOSED / COMPLETE WITH MEMORY LIMITATION |
| Latest Session | All rolling/session records name `SESSION_002` | CONSISTENT | `SESSION_002` |
| Session status | Historical records said PAUSED | SUPERSEDED | READY-FOR-CLOSURE-REVIEW |
| Started / last active / closed | Historical records agreed on 2026-10-02 / 2026-10-03 / — | SUPERSEDED | Started 2026-10-02; last active 2026-10-10; not completed |
| Latest completed gate | New runtime evidence adds destination validation, Phase 3C-4, and Phase 3C-6 | SUPERSEDED | Bounded PASS through frames 0–499; full-scene failure characterized |
| `STOPPED HERE` | New conclusion records both full-scene OOM boundaries | SUPERSEDED | Baseline OOM around frame 1294; allocator-opt OOM at frame 1333 |
| Immediate `NEXT TASK` | Runtime gates are complete for review | SUPERSEDED | Review closure documentation; formally close `SESSION_002` or open a new Phase 4 variant Session |
| Next research gate | No gate selected until the decision is made | SUPERSEDED | Conditional; no runtime gate currently authorized |
| Blockers | Destination validation passed; full-scene memory remains limiting | SUPERSEDED | Memory capacity/residency limitation; paper metrics remain unverified |
| Current HEAD / baseline | Current Git state is newer than historical reconciliation | SUPERSEDED | HEAD `108d73e...`; released source/config baseline remains `e418398...` |
| Environment prerequisites | Destination validation and bounded migration regression passed | SUPERSEDED | RTX 5080 environment operationally validated |

## Runtime Conclusion Reconciliation — 2026-10-10

The destination host passed validation, and the released online path passed
bounded reproduction through frames 0–499. The released full-scene `room0`
attempt OOMed during mapping around frame 1294; the runtime-only allocator
attempt OOMed during mapping at frame 1333. Neither full-scene attempt reached
frame 1999. No evaluation, paper metric reproduction, post-opt, source/config
change, commit, or push occurred.

Canonical current values are: Phase 3 `CLOSED / COMPLETE WITH MEMORY
LIMITATION`; latest Session `SESSION_002` `READY-FOR-CLOSURE-REVIEW`; bounded
runtime PASS through frames 0–499; full-scene baseline and allocator-opt OOM
characterization recorded; no paper metrics or evaluation were run. The next
authorized phase, if any, must use larger VRAM for the pure baseline or be a
separately tracked Phase 4 memory-management research variant.
