# P7-POST-01 — Artifact Preservation Inventory

All paths below are on the research server unless stated otherwise. SHA256 coverage was independently rechecked on 2026-10-28. “Present locally” is not equivalent to an external backup.

## Full-scene experiment roots

| Scene / run | Evidence root | Model root | Combined inventory | Preservation state |
|---|---|---|---:|---|
| Replica room0 / `p7_bcgm_g3_room0_on_0_1999_r01` | `/home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/` | `/home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica/p7_bcgm_g3_room0_on_0_1999_r01/` | 1,793 unique files; 2,616,652,085 logical bytes; 2,620,317,696 allocated bytes | Present on server; Gate 4 manifest 212/212 entries rehashed |
| Replica room1 / `p7_bcgm_r1_full_room1_on_0_1999_r01` | `/home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate3_room1/p7_bcgm_r1_full_room1_on_0_1999_r01/` | `/home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica/p7_bcgm_r1_full_room1_on_0_1999_r01/` | 1,632 unique files; 2,530,849,308 logical bytes; 2,534,219,776 allocated bytes | Present on server; original runtime manifest 1,629/1,629 and supplemental ATE manifest 3/3 rehashed |

Counts and byte totals are per combined evidence/model roots; they include many small outputs and do not duplicate files across the two roots. Gate1B and Gate2 evidence remain in their run-specific roots. The room0 Gate 4 manifest is the cross-gate evidence index; its summed manifest size includes some referenced historical Phase 4/6 files.

## Critical scientific artifacts

| Artifact | Room0 SHA256 / size | Room1 SHA256 / size |
|---|---|---|
| Final `params.npz` | `a02dd4b4ecfd9c982866cf4a4c38c187ef22c75049b8328e18eea20608944917` / 292,664,335 B | `27a388536ced6a5cf5dc59395a980e1f74a99c2a438c4290773d4e54eafadf32` / 292,624,100 B |
| `params.ply` | `409d1c3637e3f951f950d14bf066a88df66de8dc41a01762c312a0871ab300fc` / 305,972,061 B | `d4613f5dd81fca9ad676fcbdd6484dafde2f9d17eb902d596031674f9416c082` / 305,929,969 B |
| `seg_params.ply` | `98a41a36e69e113c7e7da8dcfcd8c279c08c25da8af7525e26dcbdb7df262b89` / 305,972,061 B | `9381a9be2b816601f2010b2f1248e2c907d1861a5a3ae4153aba147eface3a8c` / 305,929,969 B |
| `run_summary.json` | `cad87cf405cd9aab6cb6d226e0a49aeeab455f8b6d92858c7e9263ba95923e41` / 6,474 B | `e3d4511e44d43694f2ac9ea0bab722f3713db179000fa89f564d0d46369a920c` / 12,413 B |
| `nvml_samples.csv` | `3303dfed8f1a2e38213d74890cd950b41dfa8989f9a250174226d2059a9c1c86` / 515,588 B | `df2250a71502b1cf2559819debdf6086a543413293b8c196447a9f8b5e57ba95` / 529,996 B |
| `insertion_counts.jsonl` | `b1e6daa103407713585f84d4900b6b5f6c1864ec2d6e771fb2c7976dfff23f96` / 190,366 B | `214e1fa0639f3bcf973009bc0e77881c9283ee583f658ba95b02e7f5e44e0567` / 190,339 B |

Room0 additionally has offline ATE JSON/Markdown and the advanced visualization package. Room1 offline ATE JSON/Markdown are protected by its supplemental manifest. Each run directory includes six evaluator-native arrays; per-array hashes are in the original manifests. Evaluation arrays cover 401 views. Checkpoint ZIP CRC passed for both runs, and PLY vertex counts align with their checkpoints.

## Gate coverage and backup assertions

- Room0: Gate 4 manifest contains 212 entries and all paths, sizes and hashes pass. Summary verifies COMPLETE, exit 0, 2,000 frames/poses, 1,999 insertion records, 401 finite values per metric, and BCGM admission validation.
- Room1: original manifest contains 1,629 entries, all paths/sizes/hashes pass; supplemental ATE manifest 3/3 passes. Summary verifies COMPLETE, exit 0, 2,000 frames/poses, 1,999 insertion events, and Global Cap runtime flags.
- Backups: room0 laptop transfer is `USER_REPORTED_COMPLETE`; no matching laptop-side hashes were available, so integrity is not independently verified. No full room1 external backup was verified. Phase 7-A scientific roots are therefore still treated as server-held evidence.
- Current free server space was about 23.9 GB (98% used). No copy or archive was made.

Detailed file-level inventories are the Gate 4 manifest `docs/research/phase7/PHASE7_GATE4_EVIDENCE_MANIFEST.json`, room1 manifest `results/runtime_artifacts/phase7_gate3_room1/p7_bcgm_r1_full_room1_on_0_1999_r01/artifact_manifest.json`, and `docs/research/phase7/room1/PHASE7_R1_OFFLINE_ATE_INTEGRITY_MANIFEST.json`. These manifests are retained as provenance and remain local; a Git manifest entry does not back up the large referenced files.

## Selective Git file inventory

The exact 73-file approved archive inventory, including tracked/untracked status, byte size, purpose, decision, SHA256 and path-level risk note, is recorded in `P7_POST01_APPROVED_STAGING_MANIFEST.json`. Total proposed source/documentation staging payload: 716,018 bytes. The five explicit excluded roots/files are recorded there.
