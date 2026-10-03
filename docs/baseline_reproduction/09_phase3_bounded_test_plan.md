# Phase 3 Bounded Test Plan

Execute gates in order. Stop on failure, classify it, preserve evidence, and do
not advance by changing the algorithm. Commands shown are future commands; none
was run during Phase 2.

## Gate 0 — Host capability inventory

- **Goal:** establish whether the host can plausibly support the preferred stack.
- **Required check:** record OS, GPU model/VRAM/compute capability, NVIDIA driver,
  installed CUDA toolkit/nvcc, GCC/G++, Conda/pip availability, disk capacity.
- **Evidence:** immutable text record associated with commit and machine.
- **PASS:** driver/toolkit/compiler plan is compatible with the selected candidate,
  or a specific compatibility recovery is proposed and classified.
- **STOP:** no CUDA-capable NVIDIA GPU, insufficient disk/data access, or unresolved
  driver/toolkit incompatibility.
- **Likely categories:** host capability, CUDA driver/toolkit, compiler.

## Gate 1 — Python/PyTorch/dependency imports

- **Goal:** verify the selected environment without launching SLAM.
- **Required check:** import PyTorch, torchvision, Kornia, imageio, OpenCV,
  pytorch-msssim, torchmetrics, W&B, plyfile, and Open3D where applicable; record
  exact versions, `torch.version.cuda`, device identity, and basic CUDA tensor op.
- **Evidence:** command, lock/package list, stdout/stderr.
- **PASS:** all dependencies needed by online path import; CUDA tensor operation
  succeeds on the intended device.
- **STOP:** import/ABI/device failure.
- **Likely categories:** environment resolution, binary ABI, driver.

## Gate 2 — Renderer import and minimal smoke test

- **Goal:** validate the pinned compiled extension before dataset/model work.
- **Required check:** import `diff_gaussian_rasterization`; construct the smallest
  valid camera/Gaussian input based on existing helper contracts; execute bounded
  RGB and depth/silhouette forward passes and one backward pass.
- **Evidence:** pinned revision, build log, shapes/dtypes/device, finite outputs and
  gradients, peak memory.
- **PASS:** import and finite forward/backward complete on CUDA.
- **STOP:** compile/import/symbol/kernel/gradient failure.
- **Likely categories:** CUDA/PyTorch/compiler ABI, renderer API mismatch.

## Gate 3 — Dataset first-sample integrity

- **Goal:** verify the semantic Replica layout and preprocessing contract.
- **Required check:** instantiate `ReplicaDataset` with canonical YAML/config and
  inspect frame 0 plus one later frame; perform the checklist in
  `02_dataset_requirements.md`.
- **Evidence:** counts, paths, shapes, dtypes, ranges, calibration, pose checks.
- **PASS:** all modalities align, values are finite/plausible, frame-0 relative
  pose is identity, and later pose is invertible.
- **STOP:** missing/misaligned files, invalid depth scale/intrinsics/pose/semantics.
- **Likely categories:** dataset version, layout, corrupt/missing files.

## Gate 4 — First-frame Gaussian initialization

- **Goal:** verify dataset-to-map initialization without an online sequence.
- **Required test:** use a recorded derived config limited to one frame and run:

  ```bash
  python scripts/slam.py <derived-room0-1-frame-config.py>
  ```

- **Evidence:** config diff, initial point/Gaussian count, parameter schemas,
  renderer/loss finiteness, artifacts, peak VRAM.
- **PASS:** initialization, frame-0 mapping/evaluation/save complete with finite
  values and expected artifacts.
- **STOP:** NaN/Inf, schema/device failure, renderer failure, OOM.
- **Likely categories:** dataset preprocessing, camera convention, renderer,
  optimizer state, GPU capacity.

## Gate 5 — 2–5 frame online run

- **Goal:** exercise actual tracking, pose propagation, pixel-driven addition,
  pruning, keyframe conditions, mapping, and save/eval.
- **Required test:** same command form with a derived config limited first to two,
  then at most five frames; no algorithm changes.
- **Evidence:** per-frame loss/pose, Gaussian count, mapping selection, iteration
  counts, peak VRAM, artifacts.
- **PASS:** all requested frames complete; pose and losses finite; Gaussian append
  and optimizer recreation succeed; artifacts pass schema checks.
- **STOP:** first repeatable pipeline failure; do not expand the frame limit.
- **Likely categories:** tracking, append/optimizer mutation, mapping, W&B, memory.

## Gate 6 — 10–20 frame online run

- **Goal:** cover multiple keyframe intervals and observe memory/count trends.
- **Required test:** derived config at 10 frames, then no more than 20.
- **Evidence:** keyframe indices, selected mapping views, Gaussian curve, allocated/
  reserved/peak memory, timing, metric samples.
- **PASS:** stable finite execution through 20 frames with expected periodic
  keyframes and no unexplained unbounded resource jump.
- **STOP:** repeated failure or unexplained state/memory divergence.
- **Likely categories:** keyframe residency/selection, Gaussian growth, renderer
  temporary buffers, tracking drift.

## Gate 7 — Short bounded sequence

- **Goal:** establish sustained behavior before full room0.
- **Required test:** choose and record a fixed prefix based on Gate 6 trends and
  available compute; retain full resolution and algorithm settings.
- **Evidence:** same telemetry plus checkpoint integrity and predicted full-run
  memory/runtime envelope.
- **PASS:** completes the predeclared prefix, produces valid evaluation and
  checkpoint/final artifacts, and presents no unresolved capacity blocker.
- **STOP:** any unresolved source/environment/data failure or unsafe projected
  resource requirement.
- **Likely categories:** cumulative drift, memory growth, long-run I/O/logging.

## Gate 8 — One full Replica room0 scene

- **Goal:** reproduce the released online baseline on the canonical scene.
- **Required command:**

  ```bash
  python scripts/slam.py configs/replica/slam.py
  ```

  If W&B cannot be used, an explicitly archived derived config may differ only in
  logging/output provenance; its diff must accompany results.
- **Evidence:** full logs, commit/status, environment lock, config, counts/timing/
  memory, all required artifacts.
- **PASS:** full dataset length completes and online final eval/save are valid.
- **STOP:** do not proceed to post-opt when online artifacts or provenance fail.
- **Likely categories:** cumulative GPU capacity, dataset corruption, drift,
  checkpoint/output failure.

## Gate 9 — Online evaluation and reload check

- **Goal:** validate saved-map evaluation independently and form comparison table.
- **Required command:**

  ```bash
  python scripts/eval_novel_view.py configs/replica/slam.py
  ```

- **Evidence:** `eval/` and `eval_train/` arrays, evaluator version, sample counts,
  units, stdout ATE, stage-labeled Paper/Reproduced/Delta table.
- **PASS:** saved map reloads; metrics are finite and consistent with automatic
  online evaluation under the same cadence/protocol.
- **STOP:** evaluator protocol/input mismatch or missing provenance.
- **Likely categories:** saved schema, config/output resolution, metric dependency.

## Gate 10 — Post-opt, only if required

- **Goal:** produce a separately labeled offline-refined map for stage ambiguity
  analysis, not rescue a failed online result.
- **Required command after preserving online output:**

  ```bash
  python scripts/post_slam_opt.py configs/replica/post_slam_opt.py
  ```

- **Evidence:** input NPZ hash/path, post config, 7k/final logs and plots, Gaussian
  count/VRAM, separate final NPZ/PLYs.
- **PASS:** 15k run completes, final artifacts are valid, aggregate metrics are
  preserved from console/W&B, and online artifacts remain untouched.
- **STOP:** post-opt preload/densification OOM, invalid input, or missing metric
  provenance; do not change algorithm to force completion.
- **Likely categories:** GPU capacity, preload, densification, older evaluator.

## Gate 11 — Paper comparison

- **Goal:** judge reproduction without hiding protocol/stage differences.
- **Required analysis:** report Paper/Reproduced/Delta for room0 PSNR, code
  MS-SSIM vs paper SSIM, LPIPS, semantic mIoU, code ATE vs paper ATE RMSE, and
  depth where available; label online and post-opt separately.
- **Evidence:** metrics, exact evaluator, hardware/env/seed/config/commit, all
  discrepancies and run-selection policy.
- **PASS:** evidence-complete comparison and failure classification. Numerical
  closeness has no predeclared paper-specified threshold.
- **STOP:** missing stage/protocol/provenance; do not claim reproduction.
- **Likely categories:** paper/source discrepancy, evaluator semantics, dependency
  drift, stochastic/hardware effects, true result gap.

## Phase boundary

Phase 3 ends with baseline recovery/reproduction evidence and a discrepancy
report. It does not authorize semantic keyframe restoration, uncertainty
weighting, BA enablement, algorithm optimization, or a research proposal.
