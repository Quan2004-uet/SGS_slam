# Phase 7 Final GitHub / Hugging Face Archival Closure

**Ngày ghi nhận:** 2026-10-28 (Asia/Tokyo)<br>
**Workstream:** `PHASE7-FINAL-ARCHIVAL-CLOSURE`, `SESSION_008`<br>
**Repository:** `/home/robot/research/SGS_slam_phase7_bcgm`, branch `phase7-bcgm`<br>
**Phase 7-A:** `RESEARCH_COMPLETED_WITH_LIMITATIONS`

## 1. Tóm tắt

Room0 và room1 đã hoàn tất full-scene 2.000 frames, evaluation và kiểm tra bằng chứng. P7-POST-01 selective archival và P7-POST-02 technical/scientific audit đã hoàn tất. GitHub archival có hai commit và remote HEAD hiện được xác minh ở `bd98f25f15f724d2d4a1414e16b7369007703332`. Bản sao Hugging Face được ghi nhận đã qua validation 3.425 file theo dữ liệu kiểm chứng do researcher cung cấp; metadata Hugging Face không truy cập được để xác minh độc lập lại trong phiên này (API trả 401, CLI gặp DNS failure). Các giới hạn kiểm chứng này được giữ tách biệt.

Không có SLAM/GPU workload, evaluation rerun, rendering, artifact mutation hay Hugging Face upload trong closure này.

## 2. Trạng thái nghiên cứu Phase 7-A

| Workstream | Kết quả |
|---|---|
| Room0 Replica | Full-scene 0–1999 hoàn tất; Gate 0–4 closure `RESEARCH_COMPLETED_WITH_LIMITATIONS` |
| Room1 Replica | R1-Gate 0 PASS, R1-Gate 1 COMPLETE, R1-Gate 2 `PASS_WITH_LIMITATIONS` |
| P7-POST-01 | Selective Git archival đã commit và hiện có trên remote branch |
| P7-POST-02 | Architecture audit, comparisons, trade-off analysis và handoff hoàn tất |
| Phase 7-B | Chưa được phê duyệt hoặc triển khai |

BCGM admission caps là 9.000 candidate Gaussian mỗi insertion event và 4.500.000 Gaussian tại thời điểm admission. Kết quả room1 cho thấy resource reductions so với historical Phase 4 reference cùng lúc với suy giảm LPIPS, Depth L1, ATE Mean và true ATE RMSE. Đây là quan sát single-run; không chứng minh statistical significance hoặc quan hệ nhân quả.

## 3. GitHub archival

- Repository: [`Quan2004-uet/SGS_slam`](https://github.com/Quan2004-uet/SGS_slam).
- Branch: `phase7-bcgm`.
- Commit `40902595b60e235f983b2ebcca5983fc7ddd55eb`: `research(phase7): archive BCGM implementation and evidence index` (selective 74-path allowlist; không chứa checkpoints/datasets/runtime artifacts).
- Commit `bd98f25f15f724d2d4a1414e16b7369007703332`: `docs(phase7): archive post-implementation audit and final handoff`.
- Runtime verification: `git ls-remote --heads origin refs/heads/phase7-bcgm` trả SHA `bd98f25f15f724d2d4a1414e16b7369007703332`; khớp local `HEAD`. Worktree sạch tại preflight trước các cập nhật closure.
- Lịch sử HTTP 403 trên commit đầu tiên được giữ như sự kiện lịch sử; commit thứ hai đã được push và remote HEAD hiện tại được kiểm tra thành công.

Không có merge vào `main`, force-push hay tag mới.

## 4. Hugging Face backup

- Dataset repository: [`QuanDinh/SGS-SLAM-assets`](https://huggingface.co/datasets/QuanDinh/SGS-SLAM-assets).
- Artifact root: `phase7_bcgm/`.
- Revision được ghi nhận trong validation evidence: `fdc1616e843319af649d3a7ebe710da51be489fc`.
- Repository type: `dataset`.
- Kích thước nguồn được báo cáo: khoảng 4.794 GiB.

### Validation inventory đã được researcher cung cấp

| Artifact group | Files | Status đã ghi nhận |
|---|---:|---|
| Room0 model output | 1,623 | PASS |
| Room0 runtime evidence | 170 | PASS |
| Room1 model output | 1,623 | PASS |
| Room1 runtime evidence | 9 | PASS |
| **TOTAL** | **3,425** | **PASS** |

Các kiểm tra được cung cấp: expected=remote=3,425; missing=0; unexpected=0; kích thước remote có mặt cho 3,425/3,425 file; size mismatch=0; size unknown=0; error count=0. Sáu SHA256 so sánh checkpoint/PLY được báo cáo PASS.

**Phạm vi xác minh trong phiên closure này:** repo metadata/current revision không thể truy cập được. Một API metadata request trả HTTP 401; `hf auth whoami` gặp DNS resolution error. Do đó revision, inventory và size totals nêu trên là validation đã được researcher cung cấp, không phải kết quả được truy vấn lại độc lập trong phiên này. Không tuyên bố SHA256 cho toàn bộ 3.425 file; hash verification được giới hạn ở sáu file quan trọng theo báo cáo validation.

## 5. Local checkpoint và sáu SHA256 critical files

SHA256 đã được tính độc lập từ các file local; hai checkpoint khớp expected values. Bốn giá trị PLY bên dưới cũng được tính lại local. Remote-side sáu giá trị được báo cáo là đã đối chiếu PASS trong validation do researcher cung cấp; lần đối chiếu remote không thể lặp lại do hạn chế truy cập vừa nêu.

| Scene | File | SHA256 local |
|---|---|---|
| Room0 | `params.npz` | `a02dd4b4ecfd9c982866cf4a4c38c187ef22c75049b8328e18eea20608944917` |
| Room0 | `params.ply` | `409d1c3637e3f951f950d14bf066a88df66de8dc41a01762c312a0871ab300fc` |
| Room0 | `seg_params.ply` | `98a41a36e69e113c7e7da8dcfcd8c279c08c25da8af7525e26dcbdb7df262b89` |
| Room1 | `params.npz` | `27a388536ced6a5cf5dc59395a980e1f74a99c2a438c4290773d4e54eafadf32` |
| Room1 | `params.ply` | `d4613f5dd81fca9ad676fcbdd6484dafde2f9d17eb902d596031674f9416c082` |
| Room1 | `seg_params.ply` | `9381a9be2b816601f2010b2f1248e2c907d1861a5a3ae4153aba147eface3a8c` |

Remote-side comparison of these six hashes is recorded as PASS in the researcher-provided HF validation evidence. This session independently recalculated the six local file hashes only; current remote metadata/content was inaccessible.

## 6. Artifact preservation and limitations

- Room0 and room1 evidence/model artifacts remain on the GPU server; GitHub contains source/config/tests/docs, not large scientific artifacts.
- Room0 laptop transfer is `USER_REPORTED_COMPLETE`; destination checksums were not independently observed in this session.
- Hugging Face backup validation was supplied as PASS for 3,425 file paths/sizes with six critical hash comparisons; current metadata access was unavailable and all-file SHA256 was not performed.
- Phase 4/6 historical evidence remains in its existing repositories; this closure did not alter or republish it.
- Scientific limitations remain: one run/seed per room, 401 sampled quality frames, no conventional Depth RMSE from `rmse.txt`, console ATE label discrepancy, Phase 4 timing-scope mismatch, Phase 6 BAM confound, room0/room1 distinct scenes, and no cap ablation. Room1 has quality degradations in LPIPS, Depth L1 and trajectory errors despite lower resource measurements.

## 7. Project handoff

`SESSION_008` closes this documentation/archive verification task. `SESSION_005` remains ACTIVE for its separate room0 workstream; `SESSION_006` and `SESSION_007` remain CLOSED. Current recommendation: complete thesis/report writing around the verified Phase 7-A results and limitations. Do not begin Phase 7-B automatically.

Canonical project state: `project_management/PROJECT_STATUS.md` and `project_management/SESSION_HANDOFF.md`. Detailed analysis: `docs/research/phase7/post_implementation/P7_POST02_*.md` and `P7_POST_FINAL_HANDOFF.md`.
