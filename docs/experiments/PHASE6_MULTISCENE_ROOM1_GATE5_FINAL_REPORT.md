# Phase 6 V-A2 Replica/room1 — Gate 5 Final Closure

**Closure:** `ROOM1_GATE5_CLOSED_QUALIFIED`  
**Run:** `p6_bam_ms_room1_gate3_0_1999_r01`  
**Scope:** saved run and saved-state evaluation verification only; no SLAM, GPU/CUDA, rendering, or evaluation workload was run for this closure.

## Provenance and method

- Dataset/scene: Replica `room1`, frames 0–1999 inclusive (2,000 frames).
- Frozen scientific source: `/home/robot/research/worktrees/sgs_slam_p6_room1_gate1_002927`, commit `002927f3b24dd69418c17da08bd4ae987bae9ee2`.
- Method: Phase 6 P6-BAM-006 V-A2, CPU Keyframe Offload plus Adaptive Mapping; seed 0; tracking 40 iterations; mapping configured at 60 iterations/frame, adaptive LOW/MID/FULL budgets 45/60/60, thresholds 0.01/0.05; LIGHT telemetry.
- Gate 4 model: `results/runtime_artifacts/phase6_bam/p6_bam_ms_room1_gate3_0_1999_r01/`.
- Gate 4 evidence: `results/runtime_artifacts/phase6_bam/multiscene_evidence/p6_bam_ms_room1_gate3_0_1999_r01/`.
- Telemetry: `results/runtime_artifacts/phase6_bam/telemetry/p6_bam_ms_room1_gate3_0_1999_r01/`.
- Gate 5 saved-state evaluation: `results/runtime_artifacts/phase6_bam/evaluation/p6_bam_ms_room1_gate3_0_1999_r01_offline/`.
- Runtime provenance records RTX 5080, driver 580.167.08, and `/home/robot/miniconda3/envs/sgs_slam_5080/bin/python`.

The run manifest records source commit, run identity, frame range, runner and preparation manifest hashes, the runtime effective-config SHA256 `6a1fc4e3c6de72760fc8bd22f1f4d15c9bd412635fbfe0f8870b95b3e81555b6`, and GPU identity. Frozen source hashes independently verify 17/17. The runtime effective config is not byte-identical to the 3,959-byte pre-run lock: the 4,064-byte runtime serialization adds the three frozen `scripts/slam.py` defaults `tracking.use_depth_loss_thres=false`, `tracking.depth_loss_thres=100000`, and `tracking.visualize_tracking_loss=false`. The first two values leave the threshold inactive; visualization is off. No approved V-A2 scientific setting differs. This is a **QUALIFIED** serialization/provenance discrepancy; the runtime file and both hash identities are preserved and must not be conflated.

## Gate 4 execution and model integrity

| Check | Result | Evidence |
|---|---|---|
| SLAM exit | PASS, code 0 | `postrun_status.txt`, `run_manifest.json`, `process_time.txt` |
| Artifact inventory/checksum generation | PASS, both code 0 | `postrun_status.txt` |
| Overall runner status | PASS | `OVERALL_STATUS=PASS` |
| Frame horizon | PASS, 2,000 / 2,000 | run manifest, log and fresh CPU validator |
| Final Gaussian state | PASS, 6,682,135 | `params.npz`, `params1999.npz`, validator |
| Keyframes | PASS, 402 | terminal sidecar and validator |
| Estimated / GT poses | PASS, 2,000 / 2,000 | final NPZ and validator |
| PLY outputs | PASS, each 6,682,135 vertices and 17 float properties | `params.ply`, `seg_params.ply`, fresh validator |
| CPU artifact integrity | PASS | Historical validator recorded `PASS_CPU_INTEGRITY`, exit 0; independently rerun CPU-only during this closure, also `PASS_CPU_INTEGRITY` |

Essential readable artifacts include `params.npz`, `params0.npz`, `params1999.npz`, both PLY files, and frame-0/frame-1999 keyframe index sidecars. The CPU validator was invoked against the exact model directory; no CUDA context or workload was used. No experiment artifacts were written or changed by the verification.

Integrity checks: Gate 4 `SHA256SUMS.txt` 7/7 PASS; Gate 4 `artifact_manifest.json` 1,623/1,623 entries PASS; frozen source manifest 17/17 PASS; Gate 5 checksum manifest 1,614/1,614 PASS. These checks were freshly computed read-only in this closure.

## Gate 5 saved-state results

The saved evaluator records 401 views at `[0, 4, 9, 14, ..., 1999]` and trajectory evaluation over all 2,000 poses. It contains 401 RGB, 401 depth and 401 semantic render images. All expected per-view arrays contain exactly 401 finite values. The aggregate is an unweighted mean of released per-view values.

| Metric | Saved value | Status / interpretation |
|---|---:|---|
| PSNR | 34.096186264494705 dB | PASS |
| MS-SSIM | 0.9714362002964924 | PASS |
| LPIPS-Alex | 0.09135246086410453 | PASS |
| Depth L1 | 0.004393707946328413 m | PASS; valid-depth pixel mean absolute error |
| Saved “Depth RMSE” | 0.004393707946328413 m | QUALIFIED; implementation is mathematically MAE, see below |
| Semantic-color mIoU | 0.9265354206849918 | QUALIFIED; color-palette metric, not class-logit mIoU |
| Released ATE Mean | 0.004655330867990601 m | PASS under released implementation |
| Supplementary true ATE RMSE | 0.004802019103114381 m | PASS; square root of mean squared pose errors |

### Metric implementation audit and qualifications

**Depth:** `utils/eval_helpers.py` computes `sqrt(error²)` per pixel for the quantity saved as RMSE, then averages it over valid-depth pixels. That is `mean(abs(error))`, the same calculation used by the L1 path. The `rmse.txt` and `l1.txt` arrays are exactly equal, as are their aggregate values. Preserve the historical result and label, but use the Depth L1 value for publication; do not describe the saved “RMSE” as conventional root-mean-square depth error.

**Semantic:** the evaluator recolors the rendered 3-channel learned semantic-color image to the nearest current-frame ground-truth RGB palette color, then averages per-color IoUs after excluding black/unlabeled GT pixels (`utils/eval_helpers.py`, `recolor_semantic_img`, `evaluate_miou`). This is GT-palette-assisted semantic-color mIoU. It is not class-ID confusion-matrix mIoU, and should be named and qualified accordingly.

**Trajectory:** the evaluator uses the saved relative `w2c` pose sequence, Horn rigid rotation/translation alignment without scale, and all 2,000 frames. “Released ATE Mean” is mean per-pose translation error; the supplementary RMSE is computed from squared errors. These are separate reported aggregations, not interchangeable.

RGB/depth quality values describe the sampled saved-state views, not all 2,000 rendered views. Saved metrics alone do not establish qualitative fidelity. No image was opened, altered, cropped, or rerendered as part of this closure.

## Runtime and throughput

Primary end-to-end runtime is `process_time.txt`: **16,075.75 s = 04:27:55.75**, or **0.1244109917 frames/s** and **8.037875 s/frame** across all 2,000 frames. The LIGHT telemetry wall is 16,072.76350169594 s (about 2.99 s lower). The online frame-loop span in `run.log` is 15,695.987124723 s; it excludes portions of process startup/finalization and must not be substituted for process wall time.

| Timing span | Total | Per-frame / note |
|---|---:|---|
| Tracking component | 7,772,968.533 ms | 3,886.484 ms/frame; includes nested work |
| Mapping component | 7,645,701.096 ms | 3,822.851 ms/frame; includes nested work |
| Preprocessing | 58,266.408 ms | 29.133 ms/frame |
| Keyframe selection | 55,444.540 ms | 27.722 ms/frame |
| Built-in evaluation during Gate 4 | 363.501 s | In-process; not Gate 5 |
| Serialization span | 13.055 s | In-process measured span |
| Offline Gate 5 wall time | NOT_MEASURED | No independent Gate 5 process-time record was found |

Tracking, mapping, preprocessing and selection spans are separately measured and partly nested; do not add them to estimate exclusive process wall time. Gate 5 is a separate saved-state process and its runtime is unavailable in the saved evidence.

## Memory and CPU offload

| Measurement | Recorded value | GiB / qualification |
|---|---:|---|
| PyTorch allocated high-water | 10,223,109,632 bytes | 9.521 GiB |
| PyTorch reserved high-water | 12,513,705,984 bytes | 11.654 GiB |
| Device-wide NVML VRAM peak | NOT_MEASURED | No supported device-wide peak instrumentation in this run |
| Peak process RSS (`process_time.txt`) | 19,119,360 KiB | 18.234 GiB; primary process peak |
| CPU keyframe archive logical payload | 10,497,024,000 bytes | 9.776 GiB logical payload, not independently measured RSS |
| CPU→GPU H2D staging | 2,258,139,648,000 bytes / 86,479 events | 2,103.056 GiB cumulative transfer volume, not resident memory; 43.24 events/frame (5.38 events/s over process wall), 26,112,000 bytes/event on average |

LIGHT telemetry samples memory periodically (400 allocator samples, every fifth frame in this run). PyTorch peak allocated/reserved values are allocator high-water counters; the run instrumentation does not reset those counters, so they are process high-water observations and not device-wide physical VRAM. RSS sampled telemetry is lower because it is periodic; `/usr/bin/time` peak RSS is reported above. CUDA event timing remains `PENDING_P5_G3_CUDA_VALIDATION`; this run does not validate CUDA event timing. No claim of device-wide VRAM peak is made.

## Adaptive mapping and keyframes

The controller was enabled for all 2,000 mapping events. The configured all-60 equivalent is 120,000 iterations; 90,840 iterations were executed (45.42 average/frame, 75.7% of that configured total).

| Selected tier | Budget | Frames |
|---|---:|---:|
| FULL | 60 | 1 |
| MID | 60 | 55 |
| LOW | 45 | 1,944 |

One initial frame had invalid/unavailable novelty signal (`signal_valid=0`) and selected the initial-frame fallback; the remaining 1,999 signals were valid and had no fallback. Final state contains 6,682,135 Gaussians and 402 keyframes. No isolated mapping-controller overhead was measured. There is no matched room1 full-scene V0 comparison here, so no speedup, energy reduction, or causal VRAM reduction is claimed.

## Artifact and visualization inventory

- Final model: NPZ final state, initial and terminal checkpoints, RGB Gaussian PLY and semantic-color PLY, effective config, and frame-0/frame-1999 keyframe sidecars.
- Gate 4 evidence: status, run and artifact manifests, source/preparation checksums, process timing and run log.
- Telemetry: summary, JSONL stream and run metadata.
- Gate 5: aggregate and trajectory metrics, exact frame schedule, six per-view metric arrays, 401 RGB renders, 401 depth renders, 401 semantic renders, 401 existing metric plots, and SHA256 manifest.
- A standalone camera-trajectory visualization was not found in these run directories. Numeric pose sequences and ATE evidence are present.
- The Gate 4 built-in RGB/depth/semantic image files match the corresponding Gate 5 images byte-for-byte (401 per modality); the archive plan includes the canonical Gate 5 copies once.

Representative existing Gate 5 IDs for a future thesis review: **0, 499, 999, 1499, 1999** (early, quarter, middle, three-quarter, terminal). This is a temporal coverage choice, not a claim that these are visually challenging; no visual inspection was performed. Future figures should compare camera-matched frames and clearly distinguish RGB, depth, raw learned semantic colors, and GT-palette-assisted recoloring. PLY visualizations should identify the color representation and viewing camera. Metric values do not by themselves prove visual quality.

## Gate decision and remaining qualifications

- **Gate 4: PASS** — exit, inventory, checksums, frame horizon and saved final map verified; fresh CPU integrity validation passed.
- **Gate 5: PASS** — saved-state evaluation has the required 401 views, 2,000-pose trajectory, finite metric arrays, outputs and 1,614/1,614 checksum verification.
- **Overall: `ROOM1_GATE5_CLOSED_QUALIFIED`** — closure is supported, with qualifications for the runtime-config serialization defaults, historical depth-RMSE label, GT-palette-assisted semantic-color mIoU, absent device-wide NVML VRAM measurement, unvalidated CUDA event timing, and unrecorded separate Gate 5 process wall time.
- Publication should report Depth L1 (not conventional RMSE), name semantic-color mIoU explicitly, use process wall for end-to-end throughput, and label allocator memory separately from physical VRAM.
- Archive status: local inventory and plan only. No remote Hugging Face inspection or upload was performed. No Git publication or room2 work was performed.

Supporting archive records: [archive plan](PHASE6_MULTISCENE_ROOM1_EVIDENCE_ARCHIVE_PLAN.md) and [per-file dry-run inventory](PHASE6_MULTISCENE_ROOM1_EVIDENCE_ARCHIVE_MANIFEST.json).
