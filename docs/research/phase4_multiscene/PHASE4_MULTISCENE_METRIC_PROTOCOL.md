# PHASE 4 Replica đa cảnh — Metric protocol

Protocol này tách online Phase 4 Variant B run khỏi saved-state evaluation. Cần kiểm tra formula, sampling, mask, aggregation và phạm vi timer trong source; không dựa riêng vào tên metric. Evaluation cần GPU/renderer nên không chạy trong Gate 0.

## 1. Source và execution path

**VERIFIED FROM SOURCE/DOCUMENTATION:** E4 đọc saved checkpoint qua `scripts/eval_novel_view.py`, chọn training split và gọi `utils/eval_helpers.py::eval`. Room0 E4 record trong `docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md` và `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/run_metadata.json`: evaluation HEAD `63adf3aed8ae2201a46d11cec473672f9e91fd0e`; harness `/tmp/phase4_vb001_eval_e4_full_released.py`; SHA256 `8c31b131e1b294fb0a089589c4f934e1c9912a4969573169f2abe333c847d5e6`.

`eval` tính training-view metrics; `eval_nvs` là NVS/test split riêng; `eval_online` cần snapshot tham số theo từng frame. `scripts/post_slam_opt.py` và `utils/gs_helpers.py` là post-SLAM regime, không trộn với kết quả online Phase 4.

Entry point released trong `scripts/eval_novel_view.py` nhận experiment config theo positional argument, đọc `scene_path` nếu có và dispatch tới `eval` hoặc `eval_nvs` theo `use_train_split`. Dạng lệnh source hỗ trợ:

```bash
/home/robot/miniconda3/envs/sgs_slam_5080/bin/python \
  scripts/eval_novel_view.py <experiment-config.py>
```

Room0 E4 dùng harness `/tmp/phase4_vb001_eval_e4_full_released.py` với SHA256 `8c31b131e1b294fb0a089589c4f934e1c9912a4969573169f2abe333c847d5e6`, nhưng tài liệu kết quả không lưu literal command invocation. Vì vậy **exact command đã chạy cho E4 là UNKNOWN**; không tự dựng cờ CLI không có trong source. Với scene mới cần config/harness có `scene_path`, output/evidence path riêng và phải lưu literal command. Gate 0 không chạy evaluation.

## 2. Metric được hỗ trợ và giới hạn

| Metric | Mức hỗ trợ | Định nghĩa cần báo cáo | Source/evidence |
|---|---|---|---|
| PSNR | **SUPPORTED; E4 VERIFIED room0** | `utils.slam_external.calc_psnr`; RGB chia 255; mask GT depth > 0; trung bình số học các frame. Nhánh mask silhouette phụ thuộc điều kiện mapping trong evaluator. | `utils/eval_helpers.py::eval`, `utils/slam_external.py::calc_psnr`, E4 `aggregate_metrics.json`. |
| SSIM | **SUPPORTED dưới dạng MS-SSIM** | Source gọi `pytorch_msssim.ms_ssim(..., data_range=1.0, size_average=True)`. Output E4 có thể ghi “SSIM”; báo cáo chuẩn hóa thành **MS-SSIM**. | `utils/eval_helpers.py::eval`; E4 result. |
| LPIPS | **SUPPORTED, AlexNet** | TorchMetrics AlexNet với `normalize=True`; input clamp [0,1]; lấy mean theo frame. Ghi package/checkpoint/version trong metadata. | `utils/eval_helpers.py`; E4 result/metadata. |
| Depth L1 | **SUPPORTED** | PNG depth Replica chia 6553,5 thành mét; valid mask `GT depth > 0`; mean absolute error trên pixel hợp lệ; sau đó mean không trọng số theo frame. Label “Depth RMSE” trong output không làm thay đổi formula L1. | `basedataset.py`, `utils/eval_helpers.py::eval`, `configs/data/replica.yaml`. |
| ATE Mean | **SUPPORTED trong helper released** | Ước lượng và GT relative-w2c translation được Horn rigid alignment (rotation + translation, không scale); lấy mean Euclidean translation error. | `utils/eval_helpers.py::evaluate_ate`, `align`; E4 `trajectory_metrics.json`. |
| ATE RMSE | **Metric bổ sung, E4 VERIFIED** | `sqrt(mean(error²))` trên cùng vector lỗi đã alignment; tách riêng khỏi scalar released. Chỉ dùng nếu lưu/khôi phục đúng per-frame error vector. | E4 `trajectory_metrics.json` và report. |
| mIoU | **SUPPORTED, có giới hạn** | Rendered continuous `semantic_colors` được đổi sang màu gần nhất trong palette GT của frame; loại GT màu đen; tính mean IoU các màu lớp hiện diện rồi mean theo frame. GT palette-assisted; không so trực tiếp `semantic_ids` với class ID. | `recolor_semantic_img`, `evaluate_miou`, `eval` trong `utils/eval_helpers.py`. |
| Runtime | **SUPPORTED nếu nêu rõ scope** | Ghi process wall và online-loop wall riêng; room0 output-save `total_online_runtime_seconds=14173.475...`; serialization 9,392 s. | Room0 `timing_summary.json`, run report. |
| FPS | **Tính được từ runtime** | Overall online FPS = số frame hoàn tất / online-loop wall. Room0: 2.000 / 14.173,475... = 0,14110865 FPS. Tracking/mapping FPS là scope riêng. | Room0 `timing_summary.json`. |
| Peak PyTorch allocated/reserved | **SUPPORTED bởi harness** | Peak của PyTorch caching allocator (`max_memory_allocated`, `max_memory_reserved`); ghi reset/read point, device, byte và phạm vi process. Đây không phải device-wide VRAM. | Room0 `memory_summary.json`. |
| Peak NVML/device-wide | **NOT VERIFIED / NOT MEASURED cho room0** | Chỉ báo khi NVML/driver thu thập được, kèm device, process/device scope và sampling interval. Nếu không, ghi `NOT_MEASURED`; không thay bằng peak PyTorch. | Room0 output-save `memory_summary.json`, E4 metadata. |

## 3. Sampling và aggregation

Room0 E4 lấy đúng 401 training views:

```text
{0} ∪ {5k − 1 | k=1…400}
= 0, 4, 9, 14, …, 1989, 1994, 1999
```

Không bỏ qua sample nào. RGB/depth/semantic tính theo frame rồi lấy arithmetic mean không trọng số; trajectory dùng đủ 2.000 pose. Kế hoạch áp dụng cùng 401 view IDs, 2.000 pose, resolution, intrinsics, mask và aggregation cho cả 8 scene. Nếu thiếu sample/pose thì đánh dấu evaluation INVALID và ghi nguyên nhân; không đổi frame list âm thầm.

Báo cáo metric từng scene trước khi tính tổng hợp. Macro mean giữa 8 scene có thể trình bày riêng; gộp pixel hoặc frame thành một pooled metric là aggregation khác và phải khai báo rõ từ trước. Lưu per-frame vectors, valid-pixel counts, metric implementation/version, seed, source/config/harness SHA, dataset identity và output checksum.

## 4. Runtime, FPS và memory

Mỗi scene ghi riêng:

1. `process_wall_seconds`: từ process start đến exit; nêu rõ có bao gồm initialization/serialization hay không.
2. `online_loop_wall_seconds`: phạm vi vòng lặp frame tương ứng với room0 `total_online_runtime_seconds`.
3. `serialization_seconds` và `evaluation_wall_seconds`.
4. `fps_online = completed_frames / online_loop_wall_seconds`; chỉ gọi full-scene FPS nếu đủ 2.000 frame.
5. PyTorch allocated/reserved peak với device, reset/read point, byte và process scope.
6. NVML peak riêng nếu đo được; kèm sample interval và device-wide/process-level scope. Nếu không đo được, ghi `NOT_MEASURED`.
7. RAM RSS/HWM, system/cgroup available memory, swap và CPU archive bytes nếu có.

Không gộp sync-heavy profiling time với E4 hoặc online wall chưa instrument. Nếu dùng instrumentation bổ sung thì áp dụng cùng cấu hình cho tất cả scene và báo cáo thành phép đo riêng.

## 5. Mẫu báo cáo theo scene

```text
Dataset/scene: Replica/<scene>, 2.000 frame, 1200×680
Stage: online Phase 4 Variant B / saved-state E4
Source SHA + branch/tag:
Config path + effective snapshot SHA256:
Harness path + SHA256:
Seed: 0
Command:
Environment: Python, PyTorch, CUDA runtime, driver, compiler, renderer revision
GPU model/VRAM; PyTorch allocated/reserved peak; NVML peak hoặc NOT_MEASURED
Process wall; online-loop wall; serialization; evaluation wall; FPS scope
Frame IDs: 401 E4 samples; skipped IDs
Trajectory: 2.000 pose; alignment; ATE mean và true RMSE bổ sung
PSNR / MS-SSIM / LPIPS-Alex / Depth L1 m / semantic-color GT-palette mIoU
Valid depth pixels và per-frame metric vectors:
Output/evaluation/visualization directories:
Manifest/checksum; completion status; limitations:
```

## 6. Không được suy diễn

- NVS cần split/config riêng; sự tồn tại của `eval_nvs` không chứng minh Phase 4 E4 đã chạy NVS.
- `eval_online` cần các snapshot online, không thể suy ra từ final checkpoint đơn lẻ.
- Không trộn kết quả `post_slam_opt.py` với online Phase 4.
- Không gọi semantic-color mIoU là categorical accuracy của `semantic_ids`.
- Không gọi MS-SSIM là single-scale SSIM.
- Không gọi released trajectory mean là RMSE.
- Không gọi PyTorch allocator peak là NVML/device-wide peak.
- Không tự điền metric/runtime/FPS/VRAM bị thiếu.

## 7. Source pointers

- `scripts/eval_novel_view.py` — load NPZ, dataset, dispatch train/NVS.
- `utils/eval_helpers.py::eval`, `eval_nvs`, `eval_online` — evaluation stage.
- `utils/eval_helpers.py::evaluate_ate`, `align`, `recolor_semantic_img`, `evaluate_miou` — trajectory/semantic formula.
- `utils/slam_external.py::calc_psnr` — PSNR.
- `datasets/gradslam_datasets/basedataset.py` — preprocessing depth/image/pose.
- `configs/data/replica.yaml` — camera và PNG depth scale.
- `docs/experiments/PHASE4_VB001_EVALUATION_RESULT.md` — room0 E4 protocol và metric.
- `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/` — E4 runtime evidence.
- `results/runtime_artifacts/phase4_vb001_minimal_output_save_full_0_1999/` — online timing/memory evidence.

## Bổ sung Gate 1 instrumentation readiness (2026-10-21)

- Runner `tools/phase4_multiscene/run_room1_gate1.py` dự kiến thu wall-clock toàn process, process exit code, số frame-log match (chỉ là chỉ báo log, cần hậu kiểm artifact để xác nhận frame hoàn tất), stdout/stderr và mẫu NVML mỗi giây (`memory.used`, `memory.total`, utilization). Đây là peak device-wide lấy từ sample, có thể bỏ lỡ đỉnh giữa hai mẫu; ghi rõ phương pháp và khoảng lấy mẫu.
- GPU telemetry hiện không thể thu trong Codex context vì `nvidia-smi` lỗi. SSH GPU report (RTX 5080, 810 MiB used) là báo cáo context khác, không thay thế telemetry run.
- `torch.cuda.max_memory_allocated()` và `max_memory_reserved()` chưa được ghi bởi baseline runner/source tại đây. Không được tuyên bố hai số allocator peak nếu chưa có instrumentation đã kiểm chứng; thêm instrumentation vào baseline source cần được đánh giá/phê duyệt riêng.
- Renderer dependency Python import thành công, nhưng kernel call chưa được kiểm chứng vì `torch.cuda.is_available()` False. Do đó Gate 1 chưa đủ điều kiện đo bất kỳ metric GPU nào. Không có metric mới được tạo trong Gate 0.
- Config snapshot/hash: `configs/replica/phase4_vb001_room1_gate1_0_49_r01.py` SHA256 `95f84b03a8ce434cf028fb15bc937800bfd4040a27486a89d4582110da57e761`; source `scripts/slam.py` SHA256 `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3`.

### Renderer và telemetry — xác minh cập nhật

- **RUNTIME VERIFIED:** PyTorch CUDA available (elevated Codex context): torch `2.7.1+cu128`, CUDA runtime `12.8`, one device NVIDIA GeForce RTX 5080. `nvidia-smi`: 16.303 MiB total, 14.997 MiB free, 810 MiB used, utilization 0%.
- **RUNTIME VERIFIED:** Synthetic one-Gaussian 16×16 smoke invoked `diff_gaussian_rasterization.GaussianRasterizer`; CUDA synchronized; finite `(3,16,16)` result and one visible Gaussian. This verifies the installed rasterizer kernel path at tiny scale only.
- Runner preflight PASS in that same elevated context. Runner NVML sampler samples device-wide used/total VRAM and GPU utilization at 1 Hz; report peak sampled usage, not instantaneous allocator peak. PyTorch allocated/reserved peaks are not instrumented and remain `NOT_MEASURED`.
- The non-elevated sandbox context still reports CUDA unavailable. The Gate 1 run must stay in a context matching the elevated diagnostic; runner refuses execution if CUDA returns false.

**Làm rõ:** Gate 1 runner gọi nguyên `scripts/slam.py`. `rgbd_slam` gọi `utils.eval_helpers.eval` với `eval_every=5` sau online frame loop dù W&B tắt; final save theo code path mặc định xảy ra sau evaluation. Do đó metric/artifact inline do nguồn sinh cần được phân biệt với saved-state evaluation hậu kiểm; nếu inline evaluation thất bại, `params.npz` có thể chưa được ghi. Không coi W&B suppression là evaluation suppression.
