# SESSION_004 — Phase 4 Variant B Full-Scene Validation, Evaluation, and Qualitative Export

## Metadata

- Session ID: SESSION_004.
- Status: CLOSED.
- Started: 2026-10-10.
- Last active/closed: 2026-10-12.
- Branch: `phase4-vb-001-cpu-keyframe-offload`.
- Variant: `PHASE4-VB-001` — CPU offload of resident keyframe payloads.

Objective: validate full-scene Variant-B memory behavior, preserve a reloadable
final state, audit the released evaluator, and complete staged saved-state
evaluation and representative camera-view export without changing the
algorithm or rerunning online SLAM.

## Work Completed

1. Reconciled the historical full-scene validator false failure as
   `PASS_RUNTIME_VALIDATOR_BUG`; the released terminal `num_frames-2` keyframe
   makes expected and observed keyframe counts both 402.
2. Passed minimal and telemetry output-save smokes over frames 0–49.
3. Completed and saved frames 0–1999 with
   `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.
4. Audited saved-state loading, rendering, RGB/depth/semantic metrics,
   trajectory alignment, sampling, and exports.
5. E1 load-only: `PASS_EVAL_E1_LOAD_ONLY`.
6. E2 single-frame RGB/depth/semantic render:
   `PASS_EVAL_E2_SINGLE_FRAME_RENDER`.
7. E3 five-frame bounded metrics: `PASS_EVAL_E3_BOUNDED_SUBSET`.
8. E4 complete released evaluation: `PASS_EVAL_E4_FULL_RELEASED`.
9. Representative frames `[0,499,999,1499,1999]` camera-view export:
   `PASS_QUALITATIVE_EXPORT`.

No source algorithm/config change, online SLAM rerun, post-SLAM optimization,
or E4 full rendered-image export occurred. The later qualitative gate exported
only five selected views and did not recompute metrics.

## Full-Scene Output-Save Result

- Frames: 0–1999, 2,000 completed.
- Runtime: 14,173.47515856901 s.
- Gaussians: 4,956,467.
- Keyframes: 402; tail `[1989,1994,1998,1999]`.
- Tracking/mapping/overall FPS: 0.3354664059815056 /
  0.25086898791330586 / 0.14110865384985266.
- Peak GPU allocated/reserved: 5,817,509,888 / 7,189,037,056 B.
- Process HWM: 17,960,493,056 B host RAM.

Saved state:
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`

## Released Evaluation Protocol

- Image/depth/semantic sampling: 401 frames,
  `{0} union {5k-1 | k=1..400}`.
- RGB: GT divided by 255; render and GT masked by GT depth > 0; released
  `calc_psnr`; MS-SSIM; LPIPS AlexNet with `[0,1]` clamping.
- Depth: Replica scale 6553.5; masked MAE in meters.
- Semantic: rendered `semantic_colors`; nearest current-frame GT palette;
  black GT ignored; no direct `semantic_ids` comparison.
- Trajectory: all 2,000 finite relative-w2c poses, normalized real-first
  quaternions, Horn rigid alignment without scale.

## Final E4 Metrics

| Metric | Value | Classification |
|---|---:|---|
| PSNR | 33.313067 dB | Released-code metric |
| MS-SSIM | 0.979470 | Released “SSIM” implementation |
| LPIPS-Alex | 0.067555 | Released-code metric |
| Depth L1 | 0.00495158 m / 0.495158 cm | Released masked MAE |
| Semantic-color mIoU | 0.916585 | Released color-palette protocol |
| Horn-aligned mean w2c translation error | 0.00274075 m | Released ATE-like mean; not true RMSE |
| Supplementary true RMSE | 0.00339827 m | Supplementary metric from same aligned errors |

- Evaluation wall time: 74.4107 s.
- Renderer/metric/trajectory times: 10.0479 / 50.8178 / 0.0101 s.
- Peak evaluation GPU allocated/reserved: 1,846,789,120 /
  2,057,306,112 B.
- Image export: none.
- Skipped sampled frames, OOM, or non-finite metrics: none.

## Camera-View Qualitative Export

- Status: `PASS_QUALITATIVE_EXPORT`.
- Frames: `[0,499,999,1499,1999]`.
- Output:
  `results/qualitative/phase4_vb001_room0_representative/`.
- Each frame contains rendered and GT RGB, raw and visualized metric depth,
  raw/recolored rendered semantic color, GT semantic color, side-by-side
  comparisons, and a six-panel qualitative grid.
- Root outputs include `contact_sheet_all_frames.png`, metric annotations,
  metadata, a 69-artifact manifest, and SHA256 checksums.
- Runtime: 9.213427657989087 s.
- Peak GPU allocated/reserved: 1,774,468,608 / 1,935,671,296 B.
- Renderer invoked: yes. New metrics computed and SLAM rerun: no.
- Existing E4 annotations were preserved for all five frames.

The export is camera-view qualitative evidence, not a paper-style free-view or
map-view `Scene Reconstruction | 3D Segmentation` figure.

## Evidence and Provenance

- Evaluation run HEAD: `63adf3aed8ae2201a46d11cec473672f9e91fd0e`.
- E4 harness SHA256:
  `8c31b131e1b294fb0a089589c4f934e1c9912a4969573169f2abe333c847d5e6`.
- Saved-state SHA256:
  `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`.
- E1--E4 evidence lives under `results/runtime_artifacts/phase4_vb001_eval_*`.
- Canonical result: `docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md`.
- Qualitative result:
  `docs/experiments/PHASE4_VB001_QUALITATIVE_EXPORT_RESULT.md`.

## Scientific Conclusion and Limits

For Replica `room0` on the tested RTX 5080, PHASE4-VB-001 resolves the measured
GPU-resident keyframe scalability failure, completes online processing, saves
a reloadable state, and completes the audited released-code evaluation from
that state. These are one-scene released-code results. They do not establish
full paper reproduction, accuracy superiority, benchmark-wide contribution,
or generalization to other scenes.

## Next Task and Closure

SESSION_004 closes at `PASS_QUALITATIVE_EXPORT`. Quantitative evaluation and
camera-view qualitative export are complete. The immediate next task is a
read-only **Scene Reconstruction / 3D Segmentation Visualization Audit** for
the saved `params.ply` and `seg_params.ply`; it must stop before rendering.

The Paper / Baseline Comparison Audit remains subsequent work and must still
verify protocol comparability, prepare a baseline-versus-PHASE4-VB-001 table,
and identify justified claims and missing scenes/experiments. PHASE4-VB002
remains future work.

Future sessions must not resume from output saving, E1--E4, or the completed
camera-view export, and must not rerun online SLAM merely to repeat saved-state
evaluation or visualization inputs.
