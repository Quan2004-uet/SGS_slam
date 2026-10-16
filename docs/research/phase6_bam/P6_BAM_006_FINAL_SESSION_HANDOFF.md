# P6-BAM-006 — Final Session Handoff and Publication Record

Date: 2026-10-17
Research branch: `phase5-profiling-instrumentation`
Experiment source revision: `002927f3b24dd69418c17da08bd4ae987bae9ee2`
Run ID: `p6_bam_006_room0_0_1999_va2_r01`
Full-scene gate: `PASS_P6_BAM_006_FULL_SCENE_QUALITY_CONSTRAINED`

## Research result

One V-A2 Replica room0 run completed frames 0–1999 and 2,000 mapping events.
It executed 90,195 mapping iterations, 24.8375% below the all-60 equivalent
of 120,000. The budget distribution was 1 FULL, 12 MID, and 1,987 LOW. Online
wall was 12,383.451 seconds (0.161506 frames/s); whole-process wall was
12,766.40 seconds (0.156661 frames/s). These are not a matched full-scene
runtime comparison: `FULL_SCENE_RUNTIME_SPEEDUP_UNVERIFIED` remains the
classification. The available matched runtime result is P6-BAM-005's single
0–499 pair (15.33% online-wall reduction).

The completed E4-compatible evaluation covers 401 final-map views and all
2,000 poses. Against stored Phase 4 E4 metrics, all seven researcher-defined
15% quality screens passed. This is a single-run screen, not statistical
non-inferiority. The controller acted predominantly as a 45-iteration policy;
adaptive superiority over a fixed-45 baseline has not been tested. `seg_params.ply`
contains learned semantic colors, not categorical semantic-ID geometry or a
per-pixel semantic predictor.

## Preserved model and evaluation paths

- Run root: `results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/`
- Comparison/evaluation root: `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/`
- Final checkpoint: `.../p6_bam_006_room0_0_1999_va2_r01/params.npz`
  (SHA256 `1193f5d5a854225d6e9fc68154d459b5eb026e056a91b5f00639b8da0facd0a5`)
- RGB Gaussian model: `.../params.ply`
  (SHA256 `dc10441cd383ad7861d27fb70a4f9a76fe9dd88a91e2bacc197b18bbe24cb50a`)
- Learned-semantic-color Gaussian model: `.../seg_params.ply`
  (SHA256 `98676b4c3e6447681f99426153dfb112bee76882ac9f5d3a18cf11f4832fec21`)
- Phase 4 protected reference:
  `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`
  (SHA256 `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`)

## Visualization packages

All three packages are preserved and passed a read-only inventory/PNG
readability check (9 + 9 + 105 PNGs):

- Original Phase 6 cameras:
  `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2/`
- Exact Phase 4 V1 camera match:
  `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/`
- Extended Phase 4 V2/V3A camera-family match:
  `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/`

The 50 Phase 4 images inside the extended package remain reference images,
not new Phase 6 predictions. Phase 4 is the immutable reference tree under
`results/runtime_artifacts/phase4_vb001_visualization/`,
`..._v2/`, and `..._v3a/`.

## Publication status

The reviewed documentation/source commit was published to
`origin/phase5-profiling-instrumentation` at
`https://github.com/Quan2004-uet/SGS_slam.git`. The remote branch ref was read
back and matched `7454f170f3ece83b38f2429a43084ff550cf49a2`.

The visualization-only backup target is the private dataset
`QuanDinh/SGS-SLAM-assets`, at
`phase6_bam/p6_bam_006/visualization/`, upload revision
`6cc42c8db3ce69f58bdb2de797c03b90bf930e73`. The remote contains 186 files
(123 PNGs, 74,675,326 bytes); an independent download matched every file by
SHA256. Staging excludes model NPZ/PLY files,
dataset/raw training data, and six `.npy` visualization intermediates; text
metadata is sanitized in copies only. Exact transfer and hash-verification
details are in `docs/research/phase6_bam/P6_BAM_006_HF_VISUALIZATION_BACKUP_REPORT.md`.

The documentation copy of this handoff in the HF backup is the sanitized
pre-upload snapshot; at staging time, it correctly left both publications
pending. This repository copy is the final post-verification handoff.

## Next research work

After publication, package the Phase 4 versus Phase 6 qualitative comparison
and prepare thesis/report material. Do not launch another SLAM run, evaluation,
variant, scene, or fixed-budget ablation without separate researcher review
and authorization. Preserve the original Phase 5 administrative status,
P6-BAM-003 historical INCONCLUSIVE result, and all previous Gate outcomes.
