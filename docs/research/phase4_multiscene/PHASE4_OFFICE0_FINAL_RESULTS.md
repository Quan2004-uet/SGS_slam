# PHASE 4 Variant B — Replica Office0 Final Results

**Trạng thái thực nghiệm:** `CLOSED_EVALUATED`  
**Trạng thái offline:** `PASS_OFFLINE_EVALUATION`  
**Visualization 3D tùy chọn:** `DEFERRED_OPTIONAL`  
**Run ID:** `p4_vb001_office0_full_0_1999_r01`

## Danh tính và provenance

| Hạng mục | Giá trị đã xác minh |
|---|---|
| Dataset / phạm vi | Replica `office0`, frame 0–1999 (2.000 frame) |
| Frozen source commit | `68f9060f7ff4d8d141be1d5f71339401327edd06` (detached worktree) |
| `scripts/slam.py` SHA256 | `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3` |
| Effective online config SHA256 | `484a1548fea309225a66a77a3edc4ae6f40c63a250466d7ee2a5e78d801e941f` |
| E4 config SHA256 | `6271a15518a0d7de9246508a1d0ce9147758d47d16a144ab26c0112ab4e34ca8` |
| Seed | 0 |
| Checkpoint SHA256 | `6d0f180d7677a38c29295ae9ffc10d745f726aac700f40338543a062a9bf7390` |
| Checkpoint validation | `PASS_CHECKPOINT_VALIDATION`; NPZ CRC `PASS`; 2.000 pose; 6.088.334 Gaussian; 402 keyframe |
| Online run | Exit code 0; 2.000/2.000 frame đã xác thực; failure classification `NONE` |

SHA nguồn, danh tính run/config và trạng thái online được lưu trong run metadata cùng checkpoint validation. SHA256 checkpoint đã được tính lại trong lần lưu trữ cuối và khớp với bằng chứng online lẫn supplementary.

## Metric chất lượng cuối cùng

Metric RGB, depth và semantic dùng tập E4 training-view gốc: 401 view tại 1200×680, frame IDs `{0} ∪ {5k-1 | k=1..400}`. Giá trị là aggregate chính xác trong evidence; các mảng per-frame và SHA256 nguồn vẫn được lưu.

| Metric | Kết quả | Phạm vi / diễn giải |
|---|---:|---|
| PSNR | 38.69793345862791 dB | 401 E4 training view |
| MS-SSIM | 0.9832896119044011 | SSIM đa tỷ lệ, không phải SSIM đơn tỷ lệ |
| LPIPS-Alex | 0.08275568896807042 | 401 E4 training view |
| Depth L1 | 0.0036909948602467406 m | 401 E4 training view; mask depth theo E4 |
| Standard Depth RMSE | 0.01903626183679585 m (1.903626183679585 cm) | Render số supplementary; 401 RMSE từng frame, sau đó lấy trung bình không trọng số |
| Aligned ATE mean | 0.005481421752582262 m (0.5481421752582263 cm) | 2.000 pose; Horn rigid alignment, không hiệu chỉnh scale |
| True aligned ATE RMSE | 0.006053878949032237 m (0.6053878949032236 cm) | RMSE trên 2.000 sai số translation sau alignment |
| Semantic-color mIoU | 0.920670209062726 | 401 view; đối sánh có hỗ trợ bảng màu GT, IoU theo màu GT khác đen hiện diện mỗi view, rồi lấy trung bình không trọng số |

`rmse.txt` của E4 giống hệt `l1.txt`, nên các giá trị đó là Depth L1, không phải standard RMSE. Standard Depth RMSE được tính riêng theo `sqrt(mean((predicted_depth_m - gt_depth_m)^2))` trên các pixel có GT depth lớn hơn 0 cho từng frame. 401 giá trị từng frame được lấy trung bình không trọng số theo số pixel hợp lệ. mIoU được báo cáo là metric màu semantic có hỗ trợ bảng màu ground truth, không phải class-ID mIoU. Metric ảnh là MS-SSIM, không phải SSIM đơn tỷ lệ.

## Runtime và bộ nhớ

| Đo lường | Kết quả | Phạm vi |
|---|---:|---|
| Wall-clock tiến trình online | 17,693.695785642994 s | Toàn bộ online runner process |
| End-to-end SLAM FPS | 0.11303460985368803 | 2.000 frame / process wall time |
| Tracking trung bình / throughput nghịch đảo | 3.6919138610363005 s/frame / 0.27086222421216116 FPS | Trung bình từ log online và nghịch đảo |
| Mapping trung bình / throughput nghịch đảo | 5.0167394688129425 s/frame / 0.1993326554461516 FPS | Trung bình từ log online và nghịch đảo |
| Online frame-loop FPS | `NOT_AVAILABLE_FROM_FROZEN_SOURCE` | Frozen source không đo riêng timer này |
| PyTorch peak allocated / reserved | 7,003,875,328 / 8,847,884,288 bytes | Worker CUDA allocator trong lời gọi `rgbd_slam` đến khi trả về/đồng bộ |
| NVML sampled peak | 9,623 MiB; 17,175 mẫu | Mức dùng sampled toàn GPU; khác với PyTorch allocator |
| Peak supplementary depth render | 1,738,032,640 allocated / 4,242,538,496 reserved bytes | Process supplementary riêng, không tính vào online peak |

Thời gian serialization checkpoint cuối không được instrument riêng. Các số liệu này không phải phép so sánh có kiểm soát với scene khác và không chứng minh hiệu ứng nhân quả giữa các scene.

## Integrity và giao thức evaluation

Evidence cuối có trạng thái `PASS_FINAL_INTEGRITY_VALIDATION`, với toàn bộ 15 kiểm tra bắt buộc đúng. Manifest E4 gốc gồm 1.612 đường dẫn; kiểm tra lại đúng tập đường dẫn đã ghi nhận cho kết quả 1.612 khớp, không thiếu file và không thay đổi file. Các file supplementary bị loại khỏi manifest E4 gốc theo thiết kế. Checkpoint hiện tại khớp SHA256 mong đợi và hash trước/sau supplementary render; NPZ CRC và schema đều đạt. Evidence ghi nhận 401 E4 metric view, 2.000 sai số trajectory hữu hạn và 401 bản ghi standard Depth RMSE hữu hạn. Exit code và stdout/stderr của E4 không được lưu, vẫn là `NOT_RECORDED`; điều này tách biệt với exit code 0 đã xác minh của online run. Không có CUDA OOM nào được ghi nhận trong evidence online hoặc supplementary.

## Vị trí artifact

- Báo cáo cuối: `docs/research/phase4_multiscene/PHASE4_OFFICE0_FINAL_RESULTS.md`
- Checkpoint và model: `/home/robot/research/SGS_slam_phase4_multiscene/experiments/Replica/p4_vb001_office0_full_0_1999_r01/`
- Online evidence: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/p4_vb001_office0_full_0_1999_r01/`
- E4 gốc: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/offline_eval/p4_vb001_office0_full_0_1999_r01_offline_eval/eval_train/`
- Supplementary và integrity evidence: `/home/robot/research/SGS_slam_phase4_multiscene/results/runtime_artifacts/phase4_multiscene/offline_eval/p4_vb001_office0_full_0_1999_r01_offline_eval/supplementary/`
- Integrity: `supplementary/final_integrity_validation.json`
- Metric cuối: `supplementary/evaluation_metrics.json`
- Trạng thái cuối: `supplementary/evaluation_status_final.json`
- Manifest E4 gốc: `supplementary/original_e4_files_manifest.json`
- Depth RMSE supplementary: `supplementary/depth_rmse_supplementary/`
- Trajectory: `supplementary/trajectory_metrics.json`

## Giới hạn và phạm vi dự án

- Exit code và stdout/stderr của E4 không có trong artifact gốc.
- Visualization 3D tùy chọn chưa chạy và vẫn là `DEFERRED_OPTIONAL`.
- Semantic-color mIoU sử dụng đối sánh màu có hỗ trợ bảng màu GT; không được diễn giải thành class-ID mIoU.
- Đây là một lần chạy scene riêng; khác biệt giữa các scene chỉ mang tính mô tả, không phải bằng chứng A/B có kiểm soát.
- Đóng Office0 không hoàn tất extension Replica tám scene. Các scene Phase 4 còn lại là `office1`, `office2`, `office3`, `office4`.

Không chạy SLAM, E4, supplementary evaluation hay visualization trong lần lưu trữ này. Checkpoint và file E4 gốc vẫn tại vị trí cũ. Không commit, push hay upload.
