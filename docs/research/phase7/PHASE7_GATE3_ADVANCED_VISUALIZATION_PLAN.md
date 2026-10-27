# Phase 7 Gate 3 — advanced visualization plan

**Status:** reference audit, checkpoint validation, rendering and package
validation complete with documented limitations. Existing V1 free-view images
were copied into the package, not regenerated.

## Checkpoint and source validation

Checkpoint SHA256:
`a02dd4b4ecfd9c982866cf4a4c38c187ef22c75049b8328e18eea20608944917`.
Read with `numpy.load(..., allow_pickle=False)`; count is 4,499,583.

| Field | Shape / type | Validation |
|---|---|---|
| `means3D` | `(4499583,3)` float32 | finite |
| `rgb_colors` | `(4499583,3)` float32 | finite; exact PLY DC-color correspondence |
| `log_scales` | `(4499583,1)` float32 | finite |
| `unnorm_rotations` | `(4499583,4)` float32 | finite |
| `logit_opacities` | `(4499583,1)` float32 | finite |
| `semantic_ids` | `(4499583,)` uint8 | finite; 29 IDs; counts below |
| `semantic_colors` | `(4499583,3)` float32 | finite; exact semantic PLY DC-color correspondence |
| `cam_unnorm_rots` | `(1,4,2000)` float32 | finite, scalar-first quaternion use per Phase 4 code |
| `cam_trans` | `(1,3,2000)` float32 | finite; stored w2c translation |
| `gt_w2c_all_frames` | `(2000,4,4)` float32 | finite |
| `w2c` | `(4,4)` float32 | finite first-frame reference |
| `intrinsics` | `(3,3)` float32 | finite |
| `org_width`, `org_height` | scalar int64 | checkpoint dimensions; observed reference frames are 1200×680 |
| `keyframe_time_indices` | `(402,)` int64 | valid saved metadata, not used to subsample visualization |

PLY hashes: `params.ply` `409d1c3637e3f951f950d14bf066a88df66de8dc41a01762c312a0871ab300fc`;
`seg_params.ply` `98a41a36e69e113c7e7da8dcfcd8c279c08c25da8af7525e26dcbdb7df262b89`.
Exact positions and DC colors were compared against NPZ arrays; no map
re-optimization or attribute remapping is planned.

## Planned output tree

New root (must be absent before `--execute`):
`results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/advanced_visualization/`.

| Family subdirectory | Products / evidence |
|---|---|
| `observed_rgb/` | five rendered RGB frames, five GT references, optional matched GT/render panels; frames 0,499,999,1499,1999 |
| `observed_metric_depth/` | raw float32 camera-z depth NPY in metres, GT raw depth reference, V2 Turbo `[0,6]` m PNG and comparisons |
| `observed_learned_semantic/` | raw learned semantic-color PNGs, GT semantic-color references and panels; no GT-assisted recoloring as prediction |
| `full_scene_rgb/` | references to existing Phase 7 `visualization/reconstruction/*.png`; no duplicate render |
| `cross_modal/` | references to existing Phase 7 `visualization/paired/*.png`; same geometry/cameras |
| `fixed_semantic_id_classes/` | V3A sampled categorical ID/color geometry and eight selected classwise images; class metadata/counts/palette source |
| `estimated_trajectory/` | all 2,000 c2w camera centers/path over the V3A center geometry; lightweight trajectory NPY/JSON; no GT overlay |
| `full_scene_semantic/` | references to existing V1 learned-color views plus V3A fixed-ID full-scene view, clearly labeled as different semantic representations |
| `cameras/`, `metadata/`, `manifest/` | byte copies of reference camera files, source hashes, configuration, validation, per-file SHA256 manifest |

An output must not be created by preflight. Existing sibling `visualization/`
is read-only. The expected V1 images are overview/oblique/top_oblique and
must not be regenerated.

## Reference camera mapping

### Observed-camera views

Frame IDs: `[0,499,999,1499,1999]`. Copy each exact Phase 4 V2
`frames/frame_NNNN/frame_metadata.json`; render with its exact
`estimated_w2c` and `intrinsics`, 1200×680. GT RGB/depth/semantic references
come from the paired Phase 4 V2 frame directory (same Replica room0/frame).
The five V2 metadata SHA256 values and exact path are in the audit evidence.
Use the Phase 4 observed-eval black background. The image RGB/semantic render
must use the native anisotropic Gaussian pass; depth uses the repository
`get_depth_and_silhouette` pass.

### Full-scene V3A diagnostics

Copy exact Phase 4 V3A camera JSONs `trajectory_observed`, `room_overview`,
`top_oblique` (960×540). Do not recalculate gravity, target, camera distance,
or intrinsics. `room_overview` uses saved frame 317 as the documented anchor;
the view itself is the fixed Phase 4 V3A virtual camera. The Phase 7 CPU
projection check shows the Phase 4 V3A camera clipping/frustum does not
contain all Phase 7 centers. Keep the exact camera and disclose clipping;
do not widen the view.

### Class/trajectory mapping

Use `semantic_ids`, exact Phase 4 29-class palette, and only these Phase 4
selected class IDs: wall 93; floor 40; ceiling 31; sofa 76; chair 20; table
80; rug 98; blinds 12. V3A center rendering method is deterministic
PCG64(seed 20261013), up to 650,000 centers, nearest center per pixel and
its disclosed one-pixel gap fill. Report P7 full class counts separately
from sample counts. Trajectory must use all 2,000 saved poses, construct
`w2c=[R(q),t]`, invert for camera center `C=-R^T t`, and preserve V3A's blue
path/green start/red end/no-GT-overlay convention.

## Renderer and execution guard

Observed full raster and full-scene RGB/semantic need the repository-native
`diff_gaussian_rasterization` CUDA extension. The proposed validated source
implementations are:

- Phase 4 observed pipeline references: `scripts/visualization/package_camera_aligned_v2.py`,
  `utils/eval_helpers.py`, `utils/slam_helpers.py`, and `utils/recon_helpers.py`.
- Phase 6 observed-camera saved-map pattern:
  `scripts/visualization/render_phase4_v2_cameras.py`.
- Phase 4 full-scene/category/trajectory method:
  `scripts/visualization/visualize_full_scene_v3a.py`.
- Existing V1 free-view renderer:
  `scripts/visualization/render_final_maps.py`; do not execute for Phase 7
  because those images already exist.

Direct-host preflight, to run before the guarded render commands:

```bash
cd /home/robot/research/SGS_slam_phase7_bcgm
nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv,noheader
nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B -c "import torch; print(torch.__version__, torch.version.cuda, torch.cuda.is_available()); print(torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'CUDA_UNAVAILABLE')"
df -h /home/robot/research/SGS_slam_phase7_bcgm
```

The initial sandboxed preflight could not access the NVIDIA driver; a direct
host-context check then succeeded (RTX 5080, Torch 2.7.1+cu128, CUDA available).
The observed-camera renderer and V3A diagnostics were executed sequentially,
then packaged and validated. No placeholder/CPU-substitute images were made.
The exact execution and validation evidence is in
`PHASE7_GATE3_ADVANCED_VISUALIZATION_EXECUTION.md` and
`PHASE7_GATE3_ADVANCED_VISUALIZATION_VALIDATION.md`.

## Validation and backup contract

After successful host rendering validate all five observed IDs, exact camera
hashes, image dimensions, nonuniform PNGs, finite float32 metric depth and
documented camera-z units, semantic ID counts/palette, 2,000 finite
trajectory centers and correct c2w inversion, unchanged checkpoint/PLYs,
unchanged Phase 4/6 source hashes, and per-file SHA256 manifest. Do not
compute/claim a new image or depth metric.

Minimal backup set excludes the already-backed-up large checkpoint/PLYs;
it includes advanced PNG/Npy artifacts, camera/class/trajectory metadata,
comparison index, validation and manifest. Current free space is close to
25 GiB and should be rechecked; do not make a redundant tar archive on this
server. Download the resulting manifest-verified bundle directly to the
laptop using the commands in the final report.
