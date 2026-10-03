# Evaluation Protocol Audit

The canonical online evaluator is `utils/eval_helpers.py::eval`. Post-opt calls
`utils/gs_helpers.py::eval`, which is similar but not artifact-equivalent. The
paper's metric names must not be assumed to describe either function exactly.

## Implemented online metrics

| Metric label | Function/path | Actual computation | Inputs and aggregation | Paper mapping |
|---|---|---|---|---|
| ATE “RMSE” | `evaluate_ate` -> Horn `align` | Mean Euclidean aligned translation error, `mean(trans_error)`; not square-root mean squared error | GT and estimated camera centers over selected frames; returned in meters, displayed x100 cm | Paper reports ATE RMSE; protocol mismatch must be disclosed |
| PSNR | `calc_psnr` inside `eval` | RGB is multiplied by the valid-depth mask; per-channel MSE -> `10 log10(1/MSE)`, then channel mean | Rendered vs GT RGB with invalid-depth pixels zeroed; final mean across evaluated frames | Paper PSNR |
| “SSIM” | `pytorch_msssim.ms_ssim` | Multi-scale SSIM, not single-scale SSIM | Valid-depth-masked rendered/GT RGB on CPU; mean across frames | Paper labels SSIM; exact protocol is ambiguous |
| LPIPS | `torchmetrics.image.lpip.LearnedPerceptualImagePatchSimilarity(net_type='alex', normalize=True)` | AlexNet LPIPS on clamped, valid-depth-masked [0,1] RGB | Per frame then mean | Paper LPIPS |
| Depth L1 | `eval` | Mean `abs(rendered_depth-GT)` over GT depth > 0 | Meters internally, summary plot/print uses cm | Paper Depth L1 |
| Depth “RMSE” | `eval` | `sqrt((error)^2)` per pixel, then mean over valid GT pixels; algebraically absolute error | Same mask/aggregation as Depth L1 | Not conventional RMSE; normally duplicates L1 |
| Semantic mIoU | `recolor_semantic_img` -> `evaluate_miou` | Snap each rendered RGB semantic vector to nearest color among colors present in that GT frame; per-color IoU; unweighted mean | Black GT pixels ignored; frame mIoUs averaged | Paper mIoU, but palette/protocol must be preserved |

All implementation claims above are `VERIFIED FROM SOURCE`.

## Sampling and masks

- Online final eval is invoked with `eval_every=5`; frame 0 and the evaluator's
  cadence-selected frames are aggregated. `VERIFIED FROM CONFIG`; `VERIFIED FROM SOURCE`
- Valid depth is `GT depth > 0`.
- With the canonical mapping config (`mapping_iters=60`, addition enabled), the
  special silhouette-weighted branch for zero-mapping/no-addition is not used.
  RGB metrics still multiply both images by the valid-GT-depth mask; invalid
  pixels become zero before metric computation. `VERIFIED FROM SOURCE`
- Semantic mIoU does not directly compare the rendered trainable RGB vectors to
  `semantic_id`. It quantizes them using the frame's GT semantic-color palette,
  then compares colors. `VERIFIED FROM SOURCE`
- The evaluator also calculates an mIoU stride-10 aggregate for W&B logging, but
  `miou.txt` contains the normal selected-frame list. `VERIFIED FROM SOURCE`

## Outputs and units

`utils.eval_helpers.eval` saves one value per evaluated frame in `psnr.txt`,
`rmse.txt`, `l1.txt`, `ssim.txt`, `lpips.txt`, and, when semantic loading is on,
`miou.txt`. Depth arrays are stored in meters; printed/plot summaries multiply by
100 for centimeters. mIoU is a fraction in code; paper tables show percent.

ATE is included in the plot title and console/W&B summary but is not saved to a
dedicated text file. Phase 3 must preserve stdout/W&B logs or add non-algorithmic
measurement instrumentation in a clearly separate reproduction harness.

## Stage mapping

- **Tracking/trajectory:** online pose arrays evaluated by the online evaluator.
  This is the correct released-source source of ATE.
- **Online rendering/depth/semantic:** automatic final call in `scripts/slam.py`.
- **Reloaded training views:** `scripts/eval_novel_view.py` defaults to `eval`,
  writing `eval_train` for the checked-in Replica config.
- **Novel views:** the same script calls `eval_nvs` only for
  `use_train_split=False`; canonical Replica NVS setup is not supplied.
- **Post-opt:** `scripts/post_slam_opt.py` evaluates with GT cameras and the older
  `utils.gs_helpers.eval`; aggregates are printed/logged and metric text saves are
  commented. This is a separate protocol/output contract.

## Comparison rules

When reporting a reproduced metric, include dataset, scene, config, commit,
environment, seed, online/post-opt stage, evaluator function, frame cadence, units,
and any derived config diff. For paper comparison explicitly flag:

1. released code ATE mean vs paper label ATE RMSE;
2. code MS-SSIM vs paper label SSIM;
3. code depth “RMSE” is actually mean absolute error;
4. semantic palette snapping and black-pixel exclusion;
5. paper training-view/semantic result stage is not explicitly identified.
