# Phase 7 Gate 1B — final validation and evidence closure

**Decision: `PASS_WITH_LIMITATIONS`**, restricted to the three matched Replica room0 frames 0–99 runs. The seven BCGM admission checks and saved-artifact validation pass, but exhaustive historical non-overwrite proof is unavailable without pre-run hashes of all Phase 4/5/6 artifacts. This is a bounded functional and measurement validation, not a full-scene or statistical performance claim. No experiment was rerun for this closure.

## Source and run identity

Frozen Phase 4 commit: `68f9060f7ff4d8d141be1d5f71339401327edd06` at `/home/robot/research/SGS_slam_phase4_multiscene`. Phase 7 branch `phase7-bcgm` has the same HEAD plus Gate 1A uncommitted source; source file hashes and arm config hashes match the executed `run_summary.json` records and the Gate 1B run contract. P4 source SHA `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3`; Phase 7 source SHA `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999`; BCGM module SHA `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400`. The common input config hash excluding run identity and BCGM switch is `21fe6546fec201254f320f090cdac4b5d3a00f54c666834075834968df859935`; the matching runtime config hash after the same exclusions is `3ac18e7c5e38fe4413b75cf894833ef7645d320eb9c5be1a0042148cd1768c5c`. Input/runtime config snapshots are both preserved: SLAM adds the same default tracking/data keys in all three runtime dictionaries, so bytewise input/runtime hashes differ without a matched-setting discrepancy. The exact files and hashes are in the manifest.

| Arm | Run ID | Completion | Final checkpoint Gaussians | Hashed files | Logical bytes |
|---|---|---|---:|---:|---:|
| p4 | `p7_bcgm_g1b_room0_p4_0_99_r01` | exit 0; 100 poses; 99 append events | 1,404,952 | 103 | 369,987,071 |
| off | `p7_bcgm_g1b_room0_off_0_99_r01` | exit 0; 100 poses; 99 append events | 1,406,470 | 103 | 370,244,666 |
| on | `p7_bcgm_g1b_room0_on_0_99_r01` | exit 0; 100 poses; 99 append events | 1,375,645 | 103 | 364,084,903 |

All three `run_summary.json` records say exit code 0, normal `rgbd_slam` return, successful final CUDA synchronization, 99 insertion records and 100 saved poses. `params.npz` and `params0.npz` in every arm pass ZIP CRC, NumPy `allow_pickle=False` load, numeric finiteness and Gaussian-field alignment; final `means3D` counts agree with the summaries. Initial checkpoint count is 815,998 in every arm. Pose arrays contain 100 GT transforms and 100 estimated camera slots. Each of six saved evaluator arrays has exactly 21 finite entries; each model directory also contains PLY exports, plots, rendered RGB/depth/semantic frames, copied config and keyframe indices. This validates readability, not independent replication of rendering/evaluation.

## BCGM-on insertion admission: 7/7 PASS

For `p7_bcgm_g1b_room0_on_0_99_r01`, the 99 JSON log records and 99 independent worker insertion records agree on every frame's before/after count and admitted increment:

1. Frames 1–99 occur exactly once and in order: **PASS**.
2. `valid_candidates = admitted + rejected`, all nonnegative: **PASS**.
3. Logged append increments match worker before/after counts: **PASS**.
4. Every admitted count is at most the 9,000 event cap: **PASS**.
5. Every post-insertion count remains at or below the 4,500,000 global cap: **PASS**.
6. Saturation flags and reason agree with counts: **PASS**.
7. Totals agree with the saved record: 599,547 candidates, 564,346 admitted, 35,201 rejected, 14 event-cap activations, zero global-cap activations, maximum 9,000 admitted: **PASS**.

Event-cap frames: 1, 2, 3, 19–29. The final checkpoint has 1,375,645 Gaussians; the last post-insertion trace has 1,375,717. The 72-count difference can result from later mapping/pruning, so the final checkpoint is not expected to equal the last insertion count. The global cap did not activate and its capacity behavior remains **NOT_VERIFIED** at runtime.

## Artifact preservation and storage

All three model and evidence paths are confined under `/home/robot/research/SGS_slam_phase7_bcgm` and distinct from Phase 4/5/6 paths. At closure, the Phase 4 frozen worktree and the original Phase 5 worktree have no tracked changes. Read-only `find` scans found no file under either original/Phase 4 `results/` or `experiments/` modified after the first Gate 1B run began (2026-10-26 18:08 UTC); the known Phase 4 full-scene telemetry anchor at `/home/robot/research/SGS_slam/results/runtime_artifacts/phase4_vb001_full_scene_0_1999/phase4_vb001_full_scene_0_1999_results.json` predates these runs. No overwritten Phase 4/5/6 artifact was observed. **Pre-run hashes for all historical artifacts were not available**, so exhaustive bytewise non-overwrite proof is **NOT_VERIFIED**. The hashed manifest covers the three Gate 1B runs and their source dependencies, not an independent backup.

Hashed run files: 309 regular files, 1,104,316,640 logical bytes (1.028 GiB). Filesystem free at closure: 29,851,250,688 bytes (27.801 GiB); used 902,969,561,088 of 982,820,896,768 bytes. Preserve all run artifacts; free space should be rechecked before any later experiment.

## Limitations and gate boundary

- Only one run per arm, one scene, 100 frames, training-view evaluation. No confidence interval, full-scene quality claim, or statistically proven speedup.
- The 4.5M global cap never bound; the observed event-cap behavior is the bounded feature validated here.
- Conventional Depth RMSE and true ATE RMSE are **NOT_MEASURED** by the saved evaluator. ATE console values are rounded aligned *mean* errors; full-precision ATE is not in the saved metric arrays.
- Stage mapping FPS excludes insertion. Unsynchronized host insertion-call time cannot isolate GPU selection cost. NVML is sampled device-wide at 1 Hz.
- No independent backup or filesystem WORM preservation is verified. Manifest hashes establish current local identity only.
- The Phase 7 source/configs and this closure package are still uncommitted; no GitHub/Hugging Face publication occurs here.

**Stop:** Gate 1B evidence closure only. Gate 2, further GPU runs and publication are outside this task.
