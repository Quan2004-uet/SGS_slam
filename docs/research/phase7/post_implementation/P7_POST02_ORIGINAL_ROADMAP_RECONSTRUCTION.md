# P7-POST-02 — Rekonstrukcija roadmap ban đầu

## Phạm vi và nhãn bằng chứng

Đây là tái dựng từ hồ sơ Phase 7 đã lưu; không thay thế hồ sơ lịch sử. `ORIGINAL_PLAN` chỉ ghi điều được tài liệu hóa; `INFERRED` là diễn giải hợp lý nhưng chưa có quyết định riêng; `UNKNOWN` không có tài liệu nguồn đầy đủ.

| Nhãn | Nội dung | Bằng chứng |
|---|---|---|
| `ORIGINAL_PLAN` | Giới hạn tăng trưởng map do pixel-driven Gaussian insertion trong khi kế thừa CPU Keyframe Offload của Phase 4; giữ tracking/mapping baseline và kiểm tra bounded admission trước khi tiến tới scene đầy đủ. | `PHASE7_GATE1A_IMPLEMENTATION_REPORT.md`; `PHASE7_GATE1B_RUN_CONTRACT.md`; Gate 1A source locations ở report audit. |
| `ORIGINAL_PLAN` | Event Cap và Global Cap; chọn candidate xác định dựa trên depth residual/silhouette; không bật clone/split densification khi BCGM hoạt động. | Gate 1A report và `utils/bcgm.py:41-109`. |
| `INFERRED` | Động cơ là kiểm soát chi phí/resource tăng theo Gaussian map mà không thay đổi objective tracking. | Hợp với Gate 1A/roadmap; không gán cho một design memo gốc chưa tìm thấy. |
| `UNKNOWN` | Không tìm thấy standalone Phase 7 Gate 0 design report trong worktree hiện tại. `PASS_PHASE7_GATE0_DESIGN_READY` là trạng thái carry-forward trong management và Gate 1A/1B. Không suy diễn thêm tiêu chí bị thiếu. | `PHASE7_GATE4_CONTRIBUTION_AND_LIMITATIONS.md`; Gate 4 manifest. |
| `IMPLEMENTED` | BCGM là bounded admission tại pixel insertion, kết hợp CPU Keyframe Offload; caps 9,000/event và 4,500,000 tổng map ở admission-time. | `scripts/slam.py:437-508`; configs; run traces. |
| `VERIFIED` | Room0 Gate 1B, Gate 2, Gate 3, Gate 4; room1 fast-track R1 Gates 0–2. Global Cap thực sự được kích hoạt trong full scene; artifact manifests/checkpoints/arrays verified. | Gate 4 reports/manifests; room1 Gate 2 closure and 1,629-entry manifest; this POST audit. |
| `DEFERRED` | Room1 visualization A–H deferred by research decision; separate P7-B not started. | Room1 final handoff; roadmap; no implementation record. |
| `NOT_SUPPORTED_BY_EVIDENCE` | Statistically significant speedup, fully matched quality retention, causal attribution of ATE/depth regressions to caps, and independent P7-B approval. | One run/seed; unmatched timer boundaries and methods; no cap ablation. |

## Gate evolution

- Room0: Gate 0 design carry-forward; Gate 1A CPU implementation; Gate 1B three-arm 100-frame validation; Gate 2 BCGM-on 500 frames; Gate 3 BCGM-on 2,000 frames and full evidence/visualization; Gate 4 administrative evidence closure.
- Room1 fast-track: R1-Gate 0 preflight/baseline audit, R1-Gate 1 one 2,000-frame BCGM-on run, R1-Gate 2 offline metrics/evidence closure. The 100/500-frame runs were deliberately omitted after room0 validation.
- Gate 4 is evidence administration, not a new algorithm/experiment. P7-B remains a research decision, not an approved roadmap.

## Expected versus observed

The bounded insertion and resource accounting goals were implemented and runtime exercised. Room1 shows lower Gaussian count and allocator peaks than historical Phase 4, but several quality measures are worse: LPIPS +10.21%, Depth L1 +26.32%, ATE Mean +29.93%, ATE RMSE +28.62% on the recorded room1 comparison. Given timing-boundary differences and one run per condition, resource changes are observations, not a causal speedup claim. The original approximate 10% quality tolerance is exceeded for these measures.

Primary evidence: `PHASE7_GATE1A_IMPLEMENTATION_REPORT.md`, Gate 1B/2/3/4 reports, `room1/PHASE7_R1_*`, `P7_POST01_ARTIFACT_PRESERVATION_INVENTORY.md`, and `P7_POST02_PHASE4_PHASE6_PHASE7_COMPARISON.md`.
