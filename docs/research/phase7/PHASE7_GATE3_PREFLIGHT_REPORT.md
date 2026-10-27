# Phase 7 Gate 3 — preflight readiness report

**Status:** `PARTIAL_GATE3_PREFLIGHT_READY`<br>
**Execution:** `NOT_STARTED`<br>
**Session:** `SESSION_005` — ACTIVE

## Verified worktree and inputs

**RUNTIME/READ-ONLY VERIFIED:** worktree branch is `phase7-bcgm`, HEAD is
`68f9060f7ff4d8d141be1d5f71339401327edd06`. Phase 7 online source, BCGM
module, frozen Phase 4 source and Gate 1B worker match the hashes in the Gate
3 run contract. Gate 3 config hash is
`1bb57b3dd38e98c39a24310ceaee656a8415ce901e61808bb19cea8422c4ff22`.

The default guarded runner checked all authorized config differences
(`run_name`, `data.end`, `data.num_frames`) and reported exact config equality
for every other value. It found 2,000 non-empty files in each required
`frames`, `depths`, `semantic_ids`, and `semantic_colors` directory, covering
IDs 0–1999. The pinned environment executable exists. Both Gate 3 run-specific
output directories are absent.

## Current capacity observations

| Resource | Current observation | Runner guard | Status |
|---|---:|---:|---|
| Filesystem free | 28,515,016,704 B (~26.55 GiB); 97% used | ≥20 GiB | PASS at observation |
| Gate 3 output budget | 6 GiB conservative estimate | Reserve 14 GiB beyond estimate | PASS at observation |
| Host `MemAvailable` | 125,635,751,936 B (~117.0 GiB) | ≥32 GiB | PASS at observation |
| GPU | Expected RTX 5080, prior Gate 2 host record was 16,303 MiB total | GPU 0 and ≥12 GiB free | `CODEX_GPU_NOT_VERIFIED` now |
| Active GPU compute apps | `nvidia-smi` process query unavailable | No unreviewed process | `NOT_VERIFIED` |

The preflight command ran in the Codex environment and returned
`CODEX_GPU_NOT_VERIFIED` because `nvidia-smi` could not communicate with the
driver. This is an environment visibility limitation, not evidence that the
direct host GPU has failed. The prior Gate 2 run's GPU observation is
historical, not a current Gate 3 readiness check. The visible OS process list
contained no SLAM workload, but device compute-process state cannot be
confirmed without `nvidia-smi`.

## Direct-host checks

Run the guarded, read-only preflight on the GPU host:

```bash
cd /home/robot/research/SGS_slam_phase7_bcgm
nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv,noheader
nvidia-smi --query-compute-apps=pid,process_name,used_gpu_memory --format=csv,noheader
df -h /home/robot/research/SGS_slam_phase7_bcgm
free -h
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B tools/phase7/gate3_on_runner.py
```

The runner refuses execution if any pinned identity, dataset, unique-path,
disk, RAM, GPU, process, package, or scientific-config check fails. Its
default mode creates no run directories and does not launch SLAM. The
`--execute` command remains outside this preparation task.

## Storage estimate and risk

Gate 2's entire model/evaluation tree is 669,833,088 bytes; its `eval/` tree
is about 169 MiB for 101 views. Four times that evaluation coverage is about
676 MiB. A separate Phase 4 room0 full-scene save contains 322,361,795-byte
NPZ and two 337,040,173-byte PLY exports. Allowing headroom for Gate 3's
larger/evolving Gaussian state, temporary serialization, 401-view renders,
logs and telemetry, the runner budgets 6 GiB and requires 20 GiB free. At the
current 27 GiB rounded free space, estimated reserve beyond the budget is
about 20.6 GiB. Recheck on the direct host immediately before any run.

Gate 3 may approach the 4.5M cap, but pruning and candidate rates affect
whether it activates. The run must not be changed to force activation. The
historical Phase 4 full-scene output-save run reached 4,956,467 Gaussians;
that observation is a scale reference, not a prediction for BCGM-on.

**Decision:** software/data/storage/RAM preflight checks pass in this
environment; current GPU readiness is not established. Preparation is
`PARTIAL_GATE3_PREFLIGHT_READY`; Gate 3 remains `NOT_STARTED`.
