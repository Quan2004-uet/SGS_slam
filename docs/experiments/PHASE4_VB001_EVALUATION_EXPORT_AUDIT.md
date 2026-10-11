# PHASE4-VB-001 Evaluation / Export Audit

## 1. Audit objective and boundary

This audit defines the repository-native evaluation and export protocol for the
saved PHASE4-VB-001 Replica `room0` full-scene state before any evaluator is
executed.

Audit date: 2026-10-11.

- Branch: `phase4-vb-001-cpu-keyframe-offload`.
- Audit HEAD: `63adf3aed8ae2201a46d11cec473672f9e91fd0e`.
- Saved-state run status: `PASS_FULL_OUTPUT_SAVE_TELEMETRY`.
- Saved-state frame range: 0--1999 (2,000 frames).
- Stable state:
  `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`.
- Online SLAM, final saving, and telemetry are complete.
- Evaluation and paper metrics remain `NOT RUN` / `NOT REPRODUCED`.

This was a source/config/artifact-metadata audit only. It did not import the
evaluator, initialize its eager CUDA LPIPS object, load the map onto CUDA,
render an image, or calculate a metric.

## 2. Saved-state checkpoint

### 2.1 Read-only verification method

`RUNTIME ARTIFACT VERIFIED`: the NPZ exists and is readable. Array metadata was
read from the embedded NPY headers through Python's ZIP reader. Only the small
intrinsics, first-frame transform, dimensions, and keyframe-index arrays were
materialized. The multi-million-element map arrays were not loaded merely to
repeat values already present in their headers. The NPZ is 322,361,795 bytes
and its recorded SHA256 is
`dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`.

| Key | Shape | Dtype | Interpretation |
|---|---:|---|---|
| `means3D` | `(4,956,467, 3)` | `float32` | Gaussian centers |
| `rgb_colors` | `(4,956,467, 3)` | `float32` | RGB precomputed colors |
| `unnorm_rotations` | `(4,956,467, 4)` | `float32` | Gaussian quaternions |
| `logit_opacities` | `(4,956,467, 1)` | `float32` | Opacity logits |
| `log_scales` | `(4,956,467, 1)` | `float32` | Isotropic log scales |
| `semantic_colors` | `(4,956,467, 3)` | `float32` | Rendered semantic-color features |
| `semantic_ids` | `(4,956,467,)` | `uint8` | Fixed Gaussian semantic metadata |
| `timestep` | `(4,956,467,)` | `float32` | Gaussian creation time |
| `cam_unnorm_rots` | `(1, 4, 2000)` | `float32` | Estimated relative w2c rotations, real-first quaternion |
| `cam_trans` | `(1, 3, 2000)` | `float32` | Estimated relative w2c translations |
| `gt_w2c_all_frames` | `(2000, 4, 4)` | `float32` | Saved relative GT w2c sequence |
| `intrinsics` | `(3, 3)` | `float32` | Camera matrix |
| `w2c` | `(4, 4)` | `float32` | First-frame w2c |
| `keyframe_time_indices` | `(402,)` | `int64` | Logical keyframe indices |
| `org_width` | scalar | `int64` | 1200 |
| `org_height` | scalar | `int64` | 680 |

The intrinsics are `fx=fy=600`, `cx=599.5`, `cy=339.5`. The keyframe array is
reloadable, has 402 entries, and ends in `[1989, 1994, 1998, 1999]`. The
standalone `keyframe_time_indices.npy` is also readable with the same shape,
dtype, and tail.

`RUNTIME INPUT VERIFIED`: `data/Replica/room0` currently contains exactly 2,000
files in each of `frames`, `depths`, `semantic_ids`, and `semantic_colors`, and
`traj.txt` contains 2,000 lines.

### 2.2 Sufficiency by task

| Task | Saved state sufficient? | Additional runtime input |
|---|---|---|
| RGB rendering | Yes | Renderer extension, dataset camera/GT RGB, CUDA |
| Depth rendering | Yes | Same, plus GT depth for metrics |
| Semantic rendering | Yes | `semantic_colors`, renderer, GT semantic-color image |
| Trajectory evaluation | Yes | Estimated and saved GT trajectories are present |
| Released semantic mIoU | Yes | Original per-frame GT semantic-color images are still required |
| Offline evaluation without online SLAM rerun | Yes | Dataset and evaluation environment remain required |

`VERIFIED FROM SOURCE`: the evaluator does not need optimizer state, resident
keyframe RGB-D-semantic payloads, or the Variant-B CPU archive. The NPZ is a
final evaluation state, not an online-resume checkpoint.

## 3. Relevant source entry points

| Path / function | Purpose and inputs | Outputs | Direct NPZ support / live-state assumption |
|---|---|---|---|
| `scripts/eval_novel_view.py::load_scene_data` | Opens NPZ and converts every key to a Torch tensor on `device`; only `semantic_ids` is excluded from float/gradient conversion by the caller | In-memory parameter dictionary | Direct loader exists. It restores no optimizer and no keyframe payload archive. It moves even metadata to CUDA and marks most tensors `requires_grad`, although evaluation runs under `no_grad`. |
| `scripts/eval_novel_view.py::__main__` | Loads an experiment config, dataset, `scene_path` or `<workdir>/<run_name>/params.npz`, then dispatches by `use_train_split` | `eval_train/` or `eval_nvs/` under the configured result directory | Repository-native standalone entry point. With checked-in Replica defaults it evaluates training views. |
| `utils/eval_helpers.py::eval` | Final/training-view evaluation using estimated `cam_unnorm_rots` and `cam_trans` | Per-frame metric text files, plots, optional rendered PNGs, console/W&B aggregate | Accepts an in-memory final parameter dictionary; no optimizer/keyframes required. |
| `utils/eval_helpers.py::eval_nvs` | Novel-view evaluation using dataset GT test poses and a hole-validity rule | Metrics, validity mask, plots, optional rendered PNGs | Accepts final map params, but the checked-in Replica configuration does not define a canonical NVS split. |
| `utils/eval_helpers.py::eval_online` | Evaluates a separate parameter snapshot for each online frame | Online metric files and plots | Requires `all_params[time_idx]`; the final NPZ does not contain this sequence, so it is not applicable. |
| `utils/eval_helpers.py::evaluate_ate` / `align` | Horn rigid alignment and translation-error reduction | One scalar returned to console/W&B | Uses live tensors built by `eval`; no dedicated trajectory file is produced. |
| `utils/slam_external.py::calc_psnr` | Per-channel MSE and PSNR | Tensor, later averaged | Called by `eval` and `eval_nvs`. |
| `utils/eval_helpers.py::recolor_semantic_img` / `evaluate_miou` | Quantizes rendered semantic colors to the frame GT palette and computes color IoU | Per-frame mIoU | Uses `semantic_colors`; does not use saved `semantic_ids` for the metric. |
| `utils/slam_helpers.py::transform_to_frame` | Builds estimated relative w2c from camera quaternion/translation and transforms all Gaussian centers | Camera-frame Gaussian centers | Requires the saved map and camera arrays only. |
| `utils/slam_helpers.py::transformed_params2rendervar` | RGB rasterizer arguments | RGB renderer input | Uses RGB color, rotation, opacity, and scale arrays. |
| `utils/slam_helpers.py::transformed_params2depthplussilhouette` | Depth/silhouette rasterizer arguments | Three-channel depth/silhouette renderer input | Separate rasterizer invocation from RGB. |
| `utils/slam_helpers.py::transformed_semantics2rendervar` | Semantic-color rasterizer arguments | Semantic renderer input | Separate rasterizer invocation from RGB/depth. |
| `utils/recon_helpers.py::setup_camera` | Creates CUDA rasterization settings from dimensions, K, and first-frame w2c | Renderer camera object | Black background, near/far 0.01/100. |
| `utils/common_utils.py::save_params` / `utils.convert_ply::convert` | NPZ and RGB/semantic PLY serialization | `params.npz`, `params.ply`, `seg_params.ply` | Export-only; no metric or image evaluation. |
| `utils/gs_helpers.py::eval` | Older/post-SLAM evaluator with GT per-frame cameras | Post-opt plots and aggregate logs | Different protocol; must not be used to label the saved online map as post-opt output. |

`scripts/slam.py` calls `utils.eval_helpers.eval` before adding final metadata and
calling `save_params`. The minimal output-save run replaced that call with a
no-op and then saved the final metadata. Standalone evaluation must therefore
use `scripts/eval_novel_view.py`, not rerun `scripts/slam.py`.

## 4. Saved-state loading analysis

### Existing loader

Yes: `scripts/eval_novel_view.py::load_scene_data` is the released direct NPZ
loader. `scene_path` can point at the saved full-scene NPZ. It converts NumPy
arrays back to Torch tensors and moves all keys to the selected device. The
caller keeps `semantic_ids` in its original dtype; all other keys are converted
to float and marked trainable even though the evaluator enters
`torch.no_grad()`.

The loader restores:

- all RGB/depth/semantic Gaussian render fields;
- the estimated 2,000-frame camera arrays;
- saved camera metadata and keyframe indices, although the released evaluator
  does not consume most of those metadata keys.

It does not reconstruct:

- optimizer state;
- online variables such as densification accumulators;
- resident or CPU-archived keyframe image payloads;
- per-frame historical Gaussian snapshots.

None of those is required by `eval`. The native evaluator reloads GT RGB,
depth, semantic color, intrinsics, and poses from Replica rather than consuming
`gt_w2c_all_frames` for its final ATE path. Thus the original 2,000-frame
semantic Replica dataset remains an evaluation dependency even though GT poses
are also saved.

### Loader caveats

1. Importing `utils.eval_helpers` eagerly constructs
   `LearnedPerceptualImagePatchSimilarity(...).cuda()` at module line 20. A
   load-only gate must avoid importing this module.
2. The native loader moves non-render metadata (`gt_w2c_all_frames`, keyframes,
   dimensions, and so on) to CUDA unnecessarily.
3. It uses `allow_pickle=True`, although this saved archive contains ordinary
   numeric arrays.
4. It has no schema/shape validation or staged allocation failure report.
5. It does not independently verify that the saved and physical dataset frame
   counts agree.

The smallest evaluation-only addition is therefore a thin saved-state gate
harness, not an algorithm change. In load-only mode it should inspect NPZ
headers and required small arrays on CPU without importing `eval_helpers`. In
render/evaluate modes it should transfer only renderer-required map/camera keys
to CUDA, retain metadata on CPU, instantiate the unchanged dataset, and call
the released helpers/formulas. This harness is proposed below and was not
implemented during this audit.

## 5. RGB metric protocol

The current Replica config takes native-size RGB at 680x1200. The loader reads
RGB as HWC floating values in the nominal 0--255 range, uses OpenCV linear
resize, converts to CHW, and divides by 255 in `eval`. No crop is applied
(`crop_edge=0`).

The active Replica mapping settings are `mapping.num_iters=60` and
`add_new_gaussians=True`. Therefore the special no-mapping silhouette branch is
inactive. Both rendered and GT RGB are multiplied by `GT depth > 0`; invalid
pixels become zero but remain in the full-image denominator.

| Metric | Exact released implementation |
|---|---|
| PSNR | `utils.slam_external.calc_psnr`: per-channel MSE over all HxW pixels, `20*log10(1/sqrt(MSE))`, then mean across 3 channels; unweighted mean across evaluated frames. |
| “SSIM” | `pytorch_msssim.ms_ssim` on CPU BCHW tensors, `data_range=1.0`, `size_average=True`; this is MS-SSIM, not single-scale SSIM; unweighted frame mean. |
| LPIPS | `torchmetrics.image.lpip.LearnedPerceptualImagePatchSimilarity(net_type='alex', normalize=True)`; clamped [0,1] BCHW inputs; per-frame scalar then unweighted frame mean. |

No semantic or silhouette mask is applied in the active branch beyond the valid
GT-depth mask. Background at invalid-depth locations is zero in both images.
Rendered RGB is not resized or cropped inside the evaluator. The evaluator uses
the estimated camera at each frame, not GT camera poses, for training-view
rendering.

The validated environment contains `torchmetrics 1.8.2` and
`pytorch-msssim 1.0.0`. The AlexNet checkpoint
`alexnet-owt-7be5be79.pth` is present in the Torch cache, so no missing LPIPS
weight download is currently identified.

## 6. Depth metric protocol

Replica depth PNG values are resized with nearest-neighbor interpolation and
divided by `png_depth_scale=6553.5`, yielding meters. Valid pixels are exactly
`GT depth > 0`. There is no additional clipping for metrics.

With the active mapping configuration, released `Depth L1` is:

```text
sum(abs(rendered_depth - gt_depth) * (gt_depth > 0))
----------------------------------------------------
                 count(gt_depth > 0)
```

It is a masked mean absolute error in meters, averaged again with an unweighted
mean over evaluated frames. Console/plot summaries multiply it by 100 and label
centimeters; `l1.txt` stores meters.

The separate variable and output named depth `RMSE` computes
`sqrt((rendered-gt)^2)` per pixel and then the same masked mean. It is therefore
also absolute error, not root-mean-square error, and should not be reported as
conventional depth RMSE. No normalized depth error is implemented.

For exported depth PNGs only, values are clipped to 0--6 m, normalized to
8-bit, and JET-colorized. Those visualization PNGs are not metric inputs and
are not reloadable raw depth.

## 7. Trajectory / ATE protocol

`VERIFIED FROM SOURCE`:

1. Dataset `traj.txt` matrices are loaded as c2w, normalized relative to the
   first frame, and inverted by `eval` to relative w2c.
2. Estimated poses are reconstructed from `cam_unnorm_rots[...,t]` and
   `cam_trans[...,t]`. Quaternions are normalized and are real-first
   `[w,x,y,z]`.
3. Frame 0 uses the dataset first-frame w2c. Frames 1--1999 use the estimated
   arrays. Frames with NaN GT pose are skipped after frame 0.
4. Although image metrics are sampled, GT poses are appended before the
   `eval_every` skip. Final ATE therefore uses all 2,000 corresponding frames
   when all GT poses are finite.
5. `evaluate_ate` extracts the translation columns `matrix[:3,3]` directly
   from the relative w2c matrices. It does **not** invert w2c to c2w camera
   centers.
6. `align(gt_points, est_points)` applies Horn closed-form rigid rotation and
   translation. There is no scale estimate: this is SE(3)-type rigid alignment,
   not Sim(3). It is also not merely first-frame alignment.
7. Per-frame error is Euclidean translation distance after alignment, in the
   dataset's meter scale.
8. The returned scalar is `mean(trans_error)`. Despite source labels and print
   text saying `ATE RMSE`, no square-mean-root reduction is performed.

The released evaluator reports only that mislabeled mean scalar to console and
optionally W&B. It does not save an ATE text file, true ATE RMSE, an estimated
trajectory file, or a trajectory plot. A later gate should preserve the
released value under an explicit name such as
`released_horn_aligned_mean_w2c_translation_error_m`, and may additionally
report a true RMSE from the same per-frame aligned errors as a separately
identified supplementary metric. Neither has been computed here.

## 8. Semantic / mIoU protocol

The active representation is rendered `semantic_colors`, not class logits and
not saved `semantic_ids`:

1. A third, separate Gaussian rasterizer call blends the per-Gaussian
   three-channel semantic colors.
2. GT semantic-color PNGs are loaded as RGB, resized nearest-neighbor, converted
   to CHW, and divided by 255.
3. For each evaluated frame, `recolor_semantic_img` finds the unique colors in
   that frame's GT semantic image and assigns every rendered pixel to its
   nearest GT color by Euclidean RGB distance.
4. `evaluate_miou` removes pixels whose GT color is black `[0,0,0]`.
5. It computes intersection/union independently for each unique non-black GT
   color present in that frame. Classes absent from that frame's GT palette are
   not included. A zero-union color is skipped.
6. Frame mIoU is the unweighted mean of those per-color IoUs, or zero if none
   remain. Overall mIoU is the unweighted mean of frame mIoUs.

The configured `num_semantic_classes=101` controls dataset construction but is
not used to build a fixed 101-class confusion matrix in this evaluator. There
is no explicit Replica-ID remapping table in the metric path. Saved
`semantic_ids` are not compared to GT IDs. “Absent-class handling” is therefore
per-frame palette exclusion, not a dataset-wide class policy.

The function can iterate all 2,000 frames if called with `eval_every=1`, but the
current released room0 config uses `eval_every=5`; the applicable semantic
metric protocol therefore has 401 frames, not 2,000.

The evaluator also prints/logs `miou_list[::10].mean()`. Given the normal
401-frame metric list, that secondary aggregate corresponds exactly to source
frames `{0} union {50k-1 | k=1..40}` = `0,49,99,...,1999` (41 values). The
normal `miou.txt` contains all 401 sampled frame values.

## 9. Frame-sampling audit

For `utils.eval_helpers.eval` and `eval_online`, the source condition is:

```python
if time_idx != 0 and (time_idx + 1) % eval_every != 0:
    continue
```

With `num_frames=2000` and `eval_every=5`, the exact image/depth/semantic metric
set is:

```text
{0} union {5k - 1 | k = 1,...,400}
= 0, 4, 9, 14, ..., 1989, 1994, 1999
```

- Count: 401 frames.
- Frame 0: included.
- Frame 1999: included.
- It is not every fifth zero-based index (`0,5,10,...`).
- Final ATE: all 2,000 finite-pose frames, independently of this render
  cadence.

For `eval_nvs`, dataset frame 0 is treated as the first training frame and is
skipped. `test_time_idx=time_idx-1` then receives the same cadence condition.
For a hypothetical 2,000-entry dataset this would evaluate dataset frames
`1,5,10,...,1995` (test indices `0,4,9,...,1994`), 400 views. This is not the
current room0 training-view gate.

The repository paper audit records training-view results but does not establish
that the paper used this exact 401-frame cadence. Paper/released sampling
equivalence is therefore `UNKNOWN`.

## 10. Export behavior

For `eval(..., save_frames=True)` the native directories and names are:

| Output | Path under evaluation root | Format / count for full gate |
|---|---|---|
| Rendered RGB | `rendered_rgb/gs_####.png` | PNG via OpenCV after multiplying by 255, 401 |
| Rendered depth visualization | `rendered_depth/gs_####.png` | JET-colorized 0--6 m PNG, 401 |
| Rendered semantic | `rendered_seg/gs_####.png` | Recolored semantic RGB PNG, 401 |
| Combined GT/render diagnostics | `plots/####.png` | Matplotlib PNG, 401 |
| Per-frame metrics | `{psnr,rmse,l1,ssim,lpips,miou}.txt` | Six text files, 401 values each |
| Aggregate plot | `metrics.png` | One PNG |

Thus the checked-in standalone call with semantic loading and `save_frames=True`
creates 1,604 per-frame PNGs plus `metrics.png` and metric text files. `####`
is the original source frame index, including `0000`, `0004`, and `1999`.
The RGB and semantic save paths do not explicitly cast their float NumPy arrays
to `uint8` before `cv2.imwrite`; this export behavior should be checked in E2.

The code can export all 2,000 frames if `eval_every` is changed to 1, which
would create 8,000 per-frame PNGs with semantics enabled. That is not the
current released room0 sampling protocol and is not proposed for E4.

There are no standalone native GT RGB, raw GT depth, or GT semantic image
exports in `eval`; GT references appear only inside the combined plot. There is
no separate RGB error map. The combined plot contains a depth-L1 error panel
and silhouette panel. There is no trajectory plot or trajectory export.

`save_frames=False` suppresses the three rendered-image directories, but with
`wandb_run=None` the evaluator still saves one combined plot per evaluated
frame. The released API does not provide a clean independent “metrics only, no
plots” flag. A bounded gate may use a thin harness to disable only
`plot_rgbd_silhouette`; a paper-comparison full gate should either preserve the
released behavior or explicitly record that output-only control as a harness
change.

`eval_nvs` uses `rendered_rgb/rgb_####.png`,
`rendered_depth/depth_####.png`, and
`rendered_semantic/seg_####.png`. Its GT image writes are commented out.

## 11. Paper / released-code comparability

The repository's prior paper audit records room0 paper targets for PSNR, SSIM,
LPIPS, mIoU, and ATE RMSE, plus dataset-average Depth L1 and runtime metrics.
The local paper PDF named in that audit is not present in the current worktree,
so this audit used the existing provenance record and did not browse the web.

| Metric | Released code status | Paper-comparison status |
|---|---|---|
| PSNR | Official released train-view evaluator | Candidate comparison, but map stage and exact paper masking/sampling remain ambiguous |
| LPIPS-Alex | Official released train-view evaluator | Candidate comparison with the same stage/protocol caveat |
| “SSIM” | Released code actually computes MS-SSIM | Not directly protocol-identical to a paper label of SSIM without further evidence |
| Depth L1 | Released masked MAE in meters, displayed cm | Candidate for the paper's Depth L1; paper room0 target is not recorded, and stage/sampling remain caveats |
| Depth “RMSE” | Algebraically duplicates L1 | Repository-only/mislabeled; not conventional RMSE |
| ATE “RMSE” | Horn-aligned mean of relative-w2c translation-column errors | Not directly equivalent to true ATE RMSE; must be disclosed |
| Semantic mIoU | Released color-palette quantization protocol | Candidate paper comparison, but stage and evaluator-protocol equivalence are not established |
| mIoU stride-10 | Secondary source aggregate | Repository-only unless paper provenance is established |
| NVS metrics | Available in source | No canonical current Replica room0 NVS config/split; not this gate |

The released code officially exposes PSNR, MS-SSIM, LPIPS, Depth L1, the
mislabeled depth RMSE, color-based mIoU, and the mislabeled ATE scalar. It does
not compute a true ATE RMSE or ATE mean/RMSE pair under conventional camera
center semantics.

## 12. Expected compute and memory behavior

- Full training-view gate: 401 sampled renders for RGB, depth/silhouette, and
  semantic metrics; ATE traverses 2,000 poses.
- Renderer calls per sampled frame: three separate calls--depth/silhouette,
  RGB, and semantic. They are not produced by one rasterizer invocation.
- Total rasterizer calls: 1,203 for the 401-frame semantic evaluation.
- The loop is frame-by-frame; it does not preload all 2,000 RGB-D-semantic
  images. It does retain the small GT pose list.
- The native loader moves the complete 4.96-million-Gaussian map and all NPZ
  metadata to CUDA. Each frame additionally creates transformed centers,
  homogeneous-coordinate intermediates, renderer variables, and rasterizer
  buffers. Semantic palette quantization materializes a pixel-by-palette
  distance matrix.
- The saved NPZ's uncompressed arrays total approximately 322 MB, but this is
  not a VRAM peak estimate. Rasterizer workspace and transient transformed
  arrays can dominate. The 16 GB RTX 5080 therefore has a real but unquantified
  evaluation-time OOM risk.
- The source is naturally chunked frame-by-frame, but it does not release and
  reload the map between frames. A bounded single-frame render is required
  before the 401-frame gate.
- Runtime cannot be estimated reliably from the online SLAM timing because
  evaluator rasterization, CPU MS-SSIM, LPIPS, semantic nearest-palette work,
  and PNG/Matplotlib export were not timed in the saved-state run. Runtime:
  `UNKNOWN` until bounded Gate E2/E3 measurement.

No full rendered-image export should be enabled until the bounded gates verify
VRAM and output behavior.

## 13. Missing dependencies and inputs

Read-only package/spec inspection of the validated
`/home/robot/miniconda3/envs/sgs_slam_5080` environment found:

- `diff_gaussian_rasterization`: installed;
- `torchmetrics 1.8.2`: installed;
- `pytorch-msssim 1.0.0`: installed;
- OpenCV `4.9.0.80`: installed;
- Matplotlib `3.10.9`: installed;
- `plyfile 1.1.3`: installed;
- cached AlexNet weights: present.

No missing Python dependency is identified statically. This does not replace a
future import/load gate. Required external input is the existing semantic
Replica `room0` dataset with all 2,000 RGB, depth, semantic-ID,
semantic-color, and pose entries.

Open questions/blockers before a paper claim:

1. exact paper sampling and mask protocol;
2. whether paper train-view/semantic values are online-map or post-opt values;
3. whether paper “SSIM” means single-scale SSIM or released MS-SSIM;
4. whether paper ATE uses camera centers and true RMSE rather than the released
   translation-column mean;
5. evaluation peak VRAM and wall time for 4.96 million Gaussians;
6. whether the native loader's eager all-key CUDA transfer should be retained
   for strict source reproduction or replaced by a documented evaluation-only
   loader for safety.

## 14. Recommended staged evaluation gates

### Gate E1 -- saved-state load only

- Frames: none.
- Work: reproducible CPU-only harness validation of NPZ schema/readability,
  full-array finiteness in bounded sequential loads, artifact hash, and the
  already observed 2,000-entry camera/dataset alignment; instantiate no
  renderer and import no eager CUDA evaluator.
- Metrics/exports: none.
- PASS: required keys/shapes/dtypes are valid, all required small metadata is
  readable, dataset counts align, and an explicit CUDA-transfer byte budget is
  recorded.
- FAIL: unreadable/missing required state, frame mismatch, or schema conflict.

### Gate E2 -- one-frame render sanity

- Frame: 0 only.
- Work: load required map fields once; run exactly three released renderer calls
  for RGB, depth/silhouette, and semantic color.
- Metrics: none.
- Outputs: one rendered RGB PNG, one raw depth NPY plus visualization PNG, one
  semantic PNG, corresponding GT references, and memory/timing log in a new
  evidence directory.
- PASS: finite outputs at 680x1200, nonempty silhouette, no OOM/CUDA error, and
  bounded memory recorded.
- FAIL: load/render error, non-finite output, empty/invalid render, or OOM.

### Gate E3 -- bounded released-metric check

- Frames: source range 0--9 with released `eval_every=5`, giving exact metric
  frames `[0,4,9]` and ten-frame ATE input.
- Metrics: released PSNR, MS-SSIM, LPIPS, Depth L1, released depth “RMSE”,
  semantic mIoU, and explicitly labeled released ATE scalar.
- Outputs: per-frame metric arrays and bounded diagnostics; no broad export.
- PASS: three finite values per image/depth/semantic metric, finite trajectory
  output, deterministic frame IDs, and acceptable VRAM/RSS.
- FAIL: dependency/model-load error, formula path divergence, NaN/Inf, OOM, or
  unexpected output overwrite.

### Gate E4 -- full saved-state evaluation

- Render metric frames: exact 401-frame set
  `{0} union {5k-1 | k=1..400}`.
- Trajectory frames: all 2,000 finite-pose frames.
- Metrics: unchanged released metrics, with labels corrected in the report but
  not in source; optional supplementary true ATE RMSE must be separately named.
- Outputs: dedicated, non-overwriting evaluation evidence directory. Decide at
  authorization time whether to preserve all 1,604 native PNGs or apply a
  documented output-only suppression.
- PASS: complete finite metric arrays with expected counts, preserved stdout
  ATE, artifact manifest, memory/timing evidence, and no source/state mutation.
- FAIL: OOM, NaN/Inf, sample-count mismatch, missing output, dependency failure,
  protocol drift, or saved-state mutation. Preserve partial evidence; no
  automatic retry.

Post-SLAM optimization and NVS are separate gates and are not prerequisites for
E1--E4.

## 15. Exact next command and harness design

The next authorized action should be Gate E1 only. Proposed future harness:

```text
scripts/phase4_vb001_eval_export_gate.py
```

Proposed exact command (not executed):

```bash
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python \
  scripts/phase4_vb001_eval_export_gate.py \
  --mode load-only \
  --config configs/replica/slam.py \
  --scene-path experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz \
  --evidence-dir results/runtime_artifacts/phase4_vb001_eval_export_gate_e1_load_only
```

Minimal harness contract:

1. `load-only` must not import `utils.eval_helpers`, initialize CUDA, render, or
   calculate metrics.
2. It must validate exact keys/shapes/dtypes and physical dataset counts, using
   NPZ header inspection for large arrays.
3. Later `render-only` and `bounded-eval` modes must load renderer-required
   numeric fields to the configured device, leave metadata on CPU, use released
   camera/renderer helpers, and write only to new gate-specific directories.
4. Metric mode must call the unchanged released formulas and record exact frame
   IDs, dependency versions, source/config/harness hashes, units, masks, and
   aggregation.
5. It must never write to or overwrite the saved full-scene state directory.

No source file needs modification to perform the existing full standalone
evaluation: a derived config can set `scene_path`, a dedicated `workdir` and
`run_name`, and `use_wandb=False`, then invoke
`scripts/eval_novel_view.py`. The proposed harness is still recommended for E1
and bounded E2/E3 because the native script eagerly imports CUDA LPIPS, transfers
all keys to CUDA, always enables rendered-frame export, and has no arbitrary
bounded-frame CLI.

## 16. Audit conclusion

`AUDIT_STATUS: PASS_EVALUATION_EXPORT_AUDIT`

The saved full-scene state is sufficient for repository-native offline
training-view RGB, depth, semantic, and trajectory evaluation without rerunning
online SLAM. A direct NPZ loader exists. Evaluation remains gated because the
native loader/evaluator eagerly uses CUDA, full evaluation entails 1,203
rasterizer calls plus substantial export, peak VRAM is unknown, and several
released metric labels differ from their actual formulas or paper terminology.

**No evaluation was executed during this audit. No metric was computed, no
SLAM was rerun, no render was produced, and no CUDA-heavy workload was run.**

## 17. Gate E1 result

`RUNTIME VERIFIED` on 2026-10-11: the separately authorized saved-state
load-only gate completed with `PASS_EVAL_E1_LOAD_ONLY`.

- Evidence:
  `results/runtime_artifacts/phase4_vb001_eval_e1_load_only/`.
- Gaussian/camera/GT/keyframe counts: 4,956,467 / 2,000 / 2,000 / 402.
- CUDA transfer was limited to the six render map arrays plus
  `cam_unnorm_rots` and `cam_trans`; metadata remained on CPU.
- Peak CUDA allocated/reserved: 297,834,496 / 306,184,192 bytes
  (1.793% / 1.843% of 16,609,378,304 bytes).
- After release, PyTorch allocated/reserved memory returned to 0 / 0 bytes;
  post-run `nvidia-smi` showed the RTX 5080 healthy and idle.
- `utils.eval_helpers` and `diff_gaussian_rasterization` were not imported.
  No renderer, metric, image export, or SLAM path ran.

The first harness invocation stopped before CUDA transfer because
`np.ascontiguousarray` promoted scalar `org_width` from shape `()` to `(1,)`.
That harness-only failure is preserved under
`attempt_001_harness_failure/`; scalar-shape preservation was corrected and the
successful E1 evidence occupies the canonical filenames. No saved state or
repository source was modified.

## 18. Post-audit staged gate results

The audit itself remained read-only as stated above. Subsequent gates were
separately authorized and executed on 2026-10-11:

- E1 selective load-only: `PASS_EVAL_E1_LOAD_ONLY`.
- E2 frame-0 RGB/depth/semantic render:
  `PASS_EVAL_E2_SINGLE_FRAME_RENDER`.
- E3 released metrics on `[0,4,9,14,19]`:
  `PASS_EVAL_E3_BOUNDED_SUBSET`.
- E4 full released evaluation: `PASS_EVAL_E4_FULL_RELEASED`.

The first E2 invocation failed before state loading or CUDA work with
`FAIL_EVAL_E2_HARNESS_IMPORT_PATH`; adding the repository root to the temporary
harness import path resolved it. This was not a renderer or saved-state failure.

## 19. E4 released evaluation result

`RUNTIME VERIFIED`: E4 evaluated exactly 401 image/depth/semantic frames using
`{0} union {5k-1 | k=1..400}` and all 2,000 finite trajectory frames. No frame
was skipped, no image set was exported, and online SLAM was not rerun.

| Metric | Result |
|---|---:|
| PSNR | 33.313067 dB |
| MS-SSIM | 0.979470 |
| LPIPS-Alex | 0.067555 |
| Depth L1 | 0.00495158 m / 0.495158 cm |
| Semantic-color mIoU | 0.916585 |
| Released Horn-aligned mean w2c translation error | 0.00274075 m |
| Supplementary true RMSE | 0.00339827 m |

The released Horn mean remains explicitly distinct from true RMSE. Evaluation
runtime was 74.4107 s; peak GPU allocated/reserved was 1,846,789,120 /
2,057,306,112 bytes. The canonical result is
`docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md`; runtime evidence is under
`results/runtime_artifacts/phase4_vb001_eval_e4_full_released/`.

## 20. Updated next task

The saved-state Evaluation / Export Gate is complete through E4. The next task
is a **Paper / Baseline Comparison Audit**, not another evaluation or SLAM run.
It must establish paper-table comparability before any reproduction or
superiority claim. PHASE4-VB002 remains future work.
