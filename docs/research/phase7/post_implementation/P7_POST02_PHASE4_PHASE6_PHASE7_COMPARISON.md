# P7-POST-02 — So sánh định lượng Phase 4 / 6 / 7

Nguồn: room1 `PHASE7_R1_ROOM0_ROOM1_COMPARISON.md`, `PHASE7_R1_FULL_SCENE_METRIC_TABLE.md`; room0 `PHASE7_GATE4_FINAL_METRIC_TABLE.md`; raw summaries and evaluator arrays referenced by corresponding manifests. Mỗi Phase7 scene chỉ một run/seed; các delta là mô tả.

## A. Phase 4 room1 versus Phase 7 room1

| Metric (tốt hơn) | Phase 4 | Phase 7 R1 | Δ P7−P4 | Δ tương đối |
|---|---:|---:|---:|---:|
| Runtime s (lower) | 18,472.333261692 | 14,564.629470040 | -3,907.703791652 | -21.1544%* |
| E2E FPS (higher) | .1082700259 | .137318975681 | +.029048949781 | +26.8301%* |
| Tracking FPS (higher) | .2555125699 | .339028112990 | +.083515543090 | +32.6855%* |
| Mapping FPS (higher) | .1931999681 | .248121108168 | +.054921140068 | +28.4271%* |
| CUDA allocated B (lower) | 8,066,530,816 | 5,628,716,544 | -2,437,814,272 | -30.2213% |
| CUDA reserved B (lower) | 10,626,269,184 | 7,761,559,552 | -2,864,709,632 | -26.9588% |
| NVML sampled peak MiB (lower) | 11,341 | 10,355 | -986 | -8.6941% |
| Final Gaussians (context) | 6,663,167 | 4,498,964 | -2,164,203 | -32.4801% |
| PSNR dB (higher) | 33.936226847 | 33.326330803 | -.609896044 | n/a for dB |
| MS-SSIM (higher) | .969905490 | .968103481 | -.001802009 | -.1858% |
| LPIPS (lower) | .097438466 | .107388632 | +.009950166 | +10.2117% worse |
| Depth L1 m (lower) | .004363715 | .005512088 | +.001148374 | +26.3164% worse |
| mIoU (higher) | .923663420 | .919729327 | -.003934092 | -.4259% |
| ATE Mean m (lower) | .004262121 | .005537752 | +.001275632 | +29.9295% worse |
| True ATE RMSE m (lower) | .004411848 | .005674387 | +.001262539 | +28.6170% worse |

`*` Runtime rows are not a matched timing claim: Phase4 evaluated/saved separately (offline evaluation +370.505805s), while R1 wrapper wall includes its in-run evaluation/save boundary. Tracking/Mapping stage FPS are not whole-run FPS and insertion overhead is outside mapping stage timing. Memory measures are different scopes: CUDA allocated/reserved are PyTorch allocator peaks, NVML is sampled device-wide memory. Do not combine or equate them.

## B. Phase 6 room1 versus Phase 7 room1

| Metric | Phase 6 BAM | Phase 7 BCGM | Δ P7−P6 | Meaning |
|---|---:|---:|---:|---|
| Runtime s | 16,075.75 | 14,564.629470 | -1,511.120530 (-9.4000%) | different mapping policy/harness; descriptive only |
| E2E FPS | .124410992 | .137318976 | +.012907984 (+10.3753%) | descriptive only |
| CUDA allocated B | 10,223,109,632 | 5,628,716,544 | -4,594,393,088 (-44.9412%) | allocator evidence; distinct run/method |
| CUDA reserved B | 12,513,705,984 | 7,761,559,552 | -4,752,146,432 (-37.9755%) | same caveat |
| NVML peak | not measured | 10,355 MiB | not estimable | no matched evidence |
| Gaussians | 6,682,135 | 4,498,964 | -2,183,171 (-32.6718%) | map-size observation |
| PSNR dB | 34.096186264 | 33.326330803 | -.769855461 | lower P7 |
| MS-SSIM | .971436200 | .968103481 | -.003332719 (-.3431%) | lower P7 |
| LPIPS | .091352461 | .107388632 | +.016036171 (+17.5542%) | worse P7 |
| Depth L1 m | .004393708 | .005512088 | +.001118380 (+25.4541%) | worse P7 |
| mIoU | .926535421 | .919729327 | -.006806093 (-.7346%) | lower P7 |
| ATE Mean m | .004655331 | .005537752 | +.000882421 (+18.9551%) | worse P7 |
| ATE RMSE m | .004802019 | .005674387 | +.000872368 (+18.1667%) | worse P7 |

Phase6 includes BAM/adaptive mapping; Phase7 does not. This is not an isolated BCGM effect. Phase6 tracking/mapping stage FPS and NVML were not established as matched quantities.

## C. Phase 7 room0 versus room1

Same method family, different Replica scenes. The table gives the exact values (rounded to displayed precision); deltas are room1−room0 and purely descriptive.

| Metric | Room0 | Room1 | Δ R1−R0 |
|---|---:|---:|---:|
| Runtime (s) | 14,165.030217954 | 14,564.629470040 | +399.599252086 (+2.8210%) |
| E2E FPS | .141192780335 | .137318975681 | -.003873804654 (-2.7436%) |
| Tracking FPS | .347069322852 | .339028112990 | -.008041209862 (-2.3169%) |
| Mapping FPS | .256792587139 | .248121108168 | -.008671478970 (-3.3768%) |
| CUDA allocated (B) | 5,442,630,656 | 5,628,716,544 | +186,085,888 (+3.4190%) |
| CUDA reserved (B) | 6,784,286,720 | 7,761,559,552 | +977,272,832 (+14.405%) |
| NVML sampled peak (MiB) | 7,684 | 10,355 | +2,671 (+34.761%) |
| Final Gaussians | 4,499,583 | 4,498,964 | -619 (-.0138%) |
| PSNR (dB) | 32.444045252 | 33.326330803 | +.882285551 |
| MS-SSIM | .975780536 | .968103481 | -.007677055 (-.7868%) |
| LPIPS | .076533444 | .107388632 | +.030855188 (+40.316%, worse) |
| Depth L1 (m) | .005907558010 | .005512088386 | -.000395469624 (-6.6943%, better) |
| mIoU | .913442026 | .919729327 | +.006287301 (+.6883%) |
| ATE Mean (m) | .002489759244 | .005537752230 | +.003047992986 (+122.42%, worse) |
| True ATE RMSE (m) | .003249278229 | .005674386822 | +.002425108593 (+74.64%, worse) |
| Valid / admitted / rejected | 8,698,235 / 4,363,012 / 4,335,223 | 33,408,344 / 3,892,851 / 29,515,493 | event totals differ by scene |
| Event / Global saturation flags | 104 / 789 | 294 / 1,251 | flags are trace definitions; R1 global cap was strictly admission-binding in 1,250 events |

Different scene complexity and geometry prevent causal comparison. Room0/room1 flags are derived from `event_saturated` / `global_saturated`; combined `budget_saturated` is not a separate cap count.

## Metric semantics and statistical boundary

PSNR/MS-SSIM/mIoU higher is better; LPIPS, Depth L1 and ATE errors lower is better. Six evaluator arrays cover 401 sampled IDs, not all 2,000; ATE uses all 2,000 poses and Horn rigid SE(3) on W2C translation columns, no scale fitting. `rmse.txt` duplicates Depth L1, not conventional depth RMSE. Console label “ATE RMSE” reports ATE Mean. One seed/run and no cap ablation mean no confidence interval, significance or causal cap-to-quality inference.
