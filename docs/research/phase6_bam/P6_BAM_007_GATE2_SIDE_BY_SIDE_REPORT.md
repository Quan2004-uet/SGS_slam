# P6-BAM-007 — Gate 2 CPU-Only Side-by-Side Comparison

Status: `PASS_P6_BAM_007_GATE2_SIDE_BY_SIDE`  
Date: 2026-10-17  
Session: `SESSION_021`  
Branch / HEAD: `phase5-profiling-instrumentation` /
`17fe98a82a1c7c38b05b7fdefe154bb7b0002453`

## Authorization and scope

Gate 2 was explicitly authorized for composition of existing Phase 4 and Phase
6 visualization PNGs. The work used Pillow-only CPU image composition. It did
not load NPZ/PLY models, invoke CUDA, render scenes, run SLAM/tracking/mapping/
optimization, or recompute evaluation metrics. No algorithm/configuration,
checkpoint, or source visualization was modified. No GitHub push, Hugging Face
upload, or commit was performed.

The authoritative source list was Appendix A of
`docs/research/phase6_bam/P6_BAM_007_QUALITATIVE_COMPARISON_PLAN.md`. Its 43
records were parsed as written; the utility fails on any changed headers,
count, family/readiness distribution, path, hash, dimensions, or camera
provenance.

## Repository and source provenance

- Previous published HEAD and current HEAD: both
  `17fe98a82a1c7c38b05b7fdefe154bb7b0002453`.
- Branch: `phase5-profiling-instrumentation`.
- Phase 4 source: immutable `PHASE4-VB-001 — CPU Keyframe Offload` artifacts,
  including V1, V2 fixed-frame, and V3A full-scene visualization families.
- Phase 6 source: P6-BAM-006 V-A2 saved visualization artifacts; no models were
  loaded during this task.
- Gate 1 verified all 43 pair paths, image SHA256s and dimensions. Gate 2
  rechecked all 86 source image hashes and camera provenance before composing.
- V1/V3A authoritative camera JSONs and Phase 6 camera copies were byte-equal
  and matched the recorded SHA256s. All five V2 `frame_metadata.json` files
  and their copied camera metadata were byte-equal and matched the expected
  camera SHA256s. V1 and V3A `top_oblique` remain distinct camera definitions.

## Output location and inventory

Final accepted package:

`results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate2_side_by_side/run_02/`

The requested unsuffixed `gate2_side_by_side/` path was absent at task start.
During the first run, all 43 full-resolution pairs were composed, but contact
sheet generation stopped on this server's older Pillow API before manifests or
previews were produced. Those files were left untouched. The final complete
package is isolated at `run_02/`; the pair files in the first attempt were not
overwritten.

| Family | Paired PNGs |
|---|---:|
| V1 | 6 |
| V2 | 15 |
| V3A cross-modal | 12 |
| V3A classwise | 9 |
| V3A trajectory | 1 |
| **Total** | **43** |

Readiness distribution is 12 `READY_FOR_SIDE_BY_SIDE` and 31
`READY_WITH_EXPLICIT_CAVEAT`. No pair was missing, blocked, or substituted.
Seven reduced contact-sheet previews are present under `previews/`. Full
resolution pairs preserve both native source panels pixel-for-pixel; headings,
system labels, separators, and caveat text occupy newly composed bands outside
the original panels.

Key package files:

- `pairs/` — 43 full-resolution comparison PNGs.
- `previews/` — seven labeled reduced previews; source pair IDs appear in the
  pair manifest.
- `metadata/pair_manifest.json` — pair IDs, both source paths and hashes,
  camera provenance, dimensions, classifications, visible caveats, output
  paths/hashes, and composition geometry.
- `metadata/validation_report.json` — independent validation summary and gate
  status.
- `metadata/SHA256SUMS.txt` — 54 generated file hashes, excluding itself.
- `metadata/README.md` — composition method, modality interpretation,
  attribution, limitations, and review order.
- `logs/composition.log` — CPU-only run summary.

## Validation results

- Appendix A parsed as exactly 43 rows with the expected 6/15/12/9/1 family
  distribution and 12/31 readiness distribution.
- Both source PNGs exist and are RGB/readable for all pairs. All 86 source
  SHA256s match the Gate 1 values. All Phase 4/Phase 6 source dimensions match
  the audit record and each other within a pair.
- All 43 camera definitions/copies match their expected SHA256s and byte
  provenance. Camera mismatch count: 0.
- Generated paired images: 43/43 readable, nonuniform, and at expected output
  dimensions. Source panel pixels match decoded originals exactly in all
  86/86 panel regions. Full-resolution pair resampling: none. Source images
  changed: 0.
- Seven previews generated and readable. Preview content is reduced and
  labeled as preview; source pair IDs are listed in the manifest.
- Independent verification checked all 54 entries in `SHA256SUMS.txt` against
  the files on disk. Pair outputs, previews, manifests, README, and log are all
  covered.
- Protected model hashes were checked before and after composition and remain
  unchanged:
  - Phase 4 `params.npz`:
    `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`
  - Phase 6 `params.npz`:
    `1193f5d5a854225d6e9fc68154d459b5eb026e056a91b5f00639b8da0facd0a5`
  - Phase 6 `params.ply`:
    `dc10441cd383ad7861d27fb70a4f9a76fe9dd88a91e2bacc197b18bbe24cb50a`
  - Phase 6 `seg_params.ply`:
    `98676b4c3e6447681f99426153dfb112bee76882ac9f5d3a18cf11f4832fec21`
- Python syntax compilation, three CPU-only utility tests, independent manifest
  and pixel validation, and `git diff --check` passed.

## Scientific interpretation and limits

- RGB panels are labeled unfiltered RGB Gaussian reconstruction.
- V2 depth panels use the shared fixed 0–6 m visualization range. This is a
  visual comparison; no depth metric was recomputed.
- Raw learned semantic-color panels are not categorical IDs and are not
  GT-palette-assisted recoloring. The learned color values are independently
  optimized and need not match between runs.
- Fixed semantic-ID views use the verified Replica palette and show fixed
  per-Gaussian metadata. They are not categorical per-pixel predictions.
- Geometry panels show sampled Gaussian centers, not continuous surfaces or a
  mesh.
- Trajectory panels show each system's independently estimated camera
  trajectory over reconstructed geometry. They do not establish identical
  poses or provide a direct quantitative ATE comparison.
- A matched camera viewpoint does not imply identical estimated trajectories.
  V1 `top_oblique` and V3A `top_oblique` have distinct camera hashes.
- Existing artifact limitations remain: full-scene runtime speedup is
  unverified; the quality result is a single-run screening result, not
  statistical non-inferiority; and no adaptive superiority over fixed-45 is
  established.

## Changed files and session state

Implementation and tests:

- `scripts/visualization/compose_phase4_phase6_comparisons.py`
- `tests/test_phase4_phase6_compositor.py`
- This Gate 2 report.

The SESSION_021 initialization documents and canonical state files were updated
to record Gate 2 completion and Gate 3 as pending. SESSION_020 remains closed.
Historical untracked Phase 5 reports, older session files, and `vds` remain
untouched. No GitHub or Hugging Face publication occurred.

## Gate result and next approval point

Gate 2 classification: `PASS_P6_BAM_007_GATE2_SIDE_BY_SIDE`.

Gate 3 (thesis/slide packaging) is pending researcher approval. Gate 4 validation
and Gate 5 review/backup/publication have not started. This report does not
claim researcher review or acceptance of the figures.
