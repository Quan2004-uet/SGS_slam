# SESSION_021 — Phase 4 vs Phase 6 Qualitative Comparison and Thesis Preparation

- Started: 2026-10-17.
- Status: `CLOSED` (2026-10-18; P6-BAM-007 Gate 5C final closure complete).
- Objective: prepare, validate, and hand off scientifically fair Phase 4 vs
  Phase 6 qualitative comparison and thesis visualization artifacts.
- Branch / starting HEAD: `phase5-profiling-instrumentation` /
  `17fe98a82a1c7c38b05b7fdefe154bb7b0002453`.
- Previous session: SESSION_020 closed 2026-10-17; its closure, artifacts,
  scientific gates, and publication records are preserved.

## Authorization

Authorized at initialization: documentation and Git inspection; saved-artifact,
camera, manifest, inventory, existence and SHA256 checks; creation of this
record and the planning report; updates to canonical state files. No SLAM,
tracking, mapping, evaluation, model modification, rerender, new experiment,
fixed-budget ablation, source artifact modification, HF upload, or GitHub push
is authorized. Gates 2 and 3 were subsequently explicitly authorized and
passed; Gates 4 and 5 remain pending separate researcher approval.

## Current scientific state

- Phase 4 closure: `PASS_PHASE4_CLOSURE`; validated reference
  `PHASE4-VB-001 — CPU Keyframe Offload`.
- Protected Phase 4 checkpoint:
  `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`
  SHA256 `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`.
- P6-BAM-006 V-A2 full-scene gate:
  `PASS_P6_BAM_006_FULL_SCENE_QUALITY_CONSTRAINED`. The 2,000-frame result,
  90,195 mapping iterations, 5,004,577 final Gaussians, 402 keyframes, and
  401-view final-map evaluation are recorded in the P6-BAM-006 reports.
- Full-scene runtime speedup remains
  `FULL_SCENE_RUNTIME_SPEEDUP_UNVERIFIED`; 1,987/2,000 events used LOW/45,
  adaptive superiority over fixed-45 is unproven, and the quality screen is a
  single run rather than statistical non-inferiority.
- `seg_params.ply` is learned semantic-color output. Fixed semantic IDs are
  separate per-Gaussian metadata/diagnostics, not a per-pixel predictor.

## Verified artifact roots and integrity

- Phase 4 checkpoint and visualization roots:
  `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/`,
  `results/runtime_artifacts/phase4_vb001_visualization/` (9 PNGs),
  `results/runtime_artifacts/phase4_vb001_visualization_v2/` (75 PNGs), and
  `results/runtime_artifacts/phase4_vb001_visualization_v3a/` (26 PNGs).
- Phase 6 run root:
  `results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/`.
  The existing `params.npz`, `params.ply`, and `seg_params.ply` match the
  expected SHA256 values in the final handoff. `params1999.npz` is present.
- Phase 6 visualization roots under
  `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/`:
  `va2/` (9 PNGs; original cameras), `va2_phase4_matched/` (9 PNGs; Phase 4
  V1 cameras), and `va2_phase4_extended_matched/` (105 PNGs; V2/V3A cameras).
- Extended package inventory: 65 fidelity PNGs (50 copied Phase 4 references),
  26 cross-modal overview PNGs, 13 semantic-ID structure PNGs, and 1 trajectory
  PNG. Its report/validation metadata and camera checksums are available.
- Phase 4 checkpoint SHA256 and all three expected Phase 6 model SHA256 values
  were confirmed locally. The HF backup remains
  `PASS_P6_BAM_006_HF_VISUALIZATION_BACKUP`: private dataset
  `QuanDinh/SGS-SLAM-assets`, prefix `phase6_bam/p6_bam_006/visualization/`,
  commit `6cc42c8db3ce69f58bdb2de797c03b90bf930e73`, 186 files / 123 PNGs,
  independently verified against staged SHA256 values per the saved report.
  No live remote query or transfer was performed.

## Initial comparability audit

The audit is documented in
`docs/research/phase6_bam/P6_BAM_007_QUALITATIVE_COMPARISON_PLAN.md`.
It identifies 43 candidate pairs from existing images:

- 6 V1 map-view pairs (3 RGB and 3 learned semantic-color):
  `READY_WITH_EXPLICIT_CAVEAT`.
- 15 V2 observed-frame pairs (frames 0, 499, 999, 1499, 1999; RGB, depth,
  raw learned semantic-color): `READY_WITH_EXPLICIT_CAVEAT`.
- 12 V3A fixed-ID categorical/class-wise pairs: `READY_FOR_SIDE_BY_SIDE`.
- 10 remaining V3A pairs (RGB, raw learned color, Gaussian-center geometry,
  and trajectory overlay): `READY_WITH_EXPLICIT_CAVEAT`.
- Totals: 12 ready, 31 caveated, 0 noncomparable, 0 missing in the audited
  families. The non-matched original Phase 6 camera family is excluded.

V1 and V3A `top_oblique` are explicitly distinct camera definitions; matching
names are not treated as camera identity. V1/V3A Phase 4 camera hashes and
extended-package copies match the saved validation records. V2 frame metadata
and five embedded Phase 4 reference packages are paired by fixed frame ID;
copied camera metadata is documented as byte-identical in the package report.
Gate 2 reverified these exact pair records and source hashes before composition.

## Work completed and remaining

Gate 0 (read-only project/artifact audit): complete.
Gate 1 (camera/modality matrix and per-image source audit): complete; all 43
pair paths, hashes, dimensions, camera checksums, interpretations, and
readiness classes are recorded in the planning report.
Gate 2: `PASS_P6_BAM_007_GATE2_SIDE_BY_SIDE`. The final accepted output is
`results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate2_side_by_side/run_02/`
with 43 pairs (6 V1, 15 V2, 12 V3A cross-modal, 9 V3A classwise, 1 V3A
trajectory) and 7 preview sheets. All 86 source checksums and 43 camera checks
passed; full-resolution panels matched source pixels exactly. The initial
pair-only attempt in the parent output directory is preserved; the validated
package is isolated in `run_02/`.

Gate 3: `PASS_P6_BAM_007_GATE3_THESIS_PACKAGING`. Eight scientific figures,
five 16:9 slides, and one thesis summary plate (14 PNGs total) are available at
`results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate3_thesis_packaging/run_04/`.
The required full-scene semantic 3D figure contains learned-color and fixed-ID
rows for both V3A `room_overview` and `top_oblique`. Gate 2 source hashes,
camera provenance, source panel pixels, all 14 outputs, and protected Phase 4
/ Phase 6 checkpoint hashes passed automated validation. Five CPU-only tests,
Python compilation, and `git diff --check` passed.

The unsuffixed Gate 3 directory, `run_02/`, and `run_03/` were left intact.
The first two contain partial files from failed utility attempts; `run_03/` is
complete but was superseded after visual inspection prompted more explicit
Figure 08 camera-view labels. `run_04/` is the final validated package. No
SLAM, evaluation, GPU rendering, model loading, or metric recomputation was
performed. Phase 4 and Phase 6 source images/models remain unchanged. No GitHub
push or Hugging Face upload occurred.

Next approval point: researcher approval for Gate 4 validation. Gate 4 and
Gate 5 have not started; SESSION_021 remains active.

Initialization classification: `PASS_SESSION_021_INITIALIZATION`.
Current Gate 2 classification: `PASS_P6_BAM_007_GATE2_SIDE_BY_SIDE`.
Current Gate 3 classification: `PASS_P6_BAM_007_GATE3_THESIS_PACKAGING`.

## Final closure — 2026-10-18

P6-BAM-007 milestones: Gates 0–3 PASS; Gate 4 `PASS_WITH_LIMITATIONS`; Gate 5A `PASS_TECHNICAL_FREEZE`; Gate 5B `PASS_REMOTE_VERIFIED`; Gate 5C `PASS_FINAL_CLOSURE`.

Final artifact roots and evidence:
- Gate 4 corrective Figure 02 and corrected Slides 01/02/05: `results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate4_corrective_packaging/run_08/`.
- Eight scientific figures, five slides and thesis plate: `results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate3_thesis_packaging/run_04/`.
- Figure 8B supplementary splatting validation and reports/coverage summaries: `results/runtime_artifacts/phase6_bam/semantic_gaussian_render_validation/`.
- Frozen publication contract, accepted manifests, final backup and Gate 5C closure evidence are retained under `results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/`.

Publication revisions: GitHub commit `f3f0e508c8feccd302c7ec5acede4f8935654829` on `phase5-profiling-instrumentation`; private Hugging Face dataset revision `f5a53f74901dbe09329471009be92356c32fa901` at `phase6_bam/p6_bam_007/` (59 artifacts). No HF re-upload occurred during Gate 5C.

Laptop backup acceptance was based on researcher-provided terminal output, not direct Codex laptop access: `/home/quan/research/SGS_slam_backups/P6-BAM-007/final_package/`; 86 physical files, 84 inventory entries, 47,535,429 payload bytes, 85/85 SHA256 checks PASS. Acceptance record: `results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate5c_final_closure/run_01/LAPTOP_BACKUP_ACCEPTANCE.json`.

Scientific limitations remain: single-run quality evidence does not establish statistical non-inferiority; no matched full-scene runtime speedup is established; iteration reduction is not runtime reduction; V-A2 selected LOW/45 in 1,987/2,000 events and superiority over fixed-45 is unproven; Figure 01 uses Phase 4 estimated poses; Figure 08 Fixed-ID views show sampled Gaussian centers while Figure 8B uses Gaussian splats; `top_oblique` is virtual; alpha coverage is not 3D completeness; Mode C fixed-ID palette splats are not per-pixel semantic predictions.

SESSION_021 closure does not close the Phase 5 workstream. P5-LEAN and its current active status are preserved independently.
