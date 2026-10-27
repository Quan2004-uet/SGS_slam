# Phase 7 Gate 3 — full-scene run contract

**Preparation status:** `PARTIAL_GATE3_PREFLIGHT_READY`<br>
**Gate 3 execution:** `NOT_STARTED`<br>
**Session:** `SESSION_005` — ACTIVE

## Objective and unique run

Prepare exactly one BCGM-on online run for Replica `room0`, frames 0–1999
inclusive (2,000 frames):

`p7_bcgm_g3_room0_on_0_1999_r01`

Output locations, both currently absent:

- Config: `configs/replica/phase7_gate3_room0_on_0_1999_r01.py`
- Runner: `tools/phase7/gate3_on_runner.py`
- Model/checkpoint/evaluation: `experiments/Replica/p7_bcgm_g3_room0_on_0_1999_r01/`
- Run logs/telemetry: `results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/`

The run is not launched by the default runner invocation. `--execute` is the
only path that creates run output directories and launches the reused
`gate1b_worker.py`; there is no retry or alternate arm.

## Scientific configuration lock

Gate 3 config deep-copies the exact Gate 2 config and changes only these
three paths, verified by CPU test and the runner preflight:

| Config path | Gate 2 | Gate 3 | Authorization |
|---|---:|---:|---|
| `run_name` | `p7_bcgm_g2_room0_on_0_499_r01` | `p7_bcgm_g3_room0_on_0_1999_r01` | Unique run identity |
| `data.end` | 500 | 2000 | Exclusive end for inclusive processed IDs 0–1999 |
| `data.num_frames` | 500 | 2000 | 2,000-frame trajectory allocation |

All other config values compare equal, including seed 0, frame start 0,
stride 1, 1200×680 resolution, semantic loading, tracking 40 iterations,
mapping 60 iterations, `map_every=1`, `keyframe_every=5`, mapping window 24,
pixel-driven insertion, pruning settings, evaluation cadence, and disabled
gradient clone/split densification. BCGM remains enabled with Event Cap
9,000 and Global Cap 4,500,000. Phase 6 BAM is not present/enabled.

| Identity | SHA256 |
|---|---|
| Phase 7 `scripts/slam.py` | `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999` |
| `utils/bcgm.py` | `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400` |
| Frozen Phase 4 `scripts/slam.py` | `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3` |
| Reused Gate 1B worker | `9a449ef10506ebbe6ccd0616d29aa02e9183554b333d605c9440ec07e09ad40b` |
| Gate 2 config | `ff025785249c1811c9ee3b3359cd4656b1992e78d9465b610bfe840ea2026b49` |
| Gate 3 config | `1bb57b3dd38e98c39a24310ceaee656a8415ce901e61808bb19cea8422c4ff22` |
| Gate 3 runner (prepared) | `1d97bb2d1dec0056a7d5a3e081d1ca3ee649a5f13ffd68b8563647300622a7a6` |
| NVML helper | `60c70dd0ca0f722c9ad6451cce29c1e269c5ac5eea96998dc150e220d0751c9c` |

Runner preflight also pins branch `phase7-bcgm`, HEAD
`68f9060f7ff4d8d141be1d5f71339401327edd06`, base Replica config, camera
config and room0 trajectory hashes, the unique output paths, dataset frame
files, disk/RAM/GPU requirements, and the config equality contract.

## Protected preflight and execution commands

Read-only direct-host preflight (no `--execute`):

```bash
cd /home/robot/research/SGS_slam_phase7_bcgm
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B tools/phase7/gate3_on_runner.py
```

Exact guarded execution command, **not executed**:

```bash
cd /home/robot/research/SGS_slam_phase7_bcgm
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B tools/phase7/gate3_on_runner.py --execute
```

Preflight requirements: expected branch/HEAD and source identities; 2,000
non-empty RGB, depth, semantic-ID and semantic-color inputs for frame IDs
0–1999; absent unique outputs; at least 20 GiB filesystem free; at least
32 GiB host `MemAvailable`; RTX 5080 index 0 with at least 12 GiB free VRAM;
no unreviewed compute process; pinned PyTorch 2.7.1+cu128/CUDA 12.8 and
renderer import. If the NVIDIA interface is invisible, preflight returns
`CODEX_GPU_NOT_VERIFIED` and refuses `--execute`.

The measured Gate 2 model/eval tree is 669,833,088 bytes, including an eval
tree of about 169 MiB. Scaling evaluation from 101 to 401 views and allowing
for a full-scene checkpoint/PLY plus serialization/log headroom gives a
conservative **6 GiB new-output budget**. Keep a further 14 GiB reserve by
requiring 20 GiB free. This is a guard estimate, not a claim that exact output
size is known. The Phase 4 output-save model tree is 996,453,677 bytes. CPU
RAM minimum is set above its historical 17.96 GiB process HWM.

## Required result validation

For a future authorized run, require exit code 0; `COMPLETE`; frames/GT poses
and estimated camera slots = 2,000; insertion records/transitions = 1,999;
checkpoint ZIP CRC and NumPy load with `allow_pickle=False`; finite arrays;
aligned Gaussian payloads; six finite evaluation arrays of 401 views; and
per-event admission/worker-transition checks. Record Event Cap and Global Cap
using their separate flags. Do not force Global Cap activation: if no
`global_saturated` event occurs, report it as not runtime-verified. Pruning
may later reduce map count and is not a cap failure.

Report process wall/E2E FPS separately from tracking/mapping stage FPS;
report CUDA allocated/reserved separately from recovered sampled device-wide
NVML; include Gaussian count/insertion counts; retain evaluator definitions.
The evaluator's “Depth RMSE” is Depth L1 and its “ATE RMSE” is aligned mean
translation error. No isolated sorting profiler is added to the scientific
source; selection/sorting cost remains unmeasured unless a separate
non-invasive measurement is designed.

## Current readiness boundary

Read-only preflight verified Git/source/config/dataset/storage/RAM/output-path
conditions, then blocked at GPU discovery: this Codex environment's
`nvidia-smi` returned error 9. Status is `CODEX_GPU_NOT_VERIFIED`; this does
not establish host GPU failure. Run the read-only command on the intended
direct host before requesting/performing any separately authorized execution.
Gate 3 remains `NOT_STARTED`.
