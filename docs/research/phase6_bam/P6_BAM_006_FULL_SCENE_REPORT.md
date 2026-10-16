# P6-BAM-006 — Full-Scene V-A2 Execution Report

Date: 2026-10-16\
Run: `p6_bam_006_room0_0_1999_va2_r01`\
Source revision: `002927f3b24dd69418c17da08bd4ae987bae9ee2`\
Gate: `PASS_P6_BAM_006_FULL_SCENE_QUALITY_CONSTRAINED`

## Outcome

The single authorized V-A2 run completed Replica room0 frames 0–1999, saved and CPU-validated its recovery/final model before evaluation, completed the in-process Phase 4 E4-compatible 401-view evaluation, and produced the approved RGB and learned-semantic-color 3D visualization package. No second SLAM or evaluation attempt was made. The result passes the specified 15% full-scene quality screen against the stored Phase 4 reference. It does **not** establish matched full-scene runtime improvement: historical Phase 4 process timing is not comparable to the new online-loop timer, and no matched 2000-frame V0 was authorized.

## Provenance and frozen setup

- Branch: `phase5-profiling-instrumentation`; source revision above; Phase 4 tag peels to `37522db553ff18b96592073f9de699db7fa48600`.
- Wrapper: `configs/replica/phase6_bam_va2_full_0_1999.py`; Replica room0, start 0/end 2000 exclusive, stride 1, 2000 frames, 680×1200, seed 0, tracking 40, mapping maximum 60, map interval 1, keyframe interval 5/window 24, CPU Keyframe Offload enabled, LIGHT profiler, semantic input enabled, eval interval 5, checkpoint interval 1999, checkpoint-first finalization enabled, WandB disabled.
- Controller: adaptive LOW/MID/FULL 45/60/60, novelty thresholds 0.01/0.05.
- Exact command is recorded at `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/launch_command.txt`; effective config and prelaunch provenance are in `effective_config.json` and `prelaunch_manifest.json`.
- Source/config was not modified for this run. Prelaunch hashes matched the approved readiness manifest.

## Execution and runtime

The process returned 0 and completed exactly 2,000 frames and 2,000 mapping events, with no CUDA OOM, fatal exception, or non-finite final state reported. Frame 1999 completed with a LOW/45 decision. Whole-process time was 12,766.40 s; `/usr/bin/time` peak RSS was 17,627,216 KiB. The online frame-loop timer measured 12,383.451 s, yielding 0.161506 online frames/s. Whole-process throughput was 0.156661 frames/s. The online timer excludes initialization, final evaluation and serialization; process time includes startup, online work, evaluation and saving.

LIGHT mapping host-span sum was 6,072.273 s and tracking host-span sum 6,070.039 s. These spans overlap and are not additive to each other or substitutes for online wall. Evaluation took 369.807 s. Torch allocator high-water was 7,443,113,472 allocated / 8,227,127,296 reserved bytes; periodic LIGHT sampled peaks were 2,162,656,256 / 8,204,058,624 bytes. Allocator values are not device-wide VRAM measurements. Sampled process RSS/HWM peaked at 13,077,786,624 / 13,137,969,152 bytes; the external process RSS measurement is reported separately above.

## Mapping and offload

All 2,000 events retained configured maximum 60 and executed the selected effective budget. Tier counts: FULL 1, MID 12, LOW 1,987, FIXED 0. Frame 0 used the expected invalid-initial-signal FULL fallback; the other 1,999 events had valid current-event novelty signals and no fallback. Novelty fraction range was 0.0000324–0.0169179, median 0.00035354, mean 0.00102610. Total execution was 90,195 iterations versus a 120,000-iteration all-60 reference, a 24.8375% iteration reduction. Every event preserved the required 21-iteration pruning floor.

The final model has 5,004,577 Gaussians and 402 keyframes ending at frame 1999. CPU keyframe archive: 10,497,024,000 logical bytes. H2D staging: 85,969 events / 2,244,822,528,000 cumulative bytes. LIGHT sampled Gaussian peak was 4,999,848; final exact count is from the saved checkpoint. Detailed tier, frame-segment and novelty records are in `mapping_budget_distribution.json` and `.csv`; memory/offload values are in `memory_archive_h2d.json`.

## Checkpoints and evaluation

Checkpoint-first order was observed: `params1999.npz` and terminal keyframe metadata were saved; final metadata and `params.npz`, `params.ply`, and `seg_params.ply` were produced and CPU-validated before final evaluation. The in-process evaluator completed (401 views); saved-state recovery was not needed. The final NPZ passed ZIP/array/schema/finite checks, has 2,000 estimated and GT poses, aligned semantic ID/color arrays, 5,004,577 Gaussian entries, and 402 keyframes. It is 325,488,945 bytes, SHA256 `1193f5d5a854225d6e9fc68154d459b5eb026e056a91b5f00639b8da0facd0a5`. Recovery NPZ SHA256: `b4d457008b85094d0d0e234fa7146554df5f14684717eb7efe45e121a1e1a218`.

Final-map views were exactly `[0,4,9,...,1994,1999]`; all 401 finite per-view values and corresponding RGB/depth/semantic renders are preserved under the run's `eval/` directory. ATE uses all 2,000 poses, relative-w2c convention and Horn rigid alignment without scale. Metrics:

| Metric | V-A2 | Phase 4 E4 reference | Relative degradation | 15% screen |
|---|---:|---:|---:|---|
| ATE Mean (m) | 0.002843988 | 0.002740749 | +3.7668% | PASS |
| True ATE RMSE (m) | 0.003436795 | 0.003398271 | +1.1336% | PASS |
| PSNR (dB) | 32.944552 | 33.313067 | −0.368515 dB | PASS |
| PSNR-implied MSE change | +8.8558% | — | — | PASS |
| MS-SSIM | 0.978003691 | 0.979470255 | −0.1497% | PASS |
| LPIPS-Alex | 0.070752040 | 0.067555264 | +4.7321% | PASS |
| Depth L1 (m) | 0.004943029 | 0.004951577 | −0.1726% | PASS |
| Semantic-color mIoU | 0.913530865 | 0.916585480 | −0.3333% | PASS |

PSNR-implied MSE change is `10 ** ((PSNR_Phase4 - PSNR_VA2)/10) - 1`, not a directly aggregated pixel-MSE ratio. The stored evaluator's `rmse.txt` is numerically identical to depth L1 because its implementation averages `sqrt(error**2)`; it is not a conventional aggregate RMSE. The P5-LEAN provisional quality margins also pass. Single-run comparison is screening evidence, not statistical non-inferiority.

## 3D visualization and integrity

The approved offline renderer completed three deterministic 1600×900 views for RGB Gaussian reconstruction and learned semantic-color Gaussian reconstruction, with paired images and camera/view metadata. It ran from saved PLY/NPZ only; no tracking, mapping or evaluation was performed by the visualization job. `seg_params.ply` represents learned semantic colors, not categorical semantic IDs; IDs remain in NPZ. Visualization status is `PASS_V1_FINAL_RECONSTRUCTION_VISUALIZATION` and `PASS_V2_FINAL_SEMANTIC_VISUALIZATION`.

Phase 4 `params.npz`, `params.ply`, `seg_params.ply`, and keyframe-index hashes were rechecked and match the recorded reference. P6-BAM-005 V0/V-A2 checkpoint hashes also remain unchanged. The new run, telemetry, evaluation and visualization are isolated under `results/runtime_artifacts/phase6_bam/`. The comparison directory contains `artifact_manifest.json` and `SHA256SUMS.txt`; all 1,659 listed artifacts passed `sha256sum -c` after generation.

## Interpretation and boundary

The execution and quality checks pass for one V-A2 full-scene run. The 24.84% reduction is in mapping iterations, not an established runtime speedup. Phase 4's historical 14,173.475 s process measurement is context only and is **NOT_COMPARABLE** to this run's online-loop measurement; no causal or matched full-scene speedup is claimed. P6-BAM-005 remains the controlled bounded 0–499 V0/V-A2 evidence (15.33% online-wall reduction). No further SLAM run is authorized by this report.

## Evidence index

- Run root: `results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/`
- Telemetry: `results/runtime_artifacts/phase6_bam/telemetry/p6_bam_006_room0_0_1999_va2_r01/`
- Comparison, timing, metrics, manifest and full log: `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/`
- 3D package: `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2/`
- Gate: `PASS_P6_BAM_006_FULL_SCENE_QUALITY_CONSTRAINED`; runtime claim qualification: `FULL_SCENE_RUNTIME_SPEEDUP_UNVERIFIED`.
