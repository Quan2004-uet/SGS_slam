# SESSION_019 — P6-BAM-006 Authorized Full-Scene V-A2

- Started: 2026-10-16.
- Completed: 2026-10-16.
- Status: `CLOSED`.
- Objective: execute exactly one authorized V-A2 Replica room0 run over frames 0–1999, preserve the final model before evaluation, complete the existing E4-compatible evaluation and saved-model 3D visualization, and report the result.
- Source revision: `002927f3b24dd69418c17da08bd4ae987bae9ee2`.
- Branch: `phase5-profiling-instrumentation`.
- Phase 4 tag peeled to `37522db553ff18b96592073f9de699db7fa48600`.

## Result

`PASS_P6_BAM_006_FULL_SCENE_QUALITY_CONSTRAINED`. Exactly one run completed 2,000 frames and 2,000 mapping events with process exit 0. Checkpoint-first saving preserved and CPU-validated the recovery/final NPZ, RGB PLY, learned semantic-color PLY, trajectories and keyframe metadata before evaluation. The existing E4 evaluator completed 401 final-map views; ATE used all 2,000 poses. All seven researcher-defined 15% checks passed against stored Phase 4 E4 values. The existing offline 3D renderer passed for RGB and learned semantic-color maps.

V-A2 executed 90,195 mapping iterations, 24.8375% below the 120,000 all-60 equivalent; tiers were 1 FULL, 12 MID, 1,987 LOW. Online wall was 12,383.451 s and whole-process wall 12,766.40 s. Final model contained 5,004,577 Gaussians and 402 keyframes. CPU archive was 10,497,024,000 logical bytes; H2D staging was 85,969 events / 2,244,822,528,000 cumulative bytes.

Full-scene runtime speedup remains `FULL_SCENE_RUNTIME_SPEEDUP_UNVERIFIED`: no matched full-scene V0 exists and historical Phase 4 process timing is not comparable to the new online-loop timer. This is one-run execution/quality screening, not statistical non-inferiority.

## Integrity and scope

- Phase 4 params NPZ/PLY/semantic PLY/keyframe hashes match their recorded references; P6-BAM-005 V0/V-A2 checkpoint hashes also match.
- All 1,659 files in the new P6-BAM-006 SHA256 inventory passed validation.
- No algorithm/config source modification, additional SLAM run, recovery evaluator run, or extra experiment was performed.
- Reports: `docs/research/phase6_bam/P6_BAM_006_FULL_SCENE_REPORT.md`, `P6_BAM_006_FULL_SCENE_COMPARISON.md`, and `P6_BAM_006_3D_VISUALIZATION_INVENTORY.md`.
- Runtime evidence: `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/`, the unique run root, and its unique telemetry root.

## Next decision

Researcher review of the completed reports. No additional SLAM, evaluation, scene, or variant run is authorized automatically. No push performed.
