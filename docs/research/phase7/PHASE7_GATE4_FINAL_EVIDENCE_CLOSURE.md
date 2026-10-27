# Phase 7 Gate 4 — Final Evidence Closure

**Phân loại:** `PHASE7_GATE4_FINAL_EVIDENCE_CLOSURE` (Gate hành chính/nghiệm thu nghiên cứu được chỉ định sau Gate 3; không thay đổi các Gate ID trước đó).
**Kết luận:** `FINAL_EVIDENCE_CLOSURE_COMPLETE` — có các giới hạn lịch sử được ghi rõ bên dưới.
**Session:** `SESSION_005` — `ACTIVE`; chờ researcher review, không đóng tự động.
**Run được nghiệm thu:** `p7_bcgm_g3_room0_on_0_1999_r01`, Replica room0, frame 0–1999.

## Phạm vi và phương pháp

Đây là closure trên artifacts đã lưu. Kiểm tra JSON/CSV/JSONL/log, băm SHA256, kiểm tra ZIP CRC, đọc sáu mảng evaluator, đối chiếu mã evaluator và hồ sơ Gate trước. Không chạy SLAM, CUDA, rendering, optimization; không sửa source/config/checkpoint/dataset hoặc artifact Phase 4/6. Các con số dưới đây là `RUNTIME VERIFIED` từ run artifacts, trừ những mục được gắn `DOCUMENTED / LIMITATION`.

Git identity quan sát: branch `phase7-bcgm`, HEAD `68f9060f7ff4d8d141be1d5f71339401327edd06`. Working tree có các thay đổi Phase 7 được giữ lại; không reset/clean/stash/commit/push.

## Gate status audit

| Gate | Trạng thái closure | Nguồn và giới hạn |
|---|---|---|
| Gate 0 | `PASS_PHASE7_GATE0_DESIGN_READY` (được ghi nhận) | Được dẫn trong Gate 1A, Gate 1B handoff và project records. Không tìm thấy báo cáo Gate 0 độc lập trong Phase 7 worktree; trạng thái là documented carry-forward, không tái tạo bằng chứng gốc. |
| Gate 1A | `PASS_PHASE7_GATE1A_CPU_READY` | `PHASE7_GATE1A_IMPLEMENTATION_REPORT.md`; 9 CPU tests theo báo cáo, không phải full-scene runtime. |
| Gate 1B | `PASS_WITH_LIMITATIONS` | `PHASE7_GATE1B_FINAL_VALIDATION_REPORT.md` và evidence manifest; ba nhánh Replica room0 0–99. Giới hạn: một run/arm, không có ý nghĩa thống kê; Global Cap không kích hoạt; thiếu pre-run hashes toàn bộ artifact lịch sử. |
| Gate 2 | `PASS_GATE2_WITH_COMPARISON_LIMITATIONS` | Final validation, metric comparison, NVML recovery và Gate 2 manifest; 500 frame. Không có matched Phase 4 quality/NVML/trajectory baseline; Global Cap chưa kích hoạt ở Gate 2. |
| Gate 3 | `COMPLETE_WITH_LIMITATIONS` | Run summary/log/checkpoint/evaluation arrays, insertion records, offline ATE và advanced visualization manifest. Global Cap runtime được xác minh; chất lượng là training-view evaluation; Phase 4 resource comparison không matched; Phase 6 chỉ là qualitative reference nơi có artifact tương ứng. |
| Gate 4 | `FINAL_EVIDENCE_CLOSURE_COMPLETE` | Tài liệu này, metric table, contribution report, evidence manifest và final handoff. Đây là evidence closure, không phải Gate khoa học mới. |

## Gate 3 execution và checkpoint

`run_summary.json` xác nhận `status=COMPLETE`, `process_exit_code=0`, `execution_validation_pass=true`, frame range `[0,1999]`, 2.000 frames, 2.000 saved/estimated poses và 1.999 insertion events. `params.npz` ZIP CRC trả về `None` (không có member hỏng); summary xác nhận 4.499.583 Gaussian, Gaussian fields aligned, numeric finite, NumPy load thành công. Checkpoint SHA256: `a02dd4b4ecfd9c982866cf4a4c38c187ef22c75049b8328e18eea20608944917`.

Six evaluator arrays trong `experiments/Replica/<run_id>/eval/` mỗi mảng có 401 giá trị finite. Aggregate là arithmetic mean trên các giá trị đã lưu. `ssim.txt` là MS-SSIM. `rmse.txt` byte-identical với `l1.txt`, do đó kết quả depth là L1 chứ không phải conventional Depth RMSE. Đây là training-view evaluation theo evaluator hiện hành, không phải novel-view/generalization test.

Offline ATE JSON và Markdown khớp: 2.000 estimated/GT poses finite; Horn rigid SE(3) alignment áp dụng lên translation columns của W2C, không scale fitting, không subset. ATE Mean `0.0024897592444028008 m`; ATE RMSE `0.0032492782294292577 m`; median `0.0015416674157756505 m`; max `0.009684450577739244 m`. Console line `Final Average ATE RMSE: 0.25 cm` thực tế in 100 × arithmetic mean của per-pose Euclidean translation error; label RMSE gây hiểu nhầm. ATE RMSE ở đây là metric offline được tính riêng.

## BCGM admission và cap

Parser độc lập đọc 1.999 `BCGM_INSERTION` JSON records trong `stdout_stderr.log`, frame 1–1999, không thiếu/trùng. Mỗi record đạt:

- `valid_candidates = admitted + rejected`;
- `after = before + admitted`;
- `admitted = min(valid_candidates, 9000, max(0, 4500000 - before))`;
- `admitted <= 9000`, cap fields đúng 9.000/4.500.000;
- `event_saturated` và `global_saturated` khớp điều kiện source; không dùng `budget_saturated` thay cho global flag.

Tổng: valid `8.698.235`, admitted `4.363.012`, rejected `4.335.223`; Event Cap activations `104`; Global Cap activations `789`; max admitted/event `9.000`. Run summary ghi `bcgm_admission_valid=true`, `global_cap_runtime_verified=true`. Admission cap giới hạn số điểm thêm tại thời điểm chèn; pruning sau đó có thể giảm map. Vì vậy final map count có thể thấp hơn giới hạn/các transition gần cuối mà không phải cap failure. Không bật gradient clone/split densification; tracking objective không bị sửa; CPU Keyframe Offload được giữ.

## Chất lượng, runtime và memory

Giá trị aggregate chính xác được trình bày trong `PHASE7_GATE4_FINAL_METRIC_TABLE.md`. Runtime `14.165,030217954074 s`, E2E `0,1411927803348428 FPS`; Tracking `0,347069322852072 FPS`; Mapping `0,2567925871385077 FPS`. E2E FPS tính bằng frame count/process wall; stage FPS là reciprocal của stage average frame time, không thay thế whole-system throughput.

CUDA peak allocated `5.442.630.656 B` và reserved `6.784.286.720 B` là process PyTorch allocator peaks trong scope được summary mô tả. NVML CSV có 13.941 valid samples, không invalid/error; device-wide sampled peak `7.684 MiB` lúc `2026-10-27T07:48:11+00:00`, GPU 0; max sampled utilization `99%`. NVML là 1 Hz sampled device-wide observation, không phải unsampled absolute/process peak và không được đồng nhất với CUDA allocated/reserved.

## Phase 4/6 historical comparison

Phase 4 output-save reference được audit trong `PHASE7_GATE3_BASELINE_REUSE_AUDIT.md`: runtime `14.173,475159 s`, CUDA allocated/reserved `5.817.509.888 / 7.189.037.056 B`, final count `4.956.467`. Đây là bối cảnh tài nguyên/map size với `COMPARABLE_WITH_LIMITATIONS`: harness/timer/evaluation/save boundaries khác; không claim matched speedup hay causal BCGM benefit. Phase 4 full-scene RGB/depth/semantic/ATE/NVML quality metrics không đo (`NOT_MEASURED`). Phase 6 chỉ dùng cho visualization tương ứng; không tìm thấy metric Phase 6 cùng scene/config/protocol đủ điều kiện để so định lượng, do đó quantitative Phase 6 là `NOT_COMPARABLE` hoặc `NOT_MEASURED`.

## Advanced visualization

Validation report ghi nhận đủ tám families A–H, 113 PNG, 6 NPY, 24 JSON và 1 TXT trong advanced visualization tree (144 files); frame observed cameras `0,499,999,1499,1999`, ba cột Phase 4/6/7, 2.000 estimated poses trong trajectory metadata. File-level manifest và camera/semantic metadata có trong thư mục advanced visualization. Các giới hạn: V3A frustum clipping; modality conventions có khác biệt được gắn nhãn; fixed semantic-ID center plots là sampled diagnostics, không phải pixel-wise predictions; qualitative trajectory plot không phải ATE plot; learned semantic colors khác categorical IDs.

`LAPTOP_TRANSFER: USER_REPORTED_COMPLETE`. Không có laptop-side hashes đối chiếu trong phiên này nên integrity của bản copy ngoài máy chủ chưa được xác minh độc lập.

## Source, config và provenance

Run summary identity khớp file hiện tại: `scripts/slam.py` SHA256 `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999`; `utils/bcgm.py` `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400`; Gate 3 config `1bb57b3dd38e98c39a24310ceaee656a8415ce901e61808bb19cea8422c4ff22`; runner `1d97bb2d1dec0056a7d5a3e081d1ca3ee649a5f13ffd68b8563647300622a7a6`; Gate 1B worker `9a449ef10506ebbe6ccd0616d29aa02e9183554b333d605c9440ec07e09ad40b`. These match summary/preflight recorded identities. Frozen Phase 4 source SHA `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3` is recorded by Gate 3 baseline audit. No algorithm/config changes are part of Gate 4.

Gate 4 machine manifest records exact paths, sizes and SHA256 for run evidence, checkpoint/PLY, evaluator arrays, source/config, visualization payloads and reports. It excludes itself to avoid a self-referential checksum. The manifest's SHA256 is supplied in the final response, not embedded in any file it hashes.

## Current state and stop boundary

- Gate 3: `COMPLETE_WITH_LIMITATIONS`.
- Gate 4: `FINAL_EVIDENCE_CLOSURE_COMPLETE`.
- Phase 7: `RESEARCH_COMPLETED_WITH_LIMITATIONS`.
- Gate 3 full-scene execution is complete; no new work was run during closure.
- Session `SESSION_005` remains `ACTIVE` pending researcher review.
- Current Codex environment cannot query the NVIDIA driver (`nvidia-smi` communication failure); this is an environment observation only. Saved run summary records host RTX 5080/CUDA 12.8 preflight and completed execution. Current `df` reports `26.47 GiB` available, filesystem 98% used; this closure generated only small documentation/manifest files.
- No commit, push, upload, checkpoint deletion, SLAM, CUDA or rendering occurred.

**Next action:** researcher reviews the thesis-ready metric table and limitations, confirms the laptop copy independently if required, then explicitly instructs session closure or the next research objective.
