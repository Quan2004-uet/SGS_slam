# Phase 7 Gate 3 — Advanced visualization reference audit

**Audit:** complete from source, saved artifacts, camera JSONs and checkpoint.
**Generation status:** executed after direct-host GPU preflight; see the execution
and validation reports. Existing Phase 7 free-view source images were not regenerated.

## Sources examined

| Family | Phase 4 implementation/evidence | Phase 6 comparison | Phase 7 evidence |
|---|---|---|---|
| Observed-camera qualitative RGB/depth/semantic | `scripts/visualization/package_camera_aligned_v2.py`; `runtime_artifacts/phase4_vb001_visualization_v2/GATE_V2_REPORT.md`; source frames under `results/qualitative/phase4_vb001_room0_representative/` | `scripts/visualization/render_phase4_v2_cameras.py`; `runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/` | Gate 3 checkpoint and run; existing free-view package in `results/runtime_artifacts/phase7_gate3/<run>/visualization/` |
| Full-scene RGB and learned semantic color | `runtime_artifacts/phase4_vb001_visualization/` V1/V2 summary and camera JSONs | `.../phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/` | Existing `visualization/reconstruction/`, `semantic/`, `paired/`; already complete and must remain untouched |
| Geometry, fixed semantic IDs, classwise, trajectory | `scripts/visualization/visualize_full_scene_v3a.py`, `runtime_artifacts/phase4_vb001_visualization_v3a/GATE_V3A_REPORT.md` | `scripts/visualization/package_phase4_extended_visualization.py`; `.../va2_phase4_extended_matched/` | Final checkpoint fields and class counts were inspected CPU-only |
| Thesis packaging and semantic names | `scripts/visualization/package_final_v3b.py`; `runtime_artifacts/phase4_vb001_visualization_v3b/GATE_V3B_REPORT.md`; V1 `semantic_mapping.csv` | Phase 6 extended matched package and family inventory | Same mapping CSV/palette; no labels or class definitions inferred |

Reference scripts are under `/home/robot/research/SGS_slam/scripts/visualization/`.
The Phase 4 `package_camera_aligned_v2.py` is a CPU packaging utility; its
camera-aligned inputs were rendered by the Phase 4 evaluation/native
rasterization path. Phase 6's extended helper renders saved maps through the
same repository `diff_gaussian_rasterization` family at those exact cameras.

## Observed camera protocol (V2)

The selected frame IDs are exactly **0, 499, 999, 1499, 1999**. Their canonical
per-frame `frame_metadata.json` files are under
`/home/robot/research/SGS_slam/results/runtime_artifacts/phase4_vb001_visualization_v2/frames/`.
Each carries the estimated relative `w2c`, GT `w2c`, intrinsics, dimensions,
render pose provenance, metric-depth and semantic policy. Direct inspection
confirmed all five are 1200×680 with
`K=[[600,0,599.5],[0,600,339.5],[0,0,1]]`. Render pose is the Phase 4
estimated relative `w2c` from saved final-state quaternion/translation; the
ground-truth image is the corresponding observed Replica frame. Preserve
these exact metadata matrices for Phase 7 camera-aligned rendering; do not
substitute Phase 7 estimated or GT matrices.

The V2 source records RGB/GT RGB at 1200×680; raw depth arrays as float32
metres; GT semantic colors; raw learned semantic-color output; and a separate
explicitly GT-palette-assisted recoloring. Depth visualization uses the
shared **[0, 6] m** range and OpenCV **Turbo**, black for invalid/nonpositive
depth. Depth from `get_depth_and_silhouette` is camera-z (`z` after `w2c`),
not Euclidean range. Preserve the raw metric array separately from its
normalized PNG. The displayed depth error range `[0, 0.10] m` is diagnostic;
it is not a depth metric. The V2 report explicitly says no independent
categorical per-pixel semantic prediction was generated. Use raw learned
`semantic_colors` alongside GT semantic color; do not call learned colors
semantic IDs and do not use GT-assisted recoloring as an independent
prediction.

Phase 4 `setup_camera` uses a black raster background for observed-camera
evaluation. The full-map V1 renderer instead uses white. Keep these output
families distinct and preserve each family’s Phase 4 convention.

## Full-scene and V3A convention

Phase 4 V1 free-view cameras are the `overview`, `oblique`, and `top_oblique`
JSONs in `runtime_artifacts/phase4_vb001_visualization/cameras/`, rendered at
1600×900, white background. The existing Phase 7 free-view package contains
the same three byte-identical camera files (SHA256s listed below), and its
RGB/semantic/paired views have already passed renderer validation. They will
be referenced, never regenerated.

Phase 4 V3A canonical full-scene diagnostic cameras are
`trajectory_observed`, `room_overview`, and `top_oblique` in
`runtime_artifacts/phase4_vb001_visualization_v3a/cameras/`, 960×540, OpenCV
`w2c` (`+x` right, `+y` down, `+z` forward) in first-frame-relative map
coordinates. The `trajectory_observed` view is estimated frame 317; the
overview is the documented limited-offset virtual view; top-oblique uses the
validated gravity/PCA construction. Their complete `w2c`, `c2w`, K, clipping
and rationale are in the JSONs. Phase 6 extended matched copied these exact
Phase 4 V1/V3A cameras.

Phase 4 V3A trajectory code reconstructs normalized real-first (`wxyz`)
quaternion rotations and estimated `w2c` from `cam_unnorm_rots` and
`cam_trans`, then plots camera centers from `C=-R^T t` (equivalently the
translation of inverse `c2w`). It draws all 2,000 ordered estimated poses;
blue path, green start, red end; no GT overlay or trajectory alignment.

The V3A fixed-ID method deterministically samples up to 650,000 Gaussian
centers without replacement with NumPy PCG64 seed `20261013`, nearest-center
per pixel plus the documented one-pixel display gap fill, and maps IDs using
the verified 29-entry `semantic_mapping.csv`. It is a sampled center
diagnostic, not a continuous surface or per-pixel predictor. The eight
selected classes are exactly those in V3A source: wall (93), floor (40),
ceiling (31), sofa (76), chair (20), table (80), rug (98), blinds (12).

| ID / class | Palette RGB | Phase 7 Gaussian count |
|---|---:|---:|
| 93 wall | 224,64,128 | 1,173,825 |
| 40 floor | 64,0,64 | 302,136 |
| 31 ceiling | 192,192,128 | 461,911 |
| 76 sofa | 96,0,128 | 382,907 |
| 20 chair | 0,64,128 | 130,627 |
| 80 table | 32,64,0 | 144,266 |
| 98 rug | 32,128,64 | 309,895 |
| 12 blinds | 64,0,128 | 615,641 |

Counts are direct `semantic_ids` frequencies in the validated Phase 7
checkpoint, not sampled counts. Palette source SHA256:
`935f4968131737eeab1f1119bd2ecc9a73d6f713c16ea4e76a427b1e8c317613`.

## Match classification by requested family

| Family | Classification | Evidence / limitation |
|---|---|---|
| A. Observed-camera RGB | `MATCHED_WITH_LIMITATIONS` | Five exact Phase 4 estimated-w2c/K/frame references; same native rasterizer family. Different checkpoint is intended. Preserve black background and distinguish rendered result from GT. |
| B. Observed metric depth | `MATCHED_WITH_LIMITATIONS` | Same exact cameras, camera-z metres, V2 shared 0–6 m Turbo display. Phase 6 display used JET in its depth helper; use Phase 4 Turbo as canonical and document this difference. No true Depth RMSE implied. |
| C. Observed learned semantic color | `MATCHED_WITH_LIMITATIONS` | Exact V2 cameras and raw learned semantic colors; GT semantic is a separate reference. Phase 4 also shows GT-assisted recoloring; do not equate it with a prediction. |
| D. Full-scene RGB map | `EXACT_MATCHED_REFERENCE` | Existing Phase 7 free-view PNGs already use byte-identical Phase 4 V1 camera JSONs, 1600×900, white background, native renderer. Do not rerender. |
| E. RGB/semantic cross-modal map | `EXACT_MATCHED_REFERENCE` | Existing Phase 7 paired outputs use identical geometry and the same three exact V1 cameras. Reference Phase 4/6 paired panels by path. |
| F. Fixed semantic-ID classes | `MATCHED_WITH_LIMITATIONS` | Exact Phase 4 class list, palette, camera JSONs and V3A center-projection method; checkpoint population and sampled centers differ. |
| G. Estimated trajectory in geometry | `MATCHED_WITH_LIMITATIONS` | Same 2,000-pose estimated-center convention, V3A camera and display semantics; Phase 7 positions differ. Direct projection audit found some Phase 7 centers outside the Phase 4 V3A near/far/frustum coverage, so preserve camera unchanged and disclose clipping. No GT overlay is in the reference. |
| H. Full-scene semantic maps | `MATCHED_WITH_LIMITATIONS` | Learned semantic-color map is already exact V1 matched; fixed IDs require V3A camera/palette diagnostic, with different checkpoint and observed V3A camera coverage. Keep the two representations separate. |

No required family lacks a reference. Exact output paths, hashes and planned
Phase 7 destinations are in `PHASE7_GATE3_ADVANCED_VISUALIZATION_PLAN.md`.

## Verified Phase 7 inputs

Checkpoint SHA256 is
`a02dd4b4ecfd9c982866cf4a4c38c187ef22c75049b8328e18eea20608944917`.
It contains 4,499,583 finite aligned Gaussian records and 2,000 estimated
pose slots / finite `gt_w2c_all_frames`; `keyframe_time_indices` has 402
entries. `params.ply` XYZ equals `means3D` exactly, and its decoded DC color
equals `rgb_colors`; `seg_params.ply` XYZ equals `means3D` and decoded DC
color equals `semantic_colors`. Both PLYs have 4,499,583 rows. Full shapes,
hashes and camera fit measurements are recorded in the plan.

The Phase 4/6 reference artifacts, camera JSONs, reports and source scripts
were inspected read-only. Phase 4 and Phase 6 artifacts were not changed.
