# Phase 7 Gate 1B Handoff — 2026-10-27 (Asia/Tokyo)

> **Branch-local current handoff.** This Phase 7 worktree is separate from
> `/home/robot/research/SGS_slam`. Do not interpret the inherited Phase 4
> snapshot below as current Phase 7 state.

## Current Phase 7 status

- Gate 0: `PASS_PHASE7_GATE0_DESIGN_READY`.
- Gate 1A: `PASS_PHASE7_GATE1A_CPU_READY` (9/9 CPU tests, as recorded in its
  report).
- Gate 1B preparation: `PASS_PHASE7_GATE1B_PREFLIGHT_READY`.
- Gate 1B final validation: `PASS_WITH_LIMITATIONS`.
- Gate 2: `NOT_STARTED`.
- Session: `SESSION_ID_UNRESOLVED`; no ACTIVE Phase 7 session is identified in
  the available ledger. Do not assign or infer a session ID from this note.

## Gate 1B completion and evidence

Three matched arms completed Replica `room0`, frames 0–99: P4 Original
(`p7_bcgm_g1b_room0_p4_0_99_r01`), BCGM-off
(`p7_bcgm_g1b_room0_off_0_99_r01`), and BCGM-on
(`p7_bcgm_g1b_room0_on_0_99_r01`). Each summary records process exit 0, normal
SLAM return, 100 saved poses, and 99 insertion events. Checkpoint ZIP CRC,
NumPy load with pickle disabled, numerical finiteness, and Gaussian-field
alignment passed for all three.

| Metric | P4 Original | BCGM-off | BCGM-on |
|---|---:|---:|---:|
| Runtime (s) | 403.883937 | 402.661730 | 400.355505 |
| NVML peak (MiB) | 4073 | 4025 | 3955 |
| CUDA peak allocated (MiB) | 1951.903320 | 1962.746094 | 1922.678711 |
| CUDA peak reserved (MiB) | 2898 | 2812 | 2824 |
| Final Gaussians | 1404952 | 1406470 | 1375645 |
| PSNR (dB) | 40.521147 | 40.287181 | 40.558197 |
| MS-SSIM | 0.994983 | 0.994788 | 0.995030 |
| LPIPS | 0.030688 | 0.032529 | 0.031424 |
| Depth L1 (m) | 0.001940 | 0.001907 | 0.001888 |
| Semantic mIoU | 0.917751 | 0.918328 | 0.918203 |

Metric values are means of 21 saved training-view scores where applicable.
Depth evaluator `rmse.txt` is elementwise equal to L1; conventional Depth
RMSE is not measured. ATE appears only as rounded aligned mean translation
error in the console, not true or full-precision ATE RMSE. Single run per arm;
do not claim statistical significance, full-scene performance, or proven
speedup. Mapping FPS excludes pixel insertion. NVML is device-wide and sampled
at 1 Hz.

BCGM-on settings: event cap 9,000; global count cap 4,500,000. Across 99
events: 599,547 valid candidates, 564,346 admitted, 35,201 rejected, 14 event
cap activations, zero global cap activations; maximum admitted per event
9,000. All 7 admission invariants passed. The global cap behavior remains
unvalidated because it never activated.

Primary records:

- `docs/research/phase7/PHASE7_GATE1B_FINAL_VALIDATION_REPORT.md`
- `docs/research/phase7/PHASE7_GATE1B_METRIC_COMPARISON.md`
- `docs/research/phase7/PHASE7_GATE1B_EVIDENCE_MANIFEST.json`
- Evidence: `results/runtime_artifacts/phase7_gate1b/<run_id>/`
- Models/evaluations: `experiments/Replica/<run_id>/`

The manifest enumerates and hashes 309 run files (1,104,316,640 logical
bytes) and 13 source/config/runtime dependencies. It is local and read-only,
but no independent backup or WORM storage is verified. Read-only scans found
no Phase 4/5 result files modified after the runs began; missing pre-run
hashes prevent exhaustive historical bytewise non-overwrite proof.

## Source and Git state

- Worktree: `/home/robot/research/SGS_slam_phase7_bcgm`.
- Branch: `phase7-bcgm`; HEAD:
  `68f9060f7ff4d8d141be1d5f71339401327edd06`.
- Frozen Phase 4 source SHA256:
  `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3`.
- Phase 7 `scripts/slam.py` SHA256:
  `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999`.
- BCGM module SHA256:
  `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400`.
- At handoff start: one tracked modified algorithm file (`scripts/slam.py`)
  and 13 untracked Phase 7 paths. These include Gate 1B configs, runner,
  worker, tests, BCGM module and reports. No commit or push has been made.
- Main repository remains on `phase5-profiling-instrumentation` at
  `809d5ea2fd93ce8a97f8082840b44b134bc86519`; its local untracked files were
  left untouched. Phase 4 worktree remains at the frozen base. No other
  worktree was modified by this closure.

## Storage, limits, and next session

At the Gate 1B evidence closure, filesystem free space was about 27.8 GiB;
recheck before any run. The exact value is time-sensitive.

**Recommended first task:** read this handoff, verify the source and saved
artifacts against the manifest, recheck free disk and GPU/process state, then
prepare (do not execute until separately authorized) the Gate 2 experiment
design for Replica `room0`, frames 0–499. Gate 2 has not started. Preserve
separate run IDs and output paths; do not overwrite Gate 1B or Phase 4/5/6
artifacts. Carry forward the Gate 1B limitations and metric definitions.

This work period ends with Gate 1B evidence recorded and handed off. Because
the active session ID is unresolved, the project session ledger was not
closed or altered. The branch-local project-status overlay records this
boundary without creating a new session.
