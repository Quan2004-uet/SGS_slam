# Phase 7 Gate 1B — Replica room0 bounded run contract

**Contract status:** prepared, **not executed**. Frame IDs are exactly 0–99 (100 frames). The three arms run separately and sequentially after researcher authorization. No full-scene claim follows from this contract.

## Source, environment and dataset lock

| Field | Frozen value and evidence |
|---|---|
| Phase 4 source | `/home/robot/research/SGS_slam_phase4_multiscene`, HEAD `68f9060f7ff4d8d141be1d5f71339401327edd06`, clean tracked source; `scripts/slam.py` SHA256 `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3` |
| Phase 7 source | `/home/robot/research/SGS_slam_phase7_bcgm`, branch `phase7-bcgm`, HEAD `68f9060f7ff4d8d141be1d5f71339401327edd06` plus Gate 1A uncommitted delta; `scripts/slam.py` SHA256 `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999`; `utils/bcgm.py` SHA256 `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400` |
| Base Replica config | Both source roots' `configs/replica/slam.py` SHA256 `08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3` |
| Camera/data config | `/home/robot/research/SGS_slam_phase4_multiscene/configs/data/replica.yaml`, SHA256 `4c1e33544bef24c146c4ec9a622bb3ad7a314168db8d192c191db08bad3edf58` for every arm |
| Dataset | `/home/robot/research/SGS_slam/data/Replica/room0`; 2,000 each RGB, depth, semantic-ID and semantic-color files, with nonempty indices 0–99; `traj.txt` has 2,000 lines, SHA256 `5692a60076e426b403dc64025ff38c443606a506704545ee192d4dbadedaaca2` |
| Interpreter | `/home/robot/miniconda3/envs/sgs_slam_5080/bin/python`, Python 3.10.22, PyTorch 2.7.1+cu128, CUDA runtime build 12.8; `diff_gaussian_rasterization` import located in the same environment |
| GPU | NVIDIA GeForce RTX 5080, 16,303 MiB reported by NVML, driver 580.167.08, device `cuda:0`; live job/occupancy check repeats before each arm |
| Runner/worker | `tools/phase7/gate1b_runner.py` SHA256 `044a2d3354fbbea196a35def864c494d7794c093d5dd7091d2e1a289c12942ce`; `gate1b_worker.py` SHA256 `9a449ef10506ebbe6ccd0616d29aa02e9183554b333d605c9440ec07e09ad40b` |

The three source/config combinations are intentionally distinct. The two Phase 7 arms share the exact Gate 1A source; the original arm imports Phase 4 source. The current Phase 7 source is not committed, so the file hashes above, clean frozen Phase 4 tree, and explicit modified/untracked inventory are part of the source identity. Re-run the guarded preflight if any file changes.

## Arm matrix and isolated paths

All three arm configs live under `/home/robot/research/SGS_slam_phase7_bcgm/configs/replica/`. All output paths are initially absent and must remain exclusive. The model root is `/home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica/`; evidence root is `/home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate1b/`.

| Arm | Run ID | Config file and SHA256 | Effective config SHA256 | Model directory | Evidence directory |
|---|---|---|---|---|---|
| Phase 4 original (`p4`) | `p7_bcgm_g1b_room0_p4_0_99_r01` | `configs/replica/phase7_gate1b_room0_p4_0_99_r01.py` · `f559e349a65fd3d92c0de0ea553abd93f75b0767e05b6d2729549de1b5c6bc27` | `e5c921af2c53d21a8779943ebc7da87c441089be2a62696beb7139d2977e14bc` | `/home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica/p7_bcgm_g1b_room0_p4_0_99_r01` | `/home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate1b/p7_bcgm_g1b_room0_p4_0_99_r01` |
| Phase 7 BCGM-off (`off`) | `p7_bcgm_g1b_room0_off_0_99_r01` | `configs/replica/phase7_gate1b_room0_off_0_99_r01.py` · `887ab9d9e7b92c11bd002d5bed4c4c3944d993624ef86b39198d8fdd5392e3db` | `d0777bb180d135d4c38e424b73605f4df41d99dcd28af8fce804c32f55f20291` | `/home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica/p7_bcgm_g1b_room0_off_0_99_r01` | `/home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate1b/p7_bcgm_g1b_room0_off_0_99_r01` |
| Phase 7 BCGM-on (`on`) | `p7_bcgm_g1b_room0_on_0_99_r01` | `configs/replica/phase7_gate1b_room0_on_0_99_r01.py` · `498d494db39beb55f28e6c6cee3d1edcc7ed763540b5cfd947c44988ef79e853` | `c5b76b26ae0f7c6e6c60b18d258e8ae34e27c40811e17fbf13ad1766a74a5c79` | `/home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica/p7_bcgm_g1b_room0_on_0_99_r01` | `/home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate1b/p7_bcgm_g1b_room0_on_0_99_r01` |

Effective config hashes are SHA256 over sorted compact JSON of the loaded input dictionary. Removing only `run_name` and `bcgm` yields identical canonical config SHA256 `21fe6546fec201254f320f090cdac4b5d3a00f54c666834075834968df859935` for all three arms. Config snapshots are generated at execution; no artifact directories were created during preparation.

## Matched settings and interpretation

`configs/replica/slam.py` is the common scientific base. Each arm sets `data.start=0`, `data.end=100` (exclusive in `basedataset.py`), `data.num_frames=100`, `data.stride=1`, `data.sequence=room0`, seed 0, 1200×680, semantic loading on, `primary_device=cuda:0`, `map_every=1`, `keyframe_every=5`, mapping window 24, tracking 40 iterations, mapping 60 iterations, `eval_every=5`, pixel insertion on, baseline pruning on, and gradient clone/split densification off. Camera intrinsics/depth scale, losses, renderer, keyframe selection and CPU archive/staging follow the identical base source/config read sites. W&B is disabled in all three arms; config snapshots and local logs replace online W&B output.

Only the run name and BCGM control vary between otherwise matched loaded dictionaries. The original arm has no `bcgm` key; the off arm uses `{"enabled": false}`. The on arm uses `max_new_gaussians_per_event=9000` and `max_gaussians=4500000`. These are screening values, not optimized thresholds.

The released saved-state evaluator is called after the frame loop with `eval_every=5`; a complete 100-frame run should sample `{0,4,9,...,99}` (21 training views) and use the saved 100-pose trajectory. Its `ssim` is MS-SSIM; its saved `rmse` is Depth L1 rather than conventional Depth RMSE; its ATE scalar is aligned mean translation error rather than true RMSE. Semantic-color mIoU is GT-palette-assisted. Conventional Depth RMSE and true ATE RMSE are `NOT_MEASURED` unless a separate, matched supplementary evaluator is authorized and run.

## Instrumentation and evidence protocol

The same guarded host runner and worker are used for all arms. The worker wraps `add_new_gaussians` only to record frame, count before/after, and unsynchronized host call time; the wrapper does not change returned parameters. BCGM-on additionally logs `BCGM_INSERTION` valid/admitted/rejected counts, caps, saturation, and skip reason. Sorting cost is included in the enabled insertion host call and full process wall; source mapping frame time begins after insertion, so mapping FPS alone must not be used to judge admission overhead.

| Measure | Collection and scope | Limit |
|---|---|
| Total wall / end-to-end FPS | Host monotonic timer around the worker process; FPS = 100 / wall only if exit 0 and saved pose count 100 | Includes interpreter startup, online SLAM, evaluation and serialization |
| `rgbd_slam` wall | Worker timer around the call plus final CUDA synchronization | Excludes earlier module import; separate from host process wall |
| Tracking/mapping FPS | Reciprocal of source-reported average tracking/mapping frame seconds in `stdout_stderr.log` | Mapping average excludes pre-mapping pixel insertion; neither equals end-to-end FPS |
| CUDA peak allocated/reserved | Worker resets PyTorch allocator peaks after source import, before `rgbd_slam`; reads after final synchronization | Process allocator measurements; distinct from NVML device usage |
| NVML VRAM/utilization | Host samples GPU 0 device-wide memory used and utilization every 1 s; logs all samples and peak/mean in summary | Sampled device-wide; can miss between-sample peaks and includes desktop usage |
| Gaussian counts | `insertion_counts.jsonl` for 99 append events when complete; final `means3D` count and 100-pose count read from `params.npz`; BCGM-on JSON logs candidate/admission counts | A frame count trace is measured during these future runs; no result exists at Gate 1B preparation |
| Quality | Frozen source `eval` outputs and per-view arrays, 21 training views if complete | No held-out/NVS claim; true depth/ATE RMSE require supplementary evaluation |

At execution, each run must preserve `stdout_stderr.log`, `nvml_samples.csv`, `insertion_counts.jsonl`, `effective_config_input.json`, `effective_config_runtime.json`, `run_summary.json`, the copied `config.py`, final `params.npz`, checkpoint/sidecars if present, and `eval/`. Record `NOT_MEASURED` for absent values. Do not substitute CUDA allocated, CUDA reserved and NVML memory for one another.

## Historical count evidence and expected activation

The read-only Phase 4 telemetry JSON at `/home/robot/research/SGS_slam/results/runtime_artifacts/phase4_vb001_full_scene_0_1999/phase4_vb001_full_scene_0_1999_results.json` records 2,000 processed frames but retains historical `FAIL_RUNTIME`; `docs/experiments/PHASE4_VB001_FULL_SCENE_AUDIT.md` classifies the validator defect, while `docs/experiments/PHASE4_VB001_FULL_SCENE_OUTPUT_SAVE_RESULT.md` separately records `PASS_FULL_OUTPUT_SAVE_TELEMETRY`. The latter output-save run explicitly excluded evaluation. These are historical sources for cap selection, not a matched 0–99 BCGM result or successful full-scene evaluation.

The frame trace has 815,998 initial Gaussians, 1,405,832 after frame-99 insertion, 1,405,735 after frame-99 mapping/pruning, and 4,983,660 after frame 1999 in the earlier detailed run. Among the 99 frame-1–99 insertion events, 16 added more than 9,000 Gaussians (`1,2,3,18–29,81`), with maximum 13,813. Across 1,999 full-scene events, recorded additions have lower-nearest-rank P90 6,783 and P95 9,116. Thus the 9,000 event cap is expected to activate in the bounded interval; the 4.5 million global cap is expected to remain inactive there. Candidate feedback and pruning can move the actual activation frames; exact BCGM counts remain unknown until execution. The historical frame-99 after-insertion count is 3,094,168 below the proposed global cap.

## Commands, sequencing and stop conditions

Read-only preflight, already exercised for each arm:

```bash
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B /home/robot/research/SGS_slam_phase7_bcgm/tools/phase7/gate1b_runner.py --arm p4
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B /home/robot/research/SGS_slam_phase7_bcgm/tools/phase7/gate1b_runner.py --arm off
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B /home/robot/research/SGS_slam_phase7_bcgm/tools/phase7/gate1b_runner.py --arm on
```

Only after separate researcher authorization, execute one arm at a time in this order, inspecting its evidence before starting the next:

```bash
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B /home/robot/research/SGS_slam_phase7_bcgm/tools/phase7/gate1b_runner.py --arm p4 --execute
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B /home/robot/research/SGS_slam_phase7_bcgm/tools/phase7/gate1b_runner.py --arm off --execute
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B /home/robot/research/SGS_slam_phase7_bcgm/tools/phase7/gate1b_runner.py --arm on --execute
```

The runner refuses source/config/dataset hash drift, wrong branch/HEAD, changed frozen tracked source, missing/empty inputs, mismatched frame/scientific settings, any existing target model/evidence directory, less than 10 GiB free output space, or an unreviewed GPU compute process. Stop after a failed arm, CUDA/renderer/import failure, OOM, incomplete 100-frame/pose horizon, nonfinite or unreadable model, missing required telemetry/evaluation, or unexpected config/output difference. Keep partial artifacts and logs; do not lower resolution/iterations, overwrite paths, retry silently, or continue to another arm automatically. A clean process exit alone is not a quality or parity result.
