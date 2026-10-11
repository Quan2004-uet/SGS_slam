# PHASE4-VB-001 Hugging Face Artifact Backup Dry Run

## 1. Scope and status

- Status: `PASS_HF_BACKUP_DRY_RUN`.
- Date: 2026-10-12.
- Local repository: `/home/robot/research/SGS_slam`.
- Git branch/HEAD: `phase4-vb-001-cpu-keyframe-offload` / `15bcbebb4c641a72026473c93250a2b5c973c805`.
- Target: `QuanDinh/SGS-SLAM-assets`.
- Repo type: dataset.
- Authentication: valid as `QuanDinh` (`hf auth whoami`).
- This document and its machine manifest are dry-run evidence only. No upload,
  remote write, HF commit, deletion, or overwrite was performed.

## 2. Installed CLI and read-only inspection

Installed `hf` CLI version: 2.2.0. Its supported repo-file listing command is
`hf datasets list <REPO_ID>`; `--tree` gives a human tree and `--format json`
gives metadata. Repo metadata was read with `hf datasets info`.

Remote metadata:

- exists: yes;
- visibility: private;
- default revision inspected: `main`;
- current SHA: `b728a9e8bc480f7165a71198a790091c5b2977c7`;
- last modified: `2026-10-03T18:16:52+00:00`;
- main size: 26,987,983,107 bytes;
- used storage: 26,977,124,828 bytes.

Read-only top-level listing:

```text
.gitattributes
data/
migration/
```

`artifacts/`, `dataset/`, and top-level `Replica/` are absent. Existing
`data/` and `migration/` are explicitly preserved. The CLI has create/delete
branch commands but no branch-list subcommand; default `main` metadata and SHA
come from the dataset info/list API responses.

## 3. Proposed remote structure

```text
artifacts/phase4_vb001/room0/
├── final_state/
│   ├── params.npz
│   ├── params.ply
│   ├── seg_params.ply
│   └── keyframe_time_indices.npy
├── evaluation/e4/
│   └── 9 compact result/provenance files
└── qualitative/representative/
    ├── frame_0000/  (13 files)
    ├── frame_0499/  (13 files)
    ├── frame_0999/  (13 files)
    ├── frame_1499/  (13 files)
    ├── frame_1999/  (13 files)
    └── 6 root summary/contact-sheet/manifest files
```

## 4. Final-state upload mapping

| Local path | Bytes | SHA256 | Priority | Remote path | Action |
|---|---:|---|---|---|---|
| `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/keyframe_time_indices.npy` | 3,344 | `fb91f05c127819f6666259668c4d88a2d36a46f575659f576adde37b227e6d37` | HIGH | `artifacts/phase4_vb001/room0/final_state/keyframe_time_indices.npy` | `UPLOAD_NEW` |
| `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz` | 322,361,795 | `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2` | CRITICAL | `artifacts/phase4_vb001/room0/final_state/params.npz` | `UPLOAD_NEW` |
| `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.ply` | 337,040,173 | `d9b4d22ba11c73f8c1d6d0ea5f874bbb5d3254f25b333362a502a5940f604502` | HIGH | `artifacts/phase4_vb001/room0/final_state/params.ply` | `UPLOAD_NEW` |
| `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/seg_params.ply` | 337,040,173 | `6cd5a258a8147fe0c0515d04ea702d618f82c2411fc464ab9bfebd2fc2f3b726` | HIGH | `artifacts/phase4_vb001/room0/final_state/seg_params.ply` | `UPLOAD_NEW` |

## 5. E4 evaluation upload mapping

| Local path | Bytes | SHA256 | Priority | Remote path | Action |
|---|---:|---|---|---|---|
| `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/PHASE4_VB001_EVAL_E4_FULL_SUMMARY.md` | 4,500 | `5fa13f80f00ac62e30775f6cb66bc9ca429a0b858eaa8cfd73acf9b56bf4691b` | HIGH | `artifacts/phase4_vb001/room0/evaluation/e4/PHASE4_VB001_EVAL_E4_FULL_SUMMARY.md` | `UPLOAD_NEW` |
| `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/aggregate_metrics.json` | 4,638 | `cc79293d2c538440bc9779cf8712f40e13fa25cfecbab4c8bd5a49c17a5fa282` | HIGH | `artifacts/phase4_vb001/room0/evaluation/e4/aggregate_metrics.json` | `UPLOAD_NEW` |
| `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/evaluated_frame_ids.json` | 3,884 | `ccb1ff8a2cf60fa5c9818766b3480774d37e4cbb24c83bf22f9c797538d81d13` | HIGH | `artifacts/phase4_vb001/room0/evaluation/e4/evaluated_frame_ids.json` | `UPLOAD_NEW` |
| `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/memory_summary.json` | 1,601 | `1d5652326172480dce7f39e683f178d2bfc6f4ba424e59ff91042c53a1a157fe` | HIGH | `artifacts/phase4_vb001/room0/evaluation/e4/memory_summary.json` | `UPLOAD_NEW` |
| `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/per_frame_metrics.json` | 237,728 | `f7b4d38c2fd3b9222b7ce2b7c91b50cd6c3d4e4b1b950cf89911a6fd484d7d75` | HIGH | `artifacts/phase4_vb001/room0/evaluation/e4/per_frame_metrics.json` | `UPLOAD_NEW` |
| `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/phase4_vb001_eval_e4_full_results.json` | 10,138 | `a1a74fc6488acfc4667acf92bf1de43d6d4ce4a890c43994df1213c90cb64750` | HIGH | `artifacts/phase4_vb001/room0/evaluation/e4/phase4_vb001_eval_e4_full_results.json` | `UPLOAD_NEW` |
| `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/run_metadata.json` | 1,188 | `cae8368e68fe3669a2ac60bb87392a15ca32a9f22ba02ee38a4d03be7a901f4e` | HIGH | `artifacts/phase4_vb001/room0/evaluation/e4/run_metadata.json` | `UPLOAD_NEW` |
| `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/timing_summary.json` | 305 | `501ecc20048393249004bd342a47d2ee44215e62f22af84464c41020126eca9e` | HIGH | `artifacts/phase4_vb001/room0/evaluation/e4/timing_summary.json` | `UPLOAD_NEW` |
| `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/trajectory_metrics.json` | 19,391 | `6a1b36ffdaf718fabaa98851394d26d523882e37d2bc48e86799ad61840a6368` | HIGH | `artifacts/phase4_vb001/room0/evaluation/e4/trajectory_metrics.json` | `UPLOAD_NEW` |

Only canonical compact E4 outputs are selected. No temporary or giant runtime
log is included.

## 6. Qualitative upload mapping

All five frame directories map one-to-one from
`results/qualitative/phase4_vb001_room0_representative/frame_NNNN/` to
`artifacts/phase4_vb001/room0/qualitative/representative/frame_NNNN/`. Each contains exactly
the required 13 RGB/depth/semantic/composite files:

```text
rendered_rgb.png
gt_rgb.png
rgb_side_by_side.png
rendered_depth_raw.npy
gt_depth_raw.npy
rendered_depth.png
gt_depth.png
depth_side_by_side.png
rendered_semantic_raw.png
rendered_semantic_recolored.png
gt_semantic.png
semantic_side_by_side.png
qualitative_grid.png
```

Root qualitative mapping:

| Local path | Bytes | SHA256 | Priority | Remote path | Action |
|---|---:|---|---|---|---|
| `results/qualitative/phase4_vb001_room0_representative/QUALITATIVE_EXPORT_SUMMARY.md` | 1,165 | `4599774e26d6719ae1f9caadefa8fe09f2e1409725d6f5e8f5e540da5b65d4aa` | MEDIUM | `artifacts/phase4_vb001/room0/qualitative/representative/QUALITATIVE_EXPORT_SUMMARY.md` | `UPLOAD_NEW` |
| `results/qualitative/phase4_vb001_room0_representative/artifact_checksums.sha256` | 10,585 | `da5372c5f67759f5a3e2de0bbc12ee31c0a7a3b0fbe4fc3f278b84f7b2e42b64` | MEDIUM | `artifacts/phase4_vb001/room0/qualitative/representative/artifact_checksums.sha256` | `UPLOAD_NEW` |
| `results/qualitative/phase4_vb001_room0_representative/contact_sheet_all_frames.png` | 2,569,461 | `dec2e6bcf067a2f4775a611d70768e6fe14db7ddedec13a4c6846161ce2ac315` | MEDIUM | `artifacts/phase4_vb001/room0/qualitative/representative/contact_sheet_all_frames.png` | `UPLOAD_NEW` |
| `results/qualitative/phase4_vb001_room0_representative/per_frame_metric_annotations.json` | 1,892 | `d6c66a82747882a760a743a18d0d87cbd102953980d6936a42d58920de8fc043` | MEDIUM | `artifacts/phase4_vb001/room0/qualitative/representative/per_frame_metric_annotations.json` | `UPLOAD_NEW` |
| `results/qualitative/phase4_vb001_room0_representative/qualitative_manifest.json` | 15,802 | `cfaa583e99b9ee2057e50f8ef55d55f95f86c508da559521d6fadb25ea746482` | MEDIUM | `artifacts/phase4_vb001/room0/qualitative/representative/qualitative_manifest.json` | `UPLOAD_NEW` |
| `results/qualitative/phase4_vb001_room0_representative/qualitative_metadata.json` | 2,120 | `2c89141b1e5b3ea2558e819330518dca11d44484f24a799f4dcfd5b686bad416` | MEDIUM | `artifacts/phase4_vb001/room0/qualitative/representative/qualitative_metadata.json` | `UPLOAD_NEW` |

The machine-readable manifest records the exact local path, size, SHA256, and
remote path for all 65 frame files plus these 6 root files.

## 7. Remote collision result

The read-only top-level remote tree contains no `artifacts/` directory at
revision `b728a9e8bc480f7165a71198a790091c5b2977c7`. Therefore all 84 proposed paths are absent and are
classified `UPLOAD_NEW`. Counts:

- `UPLOAD_NEW`: 84;
- `SKIP_IDENTICAL`: 0;
- `CONFLICT_REVIEW_REQUIRED`: 0.

No remote content was downloaded. Before Step 2, repeat the top-level/tree
check and stop if `artifacts/phase4_vb001/room0/` appeared after this dry run.
Never overwrite a newly conflicting path automatically.

## 8. Explicit exclusions

- `EXCLUDED_FROM_UPLOAD`: data/ and data/Replica/ — Dataset is outside artifact-backup scope.
- `EXCLUDED_FROM_UPLOAD`: dataset ZIP archives — No dataset archive is part of the proposed paths.
- `EXCLUDED_FROM_UPLOAD`: migration/ packages — Existing remote migration namespace is preserved and untouched.
- `EXCLUDED_FROM_UPLOAD`: unrelated checkpoints and experiments — Only one final state, E4 evidence, and one qualitative package are selected.
- `EXCLUDED_FROM_UPLOAD`: full repository source tree and .git/ — Git/GitHub remains source authority; backup is artifacts only.
- `EXCLUDED_FROM_UPLOAD`: Conda environments — Environment directories are outside all selected roots.
- `EXCLUDED_FROM_UPLOAD`: /tmp harnesses — Temporary execution harnesses are deliberately omitted.
- `EXCLUDED_FROM_UPLOAD`: cache and build directories — No cache/build directory occurs in the proposed manifest.
- `EXCLUDED_FROM_UPLOAD`: CUDA binaries — Renderer/system binaries are not experiment artifacts.
- `EXCLUDED_FROM_UPLOAD`: old failed-run giant logs — Only compact canonical E4 evidence files are selected.

The three selected roots contain no ZIP/TAR/TAR.GZ/TGZ/ZST archive, dataset
directory, `.git`, cache, or build directory. The local `data/` and
`data/Replica/` directories and an existing `/tmp` qualitative harness were
observed but remain outside the manifest. No local migration package or
`data/Replica_data.zip` currently exists; the remote migration/data trees are
untouched.

## 9. Storage summary

| Category | Files | Bytes | Decimal size |
|---|---:|---:|---:|
| Final state | 4 | 996,445,485 | 996.445 MB |
| E4 evaluation | 9 | 283,373 | 0.283 MB |
| Qualitative | 71 | 70,338,585 | 70.339 MB |
| **Total** | **84** | **1,067,067,443** | **1.067067 GB / 0.993784 GiB** |

## 10. Ten largest proposed files

1. `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.ply` — 337,040,173 bytes (337.040 MB)
2. `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/seg_params.ply` — 337,040,173 bytes (337.040 MB)
3. `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz` — 322,361,795 bytes (322.362 MB)
4. `results/qualitative/phase4_vb001_room0_representative/frame_0000/gt_depth_raw.npy` — 3,264,128 bytes (3.264 MB)
5. `results/qualitative/phase4_vb001_room0_representative/frame_0000/rendered_depth_raw.npy` — 3,264,128 bytes (3.264 MB)
6. `results/qualitative/phase4_vb001_room0_representative/frame_0499/gt_depth_raw.npy` — 3,264,128 bytes (3.264 MB)
7. `results/qualitative/phase4_vb001_room0_representative/frame_0499/rendered_depth_raw.npy` — 3,264,128 bytes (3.264 MB)
8. `results/qualitative/phase4_vb001_room0_representative/frame_0999/gt_depth_raw.npy` — 3,264,128 bytes (3.264 MB)
9. `results/qualitative/phase4_vb001_room0_representative/frame_0999/rendered_depth_raw.npy` — 3,264,128 bytes (3.264 MB)
10. `results/qualitative/phase4_vb001_room0_representative/frame_1499/gt_depth_raw.npy` — 3,264,128 bytes (3.264 MB)

Equal-size raw-depth NPY files are ordered lexicographically; only the first
seven of the ten equal 3,264,128-byte files fit after the three final-state
artifacts in this top-ten list.

## 11. Proposed Step 2 strategy (not executed)

1. Re-run authentication, repo metadata, and collision checks; require all 84
   destinations to remain absent.
2. Re-hash local files and compare to `proposed_upload_manifest.json`; stop on
   any local size/hash drift.
3. Upload only the three exact local roots to their exact category roots using
   the installed `hf upload ... --repo-type dataset` command. Do not upload the
   repository root and do not use delete options.
4. Prefer three clearly named HF commits (final state, E4 evidence,
   qualitative package) so a failure is attributable and resumable.
5. After upload, list the new remote subtree and verify every remote path,
   size, and available LFS/OID metadata. Download/hash only when remote metadata
   cannot establish identity.
6. Preserve existing `data/` and `migration/` unchanged.

Proposed category commands are intentionally not run in Step 1:

```text
hf upload QuanDinh/SGS-SLAM-assets <final-state-local-dir> artifacts/phase4_vb001/room0/final_state --repo-type dataset
hf upload QuanDinh/SGS-SLAM-assets <e4-local-dir> artifacts/phase4_vb001/room0/evaluation/e4 --repo-type dataset
hf upload QuanDinh/SGS-SLAM-assets <qualitative-local-dir> artifacts/phase4_vb001/room0/qualitative/representative --repo-type dataset
```

## 12. Risks and approval gate

- Remote state can change after this inventory; Step 2 must re-check collisions.
- The three final-state files total nearly 1 GB and may use Git LFS/Xet;
  interruption handling and post-upload verification are required.
- Folder upload must remain rooted at the three selected directories. Running
  it from repository root could accidentally include dataset or source files.
- `hf upload` may split folder uploads into multiple commits. Step 2 reporting
  must record every resulting remote commit.
- Existing remote `data/` and `migration/` are large and must never be used as
  upload destinations for this artifact package.

**STOPPED HERE — DRY-RUN INVENTORY AND REMOTE INSPECTION COMPLETE. EXPLICIT
USER APPROVAL IS REQUIRED BEFORE ANY STEP 2 UPLOAD.**

NO FILES UPLOADED. NO REMOTE FILES MODIFIED. NO HF COMMIT CREATED.
