# SESSION_020 — P6-BAM-006 Final Research Checkpoint and Publication

- Started: 2026-10-17.
- Status: `IN_PROGRESS`.
- Objective: audit completed P6-BAM-006 evidence, publish reviewed source and
  reports to the existing research branch, back up all three validated
  visualization packages to the private Hugging Face dataset, and close safely
  without launching SLAM or evaluation.
- Starting branch/HEAD: `phase5-profiling-instrumentation` /
  `0df67b3b19a17233d894af389d10c05796d9ed1b`.
- Experiment source revision: `002927f3b24dd69418c17da08bd4ae987bae9ee2`.

## Scope and constraints

No SLAM, tracking, mapping, evaluator, or new GPU workload is authorized in
this session. Phase 4 and all prior Phase 6 outputs remain immutable. The
SESSION_019 experiment record remains historical and unchanged.

## Evidence audited

- Full-scene reports: `docs/research/phase6_bam/P6_BAM_006_FULL_SCENE_REPORT.md`,
  `P6_BAM_006_FULL_SCENE_COMPARISON.md`, and
  `P6_BAM_006_3D_VISUALIZATION_INVENTORY.md`.
- Original Phase 6 visualization:
  `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2/`
  (9 PNGs).
- Phase 4 V1 matched visualization:
  `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/`
  (9 PNGs).
- Phase 4 V2/V3A extended matched visualization:
  `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_extended_matched/`
  (105 PNGs; 50 are explicitly retained Phase 4 reference images).
- Phase 6 NPZ/PLY hashes and protected Phase 4 checkpoint hash matched the
  recorded values. All 123 package PNGs opened, had nonzero dimensions, and
  were nonuniform under a CPU-only check.

## Research result and limitations

P6-BAM-006-FULL result remains
`PASS_P6_BAM_006_FULL_SCENE_QUALITY_CONSTRAINED`: 2,000 frames/events,
90,195 mapping iterations (24.8375% below 120,000 all-60 equivalent), 401
E4 views, all 2,000 poses, and all seven 15% quality screens passed against
the protected Phase 4 reference. Online wall was 12,383.451 s and process
wall 12,766.40 s. Final model: 5,004,577 Gaussians and 402 keyframes.

`FULL_SCENE_RUNTIME_SPEEDUP_UNVERIFIED` remains in force. The controller chose
LOW/45 for 1,987 of 2,000 events; no advantage over fixed-45 is established.
This is a single-run quality screen, not statistical non-inferiority.
`seg_params.ply` is a learned semantic-color map; fixed semantic-ID structure
is a separate diagnostic and does not represent per-pixel prediction.

## Publication and closure

GitHub and Hugging Face results will be recorded here only after independent
remote verification. Exact remote commit, uploaded path/counts/hashes, final
closure status, and the next research task will be appended before closure.
