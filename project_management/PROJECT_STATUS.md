# SGS-SLAM Project Status

> **CURRENT PROJECT-STATE AUTHORITY.** This file is the canonical
> human-readable source for the current Phase, phase status, latest Session,
> project-wide gate status, baseline status, next milestone, and highest-priority
> next task. Verify it against repository/runtime evidence, then use
> `SESSION_HANDOFF.md` for the exact operational resume point.

Last reconciled: 2026-10-10. Phase 3 runtime bounded reproduction and
full-scene failure characterization are recorded; the close-versus-variant
decision remains for researcher review.

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
Current documentation HEAD: `dd8caa772bd9511c018d298e38c081a679de2c72` (`main`)\
Released source/config baseline and audited commit: `e4183986204242a8bb422624618af07780a49d26` (`main`)\
Research objective: establish and characterize the released SGS-SLAM baseline before proposing changes.\
Dataset: author-distributed semantic Replica package at `data/Replica`\
Canonical scene/config: Replica `room0`, `configs/replica/slam.py`, seed 0

The later HEAD contains documentation/migration commits; a scoped diff verifies
no change from the released baseline in `scripts/`, `utils/`, `datasets/`, or
`configs/`. Runtime evidence remains under Git-ignored `results/` paths.

## Current Phase

Phase: Phase 3 — Baseline Recovery & Reproduction\
Status: READY FOR REVIEW\
Objective: bounded runtime reproduction and full-scene memory/failure characterization are documented; researcher decision is pending.\
Entry condition: Phase 1 documentation and Phase 2 static reproduction audit are complete.\
Exit / stop condition: finish the authorized baseline recovery/reproduction gates; stop before algorithmic research modifications unless separately authorized.

## Latest Session

Session ID: SESSION_002\
Status: READY-FOR-REVIEW\
Started: 2026-10-02\
Last active: 2026-10-10\
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
- Destination-host validation / migration regression: PASS on RTX 5080; see `results/runtime_artifacts/server_validation_2026-10-09/`.
- Phase 3C-4 — bounded online frames 0–99: PASS; guard intercepted index 100; see `results/runtime_artifacts/phase3c4/`.
- Phase 3C-6 — bounded online frames 0–499: PASS; guard intercepted index 500; see `results/runtime_artifacts/phase3c6/`.
- Full-scene runtime characterization: baseline OOM during mapping around frame 1294; allocator-opt runtime-only attempt OOM during mapping at frame 1333; see `docs/experiments/PHASE3_RUNTIME_CONCLUSION_2026-10-10.md`.

Historical snapshot note: `07_phase3b_status.md` records the original dataset-blocked attempt, and the Phase 2 contract records the then-unverified runtime state. Later recovery and runtime reports supersede those earlier statuses; the historical documents are retained as provenance.

## READY FOR REVIEW

- Phase 3 bounded reproduction is verified through frames 0–499 on the RTX 5080.
- Full Replica `room0` frames 0–1999 did not complete: the released baseline OOMed around frame 1294 and the allocator-opt runtime-only attempt OOMed at frame 1333.
- Researcher must choose whether to close Phase 3 with the documented memory limitation or authorize a separately tracked memory-management research variant.

## NOT STARTED

- Phase 3 full-scene execution and paper-protocol evaluation.
- Phase 4 — Mathematical / Algorithmic Verification as runtime work.
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

Released source/config baseline: commit `e4183986204242a8bb422624618af07780a49d26`, branch `main`; source and experiment config have not been modified. The runtime-verified old-host environment was `/home/quan/miniconda3/envs/sgs_slam_baseline`, Python 3.9.25, PyTorch 2.0.1, torchvision 0.15.2, CUDA 11.8, NumPy 1.26.4, OpenCV 4.9.0.80; GTX 1650 Ti with 4096 MiB. Dataset is author-distributed `data/Replica`, scene `room0`, 680×1200, 2,000 frames. The renderer is `diff-gaussian-rasterization-w-depth` at revision `cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110`. Destination-host compatibility remains an operational prerequisite and must not be inferred from the old-host record.

The released online pipeline is runtime-verified through bounded frame 499 on
the RTX 5080. Full-scene `room0` did not complete: baseline OOM occurred around
frame 1294, and allocator-opt runtime-only OOM occurred at frame 1333. This
does not establish full-scene metrics or paper reproduction.

## Current Research Question

Whether to close the released baseline runtime reproduction with its documented
16 GB memory limitation, or authorize a separate memory-management research
variant.

## NEXT MILESTONE

Researcher review of the Phase 3 runtime conclusion and selection of one of:
(A) close Phase 3 with the documented memory limitation; or (B) start an
explicit non-baseline memory-management variant.

## IMMEDIATE OPERATIONAL NEXT TASK

No runtime task is authorized. Review
`docs/experiments/PHASE3_RUNTIME_CONCLUSION_2026-10-10.md` and decide whether to
close Phase 3 with the documented OOM limitation or authorize a separate
memory-management research variant. Keep `SESSION_002` `READY-FOR-REVIEW`.

## NEXT RESEARCH GATE

No next runtime gate is selected. After researcher review, either close Phase 3
baseline runtime reproduction with its documented memory limitation, or create
a separately identified non-baseline memory-management research variant.

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
| Phase status | Historical records said objective remained open | SUPERSEDED | READY FOR REVIEW |
| Latest Session | All rolling/session records name `SESSION_002` | CONSISTENT | `SESSION_002` |
| Session status | Historical records said PAUSED | SUPERSEDED | READY-FOR-REVIEW |
| Started / last active / closed | Historical records agreed on 2026-10-02 / 2026-10-03 / — | SUPERSEDED | Started 2026-10-02; last active 2026-10-10; not completed |
| Latest completed gate | New runtime evidence adds destination validation, Phase 3C-4, and Phase 3C-6 | SUPERSEDED | Bounded PASS through frames 0–499; full-scene failure characterized |
| `STOPPED HERE` | New conclusion records both full-scene OOM boundaries | SUPERSEDED | Baseline OOM around frame 1294; allocator-opt OOM at frame 1333 |
| Immediate `NEXT TASK` | Runtime gates are complete for review | SUPERSEDED | Researcher decision: close Phase 3 with memory limitation or authorize variant |
| Next research gate | No gate selected until the decision is made | SUPERSEDED | Conditional; no runtime gate currently authorized |
| Blockers | Destination validation passed; full-scene memory remains limiting | SUPERSEDED | Memory capacity/residency limitation; paper metrics remain unverified |
| Current HEAD / baseline | Current Git state is newer than historical reconciliation | SUPERSEDED | HEAD `dd8caa...`; released source/config baseline remains `e418398...` |
| Environment prerequisites | Destination validation and bounded migration regression passed | SUPERSEDED | RTX 5080 environment operationally validated |

## Runtime Conclusion Reconciliation — 2026-10-10

The destination host passed validation, and the released online path passed
bounded reproduction through frames 0–499. The released full-scene `room0`
attempt OOMed during mapping around frame 1294; the runtime-only allocator
attempt OOMed during mapping at frame 1333. Neither full-scene attempt reached
frame 1999. No evaluation, paper metric reproduction, post-opt, source/config
change, commit, or push occurred.

Canonical current values are: Phase 3 `READY FOR REVIEW`; latest Session
`SESSION_002` `READY-FOR-REVIEW`; bounded runtime PASS through frames 0–499;
full-scene baseline and allocator-opt failure characterization recorded; next
decision is either close Phase 3 with the documented memory limitation or start
a separately tracked memory-management research variant.
