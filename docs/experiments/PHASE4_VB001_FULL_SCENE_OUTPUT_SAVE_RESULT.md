# PHASE4-VB-001 Full-Scene Output-Save Result

- Date: 2026-10-11.
- Experiment ID: `PHASE4_VB001_MINIMAL_OUTPUT_SAVE_FULL_0_1999_TELEMETRY`.
- Variant: `PHASE4-VB-001` — CPU offload of resident keyframe payloads.
- Branch: `phase4-vb-001-cpu-keyframe-offload`.
- Run HEAD: `68f9060f7ff4d8d141be1d5f71339401327edd06`.
- Status: `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.

## Objective

Run the unchanged PHASE4-VB-001 online pipeline over Replica `room0` frames
0–1999 and preserve a reloadable final map, camera trajectory, semantic state,
keyframe indices, and lightweight timing/memory telemetry. Evaluation and all
paper metrics were explicitly excluded.

## Environment and dataset

- GPU: NVIDIA GeForce RTX 5080, 16,609,378,304 physical bytes.
- Python: 3.10.22.
- PyTorch: 2.7.1+cu128; PyTorch CUDA runtime: 12.8.
- Dataset: author-distributed Replica, scene `room0`.
- Physical sequence: 2,000 frames, 680 × 1200.
- Config: `configs/replica/slam.py`, seed 0, source start/end/stride 0/-1/1.
- Environment: `/home/robot/miniconda3/envs/sgs_slam_5080`.
- NVIDIA driver recorded by the run preflight: 580.167.08.

## Implementation contract

The run used PHASE4-VB-001 unchanged. Archived keyframe color, depth,
semantic ID, and semantic color payloads remained CPU-authoritative;
`est_w2c` remained GPU-resident. There was no pinned memory, non-blocking
transfer, persistent GPU cache, logical-keyframe eviction, precision or
resolution change, iteration change, mapping-window change, keyframe-cadence
change, renderer/loss/semantic change, pruning/densification change, or RNG
policy change.

The minimal harness set `config["data"]["num_frames"] = 2000`, replaced only
the module-level evaluator with a no-op that returned normally, allowed the
released final-state augmentation and original `save_params(...)` call to
execute, then wrote a standalone `keyframe_time_indices.npy`. It did not run
evaluation or alter the online algorithm.

- Harness: `/tmp/phase4_vb001_minimal_output_save_full_0_1999_telemetry.py`.
- Harness SHA256: `7b13a78ae476e74d1bdb2e18884bfb83ddc1ee428b2d3891d90ed4d391f52e81`.
- `scripts/slam.py` SHA256: `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3`.

Executed command:

```bash
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python \
  /tmp/phase4_vb001_minimal_output_save_full_0_1999_telemetry.py
```

## Validation history

- Gate 1: `PASS`.
- Gate 2: `PASS`.
- Gate 3, frames 0–99: `PASS_FRAME_LIMIT`.
- Gate 4, frames 0–499: `PASS_FRAME_LIMIT`; peak GPU allocated/reserved about
  3.469/4.526 GB.
- Gate 5, frames 0–999: `PASS_FRAME_LIMIT`; runtime 7,183.993 s; peak GPU
  allocated/reserved about 5.958/6.950 GB.
- Earlier full-scene runtime: online frames 0–1999 completed. Its original
  `FAIL_RUNTIME` was a validator bug that omitted the released terminal
  `num_frames-2` keyframe; corrected classification:
  `PASS_RUNTIME_VALIDATOR_BUG`.
- Minimal output-save smoke, frames 0–49: `PASS_MINIMAL_OUTPUT_SAVE_SMOKE`.
- Telemetry output-save smoke, frames 0–49:
  `PASS_TELEMETRY_OUTPUT_SAVE_SMOKE`.
- This full-scene output-save run: `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.

The earlier full-scene runtime evidence remains useful for detailed Variant-B
residency invariants. It did not save final state because its harness stopped
before `save_params(...)`. This run solved that missing-final-state problem.

## Final result

- Completed frames: 2,000, exactly 0–1999.
- Last completed frame: 1999.
- Runtime: 14,173.47515856901 s, approximately 3 h 56 m 13 s.
- Final Gaussians: 4,956,467.
- Logical keyframes: 402.
- Final keyframe tail: `[1989, 1994, 1998, 1999]`.
- `SAVE_SUCCESS`: true.
- `ARTIFACT_COMPLETENESS`: true.
- `TELEMETRY_COMPLETENESS`: true.

The keyframe list matches the released condition:

```python
(time_idx == 0) or ((time_idx + 1) % keyframe_every == 0) \
    or (time_idx == num_frames - 2)
```

## Timing

| Field | Value |
|---|---:|
| Tracking iteration average | 74.54126408960057 ms |
| Tracking frame average | 2.9809244149923324 s |
| Mapping iteration average | 66.4294029156367 ms |
| Mapping frame average | 3.986144354939461 s |
| Tracking iterations / frames | 79,960 / 1,999 |
| Mapping iterations / frames | 120,000 / 2,000 |
| Tracking FPS | 0.3354664059815056 |
| Mapping FPS | 0.25086898791330586 |
| Overall SLAM FPS | 0.14110865384985266 |
| Final serialization | 9.3924627660017 s |

Tracking and mapping FPS are reciprocals of the released average frame times.
Overall FPS is completed frames divided by online wall-clock runtime.

## Memory

| Field | Bytes | Percent of physical GPU |
|---|---:|---:|
| Peak GPU allocated | 5,817,509,888 | 35.025452377100606% |
| Peak GPU reserved | 7,189,037,056 | 43.28299906486374% |
| Final GPU allocated | 26,925,056 | — |
| Final GPU reserved | 2,258,632,704 | — |
| Process RSS before | 923,222,016 | — |
| Process RSS after | 13,170,110,464 | — |
| Process RSS/HWM | 17,960,493,056 | — |
| Process RSS growth | 12,246,888,448 | — |

RSS/HWM is host RAM, not GPU VRAM. The minimal harness intentionally did not
add heavy residency instrumentation, so CPU archive bytes, GPU archived
payload bytes, GPU `est_w2c` bytes, staged-payload peak, simultaneous staging,
and persistent staged-payload-at-end are `UNKNOWN` for this run. This is not a
failure: the earlier detailed full-scene Variant-B run already established the
residency invariants.

## Saved parameter keys

`params.npz` is readable and contains exactly these keys:

```text
cam_trans
cam_unnorm_rots
gt_w2c_all_frames
intrinsics
keyframe_time_indices
log_scales
logit_opacities
means3D
org_height
org_width
rgb_colors
semantic_colors
semantic_ids
timestep
unnorm_rotations
w2c
```

These provide Gaussian/map state, estimated trajectory, GT trajectory/camera
metadata, semantic state, keyframe metadata, and original image dimensions.

## Artifact inventory

Stable output directory:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/`

Evidence directory:
`results/runtime_artifacts/phase4_vb001_minimal_output_save_full_0_1999/`

| Artifact | Size (bytes) | SHA256 |
|---|---:|---|
| `keyframe_time_indices.npy` | 3,344 | `fb91f05c127819f6666259668c4d88a2d36a46f575659f576adde37b227e6d37` |
| `params.npz` | 322,361,795 | `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2` |
| `params.ply` | 337,040,173 | `d9b4d22ba11c73f8c1d6d0ea5f874bbb5d3254f25b333362a502a5940f604502` |
| `seg_params.ply` | 337,040,173 | `6cd5a258a8147fe0c0515d04ea702d618f82c2411fc464ab9bfebd2fc2f3b726` |

Checksums were verified after the run. Runtime binary artifacts and large logs
remain Git-ignored on the server; no Git LFS policy was introduced.

Small evidence files include the result JSON, timing and memory summaries, run
metadata, artifact manifest/checksums, pre/post system state, and Markdown
summary in the evidence directory.

## Scientific interpretation

`RUNTIME VERIFIED`: PHASE4-VB-001 removed the GPU-memory scalability failure
that caused the unchanged Phase 3 baseline to OOM after frame 1293 on this
16 GB RTX 5080. Replica `room0` now reaches frame 1999 without GPU OOM, and a
reloadable final online state is available. Peak GPU allocated/reserved memory
in this final run was about 5.82/7.19 GB, substantially below the 16.61 GB
physical device capacity. For this scene and run, offloading resident
keyframe payloads addresses the identified GPU-resident keyframe-memory
limitation.

This result does not establish reconstruction accuracy, metric equivalence,
paper reproduction, or generalization to other scenes/datasets.

## Evaluation status and next gate

Evaluation status: `NOT RUN`. No ATE, PSNR, SSIM, LPIPS, DepthL1, mIoU,
rendering metrics, semantic metrics, post-SLAM optimization, full rendered
image export, or paper metrics were run or reproduced.

The next step is an **Evaluation / Export Audit** from the saved full-scene
state. Before executing evaluation, the audit must establish the exact saved-
state loading path, evaluator/renderer entry point, RGB/depth/trajectory/
semantic metric protocols, frame sampling, GT alignment, and output paths.
Online SLAM should not be rerun if saved-state loading succeeds.

PHASE4-VB002 remains a future runtime-optimization track and was not started.

## Provenance

- Full runtime log and telemetry are in the Git-ignored evidence directory.
- `run_metadata.json` records branch, run HEAD, environment, GPU, source hash,
  harness hash, frame range, and timestamp.
- `artifact_manifest.json` and `artifact_checksums.sha256` record and verify
  the final artifacts.
- No source, algorithm, experiment config, dataset, or metric implementation
  was changed by this output-saving run.
