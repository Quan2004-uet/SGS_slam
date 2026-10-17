# P6-BAM-007 — Phase 4 / Phase 6 Qualitative Comparison Plan

Status: `INITIALIZED — GATES 0–1 AUDITED; GATES 2–5 NOT AUTHORIZED`

Date: 2026-10-17  
Branch / audit HEAD: `phase5-profiling-instrumentation` /
`17fe98a82a1c7c38b05b7fdefe154bb7b0002453`  
P6 experiment source revision: `002927f3b24dd69418c17da08bd4ae987bae9ee2`

This report plans camera-aligned figure packaging from existing, validated
outputs. It does not claim that comparison figures have been generated. Phase 4
and Phase 6 models, evaluation data, and source PNGs remain immutable.

## 1. Scientific references and provenance

### Phase 4

- Gate: `PASS_PHASE4_CLOSURE`; reference `PHASE4-VB-001 — CPU Keyframe Offload`.
- Checkpoint:
  `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`
- Expected and locally verified SHA256:
  `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`.
- Visualization families:
  - `results/runtime_artifacts/phase4_vb001_visualization/` — 9 PNGs; V1.
  - `results/runtime_artifacts/phase4_vb001_visualization_v2/` — 75 PNGs;
    fixed frames 0, 499, 999, 1499, 1999.
  - `results/runtime_artifacts/phase4_vb001_visualization_v3a/` — 26 PNGs;
    full-scene RGB, geometry, semantic, and trajectory diagnostics.
  - V2/V3A gates are respectively `PASS_V2_CAMERA_ALIGNED_QUALITATIVE` and
    `PASS_V3A_FULL_SCENE_VISUALIZATION_PROOF`; V1 gate is
    `PASS_V1_VISUALIZATION_AUDIT`.

### Phase 6

- Run: `P6-BAM-006-FULL`, method V-A2 (Budget-Aware Mapping + CPU Keyframe
  Offload), gate `PASS_P6_BAM_006_FULL_SCENE_QUALITY_CONSTRAINED`.
- Run root:
  `results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/`.
- Verified source hashes: `params.npz`
  `1193f5d5a854225d6e9fc68154d459b5eb026e056a91b5f00639b8da0facd0a5`;
  `params.ply`
  `dc10441cd383ad7861d27fb70a4f9a76fe9dd88a91e2bacc197b18bbe24cb50a`;
  `seg_params.ply`
  `98676b4c3e6447681f99426153dfb112bee76882ac9f5d3a18cf11f4832fec21`.
- Visualization root:
  `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/`.
  - `va2/` — 9 PNGs; original Phase 6 camera family, not Phase 4 camera matched.
  - `va2_phase4_matched/` — 9 PNGs; Phase 4 V1 `overview`, `oblique`,
    `top_oblique` cameras.
  - `va2_phase4_extended_matched/` — 105 PNGs; V2/V3A camera families.
- Extended package counts: 65 PNGs in `reconstruction_fidelity/` (50 are
  copied Phase 4 references, not new Phase 6 predictions), 26 in
  `cross_modal_overview/`, 13 in `semantic_id_structure/`, and 1 in
  `trajectory_in_geometry/`.
- The existing HF visualization-only backup is documented as independently
  verified: private `QuanDinh/SGS-SLAM-assets`, path
  `phase6_bam/p6_bam_006/visualization/`, commit
  `6cc42c8db3ce69f58bdb2de797c03b90bf930e73`, 186 files / 123 PNGs. Its report
  is `docs/research/phase6_bam/P6_BAM_006_HF_VISUALIZATION_BACKUP_REPORT.md`.

## 2. Camera evidence and identity

### Phase 4 V1 family

Camera sources are the authoritative files in
`results/runtime_artifacts/phase4_vb001_visualization/cameras/`. The extended
package contains copies under `.../va2_phase4_extended_matched/cameras/v1/`.
Recorded SHA256 values:

| View | SHA256 |
|---|---|
| `overview` | `c5e0029b1758788322538ce27e587c8cdfa5a3277aba331431e50d5ac80865bb` |
| `oblique` | `9846a224e93b3615afd45097b9106037c3550b5199b74d4e0550f328ad220120` |
| `top_oblique` | `0d865494919fb2066cf769ef654163ee3f1e262d5ebb4cf8b95681d6934ec196` |

The Phase 6 V1 matched package was rendered from these Phase 4 camera
definitions. V1 `top_oblique` is not the V3A `top_oblique` camera.

### Phase 4 V2 observed-frame family

Authoritative source metadata is each
`results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_NNNN/frame_metadata.json`.
The fixed frame IDs are `0000`, `0499`, `0999`, `1499`, `1999`; metadata
contains the Phase 4 estimated `w2c`, intrinsics, and dimensions. The extended
Phase 6 package copies camera metadata under
`.../va2_phase4_extended_matched/reconstruction_fidelity/cameras/phase4_v2/`.
Its validation report records byte-identical copies. During Gate 2, compare
source/copy hashes and image dimensions for every one of the five pairs before
composing any figure.

### Phase 4 V3A full-scene family

Authoritative files are under
`results/runtime_artifacts/phase4_vb001_visualization_v3a/cameras/`; copies
are under `.../va2_phase4_extended_matched/cameras/v3a/`. Recorded SHA256:

| View | SHA256 |
|---|---|
| `room_overview` | `f5598e540e78c8c838f3db0e83194520477e528735b65336c5f66a590b7a8cfc` |
| `top_oblique` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` |
| `trajectory_observed` | `df75161d510552a31bd5096ac3cc5a07eea5b58cf9c0ac777d15aa507af17f1a` |

The V1 and V3A `top_oblique` hashes differ and denote different cameras.
Pair only within the V1 or V3A family; never join views using the name alone.

## 3. Candidate pair matrix

Classification is based on the saved report, package manifest, camera hashes,
and presence of source images. `READY_FOR_SIDE_BY_SIDE` means an existing
same-camera/same-modality pair can be shown directly while retaining the
representation's stated meaning. `READY_WITH_EXPLICIT_CAVEAT` requires a
caption or nearby legend explaining the listed limitation. Gate 2 must extract
the precise image SHA256, resolution, and camera-source record into a generated
pair manifest before composing figures.

| Family / modality | Phase 4 source | Phase 6 source | Camera source / checksum | Frame/view and resolution | Meaning and interpretation | Status |
|---|---|---|---|---|---|---|
| V1 RGB map | `phase4_vb001_visualization/reconstruction/{overview,oblique,top_oblique}.png` | `phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/reconstruction/{overview,oblique,top_oblique}.png` | Phase 4 V1 camera JSON; three hashes above | 3 views, 1600×900 per image | RGB Gaussian reconstruction; same view, independently trained map | `READY_WITH_EXPLICIT_CAVEAT` |
| V1 learned semantic color | `phase4_vb001_visualization/semantic/{overview,oblique,top_oblique}.png` | `.../visualization/va2_phase4_matched/semantic/{overview,oblique,top_oblique}.png` | Same exact V1 cameras | 3 views, 1600×900 | Learned per-Gaussian semantic colors; color values are not categorical class IDs | `READY_WITH_EXPLICIT_CAVEAT` |
| V2 RGB | `phase4_vb001_visualization_v2/frames/frame_NNNN/rendered_rgb.png` | `.../visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/rgb/unfiltered/frame_NNNN.png` | Frame metadata; copied byte-identical per package validation | 5 frames, expected 1200×680 | Observed-frame RGB render at Phase 4 estimated camera | `READY_WITH_EXPLICIT_CAVEAT` |
| V2 depth | `...v2/frames/frame_NNNN/rendered_depth_common_0_6m.png` (preferred shared scale) | `...extended_matched/reconstruction_fidelity/phase6_rendered/depth/frame_NNNN_common_0_6m.png` | Same per-frame Phase 4 camera | 5 frames, expected 1200×680 | Metric depth display, shared 0–6 m range; use common scale | `READY_WITH_EXPLICIT_CAVEAT` |
| V2 learned semantic color | `...v2/frames/frame_NNNN/rendered_semantic_raw.png` | `...extended_matched/reconstruction_fidelity/phase6_rendered/semantic/raw/frame_NNNN.png` | Same per-frame Phase 4 camera | 5 frames, expected 1200×680 | Raw learned semantic-color render; distinct from GT-palette-assisted recoloring | `READY_WITH_EXPLICIT_CAVEAT` |
| V3A RGB overview | `phase4_vb001_visualization_v3a/rgb/unfiltered/{room_overview,top_oblique,trajectory_observed}.png` | `...extended_matched/cross_modal_overview/rgb/unfiltered/{room_overview,top_oblique,trajectory_observed}.png` | Phase 4 V3A JSON; three hashes above | 3 views, nominal 960×540 | RGB Gaussian map views | `READY_WITH_EXPLICIT_CAVEAT` |
| V3A raw learned semantic color | `...v3a/semantic/raw/{room_overview,top_oblique,trajectory_observed}.png` | `...extended_matched/cross_modal_overview/semantic/raw/{room_overview,top_oblique,trajectory_observed}.png` | Same exact V3A cameras | 3 views, nominal 960×540 | Learned colors; not a fixed class palette | `READY_WITH_EXPLICIT_CAVEAT` |
| V3A geometry-only centers | `...v3a/geometry/{room_overview,top_oblique,trajectory_observed}.png` | `...extended_matched/cross_modal_overview/geometry/{room_overview,top_oblique,trajectory_observed}.png` | Same exact V3A cameras | 3 views, 960×594 including title band | Gaussian-center diagnostic; not a continuous surface or novel-view accuracy | `READY_WITH_EXPLICIT_CAVEAT` |
| V3A fixed semantic IDs | `...v3a/semantic/categorical/{room_overview,top_oblique,trajectory_observed}.png` | `...extended_matched/semantic_id_structure/{room_overview,top_oblique,trajectory_observed}.png` | Same exact V3A cameras and verified 29-class Replica palette | 3 views, 960×594 | Fixed per-Gaussian IDs visualized categorically; not learned colors or per-pixel output | `READY_FOR_SIDE_BY_SIDE` |
| V3A fixed semantic-ID classwise | `...v3a/semantic/classwise/{blinds,ceiling,chair,floor,rug,sofa,table,wall}_top_oblique.png` plus `selected_classes_overview_top_oblique.png` | `...extended_matched/semantic_id_structure/` same filenames | Exact V3A `top_oblique` camera | 9 selections, 960×594 | Same palette/selection labels; compare class presence as Gaussian-center diagnostics | `READY_FOR_SIDE_BY_SIDE` |
| V3A estimated trajectory | `...v3a/trajectory/estimated_trajectory_3d.png` | `...extended_matched/trajectory_in_geometry/estimated_trajectory_3d.png` | Exact V3A `top_oblique` camera | 1 view, 960×594 | Each system's estimated trajectory over its reconstructed geometry | `READY_WITH_EXPLICIT_CAVEAT` |

### Inventory summary

There are **43 candidate pairs** in the matched families: V1 has 6, V2 has 15,
and V3A has 22. Of these, **12 are ready for direct side-by-side** (fixed-ID
categorical and class-wise views), **31 are ready with explicit caveats**, and
0 are currently noncomparable or missing. The original Phase 6 `va2/` family
is excluded because it does not use the Phase 4 camera set. The exact per-pair
image file hashes and dimensions remain to be emitted in the Gate 2 pair
manifest; the figure package must not infer comparability from names alone.

## 4. Scientific interpretation constraints

1. **Observed-view fidelity:** the five V2 Phase 6 predictions use the Phase 4
   estimated camera parameters. Show the exact same reference camera for both
   maps; do not substitute P6 estimated poses or claim trajectory equality.
2. **Depth:** use the same fixed `[0, 6] m` display scale and colorbar for both
   map renders. Ground-truth depth may be shown once as a shared reference.
   Distinguish rendered depth from GT and do not recompute error metrics.
3. **Semantic color:** label the learned color pass as `Learned semantic color`
   or `Raw learned semantic-color rendering`. Do not call it semantic-ID output.
   Do not mix it with Phase 4's GT-palette-assisted `rendered_semantic_recolored`
   or `semantic_color_mIoU` evaluation protocol. GT images may appear as a
   separately labeled reference, not as a prediction.
4. **3D diagnostics:** label geometry-only views `Gaussian-center geometry
   diagnostic`; these do not depict a continuous surface. Label fixed IDs as
   `Fixed per-Gaussian semantic IDs` and learned colors separately.
5. **Trajectory:** present the Phase 4 and Phase 6 estimated trajectories
   independently on their corresponding reconstructed geometries, under the
   same V3A camera. They need not be identical; do not imply they are.
6. **Presentation:** use consistent family-specific view labels, panel sizes,
   modality names, scales, and the verified 29-class legend. Keep original
   unfiltered source images. No crop, contrast, color, or other cosmetic change
   may conceal reconstruction artifacts. Any resizing for layout must be
   uniform and documented; source pixels remain untouched.

## 5. Proposed figure layouts

### Figure A — observed-frame reconstruction fidelity

Five frame rows (`0, 499, 999, 1499, 1999`) and modality blocks for RGB, depth,
and raw learned semantic color. Within each block show Phase 4 and Phase 6
renders at equal displayed dimensions; include GT RGB/depth/semantic only as
clearly labeled single reference columns where appropriate. Depth panels share
the same `[0, 6] m` scale. Avoid duplicating GT as if it were a method output.

### Figure B — full-scene cross-modal 3D overview

Rows for `room_overview`, V3A `top_oblique`, and `trajectory_observed`; columns
for Phase 4/Phase 6, with separately labeled RGB reconstruction, Gaussian
center geometry diagnostic, raw learned semantic-color map, and fixed semantic
IDs where this column remains legible. If a single slide is too dense, split by
modality while retaining the same three V3A views and camera identity.

### Figure C — fixed semantic-ID structure

Use the same 29-class Replica palette and legend for both systems; show three
categorical views and a selected class-wise panel with the same class set. State
that colors map fixed per-Gaussian IDs. Do not imply a learned per-pixel
semantic prediction.

### Figure D — estimated trajectory in reconstructed geometry

Place Phase 4 and Phase 6 trajectory overlays in separate, clearly labeled
panels rendered from the same V3A `top_oblique` camera definition. Label the
trajectory as estimated per system; retain differences rather than aligning or
editing paths to imply identity.

## 6. Ordered execution stages

Only Gates 0–1 are authorized in this initialization.

| Gate | Work | State |
|---|---|---|
| 0 — read-only source/artifact audit | Confirm repository identity, protected references, report claims, model hashes, package files and backup report | Completed for initialization |
| 1 — camera/modality matrix | Inventory candidate pairs, distinguish camera families, record interpretation constraints and missing caveats | Initial audit documented; per-pair machine-readable hash/resolution manifest is a Gate 2 preflight |
| 2 — CPU-only side-by-side figures | After researcher approval, compose only existing PNGs in a new isolated output root; verify source hashes remain unchanged | Not authorized / not started |
| 3 — thesis/slide packaging | After approval, create labeled thesis-quality layouts and captions from Gate 2 outputs | Not authorized / not started |
| 4 — validation and interpretation | Validate layout, sources, camera identity, shared scales, caption claims, manifest and diff; no metric recomputation | Not authorized / not started |
| 5 — review, backup, publication | Researcher review, approved backup, and separately authorized GitHub publication if requested | Not authorized / not started |

Any proposal requiring new rendering, evaluation, or data retrieval must be
separated from these CPU-only composition gates and receive explicit approval.

## 7. Proposed output tree

All future outputs should be new and isolated, with no modification to source
PNGs or models:

```text
results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/
  source_pair_manifest.json
  figures/
    observed_frame_fidelity_rgb_depth_semantic.png
    full_scene_cross_modal_overview.png
    fixed_semantic_id_structure.png
    estimated_trajectory_in_geometry.png
  thesis/
    figure_captions.md
    source_provenance.md
  validation/
    validation_report.json
    source_hashes_before_after.txt
```

The precise export formats and whether figures belong in a slide deck or thesis
document remain for the researcher to choose at the Gate 2 approval point.

## 8. Acceptance criteria for future gates

- Every pair manifest row records Phase 4 path, Phase 6 path, both image
  SHA256s, camera source/hash, frame or view, image dimensions, modality,
  semantic interpretation, classification, and caveat.
- Camera JSON or frame metadata equality is verified by bytes/hash, not labels.
- Phase 4 V1 `top_oblique` and V3A `top_oblique` remain separate groups.
- The five frame IDs and all three modalities are present; depth has one shared
  fixed range and color scale.
- GT is visibly identified as reference only; no semantic recoloring is
  described as raw learned semantic color.
- Fixed ID figures use the verified common palette and state their
  per-Gaussian metadata meaning.
- Geometry and trajectory figures state that Gaussian centers are diagnostics
  and trajectories are independently estimated.
- Source image/model hashes remain unchanged; outputs are written only to a
  new directory; originals remain available and unfiltered.
- Captions make no claims of statistical non-inferiority, full-scene runtime
  speedup, adaptive superiority over fixed-45, novel-view accuracy, or
  identical trajectories.
- No SLAM run, rerender, metric recomputation, or model mutation is involved.

## 9. Unresolved questions

- At Gate 2, verify the exact subpaths of the 15 Phase 6 frame renders against
  the actual manifest (the report provides family inventory but path discovery
  should be manifest-driven).
- Confirm the source image dimensions and hashes for every proposed pair and
  resolve any differing title bands/borders with layout-only padding rather
  than cropping.
- Decide whether GT semantic should be omitted from the primary comparison or
  included as one reference column; it must not be confused with model output.
- Researcher to select thesis figure export formats and whether a slide deck is
  in scope.
- No live Hugging Face state query was made; only the prior independently
  verified backup report was consulted.

## 10. Next approval decision

Researcher approval is required before Gate 2 begins. The requested approval
should authorize CPU-only composition from existing PNG files into the new
`p6_bam_007_qualitative_comparison/` tree. Gates 3–5 and any additional
rendering/evaluation/publication remain separate approvals. Until then, this
plan and its read-only audit are the complete SESSION_021 initialization.

## Appendix A — Per-pair source audit (read-only initialization)

The following 43 records were checked against the existing local PNGs and camera metadata. Image SHA256 and dimensions are from the source files; no image was created or changed. Camera SHA256 identifies the applicable Phase 4 camera JSON or copied per-frame camera metadata. Exact camera identity within each pair is supported by the V1/V3A camera byte checks and the V2 metadata byte checks recorded in SESSION_021.

| Family | Frame/view | Modality | Phase 4 PNG | Phase 6 PNG | Camera SHA256 | P4/P6 size | P4 image SHA256 | P6 image SHA256 | Interpretation | Classification |
|---|---|---|---|---|---|---|---|---|---|---|
| V1 | overview | RGB Gaussian reconstruction | `results/runtime_artifacts/phase4_vb001_visualization/reconstruction/overview.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/reconstruction/overview.png` | `c5e0029b1758788322538ce27e587c8cdfa5a3277aba331431e50d5ac80865bb` | 1600×900 / 1600×900 | `edabe4dcc998ed9adbe4059592c46023ea4a03ab09c16d86b05192c9139e4513` | `b56f6fe1e46191f5d356d169ee7242102a13d267ba9598deacdc49c295c2b638` | RGB Gaussian map render; independently trained maps; same camera. | READY_WITH_EXPLICIT_CAVEAT |
| V1 | overview | Learned semantic color | `results/runtime_artifacts/phase4_vb001_visualization/semantic/overview.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/semantic/overview.png` | `c5e0029b1758788322538ce27e587c8cdfa5a3277aba331431e50d5ac80865bb` | 1600×900 / 1600×900 | `ae057dd2120f653b4151474e260deb64b41c92929ac8d82deda80d70400749ea` | `c29d5aaf2893294b358bf3431b57bf8ec5d8c408a256ba1d716c6a06581103e7` | Learned per-Gaussian semantic colors; not categorical IDs. | READY_WITH_EXPLICIT_CAVEAT |
| V1 | oblique | RGB Gaussian reconstruction | `results/runtime_artifacts/phase4_vb001_visualization/reconstruction/oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/reconstruction/oblique.png` | `9846a224e93b3615afd45097b9106037c3550b5199b74d4e0550f328ad220120` | 1600×900 / 1600×900 | `99621657f7d005327f1a999e6d033adecc2bc316eb6c8d64f5932916c91b0efd` | `e945e65ffe311b12fa0170d6e4e6317357c697678a7de3af6b8fa7b32bb3e0be` | RGB Gaussian map render; independently trained maps; same camera. | READY_WITH_EXPLICIT_CAVEAT |
| V1 | oblique | Learned semantic color | `results/runtime_artifacts/phase4_vb001_visualization/semantic/oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/semantic/oblique.png` | `9846a224e93b3615afd45097b9106037c3550b5199b74d4e0550f328ad220120` | 1600×900 / 1600×900 | `44062aa0cca17c94efc478c28652538b2efc846297aee4a299441341820085a1` | `c7657cca66be4cad45bb9d828466e0fca170273df78e23108884b4fdb41f87de` | Learned per-Gaussian semantic colors; not categorical IDs. | READY_WITH_EXPLICIT_CAVEAT |
| V1 | top_oblique | RGB Gaussian reconstruction | `results/runtime_artifacts/phase4_vb001_visualization/reconstruction/top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/reconstruction/top_oblique.png` | `0d865494919fb2066cf769ef654163ee3f1e262d5ebb4cf8b95681d6934ec196` | 1600×900 / 1600×900 | `75105e06d8213286dd412a5907e5d5756c0c356b1e2a2ec21322c7f650c0069f` | `76abc689a76d90922af2ce585ab262bc48f86ba73ccf05cf21a1633c69dabc62` | RGB Gaussian map render; independently trained maps; same camera. | READY_WITH_EXPLICIT_CAVEAT |
| V1 | top_oblique | Learned semantic color | `results/runtime_artifacts/phase4_vb001_visualization/semantic/top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/semantic/top_oblique.png` | `0d865494919fb2066cf769ef654163ee3f1e262d5ebb4cf8b95681d6934ec196` | 1600×900 / 1600×900 | `b7a6f1fb7abe4cc9dba6aaf6301b83f878d352ef3b8f1bef754921d3c473d488` | `84f32c8ba290a68fe4d9fce2a8ff2a54e4d693c27c9545bd11cdf5ca69890fa6` | Learned per-Gaussian semantic colors; not categorical IDs. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 0000 | RGB | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_0000/rendered_rgb.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/rgb/unfiltered/frame_0000.png` | `99d64e939a4d9034c9faee2086579a8f1f4ad5cd77cd3c6bb1462e53c3fbc2ed` | 1200×680 / 1200×680 | `b44aa4447f696b92dd83dc59597ca76edb6156a9ccb250183c10d255793265b7` | `96494335571e925e01fc22aef4d08c832d57530a91a3a923cdfd3e53e9f38b56` | Observed-frame RGB; P6 uses the Phase4 estimated camera. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 0000 | Metric depth [0,6 m] | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_0000/rendered_depth_common_0_6m.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/depth/frame_0000_common_0_6m.png` | `99d64e939a4d9034c9faee2086579a8f1f4ad5cd77cd3c6bb1462e53c3fbc2ed` | 1200×680 / 1200×680 | `504958c395831d43531424837b05c4a731815f5ff2949d71762a1fa9868ef7e3` | `60ddaedec883df7c1f7e1457ca537c93ef2bfbac966ce137ddf8139bc3d0c970` | Metric depth visualization; same fixed 0–6 m display range. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 0000 | Raw learned semantic color | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_0000/rendered_semantic_raw.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/semantic/raw/frame_0000.png` | `99d64e939a4d9034c9faee2086579a8f1f4ad5cd77cd3c6bb1462e53c3fbc2ed` | 1200×680 / 1200×680 | `2c14b4b5d90f25b8d481945c7aacf77e0b213bc7e4f2435b61e33419fba76e39` | `6423dc2cd2f63d137e6022e33f5f67a7681e1feaa8106658a73945f8a7d21a06` | Raw learned semantic-color render; not GT-palette recoloring. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 0499 | RGB | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_0499/rendered_rgb.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/rgb/unfiltered/frame_0499.png` | `b946370943dddd5d191b10c6243ac6c61badf7206e9aa527d72b6ea0d4979754` | 1200×680 / 1200×680 | `9a69fcbe003dccdfc47207a3ddd55b9e6b4e5d1e626493d953e5a913c1a3f9e9` | `baa5f4ada50d83af62995bee7833f0a812e7b08fefb88ac5d1991f7825da017c` | Observed-frame RGB; P6 uses the Phase4 estimated camera. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 0499 | Metric depth [0,6 m] | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_0499/rendered_depth_common_0_6m.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/depth/frame_0499_common_0_6m.png` | `b946370943dddd5d191b10c6243ac6c61badf7206e9aa527d72b6ea0d4979754` | 1200×680 / 1200×680 | `e8f7f92756ed97129c646cf34a26bcde6aa96983b7cbea6508dc89239b4d1683` | `bbb2c53c6fe4c8ed89c9afc2143f725a5f673e72ea7ff5cd36a9524360f72e72` | Metric depth visualization; same fixed 0–6 m display range. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 0499 | Raw learned semantic color | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_0499/rendered_semantic_raw.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/semantic/raw/frame_0499.png` | `b946370943dddd5d191b10c6243ac6c61badf7206e9aa527d72b6ea0d4979754` | 1200×680 / 1200×680 | `b301accb455d31535198307e23c826357e6fb20b21ecfd52eca5aed2d1a5c2c2` | `9bc43b0bc49d09dec04dabecbd590f011b75d321f63b589b25133c8ef5909c6a` | Raw learned semantic-color render; not GT-palette recoloring. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 0999 | RGB | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_0999/rendered_rgb.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/rgb/unfiltered/frame_0999.png` | `36175f04a5fdd796c153ada50047bc89a09189f1e2855366d55c9ad34d0e8f40` | 1200×680 / 1200×680 | `d90a96ae697c5700ae2b630ece6643f21146ba83e911307cd0dd614b063c0eb1` | `35122d9fdc1ad60010c97b66dcf54bcc4f76caed7367027732f32a76e2939962` | Observed-frame RGB; P6 uses the Phase4 estimated camera. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 0999 | Metric depth [0,6 m] | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_0999/rendered_depth_common_0_6m.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/depth/frame_0999_common_0_6m.png` | `36175f04a5fdd796c153ada50047bc89a09189f1e2855366d55c9ad34d0e8f40` | 1200×680 / 1200×680 | `de04b21a154d0ca5d000d5d1508810fcf168b189b7e55ff8691063bcfd9224fc` | `06e11fb9536aeeb33aa244194ca5ebbb852d5b2cd2d9575ad49466a825e750c0` | Metric depth visualization; same fixed 0–6 m display range. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 0999 | Raw learned semantic color | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_0999/rendered_semantic_raw.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/semantic/raw/frame_0999.png` | `36175f04a5fdd796c153ada50047bc89a09189f1e2855366d55c9ad34d0e8f40` | 1200×680 / 1200×680 | `09f3eee03a18bcfa8596181421e537a1e4f6ebf2a5222e8f5728332623eb0a20` | `f036034e7534dc380e65e29ab2dd909b16f9a862901511e30b633a9f46de5ed0` | Raw learned semantic-color render; not GT-palette recoloring. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 1499 | RGB | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_1499/rendered_rgb.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/rgb/unfiltered/frame_1499.png` | `070b65b24305728dfeb7fa68ac51a08c837329db9f96715f0ecf1feba9a73f27` | 1200×680 / 1200×680 | `b81380faac7edb746bed8836d0fe312cd2227e1e01639d04345a076cedf94b46` | `d93d4a8b522469aa23012295a10cf5e3d955f63b1c8fb27fa285469923497dbb` | Observed-frame RGB; P6 uses the Phase4 estimated camera. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 1499 | Metric depth [0,6 m] | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_1499/rendered_depth_common_0_6m.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/depth/frame_1499_common_0_6m.png` | `070b65b24305728dfeb7fa68ac51a08c837329db9f96715f0ecf1feba9a73f27` | 1200×680 / 1200×680 | `59e8b38c983e7649d30101c3b02480ece9590f3c10fe791a0b57b01ea6ecf994` | `87479e51ec93a20803def08f6a97403cb61df671b43d1a62bbc736496b2a7f59` | Metric depth visualization; same fixed 0–6 m display range. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 1499 | Raw learned semantic color | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_1499/rendered_semantic_raw.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/semantic/raw/frame_1499.png` | `070b65b24305728dfeb7fa68ac51a08c837329db9f96715f0ecf1feba9a73f27` | 1200×680 / 1200×680 | `728a3d26dde85be5ab354b4f12b691708c04f391713b4bb9587fa1410b444a56` | `bc6886895f62106e5f8fd071b37c0a270254d5e018ea37de4ad248f5c2cd84d4` | Raw learned semantic-color render; not GT-palette recoloring. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 1999 | RGB | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_1999/rendered_rgb.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/rgb/unfiltered/frame_1999.png` | `4a6e8ac9260204e2f2cc41ca0c6d19c97819e8b7dabf81e1c2a267fa4f83bec9` | 1200×680 / 1200×680 | `b59c27334061317a5fb96c4ec4dfed3fe3f89cdf6cd3bb4e260d28892aac3d79` | `3e7ed1f6fb5cabba1215bb0e5733968c63cc3c2c62a98d6aeb274052e043483c` | Observed-frame RGB; P6 uses the Phase4 estimated camera. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 1999 | Metric depth [0,6 m] | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_1999/rendered_depth_common_0_6m.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/depth/frame_1999_common_0_6m.png` | `4a6e8ac9260204e2f2cc41ca0c6d19c97819e8b7dabf81e1c2a267fa4f83bec9` | 1200×680 / 1200×680 | `0499240a856338babaeee99132d424bc469ee42ac4dcc49ad55789b73c5250db` | `095cbe490a8af27d1a0beafbe26403205e965464d685aa96a5b1d94152fd71ef` | Metric depth visualization; same fixed 0–6 m display range. | READY_WITH_EXPLICIT_CAVEAT |
| V2 | 1999 | Raw learned semantic color | `results/runtime_artifacts/phase4_vb001_visualization_v2/frames/frame_1999/rendered_semantic_raw.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/reconstruction_fidelity/phase6_rendered/semantic/raw/frame_1999.png` | `4a6e8ac9260204e2f2cc41ca0c6d19c97819e8b7dabf81e1c2a267fa4f83bec9` | 1200×680 / 1200×680 | `e90656cb04793feded00706a8b3f17ede285d7050b6e9908c19fce78e7a7a1d5` | `4349ad4498fa3be9433bd64b7c8cf7dddba968599f6df528dfd3cd822d5faeda` | Raw learned semantic-color render; not GT-palette recoloring. | READY_WITH_EXPLICIT_CAVEAT |
| V3A | room_overview | RGB | `results/runtime_artifacts/phase4_vb001_visualization_v3a/rgb/unfiltered/room_overview.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/cross_modal_overview/rgb/unfiltered/room_overview.png` | `f5598e540e78c8c838f3db0e83194520477e528735b65336c5f66a590b7a8cfc` | 960×540 / 960×540 | `34d7a798509509b95d6afdde9f7ae3f5b54de393c2091996330c0bf725686977` | `106dbad927f69688c3118f33dfeecda55e660300cbf599ac82e2c316ac47b77b` | RGB Gaussian reconstruction view. | READY_WITH_EXPLICIT_CAVEAT |
| V3A | room_overview | Raw learned semantic color | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/raw/room_overview.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/cross_modal_overview/semantic/raw/room_overview.png` | `f5598e540e78c8c838f3db0e83194520477e528735b65336c5f66a590b7a8cfc` | 960×540 / 960×540 | `4f60ace50aeb0aaaf2204ba70c05702e9b514d77e15515ed5cca22fdd39c6dd7` | `7c310b4f29f24c212f39d99f974d8b95ede7e0f4a95752df07c015d1a3fa5a74` | Learned semantic colors; color basis may differ between runs. | READY_WITH_EXPLICIT_CAVEAT |
| V3A | room_overview | Gaussian-center geometry | `results/runtime_artifacts/phase4_vb001_visualization_v3a/geometry/room_overview.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/cross_modal_overview/geometry/room_overview.png` | `f5598e540e78c8c838f3db0e83194520477e528735b65336c5f66a590b7a8cfc` | 960×594 / 960×594 | `df54447ef2151b2c4b4151bf08ff85e0c5f99d7d42fdfa4d7c3f6a617d35321c` | `237534268d311a2666e12610a11d66aaa1abd5cebff2c1fb4361d5045e0d70c6` | Gaussian-center diagnostic, not a continuous surface. | READY_WITH_EXPLICIT_CAVEAT |
| V3A | room_overview | Fixed semantic IDs | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/categorical/room_overview.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/semantic_id_structure/room_overview.png` | `f5598e540e78c8c838f3db0e83194520477e528735b65336c5f66a590b7a8cfc` | 960×594 / 960×594 | `fc1ebc2d60eee0470243a21800ff373c0f113d90fc81b33a93a23c848ed0bc28` | `5a77be9d85c48f9e53bf8f97314de4a80a75ce3f8a08e5e1ad064ead9a143dca` | Fixed per-Gaussian IDs with common verified Replica palette; not per-pixel prediction. | READY_FOR_SIDE_BY_SIDE |
| V3A | top_oblique | RGB | `results/runtime_artifacts/phase4_vb001_visualization_v3a/rgb/unfiltered/top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/cross_modal_overview/rgb/unfiltered/top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×540 / 960×540 | `65d112ac28758e1c46858b3b2184fefb5cbc0b96e62f2b483631171f5b5e2c0d` | `a8da101a06ec7cd410cd313357bb8d873530488b400d9a89e5f29b5cdf190140` | RGB Gaussian reconstruction view. | READY_WITH_EXPLICIT_CAVEAT |
| V3A | top_oblique | Raw learned semantic color | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/raw/top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/cross_modal_overview/semantic/raw/top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×540 / 960×540 | `e14b8f7a2c03a88132a305b48a9083229494d9941afb777a621833b85ca1899b` | `3ee27beb7374a7a581c65033942954fff61a0ccb36ffcf8d8ab707d1f6533a99` | Learned semantic colors; color basis may differ between runs. | READY_WITH_EXPLICIT_CAVEAT |
| V3A | top_oblique | Gaussian-center geometry | `results/runtime_artifacts/phase4_vb001_visualization_v3a/geometry/top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/cross_modal_overview/geometry/top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×594 / 960×594 | `62392f372c755efc440042e400a2813095a61091a460383062cd6d95d4299cf0` | `4850e841ceeec1bb48c3d1910d62315d5b89599f1c53acda6b6f9897564246b9` | Gaussian-center diagnostic, not a continuous surface. | READY_WITH_EXPLICIT_CAVEAT |
| V3A | top_oblique | Fixed semantic IDs | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/categorical/top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/semantic_id_structure/top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×594 / 960×594 | `28a193744e273c696119d4603d8d454e98c1de40f19f36a6466af65356be34f7` | `161e042c3459dc5e33978379bea155df15c72f018be5c82b989668f1a4035a60` | Fixed per-Gaussian IDs with common verified Replica palette; not per-pixel prediction. | READY_FOR_SIDE_BY_SIDE |
| V3A | trajectory_observed | RGB | `results/runtime_artifacts/phase4_vb001_visualization_v3a/rgb/unfiltered/trajectory_observed.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/cross_modal_overview/rgb/unfiltered/trajectory_observed.png` | `df75161d510552a31bd5096ac3cc5a07eea5b58cf9c0ac777d15aa507af17f1a` | 960×540 / 960×540 | `77ac4695d9b49d5fc1fc59e7424b9b8b5b88fc6a6119d989ad17dc40e1322bb5` | `9e727a89c79b2855c324927906ff33814425e489047f887a94b1341d62fd706a` | RGB Gaussian reconstruction view. | READY_WITH_EXPLICIT_CAVEAT |
| V3A | trajectory_observed | Raw learned semantic color | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/raw/trajectory_observed.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/cross_modal_overview/semantic/raw/trajectory_observed.png` | `df75161d510552a31bd5096ac3cc5a07eea5b58cf9c0ac777d15aa507af17f1a` | 960×540 / 960×540 | `81a01aad467901fab8e1b97e3a32a01f9e43fb66ab1bf14b3a603c0a8ecde70c` | `acea575d9fe6871b5da0767fa74c326ed61975eff36b777e79f807de4186e07e` | Learned semantic colors; color basis may differ between runs. | READY_WITH_EXPLICIT_CAVEAT |
| V3A | trajectory_observed | Gaussian-center geometry | `results/runtime_artifacts/phase4_vb001_visualization_v3a/geometry/trajectory_observed.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/cross_modal_overview/geometry/trajectory_observed.png` | `df75161d510552a31bd5096ac3cc5a07eea5b58cf9c0ac777d15aa507af17f1a` | 960×594 / 960×594 | `f6ab0deda67f7520d410463cb2e927ef42300cf42d5f3d4e34eaedb722dc687f` | `62d540717b679c4069c1c2b0c9106840ca759f16ddadd8bebf1c4dfed22f002a` | Gaussian-center diagnostic, not a continuous surface. | READY_WITH_EXPLICIT_CAVEAT |
| V3A | trajectory_observed | Fixed semantic IDs | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/categorical/trajectory_observed.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/semantic_id_structure/trajectory_observed.png` | `df75161d510552a31bd5096ac3cc5a07eea5b58cf9c0ac777d15aa507af17f1a` | 960×594 / 960×594 | `6207412ca36fa3dc9e3fb12b696153cef0cf0a2a78bbec7794c06ec1a59c9105` | `0e4fd1192863d54453775caa317d8ecf8c99a97dea44256cdb24e183587096b5` | Fixed per-Gaussian IDs with common verified Replica palette; not per-pixel prediction. | READY_FOR_SIDE_BY_SIDE |
| V3A | blinds_top_oblique.png | Fixed semantic-ID class selection | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/classwise/blinds_top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/semantic_id_structure/blinds_top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×594 / 960×594 | `3de723159668f2a38b201be23ff06a93f3cfa53188b5bec5716df909d3c99393` | `1ed98645cd7192e8df649a0bdbd9937fc0ac8894d903fe747e55cbacb11f4efb` | Same selected fixed-ID class(es) and common palette; Gaussian-center diagnostic. | READY_FOR_SIDE_BY_SIDE |
| V3A | ceiling_top_oblique.png | Fixed semantic-ID class selection | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/classwise/ceiling_top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/semantic_id_structure/ceiling_top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×594 / 960×594 | `de2efb17ba83584681dc1e29ba4861facc98eba8a7fc18953852a01ecd9ff355` | `e3cbc5f5dae6f864a600aa6303d74d11cc3bb3da0dfa896e55dfb53055d2ef0f` | Same selected fixed-ID class(es) and common palette; Gaussian-center diagnostic. | READY_FOR_SIDE_BY_SIDE |
| V3A | chair_top_oblique.png | Fixed semantic-ID class selection | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/classwise/chair_top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/semantic_id_structure/chair_top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×594 / 960×594 | `d1c8abca227c49c30ba8ef73f0e2dcc7f19b739eac78ce2068e0b2ead1075fbc` | `ad6b64aef3997706826166750cd55bdab6856fae72745e8ceeb5a7450a27c7ac` | Same selected fixed-ID class(es) and common palette; Gaussian-center diagnostic. | READY_FOR_SIDE_BY_SIDE |
| V3A | floor_top_oblique.png | Fixed semantic-ID class selection | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/classwise/floor_top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/semantic_id_structure/floor_top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×594 / 960×594 | `c05e4421ba49d31ee9ea6936030e2a12d29d72eba5ba14af033c4dba36df3734` | `e9363edfd30230aeaca4ed181cfc93612b06ccf75bbd5b46c9e18dfe4990c5ab` | Same selected fixed-ID class(es) and common palette; Gaussian-center diagnostic. | READY_FOR_SIDE_BY_SIDE |
| V3A | rug_top_oblique.png | Fixed semantic-ID class selection | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/classwise/rug_top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/semantic_id_structure/rug_top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×594 / 960×594 | `c3d3dda772702727829908436b1e6329fa32aa09a5d38f15d2c6406667549c0d` | `50dc67db86dfe94045fa07e7a4cae903eb010895a662f5bbe9584e69a24177ec` | Same selected fixed-ID class(es) and common palette; Gaussian-center diagnostic. | READY_FOR_SIDE_BY_SIDE |
| V3A | sofa_top_oblique.png | Fixed semantic-ID class selection | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/classwise/sofa_top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/semantic_id_structure/sofa_top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×594 / 960×594 | `d63730e5640517a22ce96d8bda7759ffe3a63c26db41dccacc949ecdf8bd11df` | `4f0db680b0e51dfcd2ae12f7120e79b996acfef5fa9f01216d300b3a64d7aaa1` | Same selected fixed-ID class(es) and common palette; Gaussian-center diagnostic. | READY_FOR_SIDE_BY_SIDE |
| V3A | table_top_oblique.png | Fixed semantic-ID class selection | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/classwise/table_top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/semantic_id_structure/table_top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×594 / 960×594 | `9c878e27b530c40b64e260991b7458a741adf533ca311f87df4c5d18933fe436` | `5f83f37a8fdc02079f53d616705baf9d4d749ca91e9f00306d44b9d727162f10` | Same selected fixed-ID class(es) and common palette; Gaussian-center diagnostic. | READY_FOR_SIDE_BY_SIDE |
| V3A | wall_top_oblique.png | Fixed semantic-ID class selection | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/classwise/wall_top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/semantic_id_structure/wall_top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×594 / 960×594 | `57c87a132eab27639bc6113095ff6596aac390b938e4271f2d96e9eb7dc1b94a` | `06f46d017b4a7d4a1a9da6ccf7ae0c4da0a127ec2482a2043624ac2ce8dcbc88` | Same selected fixed-ID class(es) and common palette; Gaussian-center diagnostic. | READY_FOR_SIDE_BY_SIDE |
| V3A | selected_classes_overview_top_oblique.png | Fixed semantic-ID class selection | `results/runtime_artifacts/phase4_vb001_visualization_v3a/semantic/classwise/selected_classes_overview_top_oblique.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/semantic_id_structure/selected_classes_overview_top_oblique.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×594 / 960×594 | `8108e2efd4b230e007b71db7e9cba8acec063ac84a8909332b257747cbe256a1` | `f05d293c8b00e4facf68b66513b255054ded683a711c68ae4ee824ec643f9e7e` | Same selected fixed-ID class(es) and common palette; Gaussian-center diagnostic. | READY_FOR_SIDE_BY_SIDE |
| V3A | estimated_trajectory_3d | Estimated trajectory in geometry | `results/runtime_artifacts/phase4_vb001_visualization_v3a/trajectory/estimated_trajectory_3d.png` | `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/trajectory_in_geometry/estimated_trajectory_3d.png` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` | 960×594 / 960×594 | `11bc50b9601e54aee2d4f9b59256a29f4aedf4bfd0f0e589d1bd1400935b2ded` | `7ee7b691575b8240ad6cc1e5230b47df99058013cf743db3dee27ea5a88d20f5` | Each system’s independently estimated trajectory over geometry; same V3A top_oblique camera. | READY_WITH_EXPLICIT_CAVEAT |
