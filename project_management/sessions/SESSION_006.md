# SESSION_006 — Phase 7 Replica room1 Fast-Track Validation

**Status:** CLOSED; **Started:** 2026-10-27; **Last active:** 2026-10-28; **Closed:** 2026-10-28 (Asia/Tokyo)
**Run ID:** p7_bcgm_r1_full_room1_on_0_1999_r01
**Phase:** Phase 7 BCGM multi-scene validation. SESSION_005 remains ACTIVE for its separate room0 workstream.

## Gate outcomes

- R1-Gate 0: PASS from direct-host preflight saved in run summary.
- R1-Gate 1: COMPLETE, Replica room1 frames 0–1999; no short-run arms.
- R1-Gate 2: PASS_WITH_LIMITATIONS after evidence and CPU-only metric closure.
- Advanced visualization A–H: not part of this fast-track and not generated.

## Verified evidence

Exit 0; 2,000 frames/poses; 1,999 insertion events. Checkpoint SHA256 27a388536ced6a5cf5dc59395a980e1f74a99c2a438c4290773d4e54eafadf32, CRC PASS, 4,498,964 Gaussian records. PLYs match the checkpoint count. Six arrays contain 401 finite values at IDs 0,4,9,...,1999.

ATE all poses, Horn rigid SE(3) on W2C translation columns, no scale: Mean 0.005537752230 m; true RMSE 0.005674386822 m; Median 0.005576422439 m; Max 0.013747675507 m.

BCGM totals: 33,408,344 valid, 3,892,851 admitted, 29,515,493 rejected; event cap activations 294, global cap activations 1251, maximum 9,000/event; all 1,999 events pass invariants. Pruning after insertion explains why saved map count is 27 below final immediate post-insertion count.

Runtime 14564.629470 s, E2E 0.137318976 FPS, tracking 0.339028113, mapping 0.248121108; CUDA allocated/reserved 5,628,716,544/7,761,559,552 B; NVML 14,330 valid, peak 10,355 MiB.

Original runtime manifest: 1,629/1,629 paths, sizes and SHA256 match; immutable. Offline ATE JSON/MD checksums are in PHASE7_R1_OFFLINE_ATE_INTEGRITY_MANIFEST.json. Full reports are under docs/research/phase7/room1/.

## Limitations and next step

Phase 4 is the closest same-scene reference but offline evaluation is separately timed. Phase 6 includes BAM/adaptive mapping. Room0 is another scene. Single run/seed; metrics cover 401 views. rmse.txt is not true Depth RMSE; console ATE “RMSE” is mean residual. CUDA allocator and device-wide sampled NVML are different scopes.

Researcher review of comparisons remains optional future work; it is not an open execution task. SESSION_005 is a separate room0 session and was not changed.


## Controlled closure — 2026-10-28 (Asia/Tokyo)

Ownership verified: this session covers Phase 7 Replica room1 fast-track validation. R1-Gate 0 PASS, R1-Gate 1 COMPLETE and R1-Gate 2 PASS_WITH_LIMITATIONS are supported by the saved run summary, checkpoint, metric arrays, offline ATE, admission trace and verified manifests. Room1 quantitative research is complete with limitations.

- Run: `p7_bcgm_r1_full_room1_on_0_1999_r01`; evidence: `results/runtime_artifacts/phase7_gate3_room1/p7_bcgm_r1_full_room1_on_0_1999_r01/`; model: `experiments/Replica/p7_bcgm_r1_full_room1_on_0_1999_r01/`.
- Checkpoint SHA256: `27a388536ced6a5cf5dc59395a980e1f74a99c2a438c4290773d4e54eafadf32`; ZIP CRC PASS; 4,498,964 Gaussians; both PLY exports align.
- Metrics: PSNR 33.326330803279 dB; MS-SSIM 0.968103481053; LPIPS 0.107388632154; Depth L1 0.005512088386 m; semantic mIoU 0.919729327463.
- Offline ATE (2,000 poses): Mean 0.005537752230202329 m; true RMSE 0.005674386822121515 m; Median 0.005576422438909692 m; Max 0.013747675506648417 m. Horn rigid SE(3), W2C translation columns, no scale.
- Runtime 14,564.629470039974 s; E2E/Tracking/Mapping FPS 0.13731897568105528 / 0.33902811298959407 / 0.24812110816831184. CUDA allocated/reserved 5,628,716,544 / 7,761,559,552 B; NVML peak 10,355 MiB (14,330 valid samples).
- BCGM: 33,408,344 valid, 3,892,851 admitted, 29,515,493 rejected; Event Cap activations 294; Global Cap activations 1,251; invariants PASS.
- Original runtime manifest 1,629/1,629 and supplemental ATE manifest 3/3 verified.
- Room1 advanced visualization A–H remains `DEFERRED_BY_RESEARCH_DECISION`. Limits: 401 sampled metric views; `rmse.txt` is not true Depth RMSE; console ATE label is mean; single run/seed; Phase 4 runtime scope differs; Phase 6 includes BAM; room0 is a separate scene.
- No source/config/evidence mutation, rerun, CUDA workload, Git publication or Hugging Face upload was performed. Local logical closure only: `LOCAL_SESSION_CLOSED_PUBLICATION_PENDING`.

Final handoff: `docs/research/phase7/PHASE7_FINAL_PROJECT_STATE_AND_HANDOFF.md`; R1 reports: `docs/research/phase7/room1/`. Future work requires a separate researcher decision.
