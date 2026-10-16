# P6-BAM-002 — Matched LIGHT 0–10 GPU Smoke Gate

Date: 2026-10-16. Gate: `PASS_P6_BAM_002_SMOKE_INTEGRATION`; activation: `ADAPTIVE_ACTIVATION_CONFIRMED`.

This is an 11-frame functional integration result, **not** a full-scene, speedup, memory-capacity, or quality-noninferiority validation. Both authorized runs completed once; no retry or horizon expansion was performed.

## Frozen provenance and launch

- Source: branch `phase5-profiling-instrumentation`, commit `a3aefc745b73da520fa2ae53e77b0349fd25fa00` (P6-BAM-001 FIX1). The peeled Phase 4 tag was `37522db553ff18b96592073f9de699db7fa48600`.
- Interpreter: `/home/robot/miniconda3/envs/sgs_slam_5080/bin/python`; Python 3.10.22, PyTorch 2.7.1+cu128, CUDA 12.8, NVIDIA RTX 5080, driver 580.167.08. Seed 0.
- Dataset: Replica room0, frame start 0, exclusive end 11, stride 1. Source/config inspection established `num_frames=11`; runtime frame evidence is exactly `[0,1,2,3,4,5,6,7,8,9,10]` in both runs.
- Frozen configs: `configs/replica/phase6_bam_base.py`, `phase6_bam_v0.py`, `phase6_bam_va.py`, with per-run config copies and effective JSON under `results/runtime_artifacts/phase6_bam/p6_bam_002_comparison/`. V0 and V-A had the same room, resolution 680×1200, tracking 40, mapping maximum 60, keyframe selection, CPU offload, seed, LIGHT profiler and output/evaluator policy. Only variant identity and budget-control configuration differed. V-A used experimental thresholds 0.01/0.05 and tiers 30/45/60; these thresholds are not validated.
- Exact launch commands: `bash results/runtime_artifacts/phase6_bam/p6_bam_002_comparison/launch_v0.sh` and, only after V0 validation, `bash results/runtime_artifacts/phase6_bam/p6_bam_002_comparison/launch_va.sh`. Those scripts record the full `P6_BAM_RUN_ID=... /home/robot/miniconda3/envs/sgs_slam_5080/bin/python scripts/slam.py ...` invocation and process timing. Both returned code 0.
- Run IDs: `p6_bam_002_room0_0_10_v0_r01` and `p6_bam_002_room0_0_10_va_r01`. Each distinct result directory was absent before its launch. Both resolve strictly under `results/runtime_artifacts/phase6_bam/`; symlink/path checks found no escape or historical target. Runs were sequential. The wrapper's existence check is not atomic, so unique IDs and sequential launch were essential.

## Runtime-integrity findings

| Check | V0 | V-A |
|---|---:|---:|
| Frames / mapping events | 11 / 11 | 11 / 11 |
| Budget decisions | 11 FULL (controller OFF) | 1 FULL, 4 MID, 6 LOW |
| Valid novelty events | 0 by OFF-mode design | 10 |
| Configured / actually executed mapping iterations | 660 / 660 | 660 / 420 |
| Prune iteration 20 reachable | all 11 events | all 11 events |
| Final Gaussians / archived keyframes | 879,811 / `[0,4,9]` | 880,721 / `[0,4,9]` |
| LIGHT status / dropped CUDA spans | completed / 0 | completed / 0 |
| Saved numeric state | finite | finite |

V0 had `enabled=0`, `configured_iters=effective_iters=executed_iters=60` for every event. The OFF-mode novelty fields are deliberately invalid/sentinel; they are not interpreted as zero append. V-A's frame 0 used full 60 via the initial-frame fallback. Frames 1–4 selected MID 45, and frames 5–10 selected LOW 30. The frozen controller was independently reapplied to each event's recorded pre/post append counts and matched its recorded tier, fraction and budget. There were no unexpected fallback events. Actual executed totals, not selected labels, establish a 240-iteration workload reduction.

`pruning_enabled=1`, `prune_required_iters=21`, and each executed count was at least 30. Source inspection of `scripts/slam.py` places the Replica pruning call at zero-based mapping iteration 20; completed loops therefore reached that call site on every event. LIGHT telemetry has no individual prune-call counter, so this is source-plus-loop-completion evidence, not a direct prune-event trace. Between-event count decreases provide additional but non-exclusive evidence of Gaussian removal.

The final `params.npz` archives passed ZIP integrity inspection, contained 11 finite estimated and GT camera poses, and had final keyframe indices `[0,4,9]`. The matched configured output policy also emitted PLY and bounded evaluator output. No extra evaluator or post-opt workload was launched. Evaluator diagnostics are not promoted to validated ATE, PSNR, LPIPS, semantic mIoU or reconstruction non-inferiority on this short horizon. No exception, CUDA error, OOM or non-finite saved state was found.

CPU archive accounting recorded 3 keyframes and 78,336,000 logical bytes in each run. Host-to-device staging remained active: V0 375 events / 9,792,000,000 cumulative bytes; V-A 215 events / 5,614,080,000 bytes. This is evidence of the existing CPU keyframe offload and changed mapping workload, not a new transfer policy.

## Evidence and artifact safety

- Comparison metadata, exact launch scripts, logs, effective config snapshots, independent CPU validator and result JSON: `results/runtime_artifacts/phase6_bam/p6_bam_002_comparison/` (`v0_validation.json`, `va_validation.json`).
- V0 saved output: `results/runtime_artifacts/phase6_bam/p6_bam_002_room0_0_10_v0_r01/`; LIGHT JSONL, summary and run metadata: `results/runtime_artifacts/phase6_bam/telemetry/p6_bam_002_room0_0_10_v0_r01/`.
- V-A saved output: `results/runtime_artifacts/phase6_bam/p6_bam_002_room0_0_10_va_r01/`; LIGHT JSONL, summary and run metadata: `results/runtime_artifacts/phase6_bam/telemetry/p6_bam_002_room0_0_10_va_r01/`.
- The Phase 4 reference checkpoint `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz` retained size 322,361,795 bytes and SHA256 `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2` before and after these runs. Its timestamp and reference inventory were unchanged. No old output was overwritten.
- Tracked algorithm, config and profiler files remained unchanged from source commit `a3aefc7` throughout execution. Historical untracked P5 evidence, sessions 007–010 and `vds` were preserved.

## Boundary and next decision

The gate proves the current controller is integrated, sees valid current-event append novelty, selects reduced budgets in this bounded run, executes those budgets and preserves the required prune-iteration floor. One run per variant cannot establish statistically reliable runtime improvement, stable reconstruction quality or full-scene memory feasibility. Historical OFF-vs-OFF numerical divergence also precludes bit-exact matching demands. Recommend P6-BAM-003 (0–49) only after researcher review and separate authorization; do not start it automatically.
