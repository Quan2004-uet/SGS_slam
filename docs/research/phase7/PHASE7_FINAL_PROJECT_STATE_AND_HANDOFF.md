> **Historical research handoff:** Git/Hugging Face publication fields below describe the earlier research closure and are superseded for archival status by `docs/research/phase7/post_implementation/P7_FINAL_GITHUB_HF_ARCHIVAL_CLOSURE.md` (SESSION_008, 2026-10-28).

# Phase 7 — Final Research State and Handoff

**Ghi nhận:** 2026-10-28 (Asia/Tokyo)<br>
**Repository:** `/home/robot/research/SGS_slam_phase7_bcgm`<br>
**Branch / HEAD:** `phase7-bcgm` / `68f9060f7ff4d8d141be1d5f71339401327edd06`<br>
**Trạng thái:** `PHASE7_QUANTITATIVE_RESEARCH: COMPLETE_WITH_LIMITATIONS`<br>
**Local session:** `SESSION_006: CLOSED`; `SESSION_005: ACTIVE` (workstream room0 riêng)<br>
**Git/HF publication:** `LOCAL_SESSION_CLOSED_PUBLICATION_PENDING`; không commit, push hoặc upload.

## 1. Mục tiêu và đóng góp đã xác minh

Phase 7 đánh giá BCGM trên SGS-SLAM với Phase 4 CPU Keyframe Offload. Source hiện hành xác nhận bounded admission tại bước pixel-driven Gaussian insertion: lọc candidate trước khi dựng point cloud, chọn candidate có tính xác định, giới hạn tối đa 9.000 Gaussian mỗi insertion event và giới hạn map tại thời điểm admission ở 4.500.000 Gaussian. RGB/depth/semantic payload giữ alignment. Không thêm gradient clone/split densification; Phase 6 BAM không nằm trong cấu hình Phase 7. Không có bằng chứng BCGM thay tracking objective hay thêm tối ưu hóa độc lập. Pruning chạy sau đó có thể làm Gaussian count giảm; Global Cap là ràng buộc admission, không phải invariant kích thước vĩnh viễn của map.

## 2. Các cổng và trạng thái

### Replica room0

- Gate 0 — BCGM design: `PASS_PHASE7_GATE0_DESIGN_READY` (carry-forward trong hồ sơ hiện có).
- Gate 1A — CPU implementation: `PASS_PHASE7_GATE1A_CPU_READY`.
- Gate 1B — 100-frame bounded validation: `PASS_WITH_LIMITATIONS`.
- Gate 2 — 500-frame validation: `PASS_GATE2_WITH_COMPARISON_LIMITATIONS`.
- Gate 3 — full-scene 2.000 frames: `COMPLETE_WITH_LIMITATIONS`.
- Gate 4 — final evidence closure: `FINAL_EVIDENCE_CLOSURE_COMPLETE`.
- Kết luận room0: `RESEARCH_COMPLETED_WITH_LIMITATIONS`.

Run: `p7_bcgm_g3_room0_on_0_1999_r01`; artifacts nằm tại `results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/` và `experiments/Replica/p7_bcgm_g3_room0_on_0_1999_r01/`.

### Replica room1 fast-track

- R1-Gate 0 — preflight/baseline audit: `PASS`.
- R1-Gate 1 — một full-scene run, frames 0–1999: `COMPLETE`.
- R1-Gate 2 — quantitative evaluation/evidence closure: `PASS_WITH_LIMITATIONS`.
- Room1 advanced visualization A–H: `DEFERRED_BY_RESEARCH_DECISION`; không phải lỗi thực nghiệm.

Run: `p7_bcgm_r1_full_room1_on_0_1999_r01`; artifacts nằm tại `results/runtime_artifacts/phase7_gate3_room1/p7_bcgm_r1_full_room1_on_0_1999_r01/` và `experiments/Replica/p7_bcgm_r1_full_room1_on_0_1999_r01/`.

## 3. Kết quả định lượng đã đối chiếu với artifact

Các metric RGB/depth/semantic là arithmetic mean trên 401 frame được lấy mẫu (frame 0 và 4, 9, …, 1999), không phải 2.000 frame. ATE offline dùng toàn bộ 2.000 pose, Horn rigid SE(3) alignment trên translation của W2C, không scale fitting.

| Metric | Replica room0 | Replica room1 |
|---|---:|---:|
| Process runtime (s) | 14,165.030217954074 | 14,564.629470039974 |
| E2E FPS | 0.1411927803348428 | 0.13731897568105528 |
| Tracking FPS | 0.347069322852072 | 0.33902811298959407 |
| Mapping FPS | 0.2567925871385077 | 0.24812110816831184 |
| CUDA peak allocated (B) | 5,442,630,656 | 5,628,716,544 |
| CUDA peak reserved (B) | 6,784,286,720 | 7,761,559,552 |
| NVML sampled device peak (MiB) | 7,684 | 10,355 |
| Final Gaussians | 4,499,583 | 4,498,964 |
| PSNR (dB) | 32.44404525233623 | 33.32633080327897 |
| MS-SSIM | 0.9757805364090308 | 0.9681034810525223 |
| LPIPS | 0.07653344372877308 | 0.10738863215370666 |
| Depth L1 (m) | 0.005907558010394065 | 0.005512088386253674 |
| Semantic mIoU | 0.91344202637233 | 0.9197293274626335 |
| ATE Mean (m) | 0.0024897592444028008 | 0.005537752230202329 |
| True ATE RMSE (m) | 0.0032492782294292577 | 0.005674386822121515 |
| ATE Median (m) | 0.0015416674157756505 | 0.005576422438909692 |
| ATE Max (m) | 0.009684450577739244 | 0.013747675506648417 |
| BCGM valid / admitted / rejected | 8,698,235 / 4,363,012 / 4,335,223 | 33,408,344 / 3,892,851 / 29,515,493 |
| Event Cap activations | 104 | 294 |
| Global Cap activations | 789 | 1,251 |

Room0 checkpoint SHA256: `a02dd4b4ecfd9c982866cf4a4c38c187ef22c75049b8328e18eea20608944917`. Room1 checkpoint SHA256: `27a388536ced6a5cf5dc59395a980e1f74a99c2a438c4290773d4e54eafadf32`. Both ZIP CRC checks pass. Final Gate 4 manifest verified 212/212 entries (209 original evidence entries plus current closure/session records); room1 original run manifest verified 1,629/1,629 entries; room1 supplemental offline ATE manifest verified 3/3 entries.

### Comparison interpretation

- Room0 and room1 are distinct scenes; cross-scene metric differences are descriptive and not paired.
- Phase 4 room1 is the closest same-scene reference, but its runtime/evaluation boundary differs; do not claim a matched speedup.
- Phase 6 room1 includes BAM/adaptive mapping, so it is not a BCGM-only ablation. Do not attribute differences solely to BCGM.
- CUDA allocator allocated/reserved peaks and sampled device-wide NVML memory have different measurement scopes.
- There is one run/seed per condition; no statistical significance or causal performance claim is supported.
- `rmse.txt` reproduces Depth L1 and does not establish conventional Depth RMSE. The console label “Final Average ATE RMSE” refers to arithmetic mean aligned residual; the true ATE RMSE above is independently computed offline.
- Room1 quality metrics cover 401 sampled views, while trajectory ATE covers 2,000 poses.
- Resource reductions versus Phase 4 can be stated as observed values with their scope limitations; quality tradeoffs, particularly room1 Depth L1 and trajectory ATE, must remain visible.

## 4. Source, configuration, artifacts, Git

Verified SHA256:

- `scripts/slam.py`: `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999`
- `utils/bcgm.py`: `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400`
- room0 config `configs/replica/phase7_gate3_room0_on_0_1999_r01.py`: `1bb57b3dd38e98c39a24310ceaee656a8415ce901e61808bb19cea8422c4ff22`
- room1 config `configs/replica/phase7_r1_full_room1_on_0_1999_r01.py`: `3c0d43c4e6ba4a3260815daa9f2d64f468802ab49f60686135df40b22f61bd10`
- Gate 1B worker: `9a449ef10506ebbe6ccd0616d29aa02e9183554b333d605c9440ec07e09ad40b`

The original summaries, configs, checkpoints, PLYs, metric arrays, NVML CSVs, insertion traces and manifests were read-only during this synchronization. Current disk availability at closure audit was 23,932,784,640 bytes (~22.3 GiB). The worktree contains deliberate uncommitted Phase 7 source, configs, tools, tests, reports and project-management files; no destructive Git operation or publication occurred. Session closure does not imply Git archival: `LOCAL_SESSION_CLOSED_PUBLICATION_PENDING`.

Proposed selective staging plan for a separately approved future review: stage only reviewed source (`scripts/slam.py`, `utils/bcgm.py`), scoped Phase 7 configs/tools/tests, and documentation/session records. Explicitly exclude `results/`, `experiments/` checkpoints/PLY/evaluation output, datasets, caches, credentials and generated large artifacts. Review each path and diff individually; do not use `git add -A`.

## 5. Session state and future work

- `SESSION_005`: `ACTIVE`, room0 session; intentionally unchanged.
- `SESSION_006`: `CLOSED` on 2026-10-28 (Asia/Tokyo), room1 quantitative validation workstream.
- No active Phase 7 execution task is created by this closure.

Deferred/optional work: researcher review of room0/room1 comparisons; room1 advanced visualization only if separately authorized; selective Git archival review; laptop-side checksum verification if stronger transfer assurance is needed. Do not rerun SLAM or rendering merely to close this session. `docs/project_state/CURRENT_STATE.md` and `state.yaml` remain historical/derived Phase 4 migration snapshots per repository policy; canonical current state is in `PROJECT_STATUS.md` and this handoff. No new durable method decision was introduced, so `DECISIONS.md` was not changed.

## 6. Resume checklist for a new Codex session

1. Read `AGENTS.md`, this report, `project_management/PROJECT_STATUS.md`, `project_management/SESSION_HANDOFF.md`, and `project_management/sessions/SESSION_006.md`.
2. Confirm branch/HEAD and inspect `git status --short`; preserve all existing local changes.
3. Use room0 Gate 4 and room1 Gate 2 reports/manifests as evidence indexes; verify source/runtime artifacts before any new claim.
4. Begin only a separately specified research or publication task. Do not infer authorization for experiments, Git publication, Hugging Face upload or transfer verification.
