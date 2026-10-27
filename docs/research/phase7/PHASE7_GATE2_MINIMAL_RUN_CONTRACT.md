# Phase 7 Gate 2 — minimal BCGM-on run contract

**Status:** prepared; execution not authorized or performed here.
**Decision:** `PASS_GATE2_WITH_COMPARISON_LIMITATIONS`.
**Session:** `SESSION_005` — ACTIVE.

## Objective and sole arm

Run one bounded online BCGM-on experiment for Replica `room0`, frame IDs
0–499 inclusive, seed 0, using the Phase 4 CPU Keyframe Offload behavior
present in the Phase 7 source. Reuse the Gate 1B scientific settings and
validated Gate 1B worker. Gate 4 Phase 4 telemetry is the historical
runtime/memory/Gaussian-count reference; it does not provide quality metrics.

No P4 or BCGM-off 500-frame run is included. Gate 1B is reused as the
short-horizon parity/admission evidence and will not be rerun.

## Frozen identity and exact config

| Item | Value |
|---|---|
| Phase 7 branch / base HEAD | `phase7-bcgm` / `68f9060f7ff4d8d141be1d5f71339401327edd06` |
| `scripts/slam.py` SHA256 | `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999` |
| `utils/bcgm.py` SHA256 | `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400` |
| Config | `configs/replica/phase7_gate2_room0_on_0_499_r01.py` |
| Config SHA256 | `ff025785249c1811c9ee3b3359cd4656b1992e78d9465b610bfe840ea2026b49` |
| Guarded runner | `tools/phase7/gate2_on_runner.py` |
| Guarded runner SHA256 | `68f0c6774e6f111a73c523dea574602831f4c6a7a23ede70b56850aa053cdb66` |
| Reused worker SHA256 | `9a449ef10506ebbe6ccd0616d29aa02e9183554b333d605c9440ec07e09ad40b` |

Exact run-specific config values (all other science fields inherit the
Phase 4 Replica config unchanged):

```python
run_name = "p7_bcgm_g2_room0_on_0_499_r01"
workdir = "/home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica"
use_wandb = False
data = {
    "basedir": "/home/robot/research/SGS_slam/data/Replica",
    "gradslam_data_cfg": "/home/robot/research/SGS_slam_phase4_multiscene/configs/data/replica.yaml",
    "sequence": "room0", "start": 0, "end": 500, "stride": 1,
    "num_frames": 500,
}
bcgm = {
    "enabled": True,
    "max_new_gaussians_per_event": 9000,
    "max_gaussians": 4500000,
}
```

Inherited matched settings: seed 0; 1200×680; semantics on; `map_every=1`;
`keyframe_every=5`; mapping window 24; tracking 40 iterations; mapping 60
iterations; pixel-driven addition and pruning on; gradient clone/split
densification off; evaluator cadence 5; W&B off. Phase 6 BAM is not enabled.
The BCGM admission source is not modified.

## Isolated output paths and storage

- Model/evaluation/checkpoint:
  `/home/robot/research/SGS_slam_phase7_bcgm/experiments/Replica/p7_bcgm_g2_room0_on_0_499_r01/`
- Run evidence/log/NVML:
  `/home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate2/p7_bcgm_g2_room0_on_0_499_r01/`
- Both run-specific paths were absent at preparation. The runner refuses a
  collision and requires at least 10 GiB free before launch.
- Current free space: 28 GiB (filesystem 97% used). Gate 1B BCGM-on model
  directory is about 348 MiB for 100 frames; 101 evaluation views at 500
  frames imply roughly 4.8× render/evaluation output. Allow approximately
  **1.5–2.5 GiB** for this one new run, including larger final map/checkpoint
  and logs. This is a planning estimate, not a guarantee. No baseline or
  Gate 1B checkpoint will be copied.

## Direct-host preflight and execution commands

Run these from the intended GPU host/worktree, not from a Codex sandbox whose
GPU access is unverified. The first command is read-only: it checks the
branch/HEAD/source/config/worker hashes, dataset file counts and frames
0–499, unique output paths, ≥10 GiB free, effective config, BCGM limits,
densification state, and live GPU process state.

```bash
cd /home/robot/research/SGS_slam_phase7_bcgm
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B tools/phase7/gate2_on_runner.py
```

Exact execution command, **not executed**:

```bash
cd /home/robot/research/SGS_slam_phase7_bcgm
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B tools/phase7/gate2_on_runner.py --execute
```

`--execute` repeats the guarded preflight, starts one-second NVML sampling,
then invokes the existing `gate1b_worker.py`. Preflight also imports the
pinned PyTorch/renderer and checks CUDA runtime visibility/device identity
without launching SLAM. The worker's run call records
CUDA peak allocated/reserved, 499 per-frame insertion count transitions,
final Gaussian count and saved pose count. The launcher records process wall,
E2E FPS, NVML samples/peak, and tracking/mapping reciprocal FPS when emitted
by the source. Preserve partial evidence on any failure; do not silently
retry or overwrite the run paths.

## Expected post-run validation

1. Process exit 0, normal `rgbd_slam` return, 500 saved GT poses and estimated
   camera slots, 499 insertion records for frames 1–499, and final checkpoint
   `params.npz`.
2. Checkpoint ZIP CRC; `numpy.load(..., allow_pickle=False)`; finite numeric
   arrays; aligned Gaussian rows for RGB, rotation, opacity, scale, semantic
   IDs/colors; 500-frame camera/trajectory arrays.
3. 499 `BCGM_INSERTION` records and matching worker insertion transitions;
   `valid_candidates = admitted + rejected`; admitted ≤9,000; per-event and
   global cap flags/reasons consistent with counts. Record Event Cap
   activation frames and totals. If Global Cap is never reached, mark it
   `NOT_ACTIVATED / NOT_RUNTIME_VERIFIED`.
4. Report process wall/E2E FPS separately from stage tracking and mapping FPS;
   distinguish CUDA allocated, CUDA reserved, and one-second sampled
   device-wide NVML peak.
5. Preserve evaluator arrays and report RGB PSNR, MS-SSIM, LPIPS-Alex, Depth
   L1, semantic-color mIoU, and trajectory result for the evaluator's sampled
   training views. The saved evaluator's displayed “Depth RMSE” is Depth L1;
   `evaluate_ate()` is aligned mean translation error, not conventional ATE
   RMSE. Keep those labels and report absent metrics as `NOT_MEASURED`.
6. Hash source, BCGM module, config, runner, worker, effective configs and
   output artifacts in the final run record. Never mix results from the
   separate full-scene Phase 4 checkpoint.

Current instrumentation includes an unsynchronized aggregate insertion host
call timer; it does not isolate candidate selection/sorting latency. No
scientific source change is proposed for this. Treat isolated sorting cost as
`NOT_MEASURED` and report the limitation.

## Run count and limitations

Additional GPU runs prepared: **1** (this BCGM-on arm). P4/BCGM-off additional
runs: **0**. Gate 1B reruns: **0**. Phase 4 Gate 4 provides a 0–499 historical
context for runtime, CUDA memory, and Gaussian count, but not saved quality or
trajectory metrics and not a fully hash-locked source/config record. Thus
Gate 2 can report absolute BCGM-on quality and contextual resource differences;
it cannot claim a matched 500-frame BCGM-vs-P4 quality delta or statistically
established performance benefit. A same-horizon P4/off rerun would require a
separate researcher decision if that comparison becomes essential.

**Gate 2:** `NOT_STARTED`
**GATE2_EXECUTION_NOT_STARTED**

Related records: [baseline reuse audit](PHASE7_GATE2_BASELINE_REUSE_AUDIT.md),
[minimal preflight report](PHASE7_GATE2_MINIMAL_PREFLIGHT_REPORT.md), and
[Gate 1B evidence manifest](PHASE7_GATE1B_EVIDENCE_MANIFEST.json).
