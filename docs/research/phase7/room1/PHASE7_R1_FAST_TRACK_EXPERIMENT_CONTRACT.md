# Phase 7 R1 Fast-Track Experiment Contract

**Experiment:** `p7_bcgm_r1_full_room1_on_0_1999_r01`<br>
**Dataset:** Replica `room1`, frame IDs 0–1999 (2,000 frames).<br>
**Fast-track structure:** R1-Gate 0 preflight/baseline audit; R1-Gate 1 one full-scene BCGM-on run; R1-Gate 2 offline validation/evidence closure. No separate 0–99 or 0–499 experiments and no advanced visualization A–H.

## R1-Gate 0 outcome

**Current status: `HOST_EXECUTION_REQUIRED`; not `PASS_READY_FOR_FULL_SCENE`.** All Codex-visible data, baseline, config, uniqueness, disk/inode and RAM checks pass. Current Codex `nvidia-smi` cannot reach the NVIDIA driver, so current direct-host GPU/process/CUDA readiness is unverified. The historical RTX 5080 observations from Phase 4/6/room0 are not current evidence. Do not launch until the default preflight on the direct host returns `preflight=PASS`. Full findings are in `PHASE7_R1_GATE0_PREFLIGHT_AUDIT.md`.

## Locked method and config delta

The new config is a deep copy of room0 Gate 3 config. Expected recursive differences only:

| Path | Room0 Gate 3 | R1 | Reason |
|---|---|---|---|
| `run_name` | `p7_bcgm_g3_room0_on_0_1999_r01` | `p7_bcgm_r1_full_room1_on_0_1999_r01` | unique run/output identity |
| `data.sequence` | `room0` | `room1` | selected Replica scene |
| `viz.scene_name` | `room0` | `room1` | scene label metadata |
| `wandb.name` | `room0_0` | `p7_bcgm_r1_full_room1_on_0_1999_r01` | provenance label; WandB remains disabled |

Frame boundaries, seed, resolution, evaluator cadence, tracking/mapping, semantic fields, pruning, pixel-driven insertion, and output-save settings remain identical. Event Cap 9,000; Global Cap 4,500,000; BCGM enabled; clone/split densification disabled; Phase 6 BAM absent. CPU Keyframe Offload remains the implementation in the pinned Phase 7 source.

| Input | SHA256 |
|---|---|
| Phase 7 `scripts/slam.py` | `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999` |
| `utils/bcgm.py` | `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400` |
| Phase 7 Gate 1B worker | `9a449ef10506ebbe6ccd0616d29aa02e9183554b333d605c9440ec07e09ad40b` |
| Frozen base HEAD | `68f9060f7ff4d8d141be1d5f71339401327edd06` |
| Room0 reference config | `1bb57b3dd38e98c39a24310ceaee656a8415ce901e61808bb19cea8422c4ff22` |
| R1 config | `3c0d43c4e6ba4a3260815daa9f2d64f468802ab49f60686135df40b22f61bd10` |
| Replica room1 `traj.txt` | `5c650f90192da13b628308a6cbaf68fa6e048cfaa8f1870c5e66572296cc5c7d` |
| Replica `cam_params.json` | `ffbefdeb53755e1490d6936dffdee253510e68d5e443e1ba91e60202addc1a0a` |

The runner's own SHA256 is recorded in the run summary/manifest; it is not self-pinned in its source.

## Output contract

- Model/checkpoints/evaluation: `experiments/Replica/p7_bcgm_r1_full_room1_on_0_1999_r01/`
- Runtime evidence: `results/runtime_artifacts/phase7_gate3_room1/p7_bcgm_r1_full_room1_on_0_1999_r01/`
- No room0 or Phase 4/6 paths are reused for output. Both R1 output paths were absent at preparation.
- Expected final: `params.npz`, `params.ply`, `seg_params.ply`, available interval checkpoints, six evaluator arrays (401 values each), `eval/plots` for frame IDs `0,4,9,...,1999`, full log, effective input/runtime configs, 1-Hz NVML CSV, 1,999 insertion records, run summary and SHA256 artifact manifest. Offline ATE JSON/MD are then created without CUDA by `tools/phase7/r1_offline_ate.py`.

The run wrapper validates checkpoint ZIP CRC, NumPy load, finite/aligned Gaussian fields, 2,000 pose slots, both PLY vertex counts, all six 401-entry finite arrays, exact evaluator plot indices, insertion trace, and NVML telemetry. Global Cap is only verified if `global_saturated` occurs. Pruning can reduce map size after admission. No automatic retry/second arm.

## Storage and resource guard

Current Codex-visible `/` has 26,455,846,912 bytes available (about 24.64 GiB), 56,619,636 free inodes, and 117 GiB `MemAvailable`. Existing Phase 4 room1 model directory is 2,576,136,025 bytes; its run evidence is 18,849,613 bytes; separate 401-view offline evaluation is 723,337,643 bytes. The room0 Phase 7 model directory is 2,481,353,862 bytes. Use a conservative 6 GiB new-output budget and require at least 20 GiB free (14 GiB reserve beyond budget); runner also requires 10,000 free inodes and 32 GiB RAM. Current observed disk/RAM/inode margins pass, but must be rechecked by runner immediately before execution. No old artifacts are deleted, compressed, moved or copied.

## Direct-host commands

Run first from direct SSH terminal. Dry-run is read-only; it must finish with `preflight=PASS` and `execute=false`:

```bash
cd /home/robot/research/SGS_slam_phase7_bcgm
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B tools/phase7/r1_full_runner.py
```

Only after that direct-host preflight returns PASS, launch exactly one arm:

```bash
cd /home/robot/research/SGS_slam_phase7_bcgm
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B tools/phase7/r1_full_runner.py --execute
```

The `--execute` path repeats every guard, checks GPU 0 is an RTX 5080 with at least 12 GiB free, rejects unknown compute processes, verifies CUDA 12.8/PyTorch 2.7.1+cu128/native renderer/evaluation dependencies, checks source/config/dataset/output paths and resource capacity, then launches 0–1999 once. It refuses on any failed check and never shortens or retries.

After successful execution, offline ATE only (CPU; writes new evidence files and refuses overwrite):

```bash
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B tools/phase7/r1_offline_ate.py --checkpoint experiments/Replica/p7_bcgm_r1_full_room1_on_0_1999_r01/params.npz --json results/runtime_artifacts/phase7_gate3_room1/p7_bcgm_r1_full_room1_on_0_1999_r01/offline_ate_validation.json --markdown results/runtime_artifacts/phase7_gate3_room1/p7_bcgm_r1_full_room1_on_0_1999_r01/offline_ate_validation.md
```

## Comparison contract

- Strong historical reference: Phase 4 room1 full scene `p4_vb001_room1_full_0_1999_r01`, same scene/range, seed, 1200×680, Phase 4 CPU Keyframe Offload, and 401-view metric protocol. It has full checkpoint plus offline image/depth/semantic/ATE metrics; quality comparisons are reusable when definitions are confirmed identical. Runtime scope differs because Phase 4 offline evaluation (370.505805 s) is separate; no unqualified speedup.
- Secondary Phase 6 room1 full scene has 2,000 frames/401 views but includes BAM/adaptive mapping budget and a different source/config. It is a contextual method comparison, not a BCGM-only baseline.
- Phase 7 room0 is same method/config/runner but a different scene; cross-scene rows are descriptive, not paired effect estimates.

R1-Gate 1 and Gate 2 runtime-dependent reports remain `PENDING` until actual saved evidence exists.
