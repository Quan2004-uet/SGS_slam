# Phase 7 Replica room1 — Final Evidence Handoff

Run p7_bcgm_r1_full_room1_on_0_1999_r01; R1 Gate 0 PASS, Gate 1 COMPLETE, Gate 2 PASS_WITH_LIMITATIONS. SESSION_006 CLOSED on 2026-10-28 (Asia/Tokyo); SESSION_005 is unchanged and ACTIVE.

- Summary: results/runtime_artifacts/phase7_gate3_room1/p7_bcgm_r1_full_room1_on_0_1999_r01/run_summary.json; exit 0, 2,000 frames and poses.
- Checkpoint: experiments/Replica/p7_bcgm_r1_full_room1_on_0_1999_r01/params.npz; SHA256 27a388536ced6a5cf5dc59395a980e1f74a99c2a438c4290773d4e54eafadf32; ZIP CRC PASS; 4,498,964 Gaussians. Both PLY files agree.
- Metrics: experiments/Replica/p7_bcgm_r1_full_room1_on_0_1999_r01/eval; six 401-value finite arrays. Metric table: PHASE7_R1_FULL_SCENE_METRIC_TABLE.md.
- Offline ATE: mean 0.005537752230 m; true RMSE 0.005674386822 m; all 2,000 poses; no scale fit.
- BCGM: 33,408,344 valid, 3,892,851 admitted, 29,515,493 rejected; Event Cap 294; Global Cap 1251; no invariant violations.
- NVML: 14,330 valid, peak 10,355 MiB. CUDA allocator and NVML scopes differ.
- Original artifact manifest: 1,629 entries verified and unchanged. Offline ATE hashes: PHASE7_R1_OFFLINE_ATE_INTEGRITY_MANIFEST.json.
- Closure: PHASE7_R1_GATE2_FINAL_EVIDENCE_CLOSURE.md. Comparison: PHASE7_R1_ROOM0_ROOM1_COMPARISON.md.

Limitations: one run/seed; 401-view metric subset; no conventional Depth RMSE; console ATE label represents mean; Phase 4 runtime scope differs; Phase 6 contains BAM; room0 is a different scene; no advanced visualization A–H.

Next: researcher review and decide separately whether to close SESSION_006. No rerun or upload is required for this closure.


## Administrative session closure — 2026-10-28 (Asia/Tokyo)

`SESSION_006` ownership was verified against the room1 fast-track record and its R1-Gate 0/1/2 evidence; it is now `CLOSED`. No experiment, source/config change, artifact mutation, Git commit/push, or upload occurred. The consolidated Phase 7 state is in `docs/research/phase7/PHASE7_FINAL_PROJECT_STATE_AND_HANDOFF.md`.
