# Phase 7 Gate 3 — Advanced visualization final report

## Kết quả

`ADVANCED_VISUALIZATION_STATUS: PASS_WITH_LIMITATIONS`

Đã dựng đủ tám nhóm visualization từ checkpoint Gate 3 và tạo các board
so sánh ba cột **Phase 4 | Phase 6 | Phase 7**. Công việc chỉ đọc map đã lưu,
render và package; không chạy SLAM, không optimization và không thay đổi
checkpoint/config khoa học.

## Trạng thái từng nhóm

| Nhóm | Trạng thái | Output/board |
|---|---|---|
| A. Observed-camera RGB | `PASS_WITH_LIMITATIONS` | `phase7_only/observed_camera/rgb/`; `compare_phase4_phase6_phase7/A_observed_rgb/` (5 boards) |
| B. Observed metric depth | `PASS` | `phase7_only/observed_camera/depth/` (NPY + PNG); `.../B_observed_depth/` (5 boards, 15 normalized references) |
| C. Observed learned semantic color | `PASS_WITH_LIMITATIONS` | `phase7_only/observed_camera/semantic/`; `.../C_observed_semantic/` (5 boards) |
| D. Full-scene RGB Gaussian map | `PASS_WITH_LIMITATIONS` | `.../D_full_scene_rgb/` (overview, oblique, top_oblique, room_overview, trajectory_observed) |
| E. Cross-modal RGB/geometry/fixed-ID | `PASS_WITH_LIMITATIONS` | `.../E_cross_modal/` (3 V3A cameras; paired composite and geometry boards) |
| F. Selected fixed semantic-ID classes | `PASS_WITH_LIMITATIONS` | `.../F_fixed_semantic_classes/` (8 exact classes and legend) |
| G. Estimated camera trajectory in geometry | `PASS_WITH_LIMITATIONS` | `.../G_estimated_trajectory/` (geometry overlay and 3D trajectory boards) |
| H. Full-scene semantic map | `PASS_WITH_LIMITATIONS` | `.../H_full_scene_semantic/` (learned free-view, raw V3A learned, fixed IDs) |

## Artifact paths

- Phase 7 only:
  [`advanced_visualization/phase7_only/`](</home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/advanced_visualization/phase7_only/>)
- Comparison boards:
  [`advanced_visualization/compare_phase4_phase6_phase7/`](</home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/advanced_visualization/compare_phase4_phase6_phase7/>)
- Camera metadata and checksummed manifest:
  [`advanced_visualization/`](</home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/advanced_visualization/>)
- Machine-readable manifest:
  [`advanced_visualization_manifest.json`](</home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/advanced_visualization/metadata/advanced_visualization_manifest.json>)
- Execution record:
  [`PHASE7_GATE3_ADVANCED_VISUALIZATION_EXECUTION.md`](PHASE7_GATE3_ADVANCED_VISUALIZATION_EXECUTION.md)
- Validation report:
  [`PHASE7_GATE3_ADVANCED_VISUALIZATION_VALIDATION.md`](PHASE7_GATE3_ADVANCED_VISUALIZATION_VALIDATION.md)

## Integrity and backup readiness

Checkpoint SHA256 remains
`a02dd4b4ecfd9c982866cf4a4c38c187ef22c75049b8328e18eea20608944917`;
the two PLY hashes and Phase 7 SLAM/BCGM source hashes also match the saved
identities. All five observed cameras are exact Phase 4 V2 metadata; the V3A
cameras are exact Phase 4 JSONs. Manifest checks validated 143 output entries
and 210 Phase 4/6 reference hashes; manifest SHA256 is
`9fc4bb7fe98f7be41f2e9e756492f0e3c9ba2bdd996b09f974cef6a5c797d039`. The visualization directory is 112 MB;
25 GiB remain free. No checkpoint/PLY duplication and no tar archive were
created. `BACKUP_READINESS: PASS_READY_TO_TRANSFER` (not yet downloaded to the
laptop).

Run the following **from the laptop** to transfer the visualization package:

```bash
rsync -avh --progress robot@100.113.78.40:/home/robot/research/SGS_slam_phase7_bcgm/results/runtime_artifacts/phase7_gate3/p7_bcgm_g3_room0_on_0_1999_r01/advanced_visualization/ /path/to/laptop/p7_bcgm_g3_advanced_visualization/
```

## Limitations

- Phase 6 observed RGB/learned-semantic rendering has white background;
  Phase 4 and Phase 7 observed rendering use black. The board preserves each
  source image and labels all three columns. Depth boards normalize all three
  saved raw arrays with the canonical Phase 4 camera-z metres, `[0,6]` m
  Turbo display.
- The fixed-ID and geometry images are deterministic sampled Gaussian-center
  diagnostics; they do not claim a continuous surface. The exact Phase 4
  camera is retained even where Phase 7 centers are clipped.
- The V3A renderer metadata records the renderer tool checkout as
  `phase5-profiling-instrumentation` / `809d5ea…`; Phase 7 checkpoint/source
  identity is separately stated in the manifest and execution report.
- Boards are qualitative; no additional image/depth metrics are claimed.

`SESSION_005` remains `ACTIVE`. Existing Phase 7 free-view source images and
all Phase 4/6 artifacts remain unchanged. No Git commit/push or upload was
performed.
