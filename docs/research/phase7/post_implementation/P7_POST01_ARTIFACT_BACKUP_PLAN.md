# P7-POST-01 — Artifact Backup Plan

**Status:** plan only. No files were copied, compressed or uploaded.

## Preservation priority before server decommission

1. Copy both completed full-scene model roots and evidence roots intact, preserving relative paths: room0 run `p7_bcgm_g3_room0_on_0_1999_r01` and room1 run `p7_bcgm_r1_full_room1_on_0_1999_r01`. They occupy about 5.15 GB combined (logical size; report exact byte counts in `P7_POST01_ARTIFACT_PRESERVATION_INVENTORY.md`). Include checkpoint NPZ, both PLYs, six evaluator arrays, effective config, run summaries, logs, NVML CSV, insertion traces, offline ATE, manifests, and room0 visualization. Do not recreate PLY/checkpoints merely for backup.
2. Preserve Gate 1B three-arm and Gate 2 evidence roots and their manifests because they support the bounded progression and telemetry recovery findings. Preserve the Replica dataset and its `cam_params.json`, `traj.txt`, data configuration, the pinned Python environment specification, and the renderer/dependency revision needed for future offline evaluation. Dataset/environment copies require separate capacity and licensing/storage review.
3. Keep source/config and compact reports under Git. GitHub is not the archive for model checkpoints, PLYs, rendered images, datasets or run logs.

## Transfer approach

Use an independently provisioned external disk or research storage with enough free capacity; verify its available space before transfer. From the destination/laptop, run `rsync` pull commands for each evidence/model root. Use `--archive --partial --info=progress2` without `--delete`; do not create a second compressed bundle on the nearly-full server. After transfer, compare source and destination SHA256 using the source manifests and regenerate a destination-side inventory. For stronger assurance, verify checkpoint/PLY/evaluator/runtime critical files individually and keep the manifest alongside the backup.

Example (run on the laptop, destination path must be chosen by the researcher):

```bash
rsync -avh --partial --info=progress2 robot@<GPU_HOST>:/home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica/p7_bcgm_g3_room0_on_0_1999_r01/ /BACKUP/phase7/experiments/Replica/p7_bcgm_g3_room0_on_0_1999_r01/
rsync -avh --partial --info=progress2 robot@<GPU_HOST>:/home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/ /BACKUP/phase7/results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/
rsync -avh --partial --info=progress2 robot@<GPU_HOST>:/home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica/p7_bcgm_r1_full_room1_on_0_1999_r01/ /BACKUP/phase7/experiments/Replica/p7_bcgm_r1_full_room1_on_0_1999_r01/
rsync -avh --partial --info=progress2 robot@<GPU_HOST>:/home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate3_room1/p7_bcgm_r1_full_room1_on_0_1999_r01/ /BACKUP/phase7/results/runtime_artifacts/phase7_gate3_room1/p7_bcgm_r1_full_room1_on_0_1999_r01/
```

The placeholder host and destination must be replaced deliberately. These are proposed commands, not evidence that a transfer occurred. The previous room0 laptop transfer remains `USER_REPORTED_COMPLETE`, not checksum-verified. Room1 remains `SERVER_ONLY_VERIFIED` until an external destination is independently checked.
