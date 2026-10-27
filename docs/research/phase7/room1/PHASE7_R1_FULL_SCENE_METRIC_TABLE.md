# R1 Replica room1 — Full-Scene Metric Table

Status: PASS_WITH_LIMITATIONS. Run p7_bcgm_r1_full_room1_on_0_1999_r01; frames 0–1999. Evaluator utils/eval_helpers.py SHA256 e94366ca256ec2b51b5d0264a5daba2a895cc0375d7b91e976e4ea0e9e28194e; its content matches Phase 4 and Phase 6 evaluator files.

## Phase 7 room1

| Metric | Value | Definition |
|---|---:|---|
| PSNR | 33.326330803279 dB | Mean of 401 saved values |
| MS-SSIM | 0.968103481053 | ssim.txt; source calls ms_ssim |
| LPIPS | 0.107388632154 | AlexNet LPIPS |
| Depth L1 | 0.005512088386 m | masked absolute depth error |
| Semantic mIoU | 0.919729327463 | evaluator semantic recoloring and class IoU |
| ATE Mean | 0.005537752230202 m | mean aligned residual norm, 2,000 poses |
| True ATE RMSE | 0.005674386822122 m | sqrt(mean(residual norm squared)) |
| ATE Median | 0.005576422438910 m | 2,000 poses |
| ATE Max | 0.013747675506648 m | 2,000 poses |
| Process runtime | 14564.629470040 s | wrapper wall time |
| E2E FPS | 0.137318975681 | 2,000 / process runtime |
| Tracking FPS | 0.339028112990 | reciprocal stage time |
| Mapping FPS | 0.248121108168 | reciprocal stage time |
| CUDA allocated peak | 5,628,716,544 B | PyTorch allocator |
| CUDA reserved peak | 7,761,559,552 B | PyTorch allocator |
| NVML peak | 10,355 MiB | device-wide sampled; 14,330 valid samples |
| Final Gaussian count | 4,498,964 | params.npz means3D; PLY counts agree |

Console prints Final Average ATE RMSE: 0.55 cm, but evaluator evaluate_ate returns the mean aligned translation error despite that label. It matches ATE Mean (0.553775 cm) at console precision; true offline ATE RMSE is 0.567439 cm.

R1 rmse.txt and l1.txt are elementwise identical (401 entries, max absolute difference zero). Evaluator sqrt-squares each pixel residual then averages, reproducing L1. Do not report conventional Depth RMSE. Metrics cover sampled IDs 0,4,9,...,1999 (401 of 2,000), not every view. Arithmetic means above are independently calculated from all saved values; console output agrees at shown precision. Single run and seed; no statistical significance.

BCGM: 33,408,344 candidates; 3,892,851 admitted; 29,515,493 rejected; Event Cap activations 294; Global Cap activations 1251; maximum per event 9,000. NVML device-wide memory is distinct from process CUDA allocator peaks.
