# P7-POST-02 — Audit kiến trúc và đường đi mã nguồn

**Source identities:** `scripts/slam.py` SHA256 `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999`; `utils/bcgm.py` `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400`; room1 config `3c0d43c4e6ba4a3260815daa9f2d64f468802ab49f60686135df40b22f61bd10`. Các hash là bằng chứng cho snapshot đã lưu; source/config không được sửa trong audit.

## Source-evidence matrix

| Thành phần | Vị trí chính xác | Kết luận |
|---|---|---|
| Tracking loss/render | `scripts/slam.py:265-348`, frame loop `838-910` | Renderer tạo RGB và depth/silhouette; semantic pass tùy cờ. Tracking dùng gradient cho camera pose, không cho Gaussian (`get_loss`, 271-283). Pose estimate lưu qua camera quaternion/translation; `do_ba` mapping branch chỉ dùng camera gradient nếu bật, không được bật trong config nghiên cứu. |
| Pixel insertion candidates | `scripts/slam.py:437-463` | Candidate mask kế thừa silhouette absence hoặc depth foreground residual; BCGM intersect positive GT depth và gọi bounded selector. |
| Candidate selection | `utils/bcgm.py:50-109` | `nonzero` cho chỉ số pixel tăng dần; allowance là min(candidate count, Event Cap, remaining Global Cap). Khi giới hạn, depth-priority trước; điểm depth error giảm dần, silhouette score `1-silhouette` giảm dần; stable sort giữ thứ tự pixel khi hòa. |
| Payload construction | `scripts/slam.py:465-508`; helper pointcloud tại `utils/slam_helpers.py` | Mask đã lọc được dùng trước pointcloud allocation (`select_before_allocation`); trường RGB/depth/semantic ID/color cùng pixel mask nên giữ alignment. Trace ghi before, valid, admitted, rejected, cap flags và after. |
| CPU Keyframe Offload | `scripts/slam.py:545-573`, mapping `1000-1065` | CPU-authoritative payload fields là color/depth/semantic_id/semantic_color. Khi chọn keyframe để mapping, payload được synchronous copy sang device rồi local staging được giải phóng. Pose metadata, map parameters/optimizer, current frame và renderer work buffers vẫn nằm trên GPU. Đây không phải toàn bộ SLAM chạy CPU. |
| Keyframe selection | `utils/keyframe_selection.py:40-109`; caller `scripts/slam.py:967-989` | Random 1,600 valid depth samples, backproject/project để xếp overlap, random permutation trong tập có overlap. Semantic-mIoU filtering ở lines 94-105 bị comment; không phải behavior đang chạy. |
| Mapping optimization | `scripts/slam.py:991-1075`; `get_loss` 333-348 | Cấu hình room1 60 iterations/map; chọn random current/keyframe, cập nhật Gaussian optimizer và semantic colors qua loss. Đây là inherited online mapper, không phải BCGM optimizer. |
| Pruning / clone-split | `scripts/slam.py:1038-1049`; `utils/slam_external.py:179-200,203-235` | Pruning có thể xóa opacity thấp/điểm lớn sau insertion. Clone/split là đường riêng; Gate 3/R1 config giữ tắt và `validate_bcgm_config` bác bỏ densification khi BCGM on. |
| Effective config | `configs/replica/phase7_r1_full_room1_on_0_1999_r01.py:1-10` và imported room0 Gate3 config | Room1 chỉ thay run identity/scene label trong config kế thừa; report run config xác nhận 2,000 frames, seed0, 1200x680, tracking40/mapping60, map cadence1, keyframe cadence5, window24, semantic on, CPU offload, BCGM caps 9000/4.5m, BAM off. |
| Phase 6 BAM | `/home/robot/research/SGS_slam/docs/research/phase6_bam/PHASE6_DEEP_TECHNICAL_AUDIT.md`; Phase6 `utils/mapping_budget.py` in the Phase6 worktree, not Phase7 | BAM adaptively allocates mapping iterations using novelty/budget policy. Phase7 room1 uses fixed mapping iterations and does not import/enable BAM. Phase6 numbers are method-confounded, not a BCGM-only comparison. |

## Interpretive boundary

BCGM bounds admitted point count, not all insertion computation. Candidate masks/depth errors are generated first; on constrained events the selector materializes candidate indices and stable-sorts score vectors. `get_pointcloud` then allocates only selected candidates. Thus point construction/map append is bounded, while candidate discovery and selection/sorting remain proportional to the image candidate set. No separate profiling isolates this overhead in full scene.

The cap is an admission rule, not a permanent map-size invariant. Mapping pruning occurs after per-frame insertion trace; therefore final count can differ from final logged `after` (room1: 4,498,991 after last insertion, checkpoint 4,498,964). This is consistent with pruning, not evidence of over-admission.

The Phase 7 contribution is the bounded deterministic admission policy and its integration/telemetry. CPU payload offload is inherited from Phase 4; tracking objective, keyframe overlap policy and mapping optimizer are not claimed as new BCGM contributions. Phase6 BAM changes mapping budget/scheduling and is absent from Phase7.
