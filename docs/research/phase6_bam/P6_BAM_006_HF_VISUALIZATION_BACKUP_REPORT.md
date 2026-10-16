# P6-BAM-006 — Hugging Face Visualization Backup

Date: 2026-10-17
Status: `PASS_P6_BAM_006_HF_VISUALIZATION_BACKUP`

## Destination and identity

- Repository: [QuanDinh/SGS-SLAM-assets](https://huggingface.co/datasets/QuanDinh/SGS-SLAM-assets), private dataset.
- Authenticated account: `QuanDinh` (verified with `hf auth whoami`; no token was displayed).
- Destination: `phase6_bam/p6_bam_006/visualization/`.
- Upload commit: `6cc42c8db3ce69f58bdb2de797c03b90bf930e73`.
- Independently observed repository HEAD after upload: the same commit.
- The destination prefix was empty before upload; the repository already contained unrelated `data/`, `migration/`, and Phase 4 artifact paths, all left intact.

## Included files

The deterministic local staging tree is
`results/runtime_artifacts/phase6_bam/p6_bam_006_publication_staging_r02/phase6_bam/p6_bam_006/visualization/`.
The upload command used the explicit source directory and exact target prefix:

```text
hf upload QuanDinh/SGS-SLAM-assets <staging>/phase6_bam/p6_bam_006/visualization phase6_bam/p6_bam_006/visualization --repo-type dataset
```

The remote contains 186 files totaling 74,675,326 bytes, including 123 PNGs:

| Package | PNGs | Notes |
|---|---:|---|
| `va2/` | 9 | Original Phase 6 camera set |
| `va2_phase4_matched/` | 9 | Exact Phase 4 V1 camera match |
| `va2_phase4_extended_matched/` | 105 | Includes 50 explicitly labeled Phase 4 reference images |
| `documentation/` | — | Full-scene, comparison, inventory, two camera-match reports, and final handoff snapshot |

The remote also includes camera JSONs, useful validation/provenance metadata,
renderer logs, `backup_manifest.json`, `source_to_staging_inventory.json`, and
`SHA256SUMS.txt`. Twenty-three text copies were sanitized to redact local home
and temporary paths; original evidence was not modified. The source-to-staging
inventory records original and staged hashes. Six `.npy` visualization
intermediates were deliberately excluded; these are listed in the manifest.
The extended package's 50 Phase 4 reference images are retained and clearly
labeled under `reconstruction_fidelity/phase4_reference/`.

Excluded: Replica datasets/raw training images, NPZ checkpoints, RGB/semantic
PLY model files, unrelated Phase 4/Phase 5 trees, unrelated run logs, caches,
environments, credentials, and Git internals.

## Transfer and remote verification

- CLI: `hf` 2.2.0; `hf upload` reported 186 files checked and returned the upload commit URL. Its progress line showed `0/123 uploaded` despite the successful committed revision; exact transferred wire bytes are therefore not claimed.
- Remote listing at the upload revision independently confirmed all 186 intended paths, including all 123 PNGs, and no additional files under the new `phase6_bam/` namespace.
- The complete target subtree was downloaded to a separate temporary verification directory from the immutable upload revision. All 186 remote files matched the staged files byte-for-byte by SHA256; 74,675,326 bytes matched, with zero missing, extra, or mismatched files.
- `SHA256SUMS.txt` covers all 183 payload files and excludes itself plus the two control manifests to avoid self-reference; all listed local hashes passed before upload. The independent remote comparison covers all 186 files, including the control manifests.
- Before/after repository file counts were 96,196 and 96,382 respectively; the increase is exactly the 186-file destination subtree. No delete operation was issued and unrelated pre-existing paths remain.

The verification download is temporary transport evidence outside the Git
worktree. Remote privacy remains `private`.
