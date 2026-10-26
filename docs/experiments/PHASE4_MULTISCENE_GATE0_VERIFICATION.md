# Phase 4 Multi-Scene Replica — Gate 0 Final Verification

Date: 2026-10-19  
Scope: CPU-only dataset inspection, static source/config/artifact audit, and Gate 1 preparation. No SLAM, CUDA tensor, renderer, evaluation, or source/config execution was performed.  
Repository HEAD: `75d9b7302adeb871308e8105246bb1b95cd804a5`.

## Result

**Dataset Gate 0: PASS (all seven requested scenes, CPU audit).** Every RGB, depth, semantic-ID, and semantic-color image for all 2,000 frames in each scene decoded; filenames/indexes and trajectory integrity passed. Intrinsics and PNG depth scale match the active Replica YAML.

**Phase 4 Variant B revision identified.** The actual room0 output-saving run used commit `68f9060f7ff4d8d141be1d5f71339401327edd06`; its source/config hashes and run metadata are recorded below. The Phase 4 closure tag at `37522db553ff18b96592073f9de699db7fa48600` is a descendant and the audited source/config/helper files listed below are byte-identical. Current HEAD is later and `scripts/slam.py`/`utils/common_utils.py` differ, so it is not the run snapshot.

**Room1 Gate 1: NO-GO.** `nvidia-smi` returned “couldn't communicate with the NVIDIA driver”. No usable GPU state/availability could be verified. Output directories report readable/writable by `os.access`, but no write probe was done. Short-run offline evaluation on room1 has not been demonstrated. Stop at Gate 0.

## Dataset integrity matrix

Audit method: Python + Pillow/NumPy, CPU, read-only; every file was opened and fully decoded (`Image.load()`), not just sampled. The active loader's filename patterns and depth scale were checked in `datasets/gradslam_datasets/replica.py`, `datasets/gradslam_datasets/basedataset.py`, and `configs/data/replica.yaml`. Index lists were required to equal exactly `0..1999`; zero-byte files were rejected. All arrays had 680×1200 spatial dimensions; RGB and semantic color were 3-channel uint8; semantic IDs were grayscale uint8 in the configured range [0,100]; depth was nonnegative integer data in [0,65535]. PIL reports depth as mode `I` / NumPy int32 after decode; the active loader reads it into int64 and divides by 6553.5. The zero value is an expected invalid-depth marker used by the evaluation mask.

| Scene | RGB/depth/ID/color | Raw depth observed | Depth meters (`/6553.5`) | Zero depth pixels | Semantic ID range | Trajectory and rotation checks | Result |
|---|---|---:|---:|---:|---:|---|---|
| room1 | 4 × 2000, contiguous; all decoded | 0–33,910 | 0–5.1743 | 12,698 | 0–98 | 2000 finite 4×4; homogeneous row exact; det 0.9999999999999997–1.0000000000000004; max orthogonality error 4.44e-16 | PASS |
| room2 | 4 × 2000, contiguous; all decoded | 0–32,928 | 0–5.0245 | 72,470 | 0–98 | Same validity; max orthogonality error 4.44e-16 | PASS |
| office0 | 4 × 2000, contiguous; all decoded | 0–28,914 | 0–4.4120 | 945,260 | 0–98 | Same validity; max orthogonality error 4.44e-16 | PASS |
| office1 | 4 × 2000, contiguous; all decoded | 0–22,330 | 0–3.4073 | 20,756 | 0–95 | Same validity; max orthogonality error 4.44e-16 | PASS |
| office2 | 4 × 2000, contiguous; all decoded | 0–39,883 | 0–6.0858 | 23,952,990 | 0–97 | Same validity; max orthogonality error 4.44e-16 | PASS |
| office3 | 4 × 2000, contiguous; all decoded | 0–44,278 | 0–6.7564 | 26,421,834 | 0–97 | Same validity; max orthogonality error 4.44e-16 | PASS |
| office4 | 4 × 2000, contiguous; all decoded | 0–41,768 | 0–6.3734 | 15,814 | 0–97 | Same validity; max orthogonality error 4.44e-16 | PASS |

All trajectories had 2,000 lines × 16 finite values; maximum error in homogeneous last row was 0.0. Rotation determinants were within 0.99–1.01 for all poses. No negative/over-uint16 depth or semantic IDs above the configured limit occurred. The high invalid-depth pixel counts in office2/office3 were retained as observed and are not a decode failure; they are masked as invalid by the released depth metric.

Root `data/Replica/cam_params.json` equals `configs/data/replica.yaml` camera values exactly: `w=1200`, `h=680`, `fx=fy=600`, `cx=599.5`, `cy=339.5`, `scale=6553.5`. The active loader reads the checked-in YAML; the JSON is a matching dataset-side metadata file. No dataset download, rewrite, conversion, or CUDA operation occurred. Dataset provenance/archive hash is documented in `docs/baseline_reproduction/runtime/08_dataset_recovery.md`; this audit did not recompute the archive hash.

## Exact Phase 4 Variant B provenance

| Evidence | Revision / hash | Classification |
|---|---|---|
| Variant B implementation base | `443d3d3251f0ac8d3e0e5489507fe13b506110a4` | **VERIFIED FROM DOCUMENTATION:** `PHASE4_VB001_IMPLEMENTATION_NOTE.md` identifies the implementation base. |
| Actual full-scene output-saving run | `68f9060f7ff4d8d141be1d5f71339401327edd06` | **VERIFIED FROM RUN RECORD:** `PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md` and `run_metadata.json`. |
| Phase 4 closure source | `37522db553ff18b96592073f9de699db7fa48600` | **VERIFIED FROM PROJECT STATE:** tag `phase4-cpu-keyframe-offload-validated`; descendant of `68f9060`. The relevant files below equal the run revision byte-for-byte. |
| Current workspace | `75d9b7302adeb871308e8105246bb1b95cd804a5` | Later source; not the room0 run snapshot. |

Run-revision file hashes:

| File | SHA256 at `68f9060` | Status versus current HEAD |
|---|---|---|
| `scripts/slam.py` | `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3` | Changed later; current adds profiler/BAM integration and checkpoint validation. |
| `configs/replica/slam.py` | `08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3` | Byte-identical. |
| `utils/keyframe_selection.py` | `1dc1711b017884a3f04b8932e2bfd78fbb72704d48bea7f5d6e86bf81679ef87` | Byte-identical. |
| `utils/slam_helpers.py` | `b8c691277a734b08a5676bbedcd92b34b718ec0347e82f56189622d274440f54` | Byte-identical. |
| `utils/slam_external.py` | `65804d58534d708037009c5a064b192cc198fe5a27cafacc55b3fcdf1610e573` | Byte-identical. |
| `utils/eval_helpers.py` | `e94366ca256ec2b51b5d0264a5daba2a895cc0375d7b91e976e4ea0e9e28194e` | Byte-identical. |
| `utils/common_utils.py` | `64b8d0b2795d0e4dc5e48dea279cd2f207bab4ce3122b2f12333c4e2a6d5ee7c` | Changed later; current includes checkpoint validation. |

### Component comparison

| Component | Evidence and conclusion |
|---|---|
| Keyframe selector | **VERIFIED:** `scripts/slam.py` calls the unchanged `utils.keyframe_selection.keyframe_selection_overlap`; file hash is identical at run revision, closure tag, and current HEAD. Candidate slicing/overlap selection was not modified for Variant B. |
| CPU-authoritative keyframe payload | **VERIFIED FROM RUN RECORD + SOURCE:** the run stores detached CPU copies of `color`, `depth`, `semantic_id`, and `semantic_color`; `est_w2c` stays in its existing GPU location. Exact run source hash is recorded. |
| CPU→GPU stage | **VERIFIED FROM RUN RECORD + SOURCE:** selected archived payloads use synchronous `.to(device, non_blocking=False)` without dtype conversion. No pinned buffer/prefetch/cache/eviction. |
| Gaussian mapping | **VERIFIED:** pixel-driven append and mapping helpers are in the run-revision `scripts/slam.py` / `utils/slam_external.py`; those run files are tied to the documented hashes. The run report states 60 mapping iterations, window 24, pruning enabled and GS clone/split densification disabled. Runtime room1 behavior remains UNKNOWN until Gate 1. |
| Tracking | **VERIFIED:** room0 config and run record use 40 tracking iterations, no GT-pose tracking; tracking/loss helpers are in the recorded run revision. Cross-scene tracking behavior is UNKNOWN until Gate 1. |
| Evaluation/export | **VERIFIED:** `utils.eval_helpers.py` is hash-identical; saved-state E1–E4 for room0 passed separately. The output-saving run specifically replaced module `eval` with a no-op to ensure final saving; it did not generate metric outputs. Room1 offline evaluation remains UNKNOWN until short-run check. |
| Unchanged algorithm/config | **VERIFIED FROM ROOM0 RUN REPORT:** no resolution, iteration, mapping-window, keyframe cadence, renderer/loss, semantic, pruning/densification, or RNG change was made. Only the experiment identity, frame horizon, W&B suppression, and output-save harness behavior differed as documented. |

**INFERRED:** the room1 smoke can use the same variant while changing scene/run identity and frame horizon only, if executed from the frozen Phase 4 source and with no method/config tuning. **UNKNOWN:** current HEAD's added profiler/BAM hooks have not been shown byte/behavior equivalent for this requested run; do not use current HEAD for Gate 1 based only on static similarity.

## Output-saving readiness

The actual room0 output directory exists and contains `params.npz`, `params.ply`, `seg_params.ply`, and `keyframe_time_indices.npy`. The run-side manifest/checksum/runtime records are present. This proves the room0 output-saving harness produced these files on room0; it does not prove target-scene room1 output or independent PLY regeneration.

| Output | Source and automatic behavior at run revision | Status for proposed room1 Gate 1 |
|---|---|---|
| `params.npz` | `utils.common_utils.save_params`; final state includes Gaussian arrays, estimated camera arrays, intrinsics/first-frame `w2c`, GT `w2c` sequence, dimensions, semantic arrays, timestep and keyframe indices. In original `scripts/slam.py`, final serialization follows evaluation. | **AVAILABLE VIA VERIFIED SAVE HARNESS.** Historical harness bypasses `eval` then calls original `save_params`; final NPZ is proven on room0. Run again in unique room1 path to verify. |
| `params.ply` | `save_params(..., save_ply=True)` calls `utils.convert_ply.convert` using means, RGB SH DC, opacity, scales, rotations. | **AVAILABLE VIA VERIFIED SAVE HARNESS.** Existing room0 file is present. Converter semantics are statically clear; independent offline rebuild from NPZ was not tested, so regeneration is **INFERRED**, not runtime-verified. |
| `seg_params.ply` | Same converter with `is_semantic=True`, using learned `semantic_colors`; does not encode fixed categorical IDs. | **AVAILABLE VIA VERIFIED SAVE HARNESS.** Existing room0 file is present. This is learned-color visualization, not categorical semantic prediction. Offline regeneration is **INFERRED**. |
| Estimated trajectory | NPZ `cam_unnorm_rots` + `cam_trans`, interpreted as relative w2c in the audited evaluator. No separate trajectory file is written by `save_params`. | NPZ **AVAILABLE**; standalone trajectory CSV/plot is **MISSING** from SLAM auto-save. Minimal offline exporter can derive poses from saved arrays; validated full-room0 ATE exists, but room1/50-frame check is pending. |
| GT trajectory | NPZ `gt_w2c_all_frames`. | **AVAILABLE** in final NPZ. |
| Camera metadata | NPZ `intrinsics`, first-frame `w2c`, `org_width`, `org_height`. | **AVAILABLE** in final NPZ. No separate camera-metadata JSON is produced by the historical SLAM source. |
| Keyframe indices | Embedded NPZ `keyframe_time_indices`; checkpoint sidecar at checkpoints. Standalone `.npy` added by output-save harness. | Embedded **AVAILABLE**; standalone `.npy` requires harness wrapper (as in room0). |
| Runtime/FPS | Source prints average tracking/mapping iteration/frame time; overall wall and FPS computed in harness. | **MISSING from source-only output.** Minimal harness must capture stdout and record start/end, completed frames and derived FPS. |
| VRAM | Not persisted by historical SLAM source. | **MISSING from source-only output.** Minimal harness records peak allocated/reserved via CUDA API; cannot be validated while GPU is inaccessible. |
| RAM | Not persisted by historical SLAM source. | **MISSING from source-only output.** Minimal harness reads `/proc/self/status` and `resource.getrusage`; sidecar needed. |
| Manifest/config/hashes | Not written by historical SLAM source. Historical harness writes `run_metadata.json`, artifact manifest, checksums, timing/memory JSON, result JSON and log. | **MISSING from source-only output; harness can write it.** Need config snapshot in evidence directory, run directory unique, hash source/config/harness. |
| Metric files/plots | Native `eval()` writes per-frame metric files/plots and optionally image outputs, but runs before final save. Room0 output-save harness replaced it with a no-op; separate E4 generated metrics under its own evidence root. | **MISSING from output-save run.** Keep `eval` bypass for safe final save, then run a separate offline evaluator against short NPZ. Need verify 11 view metrics for frames `0,4,9,…,49` and ATE over 50 poses. |

Minimum output-preservation action is a **temporary harness copy only**: adapt the existing verified harness from `/tmp/phase4_vb001_minimal_output_save_full_0_1999_telemetry.py` to scene room1 and max frame 49; point output/evidence paths to the unique directories below; keep the algorithm/config values; retain the no-op evaluation wrapper and original save call; emit the resolved config snapshot, capture logs/resource values, and validate NPZ/PLY/keyframe/checkpoint artifacts. The existing harness is hardcoded for room0 and 2,000 frames and must not be invoked unchanged. This proposed adaptation has not been executed or validated on room1.

## Room1 Gate 1 smoke configuration and preflight

Use the frozen `68f9060…`/Phase 4 closure source snapshot and the same base config hash. Proposed resolved overrides only:

| Key | Proposed value |
|---|---|
| `scene_name` and `viz.scene_name` | `room1` |
| `run_name` | `room1_phase4_vb001_gate1_0_49_r01` |
| `workdir` | `./experiments/Replica` |
| `data.sequence` | `room1` |
| `data.start`, `data.end`, `data.stride` | `0`, `-1`, `1` (keep dataset indexing unchanged) |
| `data.num_frames` | `50` (SLAM loop frames 0–49; dataset still discovers 2,000 aligned frames) |
| Other algorithm fields | unchanged from `configs/replica/slam.py` at SHA `08cc1a…`; seed 0, 40/60 iterations, cadence 5, window 24, full 1200×680, semantics on |
| `use_wandb` | `false` in the output-save harness, as in room0, to avoid external logging |
| `save_checkpoints` | keep config default `true`; at frame 0 expect `params0.npz` and `keyframe_time_indices0.npy` |
| Evaluation during SLAM | harness substitutes a no-op so final serialization is reached; offline evaluation uses the saved short state |

Prospective resolved config snapshot (created as a planning artifact, not executed):
`docs/experiments/PHASE4_MULTISCENE_ROOM1_GATE1_CONFIG.json`, SHA256
`430a22c47154f1c1bf645247498e9fa82abb9c5da0b308e53530645a8a79e555`.
It is constructed from the byte-identical Phase 4 config and contains only
the scene/run identity and 50-frame horizon overrides plus W&B suppression.
The checked-in Python config was not changed.

Proposed isolated paths (both absent at this audit):

- Model/output: `experiments/Replica/room1_phase4_vb001_gate1_0_49_r01/`
- Evidence: `results/runtime_artifacts/phase4_multiscene_gate1/room1_0_49_r01/`
- Offline eval: `results/runtime_artifacts/phase4_multiscene_gate1/room1_0_49_r01/evaluation/`

Expected artifacts: `effective_config.json` (or an equivalent frozen config snapshot in evidence), `params0.npz`, `keyframe_time_indices0.npy`, final `params.npz`, `params.ply`, `seg_params.ply`, standalone `keyframe_time_indices.npy`, stdout/stderr log, manifest/status JSON, timing summary, memory summary, artifact manifest + SHA256 list; then offline per-frame metric values for the 11 selected views, 50-pose ATE mean/RMSE and short RGB/depth/semantic render evidence. The historical run directory had an `eval/` directory but no metric artifacts because eval was intentionally bypassed.

Completion requires frames exactly 0–49 reached; no tracking/mapping exception, CUDA error or OOM; all checked tensors and saved numeric arrays finite; CPU keyframe archive and synchronous staging observed; final NPZ schema and 50 estimated/GT camera entries valid; PLY vertex counts agree with `means3D`; 50-frame keyframe list includes cadence and terminal frame according to source; checkpoint sidecar valid; all hashes/logs persisted; and offline ATE plus RGB/depth/semantic render or metrics complete without overwriting other runs. A valid process exit alone is not PASS.

## Resource and blocker check

- Disk: **99 GiB free**, 89% filesystem used; inode availability is ample (about 56.8M free). Room0 full output used about 0.97 GB, so there is space for one short run by this rough comparison. This does not certify the full seven-scene retention/evaluation plan; recheck before each full scene.
- Directory access: `experiments/Replica` and `results/runtime_artifacts` currently exist and `os.access` reports read/write/execute. This is not an actual write-probe and does not guarantee future mount state. Gate 1 preflight must do a disposable probe inside the new roots and remove only that probe.
- GPU: **NOT AVAILABLE / UNVERIFIED** in this environment. `nvidia-smi --query-gpu=...` failed to communicate with the NVIDIA driver. Do not start Gate 1 until driver/GPU visibility is restored and model/free VRAM is recorded.
- Output collision: both proposed room1 model/evidence paths were absent at audit; room0 path is separate and untouched.
- Source freeze: current HEAD `75d9b73…` is not the room0 run source. Gate 1 must use a controlled checkout/worktree of the frozen Phase 4 revision without altering the shared tree or user untracked files. Exact worktree setup and renderer availability remain to be prepared after GPU recovery.

## Gate 1 decision

**ROOM1 GATE 1: NO-GO.** Dataset Gate 0 passes, source/config provenance is identified, and a no-overwrite smoke configuration is specified. Blockers are (1) CUDA driver/GPU unavailable, (2) write-probe not performed, (3) exact frozen-source execution environment not prepared, and (4) room1 output-save plus offline ATE/render/metric chain not yet runtime-validated. Resolve those prerequisites, then request/record explicit Gate 1 authorization. Do not advance to Gate 2 or full-scene from this report.

## Actions performed and intentionally not performed

Performed: read AGENTS.md, full Task 4 plan, project status/handoff and relevant Phase 4 source/report/artifacts; checked Git HEAD/status; read-only CPU decode/integrity checks for all data; compared historical/current file hashes; inspected output artifacts and available harness; checked disk/inode/access flags and GPU visibility.

Not performed: dataset download or edits; test writes; source/Python-config changes; SLAM, renderer, CUDA, offline metric/evaluation/render, validation script execution, or Gate 1/2/full-scene work. The prospective JSON config snapshot is a planning artifact only. No canonical project-state files were changed.
