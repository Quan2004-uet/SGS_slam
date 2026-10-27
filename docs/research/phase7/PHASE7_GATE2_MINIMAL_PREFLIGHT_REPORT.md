# Phase 7 Gate 2 — minimal preflight report

**Session:** `SESSION_005` — ACTIVE
**Preparation status:** `PASS_GATE2_WITH_COMPARISON_LIMITATIONS`
**Execution status:** `NOT_STARTED`.

## Prepared run

Only `p7_bcgm_g2_room0_on_0_499_r01` is prepared: Replica `room0`, frames
0–499, seed 0, Event Cap 9,000, Global Cap 4,500,000. Config:
`configs/replica/phase7_gate2_room0_on_0_499_r01.py` (SHA256
`ff025785249c1811c9ee3b3359cd4656b1992e78d9465b610bfe840ea2026b49`).
Runner: `tools/phase7/gate2_on_runner.py`; it reuses the Gate 1B worker
without modifying it (runner SHA256
`68f0c6774e6f111a73c523dea574602831f4c6a7a23ede70b56850aa053cdb66`). The
BCGM algorithm, Phase 4 frozen source, dataset, and
Gate 1B configs/artifacts were not changed. No Phase 6 BAM and no gradient
clone/split densification.

## Baseline reuse result

The requested Phase 4 Gate 4 directory exists and its summary, log and JSON
were read and SHA256-recorded in
`PHASE7_GATE2_BASELINE_REUSE_AUDIT.md`. It is `PASS_FRAME_LIMIT` for exactly
500 processed frames. It records final 2,255,038 Gaussians, 2,564.527929 s
continuous runtime (derived 0.194968 frames/s), CUDA peak allocated
3,468,590,592 B, CUDA peak reserved 4,525,654,016 B, and CPU keyframe archive
2,637,312,000 B. Its phase-boundary validator intercepted dataset index 500
before real loading. It did not evaluate/save a final map or estimated
trajectory, and it has no NVML peak or aggregate tracking/mapping FPS.

Gate 4 runtime source identity is the recorded commit `443d3d3251f0ac8d3e0e5489507fe13b506110a4`
plus an uncommitted Phase 4 CPU-offload source diff (SHA256
`d0ac4ffa33768189d6889db78444caea992cc4c9082c733e5c7961355c1c6e5c`); the
full effective source file hash and original temporary harness are absent.
This is a CPU-offload reference with comparison limits, not byte-locked
released-baseline evidence. No Phase 4 rerun is prepared.

Gate 1B remains `PASS_WITH_LIMITATIONS`; its 100-frame metric/admission results
are reused without rerun. BCGM-on activated Event Cap 14 times and rejected
35,201 candidates. Gate 1B has one run per arm and does not supply 500-frame
quality or significance claims. Gate 4 plus Gate 1B are adequate for this
minimal single-arm run only if missing same-horizon comparator metrics are
explicitly reported.

## Preflight state and storage

- Source identity: Phase 7 `scripts/slam.py` SHA256
  `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999` and
  `utils/bcgm.py` SHA256
  `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400` were
  rechecked. Base config SHA256 is
  `08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3`.
- Output paths were absent at preparation:
  `experiments/Replica/p7_bcgm_g2_room0_on_0_499_r01/` and
  `results/runtime_artifacts/phase7_gate2/p7_bcgm_g2_room0_on_0_499_r01/`.
- Disk observation: 28 GiB free, 97% used. One-run estimate 1.5–2.5 GiB;
  guarded runner refuses launch below 10 GiB free. Recheck immediately before
  execution.
- Host GPU SSH evidence from the preceding readiness reconciliation showed an
  RTX 5080, 16,303 MiB total, 818 MiB used, 0% utilization, with
  `gnome-remote-desktop-daemon` using 264 MiB. Codex sandbox GPU access remains
  `NOT_VERIFIED`. The guarded direct-host preflight has not been run during
  this preparation; execute it on the intended host before any run.
- Gate 1B manifest results remain preserved; no checkpoint duplication or
  Phase 4/Gate 1B artifact modification was performed.

## Commands

Direct-host read-only preflight, **prepared but not run here**:

```bash
cd /home/robot/research/SGS_slam_phase7_bcgm
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B tools/phase7/gate2_on_runner.py
```

Exact one-run command, **not executed**:

```bash
cd /home/robot/research/SGS_slam_phase7_bcgm
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python -B tools/phase7/gate2_on_runner.py --execute
```

The runner preflight checks branch/HEAD and source/config hashes, first 500
input files in all four modalities, output collisions, ≥10 GiB free, effective
science settings, BCGM limits, densification disabled, pinned PyTorch/CUDA/
renderer imports, CUDA runtime visibility, GPU identity and compute processes.
`--execute` repeats these checks before
creating the evidence directory and invoking the existing Gate 1B worker.

## Expected evidence and remaining comparison limitations

Expect process runtime/E2E FPS, source-stage tracking/mapping FPS if emitted,
CUDA allocator peaks, sampled NVML peak, insertion count trace, BCGM valid /
admitted / rejected totals and Event Cap activations, `params.npz`, 500-pose
trajectory arrays, saved evaluator metrics and per-view outputs. Validate
finite/aligned Gaussian arrays and all pose dimensions before interpreting
metrics. Global Cap is expected to remain inactive and is not validated
unless it actually binds.

Gate 4 supplies no PSNR/MS-SSIM/LPIPS/Depth L1/mIoU/ATE or estimated
trajectory for comparison. Any 500-frame quality result will therefore be
absolute for BCGM-on, not a same-horizon Phase 4 delta. Its runtime is
continuous-run time without evaluation/save and is not directly equal to Gate
2 process-wall/E2E time. Selection/sorting cost remains unisolated; report
aggregate unsynchronized insertion-call timing only.

**Final decision:** `PASS_GATE2_WITH_COMPARISON_LIMITATIONS`
**Additional GPU runs required by this minimal plan:** 1
**P4/BCGM-off reruns prepared:** 0
**Gate 2:** `NOT_STARTED`
**GATE2_EXECUTION_NOT_STARTED**

Related records: [baseline reuse audit](PHASE7_GATE2_BASELINE_REUSE_AUDIT.md),
[minimal run contract](PHASE7_GATE2_MINIMAL_RUN_CONTRACT.md), and
[Gate 1B final validation](PHASE7_GATE1B_FINAL_VALIDATION_REPORT.md).
