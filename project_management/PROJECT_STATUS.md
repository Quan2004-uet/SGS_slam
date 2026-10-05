# SGS-SLAM Project Status

> **CURRENT PROJECT-STATE AUTHORITY.** This file is the canonical
> human-readable source for the current Phase, phase status, latest Session,
> project-wide gate status, baseline status, next milestone, and highest-priority
> next task. Verify it against repository/runtime evidence, then use
> `SESSION_HANDOFF.md` for the exact operational resume point.

Last reconciled: 2026-10-05. No research gate or Session status changed during
the documentation-only reconciliation.

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
Current documentation HEAD at reconciliation start: `63943487478cd876339e8ec1660e91bab1215fab` (`main`)\
Released source/config baseline and audited commit: `e4183986204242a8bb422624618af07780a49d26` (`main`)\
Research objective: establish and characterize the released SGS-SLAM baseline before proposing changes.\
Dataset: author-distributed semantic Replica package at `data/Replica`\
Canonical scene/config: Replica `room0`, `configs/replica/slam.py`, seed 0

Git inspection before this documentation task found branch `main` aligned with
`origin/main` and only `2402.03246v6.pdf` untracked. The later HEAD contains
documentation/migration commits; a scoped diff verifies no change from the
released baseline in `scripts/`, `utils/`, `datasets/`, or `configs/`. Phase
3C-3 raw evidence remains under Git-ignored
`results/runtime_artifacts/phase3c3/`.

## Current Phase

Phase: Phase 3 — Baseline Recovery & Reproduction\
Status: IN PROGRESS\
Objective: complete bounded runtime verification of the released online pipeline.\
Entry condition: Phase 1 documentation and Phase 2 static reproduction audit are complete.\
Exit / stop condition: finish the authorized baseline recovery/reproduction gates; stop before algorithmic research modifications unless separately authorized.

## Latest Session

Session ID: SESSION_002\
Status: PAUSED\
Started: 2026-10-02\
Last active: 2026-10-03\
Closed: —

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

Historical snapshot note: `07_phase3b_status.md` records the original dataset-blocked attempt, and the Phase 2 contract records the then-unverified runtime state. Later recovery and runtime reports supersede those earlier statuses; the historical documents are retained as provenance.

## IN PROGRESS

- Phase 3 — Baseline Recovery & Reproduction remains unfinished and is paused at the handoff. The 50-frame prefix is verified; the next bounded horizon has not started.

## NOT STARTED

- Phase 3C-4 — bounded online reproduction through frame 99.
- Phase 3 full-scene execution and paper-protocol evaluation.
- Phase 4 — Mathematical / Algorithmic Verification as runtime work.
- Later research phases, including limitation characterization and method changes.

## BLOCKED

- Research blocker: none known from the completed Phase 3C-3 algorithm/dataset
  evidence.
- Operational prerequisite, not classified as a research blocker: restore the
  migration assets, inspect the destination GPU/driver/CUDA/compiler/PyTorch
  ABI, rebuild the pinned renderer, and pass the recorded migration regressions
  before Phase 3C-4.

## UNKNOWN / REQUIRES VERIFICATION

- Runtime behavior, memory sufficiency, and numerical stability beyond frame 49.
- Full `room0` baseline completion and paper-protocol metric reproduction.
- Whether reported paper targets can be compared directly to this repository's evaluator and online/post-optimization outputs.
- Any runtime claims beyond the frame ranges documented in the runtime evidence files.

## Current Baseline

Released source/config baseline: commit `e4183986204242a8bb422624618af07780a49d26`, branch `main`; source and experiment config have not been modified. The runtime-verified old-host environment was `/home/quan/miniconda3/envs/sgs_slam_baseline`, Python 3.9.25, PyTorch 2.0.1, torchvision 0.15.2, CUDA 11.8, NumPy 1.26.4, OpenCV 4.9.0.80; GTX 1650 Ti with 4096 MiB. Dataset is author-distributed `data/Replica`, scene `room0`, 680×1200, 2,000 frames. The renderer is `diff-gaussian-rasterization-w-depth` at revision `cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110`. Destination-host compatibility remains an operational prerequisite and must not be inferred from the old-host record.

The released online pipeline has runtime evidence through frame 49 only. This does not establish full-scene metrics or full-scene VRAM sufficiency. Compatibility recovery is documented separately from source/config behavior.

## Current Research Question

How do Gaussian count, keyframe residency, optimizer state, numerical stability, and GPU memory evolve beyond the verified 50-frame prefix under the unchanged released `room0` online config?

## NEXT MILESTONE

Complete a guarded 100-frame run (indices 0–99) from frame 0, then review actual growth and memory evidence before selecting another horizon.

## IMMEDIATE OPERATIONAL NEXT TASK

Restore and verify the GitHub/Hugging Face migration on the destination GPU
server using `docs/project_state/SERVER_MIGRATION.md`. Validate the destination
GPU/runtime and pinned renderer, then run only the documented migration
regressions. Keep `SESSION_002` `PAUSED` during restore validation and do not
start Phase 3C-4 as part of that work.

## NEXT RESEARCH GATE

After the operational prerequisite passes, resume `SESSION_002` and run
**Phase 3C-4 — bounded online reproduction over frames 0–99**, continuously
from frame 0, with a strict guard before real dataset index 100. Preserve the
released algorithm/config, retain separate JSON/log evidence, and stop after
reviewing finite state and VRAM trends. This gate has not started.

## Consistency Reconciliation — 2026-10-05

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
| Phase status | `PROJECT_STATUS.md` says IN PROGRESS; other records say objective remains open | CONSISTENT | IN PROGRESS |
| Latest Session | All rolling/session records name `SESSION_002` | CONSISTENT | `SESSION_002` |
| Session status | All records say PAUSED | CONSISTENT | PAUSED |
| Started / last active / closed | Session/project records agree on 2026-10-02 / 2026-10-03 / — | CONSISTENT | Started 2026-10-02; last research activity 2026-10-03; not closed |
| Latest completed gate | Runtime JSON/report and all state records say Phase 3C-3 PASS | CONSISTENT | Phase 3C-3, frames 0–49 |
| `STOPPED HERE` | Runtime JSON, handoff, and Session history agree index 50 was blocked before real loading | CONSISTENT | After frame 49; before loading frame 50 |
| Immediate `NEXT TASK` | Old `PROJECT_STATUS.md` said run Phase 3C-4 directly; later handoff/migration state requires destination restore first | CONFLICTING | Restore/validate destination GPU runtime; keep Session paused |
| Next research gate | All planning/runtime records identify Phase 3C-4 | CONSISTENT | Frames 0–99; guard before real index 100 |
| Blockers | No known algorithm/dataset blocker; destination compatibility has not been validated | DERIVED distinction | No known research blocker; operational restore/runtime prerequisite remains |
| Current HEAD / baseline | Older snapshots called `e418398...` current HEAD; Git now reports `639434...`; source/config baseline remains `e418398...` | STALE current-HEAD field; CONSISTENT baseline | Documentation HEAD `639434...`; released baseline `e418398...` |
| Environment prerequisites | Old-host environment passed; destination-host ABI/GPU checks are pending | HISTORICAL + UNKNOWN destination state | Revalidate destination GPU/runtime before Phase 3C-4 |

Canonical reconciled values are: Phase 3 `IN PROGRESS`; latest Session
`SESSION_002` `PAUSED`; latest gate Phase 3C-3 PASS over frames 0–49; stopped
before loading index 50; immediate operational task is destination runtime
restore/validation; next research gate is Phase 3C-4 over frames 0–99 with a
guard before index 100.
