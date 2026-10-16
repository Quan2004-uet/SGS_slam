# P6-BAM-006 — Phase 4 Extended Camera-Matched Visualization

Status: `PASS_P6_BAM_006_PHASE4_EXTENDED_CAMERA_MATCHED_VISUALIZATION`

This is a saved-model visualization/export result for the already-completed
Phase 6 V-A2 room0 model. No SLAM, tracking, mapping, optimization, training,
or evaluation was run. A bounded set of native renderer views was produced
from saved parameters using exact Phase 4 camera definitions.

## Provenance and inputs

- Phase 6 run: `results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/`
- New output root: `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/`
- Phase 6 `params.npz` SHA256, before and after: `1193f5d5a854225d6e9fc68154d459b5eb026e056a91b5f00639b8da0facd0a5`
- Phase 6 `params.ply` SHA256, before and after: `dc10441cd383ad7861d27fb70a4f9a76fe9dd88a91e2bacc197b18bbe24cb50a`
- Phase 6 `seg_params.ply` SHA256, before and after: `98676b4c3e6447681f99426153dfb112bee76882ac9f5d3a18cf11f4832fec21`
- Output target was absent before this task. Existing Phase 4 outputs and both
  earlier Phase 6 visualization packages were left in place.

The native Phase 4 V3A utility was extended with an optional authoritative
camera-directory input. Its default camera-generation path is unchanged. A
small companion utility renders the five exact Phase 4 V2 frame cameras from
the Phase 6 checkpoint. The renderer consumes the saved checkpoint only.

## Discovered Phase 4 families

| Family | Validated Phase 4 source and status | Camera definitions and protocol | Phase 6 result |
|---|---|---|---|
| Camera-aligned reconstruction fidelity | `results/runtime_artifacts/phase4_vb001_visualization_v2/`, `PASS_V2_CAMERA_ALIGNED_QUALITATIVE` in `GATE_V2_REPORT.md` | Per-frame `estimated_w2c`, intrinsics, and 1200×680 dimensions in each `frames/frame_XXXX/frame_metadata.json`; fixed frame IDs `[0,499,999,1499,1999]` | Rendered Phase 6 RGB, learned semantic colors, and depth at the exact five Phase 4 per-frame estimated-w2c matrices. Original Phase 4 V2 RGB/depth/semantic evidence is copied alongside as reference. No metrics or GT-palette-assisted recoloring were recomputed. |
| Full-scene 3D cross-modal overview | `results/runtime_artifacts/phase4_vb001_visualization_v3a/`, `PASS_V3A_FULL_SCENE_VISUALIZATION_PROOF` in `GATE_V3A_REPORT.md` | V3A `room_overview`, `trajectory_observed`, `top_oblique`; 960×540 map views, white renderer background, OpenCV w2c convention | Re-rendered RGB Gaussian maps and raw learned-semantic colors, plus the validated geometry/categorical/combined diagnostic panels using byte-identical Phase 4 camera JSONs. |
| Fixed semantic-ID class structure | V3A `semantic/categorical/` and `semantic/classwise/`; same V3A PASS report | Same three V3A cameras; fixed IDs from `params.npz`; verified 29-entry palette in `results/runtime_artifacts/phase4_vb001_visualization_audit/semantic_mapping.csv` | Reproduced the categorical center maps, legend, and selected class-wise views. These are fixed per-Gaussian ID diagnostics, not a per-pixel predictor and not `seg_params.ply` learned-color output. |
| Estimated trajectory in reconstructed geometry | V3A `trajectory/estimated_trajectory_3d.png`; same V3A PASS report | Exact Phase 4 V3A `top_oblique.json`; 960×540 underlying view, with report title band | Reproduced from the 2,000 saved Phase 6 estimated poses over the same deterministic Gaussian-center geometry convention and exact top-oblique camera. |

The earlier V1 overview family remains in
`visualization/va2_phase4_matched/`. Its `overview`, `oblique`, and
`top_oblique` camera JSONs are preserved in the new package and match V1
byte-for-byte; this task did not rerender that already-matched family.

### Authoritative camera hashes

Phase 4 V1 cameras:

| Camera | SHA256 |
|---|---|
| `overview.json` | `c5e0029b1758788322538ce27e587c8cdfa5a3277aba331431e50d5ac80865bb` |
| `oblique.json` | `9846a224e93b3615afd45097b9106037c3550b5199b74d4e0550f328ad220120` |
| `top_oblique.json` | `0d865494919fb2066cf769ef654163ee3f1e262d5ebb4cf8b95681d6934ec196` |

Phase 4 V3A cameras:

| Camera | SHA256 |
|---|---|
| `room_overview.json` | `f5598e540e78c8c838f3db0e83194520477e528735b65336c5f66a590b7a8cfc` |
| `top_oblique.json` | `a85a5e8f06370743894a58003034e0ee415eecafbc626ec308cf9d6f0e4a745d` |
| `trajectory_observed.json` | `df75161d510552a31bd5096ac3cc5a07eea5b58cf9c0ac777d15aa507af17f1a` |

The Phase 4 V2 camera source is each frame's `frame_metadata.json` (which
contains the exact estimated w2c and intrinsics); copied metadata hashes are
recorded per frame in `metadata/validation_report.json` and the copied files
are byte-identical to their Phase 4 sources.

## New outputs and validation

The package includes:

- `reconstruction_fidelity/`: five Phase 6 RGB views, five raw learned
  semantic-color views, and five metric-depth views at 1200×680, rendered from
  saved `params.npz` using the exact Phase 4 V2 frame cameras; five Phase 4
  reference frame packages and their original camera metadata are retained
  beside them. Depth uses the Phase 4 depth/silhouette color pass and fixed
  JET display range `[0,6]` m; raw float depth arrays are also retained.
- `cross_modal_overview/`: three native RGB and three learned semantic-color
  views at 960×540; three geometry and three categorical-ID views at
  960×594 after the V3A title strip; three cross-modal panels at 2880×634;
  plus the validated center sample indices and copied exact cameras.
- `semantic_id_structure/`: 13 PNGs (three categorical camera views, the
  29-class legend, and nine selected class-wise/combined views).
- `trajectory_in_geometry/`: one trajectory overlay (960×594) and its exact
  Phase 4 top-oblique camera copy.
- `cameras/`, `metadata/`, and `logs/`: V1/V3A and frame-specific V2 camera
  evidence, JSON inventory/validation/manifest, and renderer logs.

PNG counts are 65 under `reconstruction_fidelity` (15 new Phase 6 renders plus
50 copied Phase 4 reference images), 26 under `cross_modal_overview`, 13 under
`semantic_id_structure`, and one under `trajectory_in_geometry`. Total package
PNG count is 105. CPU validation found every PNG nonempty and nonuniform and
recorded each image's dimensions, byte size, and SHA256 in
`metadata/validation_report.json` and `metadata/visualization_manifest.json`.
All V1/V3A JSON camera copies matched the authoritative Phase 4 hashes; the
five V2 frame camera metadata files matched byte-for-byte. The three Phase 6
model hashes above remained unchanged.

The first restricted-context V3A renderer attempt produced the CPU diagnostic
products but could not access CUDA; those logs and partial outputs were
preserved. The native saved-map RGB/semantic render then completed in the
authorized host GPU context. An initial V2 helper invocation exited on an
import-path issue before loading the model; its log is preserved, and the
corrected invocation completed. No output was overwritten.

## Semantic and interpretation limits

`semantic_id_structure/` represents the fixed `semantic_ids` attached to
Gaussian centers using the verified Replica palette. It is a categorical
visualization of fixed metadata. `seg_params.ply` and the V3A raw semantic
render represent learned semantic colors. Neither should be described as a
categorical per-pixel semantic predictor. The V2 copied reference contains
Phase 4 depth and GT-palette-assisted semantic visualizations. Phase 6 depth
was rendered from the saved map at the same exact cameras with the Phase 4
depth/silhouette renderer and shared display range. Phase 6 GT-palette-assisted
recoloring was not generated here.

## Changed files and checks

- `scripts/visualization/visualize_full_scene_v3a.py`: optional input of
  authoritative V3A cameras and generalized view-name iteration for the
  existing saved-model renderer.
- `scripts/visualization/render_phase4_v2_cameras.py`: exact Phase 4 V2
  per-frame camera rendering from a saved Phase 6 checkpoint.
- `scripts/visualization/package_phase4_extended_visualization.py`: safe,
  non-overwriting family packaging and CPU validation/manifest generation.
- This report.

Validation: Python syntax compilation passed for all three visualization
utilities; package validation passed for 105 PNGs; V1/V3A camera SHA checks
passed; Phase 4 V3A's original 33-file checksum list passed; Phase 6 NPZ/PLY
SHA256s were unchanged; `git diff --check` passed. No SLAM/evaluation run,
algorithm/config edit, historical artifact overwrite, deletion, or upload was
performed.
