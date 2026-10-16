# P6-BAM-005 — Matched 0–499 V0/V-A2 Run Report

**Gate: `PASS_P6_BAM_005_0_499_QUALITY_CONSTRAINED`** — bounded 500-frame screening only.

## Frozen protocol and provenance

One sequential V0 run and one V-A2 run completed on Replica `room0`, indices 0–499 (`start=0,end=500,stride=1,num_frames=500`), 680×1200, seed 0, tracking 40, mapping maximum 60, `map_every=1`, keyframe interval 5, window 24, existing CPU keyframe offload, append/prune/loss/optimizer rules unchanged, and identical LIGHT sampling. Only `mapping.budget_control` differed. V0 disabled it; V-A2 used LOW/MID/FULL=45/60/60 and unchanged fraction thresholds 0.01/0.05. Both used `eval_every=50`, checkpointing at frame 499, and the same saved-output policy.

- Branch: `phase5-profiling-instrumentation`; source commit `937cd4bb7df25824e5b43de555d5de78ce11f16c`.
- The only tracked source worktree difference during both runs was a measurement-only `time.perf_counter()` around the online frame loop in `scripts/slam.py`, SHA256 `0604b00f12f288a49e28bf1386c6d7b8089b1642acfe095358693b0b557c52ce`. It adds no CUDA synchronization and no algorithm/config behavior change.
- Validated environment: Python 3.10.22, PyTorch 2.7.1+cu128, CUDA runtime 12.8, NVIDIA GeForce RTX 5080; LIGHT profiler.
- Effective config snapshots and hashes, resolved run IDs, source/harness hashes, frozen evaluation IDs and historical reference hashes: `results/runtime_artifacts/phase6_bam/p6_bam_005_comparison/preflight_manifest.json`, `v0_effective_config.json`, and `va2_effective_config.json`.
- CPU-only parity preflight proved all effective config values matched except controller configuration and run identity/output path. Dataset files and trajectory covered all 500 frames.

The launch wrappers used the following expanded commands, sequentially:

```text
P6_BAM_RUN_ID=p6_bam_005_room0_0_499_v0_r01 PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -f 'elapsed_seconds=%e peak_rss_kb=%M exit_status=%x' -o results/runtime_artifacts/phase6_bam/p6_bam_005_comparison/v0_process_time.txt /home/robot/miniconda3/envs/sgs_slam_5080/bin/python scripts/slam.py results/runtime_artifacts/phase6_bam/p6_bam_005_comparison/v0_500_config.py > results/runtime_artifacts/phase6_bam/p6_bam_005_comparison/v0_run.log 2>&1
P6_BAM_RUN_ID=p6_bam_005_room0_0_499_va2_r01 PYTHONDONTWRITEBYTECODE=1 /usr/bin/time -f 'elapsed_seconds=%e peak_rss_kb=%M exit_status=%x' -o results/runtime_artifacts/phase6_bam/p6_bam_005_comparison/va2_process_time.txt /home/robot/miniconda3/envs/sgs_slam_5080/bin/python scripts/slam.py results/runtime_artifacts/phase6_bam/p6_bam_005_comparison/va2_500_config.py > results/runtime_artifacts/phase6_bam/p6_bam_005_comparison/va2_run.log 2>&1
```

The exact expanded commands and process start/end, exit and `/usr/bin/time` records are in `launch_v0.sh`, `launch_va2.sh`, `v0_process_record.txt`, `va2_process_record.txt`, `v0_process_time.txt`, and `va2_process_time.txt` under the comparison directory. Both returned 0. V0 was validated before the single V-A2 launch; neither was retried.

## Runtime and structural evidence

| Measure | V0 | V-A2 |
|---|---:|---:|
| Frames / mapping events | 500 / 500 | 500 / 500 |
| Configured / executed mapping iterations | 60 / 30,000 | 60 / 22,695 |
| Budget distribution | OFF: 500×60 | FULL 1, MID 12, LOW 487 |
| Online frame-loop wall | 2,319.05 s | 1,963.46 s |
| Mapping-loop LIGHT wall sum | 1,355.20 s | 1,004.94 s |
| Tracking LIGHT stage sum | 925.36 s | 920.05 s |
| Whole-process wall | 2,349.67 s | 1,994.25 s |
| Process peak RSS (`/usr/bin/time`) | 7,423,840 KiB | 7,426,524 KiB |
| LIGHT sampled RSS/HWM peak | 4,984,037,376 / 5,006,856,192 B | 4,987,191,296 / 5,017,178,112 B |
| Peak CUDA allocated / reserved (LIGHT allocator samples) | 3,597,379,072 / 4,661,968,896 B | 3,777,924,096 / 4,582,277,120 B |
| CPU archive | 102 keyframes; 2,663,424,000 logical B | 102 keyframes; 2,663,424,000 logical B |
| H2D staging | 28,164 events; 735,418,368,000 B | 21,271 events; 555,428,352,000 B |
| Final Gaussians / keyframe IDs | 2,248,654 / 102 | 2,270,111 / 102 |

V-A2 reduced mapping iterations by **24.35%**, mapping wall sum by **25.85%**, online loop wall by **15.33%**, and process wall by **15.13%**. Online-loop speedup ratio was 1.181×; process-wall ratio was 1.178×. These are one matched run pair, not statistical speedup evidence. The historical P5-LEAN target of ≥20% online wall reduction was **not met**; the researcher's current objective of a positive runtime reduction was met. LIGHT host-stage sums are not necessarily additive; `/usr/bin/time` and LIGHT HWM use different sampling conventions. No standalone online timing was inferred from process time.

V0 had 30,000/30,000 configured/effective/executed iterations. V-A2 kept configured maximum 60 throughout and executed the tier budget for each event. Its single invalid novelty event was frame 0 (`initial_frame`) and correctly used FULL=60; the remaining 499 current-event signals were valid, with no unexpected fallback. Novelty fraction min/median/max over valid events was 0.00013538 / 0.00073655 / 0.01692406. By 100-frame segments, LOW/MID/FULL counts were: 0–99: 87/12/1; 100–199: 100/0/0; 200–299: 100/0/0; 300–399: 100/0/0; 400–499: 100/0/0. All 500 events recorded the required pruning floor of 21 iterations, preserving zero-based prune iteration 20. Both runs completed with finite floating-point checkpoint arrays and valid 500-pose trajectories/keyframe IDs. LIGHT summaries report completed status, zero dropped spans and zero pending CUDA events. The summary's CUDA event accounting has no sampled event spans; allocator values are LIGHT runtime measurements, not device-wide `nvidia-smi` peaks. A separate `nvidia-smi` query during V0 could not communicate with the driver even though both CUDA runs completed; this is recorded as a host-query limitation.

The interval checkpoint `params499.npz`, final `params.npz`, keyframe IDs, config copy, six 11-entry evaluator files, RGB/depth/semantic rendered samples and composite plots are present for each variant. V0 final checkpoint SHA256: `638a44ae4df4fff10d2b2c9d88c82852e4266c91244bc2080bfb83a161358bff`; V-A2: `661d82ffb2aff193f98fa1be178f4a9c94f420a51cf68bc3d381e2a6aa112861`.

## Matched final-map quality

The unchanged `utils.eval_helpers.eval` was called by the online entrypoint after the map checkpoint. With `eval_every=50`, it renders the same 11 training views `[0,49,99,149,199,249,299,349,399,449,499]` for both final maps; the loop visits the horizon to load GT/poses, while rendering and metric files are produced only for these IDs. `psnr.txt`, `ssim.txt` (MS-SSIM), `lpips.txt`, `l1.txt`, and `miou.txt` each have 11 finite entries. RGB metrics use the evaluator's valid-GT-depth mask for this `mapping_iters=60` call; Depth L1 uses valid GT depth; semantic mIoU uses the existing GT-palette-assisted recoloring protocol. Rendered RGB/depth/semantic outputs are saved for all 11 views. ATE uses all 500 saved poses; the CPU validator reconstructs the same relative-w2c camera translations and Horn alignment used by `eval_helpers.py`, reporting released mean translation error and supplementary true RMSE.

| Metric | V0 | V-A2 | Change vs V0 | 15% screen |
|---|---:|---:|---:|---|
| ATE Mean (m) | 0.00254617 | 0.00230700 | −9.39% | PASS |
| True ATE RMSE (m) | 0.00308668 | 0.00281463 | −8.81% | PASS |
| PSNR (dB) | 36.19163 | 36.12453 | −0.06710 dB | PASS: implied MSE +1.56% |
| MS-SSIM | 0.989386 | 0.988725 | −0.000662 (−0.067%) | PASS |
| LPIPS-Alex | 0.051610 | 0.050332 | −2.48% (improved) | PASS |
| Depth L1 (m) | 0.00312353 | 0.00320590 | +2.64% | PASS |
| Semantic mIoU | 0.908787 | 0.907979 | −0.089% | PASS |

All seven researcher-defined 15% checks pass individually; no averaging across metrics was used. PSNR is interpreted using the required equivalent MSE change, not as a percentage of dB: `10^((PSNR_V0−PSNR_VA2)/10)−1 = +1.557%`. The original P5-LEAN provisional quality targets were frozen before this medium-horizon decision and all six historical quality checks also pass: PSNR decrease ≤0.5 dB, MS-SSIM absolute decrease ≤0.01, LPIPS absolute increase ≤0.02, Depth L1 increase ≤10%, mIoU absolute decrease ≤0.02, and ATE RMSE increase ≤max(10% relative, 1 mm absolute). The separate historical runtime target ≥20% online reduction is missed. The full paired per-frame values/deltas and validation calculations are in `paired_per_frame_metrics.csv` and `paired_validation.json` in the comparison directory.

These results support a bounded room0 trade-off: fewer mapping iterations coincided with lower online and process wall while all requested quality screens passed. They do not establish causal attribution, statistical non-inferiority, full-scene feasibility, or generalization. There was one seed/run per variant; the controller changes optimization work and consumes no RNG itself, but source-level RNG/numerical variability remains a limitation. No extra evaluator or render workload was launched after the runs.

## Integrity and next step

All outputs are under the two unique Phase 6 run IDs and `p6_bam_005_comparison/`. The Phase 4 full-scene checkpoint retained expected SHA256 `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`; captured P6-BAM-002, P6-BAM-003 and R1 checkpoint hashes also match preflight. No Phase 4/P6 historical run was overwritten. Historical P6-BAM-003 remains `INCONCLUSIVE_P6_BAM_003_QUALITY_OR_RUNTIME`; R1's 0–49 screening PASS is unchanged. Historical untracked P5 reports, SESSION_007–010 and `vds` were preserved.

**Recommendation:** researcher review before authorizing any next horizon. This gate is a quality-constrained **500-frame** validation only; it does not authorize 0–1999 automatically.
