# Phase 7 Gate 3 — Advanced visualization validation

**Result:** `PASS_WITH_LIMITATIONS`
All eight visualization families are present. Verification used the pinned
`sgs_slam_5080` Python environment and was CPU-only after rendering.

## Family inventory

| Family | Phase 7 output | Three-phase boards | Validation result |
|---|---|---|---|
| A. Observed-camera RGB | `phase7_only/observed_camera/rgb/`, 5 PNGs | `compare_phase4_phase6_phase7/A_observed_rgb/`, 5 boards | PASS_WITH_LIMITATIONS |
| B. Observed metric depth | `phase7_only/observed_camera/depth/`, 5 float32 NPY + 5 PNG | `.../B_observed_depth/`, 5 boards + 15 normalized source views | PASS |
| C. Observed learned semantic color | `phase7_only/observed_camera/semantic/`, 5 PNGs | `.../C_observed_semantic/`, 5 boards | PASS_WITH_LIMITATIONS |
| D. Full-scene RGB | Existing V1 free-view images copied under `phase7_only/free_view/reconstruction/`; V3A images under `v3a_diagnostics_r02/rgb/unfiltered/` | `.../D_full_scene_rgb/`, 5 boards | PASS_WITH_LIMITATIONS |
| E. Cross-modal RGB/geometry/fixed-ID structure | V3A `comparisons/` and modality folders | `.../E_cross_modal/`, 6 boards | PASS_WITH_LIMITATIONS |
| F. Selected fixed semantic-ID classes | 8 selected class panels plus palette legend in V3A output | `.../F_fixed_semantic_classes/`, 8 class boards + legend | PASS_WITH_LIMITATIONS |
| G. Estimated trajectory | V3A `trajectory/estimated_trajectory_3d.png`; all poses retained in supporting source metadata | `.../G_estimated_trajectory/`, 2 boards | PASS_WITH_LIMITATIONS |
| H. Full-scene semantics | V1 learned-color views plus V3A raw learned and fixed-ID views | `.../H_full_scene_semantic/`: 3 free-view learned, 3 V3A raw learned, 3 fixed-ID boards | PASS_WITH_LIMITATIONS |

All comparison boards have Phase 4, Phase 6, Phase 7 columns. Observed RGB,
semantic and depth PNGs are 1200×680; all saved raw depth arrays are float32,
shape `(680,1200)`, finite, and contain positive valid samples. All sampled
PNG files were non-uniform. V1 full-scene views retain their 1600×900
reference dimensions; V3A diagnostics use 960×540.

## Camera, semantic and trajectory checks

- Observed frame IDs: exactly `0, 499, 999, 1499, 1999`.
- Each copied Phase 7 observed `frame_metadata.json` is byte-identical to the
  Phase 4 V2 source; the board references the same Phase 6 matched camera
  files. Resolution and matrix shapes were checked before rendering.
- V1 free-view camera JSONs are the audited `overview`, `oblique`,
  `top_oblique` references. V3A camera JSONs are the exact Phase 4
  `trajectory_observed`, `room_overview`, `top_oblique` files. Phase 6
  matched versions use the same camera definitions. Existing Phase 7 free
  views were copied, not regenerated.
- Depth arrays represent camera-z in metres (not Euclidean range). The
  comparison boards derive the same fixed `[0,6]` m Turbo image from Phase 4,
  Phase 6 and Phase 7 raw depth; this harmonizes Phase 6's original JET
  visualization without altering its artifact.
- Learned `semantic_colors` and fixed `semantic_ids` remain separate.
  Mapping CSV:
  `/home/robot/research/SGS_slam/results/runtime_artifacts/phase4_vb001_visualization_audit/semantic_mapping.csv`.
  Selected classes/palette: wall 93 `[224,64,128]`; floor 40 `[64,0,64]`;
  ceiling 31 `[192,192,128]`; sofa 76 `[96,0,128]`; chair 20 `[0,64,128]`;
  table 80 `[32,64,0]`; rug 98 `[32,128,64]`; blinds 12 `[64,0,128]`.
- V3A metadata validates 2,000 estimated poses, W2C quaternion/translation
  convention and camera-center inversion `C=-R^Tt`; green=start, red=end,
  blue=path, with no GT overlay and no ATE interpretation.
- Fixed-class full-scene geometry is a deterministic sampled-center
  diagnostic, not a continuous surface or per-pixel predictor. Some Phase 7
  centers fall outside the unchanged Phase 4 V3A camera frusta; no camera was
  widened to conceal clipping.

## Integrity and manifests

- `params.npz` SHA256 remains
  `a02dd4b4ecfd9c982866cf4a4c38c187ef22c75049b8328e18eea20608944917`.
- `params.ply`: `409d1c3637e3f951f950d14bf066a88df66de8dc41a01762c312a0871ab300fc`.
- `seg_params.ply`: `98a41a36e69e113c7e7da8dcfcd8c279c08c25da8af7525e26dcbdb7df262b89`.
- Phase 7 `scripts/slam.py`, `utils/bcgm.py`, and Gate 1B worker retain their
  previously verified SHA256s. The only new source file is the offline
  visualization helper; no SLAM algorithm or scientific config changed.
- `advanced_visualization_manifest.json` verifies 143 output payload entries
  and 210 referenced Phase 4/6 files. Its SHA256 is recorded in the final
  report. Output and reference files were rehashed successfully.
- The existing Phase 7 free-view source images match their own saved manifest
  hashes; Phase 4/6 inputs were read-only and their recorded hashes still
  match.

## Limitations

- Phase 6 observed RGB/semantic images use a white background whereas the
  canonical Phase 4 observed renderer uses black. Phase 7 follows Phase 4;
  the board shows this renderer convention difference explicitly.
- V3A plots use the historical deterministic 650,000-center visualization
  method; they are not surface reconstructions. Map differences are expected
  because the three phases contain different learned maps.
- The V3A script writes renderer-checkout branch/HEAD metadata from its
  Phase 4 visualization-tool repository. That provenance is separated from
  Phase 7 checkpoint/source identity in the execution record and manifest.
- No new RGB/depth quality metric was calculated. Boards are qualitative.
