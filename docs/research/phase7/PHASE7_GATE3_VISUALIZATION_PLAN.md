# Phase 7 Gate 3 visualization plan

**Plan status:** reference and inputs verified; execution blocked pending
direct-host renderer GPU access.

## Locked inputs and renderer

- Run: `p7_bcgm_g3_room0_on_0_1999_r01`.
- Checkpoint: `experiments/Replica/p7_bcgm_g3_room0_on_0_1999_r01/params.npz`
  (SHA256 `a02dd4b4ecfd9c982866cf4a4c38c187ef22c75049b8328e18eea20608944917`).
- RGB map: same run's `params.ply`; semantic map: `seg_params.ply`. Both have
  4,499,583 vertices and their positions/color fields were verified equal to
  the matching checkpoint arrays.
- Renderer: Phase 4/6 validated
  `/home/robot/research/SGS_slam/scripts/visualization/render_final_maps.py`
  SHA256 `b46eb61fee2f2cc40488bcc560dc10065b4074023808c2cc027c9a270095ade0`.
- Authoritative camera directory:
  `/home/robot/research/SGS_slam/results/runtime_artifacts/phase4_vb001_visualization/cameras/`.
  Phase 6 V1-matched copies were byte-compared and have identical hashes.
- Rendering convention: native `diff_gaussian_rasterization`, 1600×900,
  white background, saved PLY coordinates unchanged, same camera JSON for RGB
  and semantic outputs.

## Output correspondence

| Phase 7 planned product | Phase 4 reference | Phase 6 matched reference | Purpose |
|---|---|---|---|
| `visualization/reconstruction/{overview,oblique,top_oblique}.png` | `phase4_vb001_visualization/reconstruction/*.png` | `phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/reconstruction/*.png` | Free-view 3D RGB Gaussian reconstruction |
| `visualization/semantic/{overview,oblique,top_oblique}.png` | same Phase 4 root `semantic/*.png` | same matched Phase 6 root `semantic/*.png` | Learned per-Gaussian semantic-color visualization |
| `visualization/paired/*_reconstruction_vs_semantic.png` | Phase 4 `paired/*.png` | matched Phase 6 `paired/*.png` | Final map panel with corresponding RGB and semantic view |
| `visualization/cameras/*.json` | Phase 4 `cameras/*.json` | Phase 6 V1-matched `cameras/*.json` | Camera provenance and byte-level comparison |
| `visualization/metadata/*` | Each reference package's metadata | Each reference package's metadata | Map, camera, source, validation, and manifest evidence |

These outputs preserve the Phase 4 V1 learned-color convention. They do not
claim categorical semantic-ID coloring. Phase 6 V3A semantic-ID/classwise
figures are a separate camera family and are not mixed into this V1-matched
package.

## Locked viewpoint metadata

| View | Camera file SHA256 | All Phase 7 centers inside frame (CPU check) |
|---|---|---|
| `overview` | `c5e0029b1758788322538ce27e587c8cdfa5a3277aba331431e50d5ac80865bb` | yes |
| `oblique` | `9846a224e93b3615afd45097b9106037c3550b5199b74d4e0550f328ad220120` | yes |
| `top_oblique` | `0d865494919fb2066cf769ef654163ee3f1e262d5ebb4cf8b95681d6934ec196` | yes |

Camera byte copies will be made only by the renderer into the new Phase 7
output. Phase 4/6 artifacts remain read-only.

## Guarded command (not executed)

First confirm direct-host GPU visibility and inspect active GPU processes:

```bash
nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv,noheader
nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader
```

Then run the offline-only renderer on the GPU host:

```bash
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B \
  /home/robot/research/SGS_slam/scripts/visualization/render_final_maps.py \
  --reconstruction /home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica/p7_bcgm_g3_room0_on_0_1999_r01/params.ply \
  --semantic /home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica/p7_bcgm_g3_room0_on_0_1999_r01/seg_params.ply \
  --params-npz /home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica/p7_bcgm_g3_room0_on_0_1999_r01/params.npz \
  --camera-dir /home/robot/research/SGS_slam/results/runtime_artifacts/phase4_vb001_visualization/cameras \
  --output /home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/visualization \
  --width 1600 --height 900 --background white --device cuda:0
```

Expected: 3 RGB PNGs, 3 semantic PNGs, 3 paired PNGs, exact camera JSONs,
metadata and validation/manifest. The renderer validates source PLY hashes,
same geometry, image dimensions/nonuniformity, and Gaussian-center framing.
Its implementation creates output subdirectories before checking for CUDA;
therefore this command must only be run after GPU visibility is confirmed.
Current environment cannot access the NVIDIA driver, so the command has not
been attempted and no visualization artifact is claimed.
