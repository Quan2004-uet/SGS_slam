# Phase 7 Gate 3 — Visualization comparison index

**State:** Phase 7 advanced renders and three-phase boards are generated. This
index maps the verified Phase 4/6 references to the Phase 7 output package;
per-file paths and SHA256 values are in the advanced visualization manifest.

| Family | Phase 4 reference | Phase 6 reference | Phase 7 artifact / intended output | Match status |
|---|---|---|---|---|
| Free-view full-scene RGB | `/home/robot/research/SGS_slam/results/runtime_artifacts/phase4_vb001_visualization/reconstruction/` (V1 cameras overview, oblique, top_oblique) | `/home/robot/research/SGS_slam/results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/reconstruction/` | Existing `/home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/visualization/reconstruction/` | `EXACT_MATCHED_REFERENCE` camera JSONs; existing P7 files retained |
| Free-view learned semantic color and paired views | `/home/robot/research/SGS_slam/results/runtime_artifacts/phase4_vb001_visualization/semantic/`, `paired/` | `/home/robot/research/SGS_slam/results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/semantic/`, `paired/` | Existing P7 `visualization/semantic/` and `visualization/paired/` | `EXACT_MATCHED_REFERENCE` viewpoints; map/checkpoint differs by experiment |
| Observed-camera RGB | `phase4_vb001_visualization_v2/frames/frame_{0000,0499,0999,1499,1999}/rendered_rgb.png` with same-frame GT/metadata | Phase 6 `va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/rgb/unfiltered/` | `advanced_visualization/phase7_only/observed_camera/rgb/`; 5 triptychs in `compare_phase4_phase6_phase7/A_observed_rgb/` | `MATCHED_WITH_LIMITATIONS`; same cameras and native rasterizer, Phase 6 background is white while Phase 4/7 use black |
| Observed-camera metric depth | Phase 4 V2 raw camera-z NPY and canonical Turbo PNG for five frames | Phase 6 saved raw NPY under `reconstruction_fidelity/phase6_rendered/depth/` | `phase7_only/observed_camera/depth/` (float32 NPY + PNG); 5 boards and normalized source views under `compare_phase4_phase6_phase7/B_observed_depth/` | `MATCHED_WITH_LIMITATIONS`; all three displays use fixed `[0,6]` m Turbo, raw metric convention preserved |
| Observed learned semantic colors | Phase 4 V2 `rendered_semantic_raw.png` and GT reference | Phase 6 `phase6_rendered/semantic/raw/` | `phase7_only/observed_camera/semantic/`; 5 triptychs in `compare_phase4_phase6_phase7/C_observed_semantic/` | `MATCHED_WITH_LIMITATIONS`; raw learned colors retained; Phase 6 uses a white background |
| RGB versus learned semantic map | Phase 4 V1 `paired/` | Phase 6 `va2_phase4_matched/paired/` | Existing P7 paired views copied under `phase7_only/free_view/paired/`; V3A boards under `compare_phase4_phase6_phase7/E_cross_modal/` | `EXACT_MATCHED_REFERENCE` cameras; relative results are qualitative |
| Fixed semantic-ID classes | Phase 4 V3A `semantic/classwise/`, `semantic/categorical/`, class/palette metadata | Phase 6 `visualization/va2_phase4_extended_matched/` corresponding V3A families | `phase7_only/v3a_diagnostics_r02/semantic/`; boards `compare_phase4_phase6_phase7/F_fixed_semantic_classes/` and `/H_full_scene_semantic/fixed_ids/` | `MATCHED_WITH_LIMITATIONS`; uses exact selected IDs/palette, different map population and known camera clipping |
| Estimated camera trajectory in map | Phase 4 V3A `trajectory/` using all 2,000 estimated poses | Phase 6 V3A-matched `trajectory/` | `phase7_only/v3a_diagnostics_r02/trajectory/`; boards `compare_phase4_phase6_phase7/G_estimated_trajectory/` | `MATCHED_WITH_LIMITATIONS`; all 2,000 P7 estimated poses, no GT overlay |
| Full-scene RGB / geometry / semantic diagnostic views | Phase 4 V3A `rgb/`, `geometry/`, `semantic/`, `comparisons/` | Phase 6 extended matched counterparts | `phase7_only/v3a_diagnostics_r02/` and boards under `compare_phase4_phase6_phase7/D_full_scene_rgb/`, `/E_cross_modal/`, `/H_full_scene_semantic/learned_v3a_raw/` | `MATCHED_WITH_LIMITATIONS`; retain exact V3A cameras and document Phase 7 center clipping |

Canonical observed frames are 0, 499, 999, 1499 and 1999; each uses the
Phase 4 V2 `frame_metadata.json` at 1200×680 and its saved estimated `w2c`
plus intrinsics. Canonical V1 free-view JSONs are already copied into the P7
free-view visualization. V3A cameras are `trajectory_observed`,
`room_overview`, and `top_oblique` at 960×540. The full source paths,
camera hashes and protocol are in
[`PHASE7_GATE3_ADVANCED_VISUALIZATION_AUDIT.md`](PHASE7_GATE3_ADVANCED_VISUALIZATION_AUDIT.md).

Phase 7 outputs and boards now exist at the paths above. Their per-file SHA256
entries are in `advanced_visualization/metadata/advanced_visualization_manifest.json`.
The checkpoint was not copied into the visualization package; Phase 4/6 source
artifacts were read-only.
