# R1-Gate 2 — Final Quantitative Evaluation & Evidence Closure

**Status: PASS_WITH_LIMITATIONS.** Read-only/CPU-only closure of the completed Replica room1 run p7_bcgm_r1_full_room1_on_0_1999_r01; no SLAM, CUDA mapping, rendering or visualization was run here.

## Verified execution and artifacts

- Run summary: COMPLETE, exit 0, frames 0–1999 (2,000), 2,000 estimated/GT poses, 1,999 insertion events.
- Checkpoint: ZIP CRC PASS; SHA256 27a388536ced6a5cf5dc59395a980e1f74a99c2a438c4290773d4e54eafadf32; numeric values finite; Gaussian fields aligned; 4,498,964 Gaussians.
- params.ply and seg_params.ply: 4,498,964 vertices each; hashes recorded in run report and final evidence manifest.
- Metrics: six arrays, 401 finite values each, IDs 0,4,9,...,1999.
- Admission: 1,999/1,999 invariant checks pass. Valid 33,408,344; admitted 3,892,851; rejected 29,515,493; Event Cap activations 294; Global Cap activations 1251.
- NVML CSV: 14,330 valid and zero invalid; peak 10,355 MiB at 2026-10-27T13:14:42+00:00.
- Original run artifact manifest: 1,629/1,629 files present and hash/size matched. Immutable original manifest not rewritten. Offline ATE post-run files are captured in a supplemental integrity manifest.

## Metrics and comparisons

See PHASE7_R1_FULL_SCENE_METRIC_TABLE.md, PHASE7_R1_BCGM_ADMISSION_VALIDATION.md and PHASE7_R1_ROOM0_ROOM1_COMPARISON.md. ATE is recalculated from 2,000 checkpoint poses using Horn rigid SE(3) on W2C translation columns, no scale: Mean 0.005537752230202 m; true RMSE 0.005674386822122 m; median 0.005576422438910 m; max 0.013747675506648 m. Checkpoint SHA matches the offline report and required expected SHA.

Phase 4 room1 is the strongest same-scene reference, but evaluation/runtime boundaries differ. Phase 6 includes BAM/adaptive mapping and cannot isolate BCGM. Room0 is another scene. Single run/seed means descriptive comparison only. CUDA allocator and NVML sampled device-wide values are different scopes.

## Metric semantics and limitations

Evaluator source utils/eval_helpers.py SHA256 e94366ca256ec2b51b5d0264a5daba2a895cc0375d7b91e976e4ea0e9e28194e is identical across Phase 4/6/R1. ssim.txt is MS-SSIM. rmse.txt is elementwise equal to l1.txt and does not provide conventional Depth RMSE. The console’s “ATE RMSE” label describes mean aligned residual; use offline true ATE RMSE separately. Metrics are over 401 sampled frames, not all 2,000. A 27-Gaussian difference between final post-insertion trace and saved count is consistent with mapping pruning after insertion, as shown by source call order.

Advanced visualization A–H was not generated in this fast-track. No session was closed: SESSION_006 and SESSION_005 remain ACTIVE.
