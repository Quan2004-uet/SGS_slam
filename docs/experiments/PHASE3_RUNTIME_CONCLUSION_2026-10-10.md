# Phase 3 Runtime Conclusion — 2026-10-10

## 1. Scope

This document concludes **Phase 3 — Baseline Recovery & Reproduction** from the
available runtime evidence. It covers the released online SGS-SLAM path on
Replica `room0`, including destination-host validation, bounded online gates,
and full-scene failure characterization.

- Released source, experiment configuration, and algorithm behavior were kept
  unchanged in the recorded runs.
- GPU server: NVIDIA GeForce RTX 5080, physical memory `16,609,378,304` bytes
  (16 GB class device).
- This is not paper-metric reproduction.
- This is not an evaluation or post-SLAM stage.
- This is not Phase 4 algorithmic modification.

The bounded harnesses used output-only controls such as disabling W&B,
checkpoint writes, and prohibited reporting hooks. The recorded evidence states
that tracking/mapping iterations, learning rates, losses, resolution, Gaussian
addition, pruning, keyframe policy, semantic behavior, renderer behavior, and
seed remained at released values.

## 2. Environment

| Field | Recorded value | Evidence status |
|---|---|---|
| Repository | `/home/robot/research/SGS_slam` | VERIFIED FROM EVIDENCE |
| Git HEAD | `dd8caa772bd9511c018d298e38c081a679de2c72` | VERIFIED FROM EVIDENCE |
| Branch | `main` | VERIFIED FROM EVIDENCE |
| Conda environment | `/home/robot/miniconda3/envs/sgs_slam_5080` | VERIFIED FROM EVIDENCE |
| Python | `3.10.22` | VERIFIED FROM EVIDENCE |
| PyTorch / CUDA runtime | `2.7.1+cu128` / `12.8` | VERIFIED FROM EVIDENCE |
| System CUDA toolkit | `12.8.93` | VERIFIED FROM EVIDENCE |
| NumPy / OpenCV | `1.26.4` / `4.9.0.80` | VERIFIED FROM EVIDENCE |
| GPU | NVIDIA GeForce RTX 5080, compute capability 12.0 | VERIFIED FROM EVIDENCE |
| GPU memory | `16,609,378,304` bytes | VERIFIED FROM EVIDENCE |
| Dataset | `data/Replica`, sequence `room0`, length 2,000 | VERIFIED FROM EVIDENCE |
| Pinned renderer | `diff-gaussian-rasterization-w-depth`, revision `cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110` | VERIFIED FROM EVIDENCE |

The destination Python/PyTorch/CUDA stack is documented as Class B
destination-host compatibility recovery for the RTX 5080. It is not evidence
that the old-host environment and destination-host environment are binary
identical.

## 3. Evidence inventory

All requested primary files were present when this conclusion was prepared.
Runtime artifacts are under ignored `results/` paths; the summaries and JSON
files below are the authoritative records used for the table.

| Evidence | Primary files used | Presence |
|---|---|---|
| Destination validation | `VALIDATION_SUMMARY.md`, `VALIDATION_REPORT.md`, `validation_summary.json`, `bounded_0_4_results.json`, `final_integrity.log` | PRESENT |
| Phase 3C-4 | `PHASE3C4_SUMMARY.md`, `phase3c4_results.json`, `phase3c4_bounded_online.log` | PRESENT |
| Phase 3C-6 | `PHASE3C6_SUMMARY.md`, `phase3c6_results.json`, `phase3c6_bounded_online.log` | PRESENT |
| Full-scene baseline | `FULL_SCENE_SUMMARY.md`, `full_scene_room0_results.json`, `full_scene_room0.log`, `pre_run_system_state.log`, `post_run_system_state.log` | PRESENT |
| Allocator-optimized full scene | `FULL_SCENE_ALLOCATOR_OPT_FAST_SUMMARY.md`, `full_scene_room0_allocator_opt_fast_results.json`, `full_scene_room0_allocator_opt_fast.log`, `pre_run_system_state.log`, `post_run_system_state.log` | PRESENT |
| Memory optimization log | `docs/experiments/FULL_SCENE_MEMORY_OPTIMIZATION_LOG.md` | PRESENT |
| Context documents | `project_management/PROJECT_STATUS.md`, `project_management/SESSION_HANDOFF.md`, `docs/baseline_reproduction/runtime/13_bounded_online_50_frames.md` | PRESENT |

Additional harness, environment, and supporting logs exist in the same runtime
folders. No requested evidence file was missing.

## 4. Runtime gate summary table

`UNKNOWN` means the value was not available in the corresponding evidence and
was not inferred.

| Gate | Target frames | Status | Completed frames | Final completed frame | Stop reason | Runtime seconds | Final/last stable Gaussians | Resident keyframes | Peak allocated | Peak reserved | Evidence path |
|---|---:|---|---|---:|---|---:|---:|---:|---:|---:|---|
| Server validation / migration regression | 0–4 | `PASS` / `PASS_FRAME_LIMIT` | 0–4 | 4 | Guard blocked index 5 before real loader | UNKNOWN | 861,729 | UNKNOWN | 1,536,845,312 B | 1,803,550,720 B | `results/runtime_artifacts/server_validation_2026-10-09/` |
| Phase 3C-4 | 0–99 | `PASS_FRAME_LIMIT` | 0–99 | 99 | Guard intercepted index 100 before real loader | 368.82347768195905 | 1,404,614 | 21 | 3,006,056,960 B | 4,353,687,552 B | `results/runtime_artifacts/phase3c4/` |
| Phase 3C-6 | 0–499 | `PASS_FRAME_LIMIT` | 0–499 | 499 | Guard intercepted index 500 before real loader | 2,247.4197974938434 | 2,257,421 | 101 | 6,254,666,752 B | 8,025,800,704 B | `results/runtime_artifacts/phase3c6/` |
| Full-scene baseline | 0–1999 attempt | `CUDA_OOM` | 0–1293 | 1293 | OOM during mapping of frame 1294 | 8089.096434480045 | 4,698,647 | 259 | 13,602,712,064 B | 15,843,983,360 B | `results/runtime_artifacts/full_scene_room0/` |
| Full-scene allocator-opt fast | 0–1999 attempt | `CUDA_OOM_ALLOCATOR_OPT` | 0–1332 | 1332 | OOM during mapping of frame 1333 | 8318.306819677353 | UNKNOWN | UNKNOWN | 12,547,390,464 B | 15,839,789,056 B | `results/runtime_artifacts/full_scene_room0_allocator_opt_fast/` |

The allocator-optimized run recorded an OOM allocation failure while PyTorch
reported approximately 3.33 GiB reserved but unallocated. No frame 2000
boundary was reached in either full-scene attempt.

## 5. Key runtime findings

- `RUNTIME VERIFIED`: destination-host validation passed on the RTX 5080,
  including the pinned renderer build/import/smoke test, Replica `room0`
  dataset index 0, first-frame initialization, and guarded frames 0–4.
- `RUNTIME VERIFIED`: Phase 3C-4 frames 0–99 passed with the guard stopping
  before index 100.
- `RUNTIME VERIFIED`: Phase 3C-6 frames 0–499 passed with the guard stopping
  before index 500.
- `RUNTIME VERIFIED`: the released full-scene baseline did not complete;
  CUDA OOM occurred during mapping around frame 1294.
- `RUNTIME VERIFIED`: the runtime-only allocator attempt did not complete;
  CUDA OOM occurred during mapping at frame 1333.
- `RUNTIME VERIFIED`: allocator optimization extended the full-scene attempt by
  approximately 39 completed frames, from `0–1293` to `0–1332`.
- `RUNTIME VERIFIED`: peak reserved memory remained near the 16 GB device
  limit: `15,843,983,360` bytes in the baseline attempt and
  `15,839,789,056` bytes in the allocator attempt.
- `RUNTIME VERIFIED`: memory growth had not plateaued by frame 499. Peak
  allocated/reserved memory grew to `6,254,666,752` / `8,025,800,704` bytes,
  while resident keyframes reached 101.
- `RUNTIME VERIFIED`: resident keyframes increased linearly under the released
  online path, reaching 101 at frame 499 and 259 at the last stable full-scene
  baseline frame 1293.
- `RUNTIME VERIFIED`: Gaussian growth slowed across later 100-frame segments
  in Phase 3C-6, but it did not stop and did not prevent full-scene OOM.
- `RUNTIME VERIFIED`: all observed losses and captured trainable/non-trainable
  tensor states remained finite in the bounded runs and at the stable points
  recorded by the full-scene evidence.
- `INFERRED`: the primary observed blocker is memory capacity/residency rather
  than numerical instability. This inference is based on finite numerical
  state alongside repeated mapping-stage OOM.

## 6. Baseline conclusion

### RUNTIME VERIFIED

- The released SGS-SLAM online baseline is runtime-verified through bounded
  prefixes up to at least frames `0–499` on the RTX 5080 16 GB device.
- The released full Replica `room0` run over frames `0–1999` did not complete
  on the RTX 5080 16 GB device.
- Runtime-only allocator optimization was insufficient to complete full
  `room0`.

### INFERRED

- Full-scene completion on this 16 GB GPU likely requires a non-trivial
  memory-management/residency-policy change or a GPU with larger VRAM.
- The evidence supports closing the current pure baseline runtime attempt with
  a documented memory limit rather than retrying the identical allocator-only
  approach.

### UNKNOWN

- Whether a source-level memory-policy change can complete all 2,000 frames
  while preserving acceptable metrics.
- Which specific memory policy would provide sufficient capacity without
  changing the scientific behavior or evaluation protocol.

Any memory-management change must be classified as an explicitly named
research variant, not as pure baseline reproduction.

## 7. What this does NOT prove

- Paper metrics have not been reproduced.
- Evaluation, ATE, rendering metrics, PSNR/SSIM/LPIPS, semantic metrics,
  post-SLAM optimization, and paper comparison have not been run as part of
  these records.
- The paper's target numbers have not been established for this repository's
  evaluator or output stage.
- A modified memory variant has not been shown to preserve acceptable metrics.
- Full-scene success on a GPU with larger VRAM has not been confirmed.
- Bounded-prefix success establishes neither full-scene completion nor
  paper-level performance.

## 8. Recommended next steps

### A. Close baseline runtime reproduction

Close the pure baseline runtime reproduction with the documented RTX 5080
memory limit and preserve the full-scene OOM evidence as the baseline failure
characterization.

### B. Run the released baseline on larger VRAM infrastructure

If paper comparison is required, use a GPU or infrastructure with sufficient
VRAM to run the unchanged released full-scene baseline. Any such run must
retain the existing source/config/algorithm and separately record its
environment and outputs.

### C. Start an explicitly marked memory-policy research variant

If continuation on 16 GB is required, begin a new non-baseline research variant
and evaluate one controlled hypothesis at a time. Candidate areas include:

- keyframe CPU offload;
- bounded GPU keyframe residency;
- optimizer-state offload;
- tensor-lifetime/autograd retention audit;
- renderer transient-memory reduction.

These changes would no longer be pure released-baseline reproduction and must
be tracked with a separate modification/experiment identifier.

## 9. Source/config integrity

- Recorded run HEAD before/after: `dd8caa772bd9511c018d298e38c081a679de2c72` /
  `dd8caa772bd9511c018d298e38c081a679de2c72`.
- Recorded run branch: `main`.
- Recorded runtime evidence reports Git status clean before and after each
  validated run.
- Current repository Git status at conclusion creation is not clean because
  `docs/experiments/FULL_SCENE_MEMORY_OPTIMIZATION_LOG.md` is an existing
  untracked research log and this conclusion is newly created. This does not
  indicate a source/config change.
- The released source/config/algorithm were not modified by the runtime runs
  or by creating this document.
- Runtime artifacts under `results/` are Git-ignored. The two documents under
  `docs/experiments/` are research records and are not source/config changes.
- No commit or push was performed.

## 10. Final state statement

Phase 3 runtime baseline on RTX 5080 16 GB is complete up to bounded
reproduction and full-scene failure characterization. The released baseline
passes frames 0–499 but fails full Replica `room0` due to CUDA OOM around
frames 1294–1333. Full 2,000-frame completion requires either more VRAM or an
explicitly authorized memory-management research variant.

