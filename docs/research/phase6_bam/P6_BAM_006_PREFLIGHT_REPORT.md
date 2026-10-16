# P6-BAM-006 — Full-Scene Readiness Preflight

**Preflight result: `BLOCKED_P6_BAM_006_PREFLIGHT`.** This is a readiness
audit only. No SLAM frame, tracking, mapping, rendering, evaluation, PLY
conversion, or large CUDA allocation was run. The 0–1999 experiment was not
started and must receive separate researcher authorization after this report
is reviewed.

The historical artifacts and source checkpoint are intact. The host RTX 5080
and saved-state evaluation/3D visualization paths are available. The blocker
is the *current* V-A2 wrapper/output-recovery contract: it does not explicitly
bound the run or select LIGHT profiling, and its periodic checkpoints do not
preserve frame 1999 before the evaluator, although final serialization occurs
only after the evaluator returns. The safe changes needed are experiment-only
and are specified below; they were not made under this preflight-only request.

## Repository and historical integrity

- Branch: `phase5-profiling-instrumentation`.
- HEAD: `36284a2cbccd3e148a628c44f6fbcba139ac3ceb`.
- Phase 4 annotated tag peels to `37522db553ff18b96592073f9de699db7fa48600`.
- P6-BAM-005 source worktree timer is committed at HEAD. Its file hash is
  `0604b00f12f288a49e28bf1386c6d7b8089b1642acfe095358693b0b557c52ce`.
- No tracked worktree modifications were present; `git diff --check` passed.
  Existing historical untracked Phase 5 reports, `SESSION_007`–`SESSION_010`,
  `P6_BAM_003_QA_001_REPORT.md`, and `vds` were preserved.
- The current `utils/eval_helpers.py` is unchanged from the Phase 4 validated
  tag. Current changes relative to Phase 4 source are in the online SLAM path
  and added profiler/controller code, not the metric helper. Those are
  attributable to the P6 instrumentation/controller work and the enabled
  V-A2 budget control, not unexplained worktree edits.
- Historical statuses remain unchanged: P5-LEAN-001 PASS; P6-BAM-001 and
  FIX1 CPU/static PASS; P6-BAM-002 smoke PASS; P6-BAM-003 historical
  INCONCLUSIVE; P6-BAM-003-R1 V-A2 0–49 screening PASS; P6-BAM-005
  0–499 quality-constrained PASS. None establishes a full-scene result.

Relevant current source/config SHA256 values:

| File | SHA256 |
|---|---|
| `scripts/slam.py` | `0604b00f12f288a49e28bf1386c6d7b8089b1642acfe095358693b0b557c52ce` |
| `utils/mapping_budget.py` | `bf5cda289f9d451b795a4b5f3faa38f29cf7f8e7a27103f4cc5ee3e7b82d573b` |
| `utils/eval_helpers.py` | `e94366ca256ec2b51b5d0264a5daba2a895cc0375d7b91e976e4ea0e9e28194e` |
| `utils/common_utils.py` | `64b8d0b2795d0e4dc5e48dea279cd2f207bab4ce3122b2f12333c4e2a6d5ee7c` |
| `utils/convert_ply.py` | `342717d8d3b94992878ee8eaac945eb1a9f4697ef9f811b19115104fcb6f94e7` |
| `utils/slam_helpers.py` | `b8c691277a734b08a5676bbedcd92b34b718ec0347e82f56189622d274440f54` |
| `utils/slam_external.py` | `65804d58534d708037009c5a064b192cc198fe5a27cafacc55b3fcdf1610e573` |
| `utils/performance_profiler.py` | `c22acfa483ea350d26c43b56c5081e6f95c56b43e343cb87450d7d8953de3514` |
| `scripts/eval_novel_view.py` | `2d37e1804bd7d35232f1cc5ed66eda30d8e6ae62acd1ddb966b1cf61bfe74a94` |
| `scripts/visualization/render_final_maps.py` | `6c24f65dbac4960d681afd7be95995ca7649d4496a36d4d2b356ce17c5051d5f` |
| `scripts/visualization/visualize_full_scene_v3a.py` | `492c3d3bbdbc9d1ee41aa30aad2898277c71b7bc6220e44c6fd891bef503d9ad` |
| `scripts/visualization/audit_final_map.py` | `4f0b7b7b7a6ca434405faea5748dc5a0b6c9d9c6484326120260d7ad77987b06` |
| `utils/recon_helpers.py` | `c31df7240cc30162c8b2ffd08c4f90b8bb68f4b8b2105b62334b7d929799830c` |
| `datasets/gradslam_datasets/replica.py` | `52531edd0e2d38092c09fb9221f108b043324ff32edb660ba4b19d195cc3cce4` |
| `datasets/gradslam_datasets/basedataset.py` | `2bc0861a99ff83c509c96a8d672e199a5c23ac4ec9ae6a771dbd0f788cf27422` |
| `configs/replica/slam.py` | `08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3` |
| `configs/replica/phase6_bam_base.py` | `849d19e6bbbe5eb7a6a0fbd7c0bf6f782af58a021e630f7e87ea40310402cd2a` |
| `configs/replica/phase6_bam_v0.py` | `2592efcb79e467a773f1508774db570284d81fcc2f3a687f1b7671f14ab5d76c` |
| `configs/replica/phase6_bam_va2.py` | `9dc62a8b883b0da49ed472a94cf7ce43bb2dd126d9ce30fe0195ab751767d6b2` |
| `configs/replica/phase6_bam_va.py` | `0376f842742659665bb96f2a3f07428d2b9e63836ec92842dffcef95385c152a` |
| `configs/replica/phase6_bam_vfixed30.py` | `ea41e0d2b06ae05d813fc615da49e9656ba1b0fb3660d09cd9d6e112d28f5e46` |
| `configs/replica/phase6_bam_vfixed45.py` | `33eb7f46879f2fd2f9e47dc3840a833551c76fcd0f509b9836328a91c619a8e2` |
| `configs/data/replica.yaml` | `4c1e33544bef24c146c4ec9a622bb3ad7a314168db8d192c191db08bad3edf58` |

The current Phase 6 wrapper was CPU-loaded with a unique disposable probe run
ID; it did not create that output directory. It resolves V-A2 to the expected
45/60/60 budgets and 0.01/0.05 thresholds, but inherits `start=0`, `end=-1`,
`num_frames=-1`, sets profiling mode `off`, and retains checkpoint interval
500. The released Replica configuration has `eval_every=5`. The P6-BAM-005
effective 500-frame snapshots instead used `eval_every=50`, interval 499, and
LIGHT profiling. A reviewed full-scene experiment-only wrapper is therefore
required; do not launch `phase6_bam_va2.py` directly.

## Phase 4 reference checkpoint

Reference path:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`

- Size: 322,361,795 bytes.
- SHA256: `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`
  (matches the expected reference).
- `zipfile.ZipFile.testzip()` returned no corrupt member. The CPU-only NPZ
  scan loaded one member at a time; all required numeric members were finite.
- Gaussian count: 4,956,467. Required means, RGB, rotation, opacity, scale,
  semantic-color and semantic-ID arrays are present. `semantic_ids` are
  `uint8` (observed IDs 0–98); `semantic_colors` are float32 Nx3.
- Estimated rotations/translations and GT relative-w2c trajectory each contain
  2,000 entries; all were finite. Keyframe index count is 402 and the tail is
  `[1989, 1994, 1998, 1999]`. Intrinsics are 600/600 with principal point
  599.5/339.5; stored size is 1200x680.
- Companion reference hashes also match the saved Phase 4 closure evidence:
  `params.ply` `d9b4d22ba11c73f8c1d6d0ea5f874bbb5d3254f25b333362a502a5940f604502`,
  `seg_params.ply` `6cd5a258a8147fe0c0515d04ea702d618f82c2411fc464ab9bfebd2fc2f3b726`,
  standalone `keyframe_time_indices.npy`
  `fb91f05c127819f6666259668c4d88a2d36a46f575659f576adde37b227e6d37`.
- Phase 4 source/config provenance is documented in the output-save and E4
  reports. Its final output was generated at run HEAD
  `68f9060f7ff4d8d141be1d5f71339401327edd06`; E4 metrics used the saved state
  and evaluator HEAD `63adf3aed8ae2201a46d11cec473672f9e91fd0e`.

Phase 4 E4 preserved values (not recomputed here): ATE Mean 0.00274075 m,
supplementary true ATE RMSE 0.00339827 m, PSNR 33.313067 dB, MS-SSIM
0.979470, LPIPS-Alex 0.067555, Depth L1 0.00495158 m, semantic-color mIoU
0.916585. E4 used all 2,000 poses and the 401 image sample
`{0} ∪ {5k−1 | k=1..400}` = `[0,4,9,...,1994,1999]`.

## Configuration and bounded-run audit

**Verified from config/source:** P6-BAM-005 V-A2 used Replica room0, 680x1200,
seed 0, tracking 40, configured mapping maximum 60, `map_every=1`, keyframe
interval 5, mapping window 24, semantic loading (101 configured IDs), the
existing CPU keyframe archive, and the V-A2 controller 45/60/60 at thresholds
0.01/0.05. Its 500-frame run used LIGHT profiling and completed 500 events.
The mapping-prune schedule remains `stop_after=20`, `prune_every=20`; the
controller's required minimum of 21 mapping iterations makes zero-based prune
iteration 20 reachable at every V-A2 tier.

Required effective full-scene values for a future reviewed wrapper:

| Field | Required value | Source status |
|---|---|---|
| Dataset / scene | Replica / room0 | Existing config |
| `start,end,stride,num_frames` | `0,2000,1,2000` | **Not explicit in current wrapper**; set and CPU-verify |
| Resolution / semantics | 680x1200 / enabled, 101 configured IDs | Inherited, verified |
| Seed / tracking / mapping maximum | 0 / 40 / 60 | Inherited, verified |
| Mapping frequency / keyframes / window | 1 / 5 / 24 | Inherited, verified |
| CPU keyframe offload | Active source path, previously runtime-verified | No config toggle; preserve source |
| Controller | adaptive 45/60/60, 0.01/0.05 | Existing V-A2 wrapper |
| Profiler | LIGHT | **Current V-A2 wrapper says OFF**; set LIGHT |
| Evaluation sample | `eval_every=5`, 401 views | Matches Phase 4 E4; P6-BAM-005 500 used 50 |
| Checkpoint | `save_checkpoints=true`, `checkpoint_interval=1999` | **Current wrapper interval 500**; required to emit `params1999.npz` before evaluation |

The proposed interval 1999 is source-supported: the loop writes a checkpoint
when `time_idx % checkpoint_interval == 0`, so it saves indices 0 and 1999.
This provides a pre-evaluation frame-1999 model snapshot and associated
`keyframe_time_indices1999.npy`. It is not the complete final archive: final
GT trajectory, intrinsics, image dimensions, `timestep`, and in-NPZ keyframe
indices are augmented after online evaluation. It is sufficient as a model
recovery source when paired with frozen config, source, dataset/trajectory and
the standalone keyframe index.

**Recommended checkpoint-first recovery contract:** adapt the already validated
Phase 4 output-save harness pattern for this unique P6 run: suppress only the
post-loop in-process `eval` call (no online behavior changes), allow released
final metadata assembly and `save_params` to create full `params.npz`, RGB and
semantic PLYs, then evaluate that saved state using the Phase 4 E4 selective
saved-state protocol into a new Phase 6 evaluation directory. Retain the
interval-1999 checkpoint as a pre-evaluation fallback. This is a measurement /
output harness, not an algorithm change, but is **not implemented or approved
for execution here**. The current normal path evaluates before final metadata
assembly and final serialization; if evaluation raises, full `params.npz` and
PLYs are absent. Periodic default-500 snapshots stop at frame 1500.

## Host, GPU, RAM, disk and dataset

GPU was checked directly on the host after the restricted execution context
could not access NVML. No tensor or CUDA workload was allocated.

- GPU: NVIDIA GeForce RTX 5080, driver 580.167.08; `nvidia-smi` CUDA version
  13.0. Free VRAM 15,370 MiB of 16,303 MiB (464 MiB reserved; 471 MiB used).
  PyTorch 2.7.1+cu128, bundled CUDA 12.8, Python 3.10.22; `torch.cuda.is_available()`
  true and one device visible. This was a metadata/availability query only.
- Background GPU activity at query: 10% utilization, 1% memory utilization;
  visible processes were Xorg (36 and 133 MiB) and
  `gnome-remote-desktop-daemon` (264 MiB). No competing compute process was
  listed. This is a point-in-time check, not a reservation or future guarantee.
- Host memory: 123 GiB total, 117 GiB available; 2 GiB swap, unused. Cgroup
  memory limits were not exposed at `/sys/fs/cgroup/memory.max`; `ulimit` did
  not impose a data/virtual-memory cap. Historical Phase 4 process HWM was
  17.96 GB and P6-BAM-005 process peak RSS was about 7.43 GB. Phase 4 logical
  CPU keyframe archive was about 10.5 GB. Static available RAM exceeds these
  observations by a wide margin, but does not guarantee full-run success.
- Disk: repository, environment, dataset and proposed output are on
  `/dev/sda2`, 916 GB total, 768 GB used, 101 GB available (89% used).
  Inodes are 7% used. `quota` is not installed, so per-user quota was not
  verified. Existing evidence sizes: Phase 4 full output 951 MiB; P6-BAM-005
  500-frame run outputs 637–643 MiB, each 19 MiB evaluation subtree, and
  9–11 MiB telemetry. Scaling the observed 19 MiB/11-view evaluation subtree
  to 401 views is about 0.7 GiB; adding a Phase 4-sized final NPZ/PLY set,
  growing interval checkpoints, full LIGHT telemetry and derived visual
  artifacts suggests budgeting **at least 10 GiB** for run/evaluation outputs
  and a further **5 GiB** for derived 3D visualization/logging. This is a
  conservative planning allowance, not a precise prediction. Even after
  reserving 20 GiB operational headroom, current free space is adequate; check
  again immediately before launch and evaluation.
- Dataset `data/Replica/room0`: 2,000 files each in `frames`, `depths`,
  `semantic_ids`, and `semantic_colors`; `traj.txt` has 2,000 lines. Indices
  0, 999 and 1999 exist and passed CPU PIL header/decode verification at
  1200x680 (RGB, 16-bit depth, grayscale IDs, RGB semantic colors). No
  extraction or transfer is indicated. The exact run should still fail closed
  if loader validation finds any missing intermediate index.

Historical capacity context: Phase 4 full-scene peak GPU allocated/reserved
was 5.818/7.189 GB at 4.956M Gaussians; its final RSS/HWM was 17.96 GB. P6-BAM-005
500-frame V-A2 peaked at 3.778/4.582 GB for 2.270M Gaussians. A 2,000-frame V-A2
map may grow to millions of Gaussians; the Phase 4 and P6 peaks do not bound its
memory. No OOM-free guarantee is made.

## Saving, evaluation and comparability

`utils/eval_helpers.eval` is the same file as the Phase 4 validated tag. The
Phase 4 evaluator contract is available and was runtime-validated by E4 from a
saved checkpoint:

- 401 training-camera renders for RGB, depth/silhouette, and semantic color,
  with IDs `[0,4,9,14,...,1994,1999]` at `eval_every=5`.
- RGB: GT-depth-positive mask; released PSNR; `ssim.txt` is actually
  `pytorch_msssim.ms_ssim`; TorchMetrics LPIPS-Alex (`normalize=True`, clamped
  inputs); unweighted per-frame means.
- Depth: Replica scale 6553.5; valid GT depth mask; masked mean absolute error
  in meters.
- Semantic: learned `semantic_colors` render recolored to each frame's GT
  palette, GT black ignored; this is not a direct comparison of saved
  `semantic_ids`.
- Trajectory: relative w2c matrices, normalized real-first `[w,x,y,z]`
  estimated quaternions, Horn rigid alignment without scale, all 2,000 poses.
  The released printed “ATE RMSE” is mean Euclidean aligned translation error;
  report it as ATE Mean and separately compute true RMSE from the same errors.

The native standalone `scripts/eval_novel_view.py` directly loads NPZ but
converts metadata tensors to CUDA unnecessarily and has no staged schema
validation. The Phase 4 E4 saved-state route used a selective-loading harness
and produced all metrics from the final archive without rerunning SLAM. Its
recorded harness was `/tmp/phase4_vb001_eval_e4_full_released.py`, SHA256
`8c31b131e1b294fb0a089589c4f934e1c9912a4969573169f2abe333c847d5e6`; the
script is a temporary artifact, not a committed reusable evaluator. Reuse or
reconstruct that audited route only after CPU review; do not run it during
preflight.

Phase 4 values above are **DIRECTLY COMPARABLE for quality only if** V-A2 uses
the same 401 frame IDs, resolution, masks, metric definitions/backend,
relative-w2c convention, and all-2000-pose Horn alignment. The proposed
`eval_every=5` achieves that protocol match; the saved P6-BAM-005 aggregate
with `eval_every=50` is not a direct quality comparator. Apply the researcher’s
15% constraints independently to ATE Mean, true ATE RMSE, MS-SSIM, LPIPS-Alex,
Depth L1, semantic mIoU, and PSNR-implied MSE increase
`10^((PSNR_V0−PSNR_VA2)/10)−1`; disclose the P5-LEAN provisional margins
separately, without replacing them.

| Metric | Phase 4 baseline source | Compatibility if future run uses Phase 4 E4 protocol | V-A2 evidence destination | Saved-state evaluation needed? |
|---|---|---|---|---|
| ATE Mean | E4 `trajectory_metrics.json`; all 2,000 poses | `DIRECTLY_COMPARABLE`: same relative-w2c, quaternion convention and Horn rigid alignment | Pose arrays in `params.npz`; derive into comparison `trajectory_metrics.json` | Yes for recommended checkpoint-first workflow; no if in-run evaluator completes, but that path is less failure-safe |
| True ATE RMSE | Supplementary E4 RMSE from the same aligned errors | `DIRECTLY_COMPARABLE` if recomputed from the exact same 2,000 per-pose errors | Same as ATE Mean | Same as above |
| PSNR | E4 `aggregate_metrics.json` and 401 per-frame records | `DIRECTLY_COMPARABLE` with same 401 IDs, GT-depth mask and released PSNR formula | `<run>/eval/psnr.txt` and comparison aggregate/per-frame tables | Yes for checkpoint-first workflow |
| MS-SSIM | E4 `aggregate_metrics.json`; source `ssim.txt` is MS-SSIM | `DIRECTLY_COMPARABLE` with same `pytorch_msssim.ms_ssim` version/options and 401 frames | `<run>/eval/ssim.txt` | Yes for checkpoint-first workflow |
| LPIPS-Alex | E4 `aggregate_metrics.json` | `DIRECTLY_COMPARABLE` with TorchMetrics AlexNet, `normalize=True`, same clamp/mask and weights | `<run>/eval/lpips.txt` | Yes for checkpoint-first workflow |
| Depth L1 | E4 `aggregate_metrics.json` | `DIRECTLY_COMPARABLE` with Replica scale 6553.5, valid-depth mask, meters and 401 frames | `<run>/eval/l1.txt` | Yes for checkpoint-first workflow |
| Semantic-color mIoU | E4 `aggregate_metrics.json` | `DIRECTLY_COMPARABLE` with current-frame GT-palette recoloring, black-GT exclusion and 401 frames | `<run>/eval/miou.txt` | Yes for checkpoint-first workflow |

The Phase 4 baseline provides all 2,000 trajectory poses and all seven
aggregate metrics. Saved-output reevaluation of V-A2 is required if the
checkpoint-first run suppresses in-loop evaluation; it must be performed only
from the preserved final checkpoint and into a new Phase 6 output directory.
P6-BAM-005’s 11-view evaluator files are not substitutes for the Phase 4
401-view full-scene protocol.

Runtime: Phase 4 reports 14,173.475 s for its full run but does not provide the
same committed `perf_counter()` boundary as P6-BAM-005. P6 online timing starts
immediately before and ends immediately after the online frame loop; it
includes profiler calls and `torch.cuda.empty_cache()`, excludes initialization,
final evaluation, and serialization. Phase 4 output saving used a temporary
harness, different profiler/instrumentation scope, and a no-op in-run
evaluator. Therefore Phase 4 runtime is **NOT_COMPARABLE** as a matched online
wall measurement. Report it as historical/exploratory context only; do not
claim online speedup from that comparison. P6-BAM-005’s 500-frame timing is
also not a 2,000-frame comparator.

## 3D Gaussian and semantic reconstruction

- Gaussian model checkpoint: **READY in the Phase 4 reference; expected from
  the unchanged P6 save path, but not yet produced for V-A2.** `params.npz`
  preserves means, RGB colors, rotations, opacity, scale, camera arrays,
  semantic IDs and learned semantic colors.
- 3D RGB export: `utils.common_utils.save_params` calls
  `utils.convert_ply.convert`, creating `params.ply`. The PLY stores x/y/z,
  degree-0 color coefficients, opacity, scale and rotation; it is a Gaussian
  map export, not just an RGB image.
- 3D semantic export: the same helper creates `seg_params.ply` with Gaussian
  geometry/appearance fields colored from learned `semantic_colors`. PLY does
  **not** include class IDs. The authoritative fixed per-Gaussian IDs remain
  in `params.npz` and require the verified Replica palette mapping for
  categorical 3D class displays.
- `SEMANTIC_MODEL_CHECKPOINT_READY`: **PASS** (Phase 4 checkpoint inspection;
  V-A2 candidate remains pending).
- `SEMANTIC_3D_EXPORT_READY`: **PASS at source/reference level**; final P6
  export depends on successful final save or deriving PLY from its checkpoint.
- `SEMANTIC_3D_VIEWER_READY`: **PASS for the Phase 4 reference**. The
  repository’s offline Gaussian-splat renderer and full-scene 3D diagnostic
  pipeline produced validated RGB and semantic 3D views from saved PLY/NPZ
  (`PASS_V1/V2` and `PASS_V3A`). New V-A2 outputs have not been rendered.
- Required future derived outputs: `params.ply`, `seg_params.ply`, and a
  separate non-overwriting Phase 6 visualization package using
  `scripts/visualization/render_final_maps.py` and, if categorical labels are
  required, the existing `semantic_mapping.csv` plus aligned `params.npz`
  through the V3A pipeline. These are 3D map products, not the 401-camera
  2D evaluation gallery. No exporter/viewer ran in this audit.
- For later SSH handoff, the native full-map RGB/semantic-view PNG package can
  be inspected directly after download; `params.ply` and `seg_params.ply` can
  be opened in a compatible Gaussian-splat viewer, with the caveat that a
  generic point-cloud viewer may not honor Gaussian scale/rotation/opacity.
  The validated Phase 4 V1/V2/V3A package provides the concrete example. An
  interactive viewer UI is not part of the `slam.py` execution path (the
  inherited `enter_interactive_post_online` config value has no active source
  read in this path).

## Proposed paths and isolation

No final run/comparison directory was created. The following canonical paths
were absent and did not resolve through symlinks at preflight time:

- Run ID: `p6_bam_006_room0_0_1999_va2_r01`.
- Result root: `results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/`.
- Telemetry root: `results/runtime_artifacts/phase6_bam/telemetry/p6_bam_006_room0_0_1999_va2_r01/`.
- Comparison/evaluation root (future): `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/`.
- Preflight-only evidence root created for this audit:
  `results/runtime_artifacts/phase6_bam/p6_bam_006_preflight_20261016/`.

Expected future resolved output paths (conditional on a separately approved
run and the checkpoint-first wrapper):

| Artifact | Proposed destination |
|---|---|
| Complete final model | `<run>/params.npz` (only after final metadata/save path) |
| Pre-evaluation frame-1999 fallback | `<run>/params1999.npz` (requires interval 1999; current interval 500 does not emit it) |
| RGB 3D Gaussian export | `<run>/params.ply` (only after `save_params`; NOT_IMPLEMENTED if that path fails) |
| Learned semantic 3D Gaussian export | `<run>/seg_params.ply` (same dependency) |
| Keyframe metadata | `<run>/keyframe_time_indices1999.npy`; final list also inside `params.npz` |
| Per-frame metrics | `<run>/eval/{psnr,rmse,l1,ssim,lpips,miou}.txt` |
| Metric plots | `<run>/eval/metrics.png` and `<run>/eval/plots/####.png` |
| Rendered evaluation views | `<run>/eval/rendered_rgb/gs_####.png`, `rendered_depth/gs_####.png`, `rendered_seg/gs_####.png` |
| ATE evidence | `<run>/params.npz` poses plus `<comparison>/trajectory_metrics.json` (source evaluator does not save a trajectory file) |
| LIGHT telemetry | `<telemetry>/` JSONL, summary and run metadata |
| Launch logs/exit/timing/config provenance | `<comparison>/` per-run records, effective config and hashes |
| 3D-view RGB/semantic package | `<comparison>/visualization/` using existing Phase 4 renderer; not generated in preflight |

The current config guard checks `os.path.exists` for result and telemetry
directories, but it is non-atomic and does not canonicalize every component
against symlink escape. Fresh unique IDs, immediate pre-launch absence checks,
canonical resolved-path checks, and sequential execution remain mandatory.
`save_params` uses `np.savez` and writes PLYs to fixed filenames without
per-file overwrite protection; the config guard and unique empty run root are
the protection. No default Phase 4 output path is used by the Phase 6 base.

## CPU/static checks and disposition

- CPU checkpoint integrity, shape, dtype and finite checks: PASS.
- Dataset 0–1999 structure and representative file checks: PASS.
- V-A2 wrapper CPU load and budget/threshold checks: PASS; frame bound and
  LIGHT mode: **FAIL for direct use of current wrapper**.
- `python -m unittest discover -s tests -p 'test_mapping_budget.py'`: 15
  passed.
- `python -m unittest discover -s tests -p 'test_performance_profiler.py'`:
  23 passed; test suite uses fakes/mocks for CUDA paths and performed no CUDA
  workload.
- Attempted `python -m pytest ...` was unavailable (`No module named pytest`);
  no package was installed. The repository's unittest suites above passed.
- Host `nvidia-smi` and no-allocation PyTorch CUDA availability/device query:
  PASS at inspection time; no CUDA tensor or kernel was run. Device utilization
  is point-in-time only.
- Phase 4 checkpoint/artifact integrity: PASS; old Phase 6 reference hashes
  match P6-BAM-005 reports; proposed final output paths absent.
- Git diff check: PASS before this report; no source/config edits made.

**Final status: `BLOCKED_P6_BAM_006_PREFLIGHT`.** Before a separate execution
authorization, the researcher should review and authorize a minimal
experiment-only V-A2 wrapper/harness that (1) explicitly sets exactly
`start=0,end=2000,stride=1,num_frames=2000`, (2) uses LIGHT, (3) preserves the
frozen 45/60/60 controller and all other algorithm settings, (4) writes a
frame-1999 fallback before evaluation and saves the complete final model
before any risky evaluator, and (5) runs same-protocol evaluation and 3D
derived outputs only from that saved state into unique non-overwriting Phase 6
paths. Recheck CUDA/device, disk, output absence and config parity immediately
before execution. This report does not authorize or start the experiment.

---

## Follow-up disposition — 2026-10-16

The requested CPU/static preparation was completed as documented in
[`P6_BAM_006_PREFLIGHT_FIX_REPORT.md`](P6_BAM_006_PREFLIGHT_FIX_REPORT.md).
The new isolated full-scene V-A2 wrapper explicitly bounds frames 0–1999,
selects LIGHT, uses the audited 401-view E4 cadence, and requests a frame-1999
checkpoint. Final metadata/NPZ/PLY serialization and CPU validation now precede
the in-process evaluator, and a reusable saved-state evaluator is available.
The preparation gate is `PASS_P6_BAM_006_PREFLIGHT_FIX_CPU_STATIC_READY`.
The historical `BLOCKED_P6_BAM_006_PREFLIGHT` result above is preserved, and
this follow-up does not authorize GPU execution. P6-BAM-006-FULL remains
pending a separate researcher request.
