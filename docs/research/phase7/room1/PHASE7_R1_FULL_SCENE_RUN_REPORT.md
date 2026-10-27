# R1 Full-Scene Run Report — Replica room1

Status COMPLETE; evidence closure PASS_WITH_LIMITATIONS. CPU/read-only evidence audit only: no SLAM/CUDA/rendering rerun.

- Run ID: p7_bcgm_r1_full_room1_on_0_1999_r01; branch phase7-bcgm; HEAD 68f9060f7ff4d8d141be1d5f71339401327edd06.
- Start/end UTC: 2026-10-27T11:09:10Z / 2026-10-27T15:11:55Z.
- Exit code 0; 2,000 frames (0–1999), 2,000 estimated/GT poses; 1,999 insertion events.
- Process runtime 14564.629470040 s; E2E 0.137318975681 FPS; Tracking 0.339028112990; Mapping 0.248121108168.
- CUDA allocated/reserved 5,628,716,544/7,761,559,552 B. NVML sampled peak 10,355 MiB, 14,330 valid samples, zero invalid, timestamp 2026-10-27T13:14:42+00:00.
- Direct-host preflight saved PASS: RTX 5080, 16,303 MiB total, 818 MiB used, 0% utilization at observation; runtime PyTorch 2.7.1+cu128, CUDA 12.8.

## Inputs and hashes

| Item | SHA256 |
|---|---|
| scripts/slam.py | ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999 |
| utils/bcgm.py | 8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400 |
| Gate 1B worker | 9a449ef10506ebbe6ccd0616d29aa02e9183554b333d605c9440ec07e09ad40b |
| R1 config | 3c0d43c4e6ba4a3260815daa9f2d64f468802ab49f60686135df40b22f61bd10 |
| utils/eval_helpers.py | e94366ca256ec2b51b5d0264a5daba2a895cc0375d7b91e976e4ea0e9e28194e |
| runner | 7d1fefabb6c45671c71786ea312d7591c7045fe13abeb4f9568c2023ba319434 |
| checkpoint | 27a388536ced6a5cf5dc59395a980e1f74a99c2a438c4290773d4e54eafadf32 |

Effective input and runtime config snapshots are in the run evidence directory. Science fields retained seed 0, 1200x680, frames 0–1999, tracking/mapping iterations 40/60, mapping every 1, keyframe every 5, mapping window 24, semantic processing, CPU Keyframe Offload, pixel-driven insertion and pruning; clone/split densification and BAM disabled. BCGM caps are 9,000 / 4,500,000.

## Checkpoint and PLY integrity

Checkpoint params.npz is 292,624,100 bytes; ZIP CRC PASS, NumPy load PASS, all numeric fields finite, Gaussian fields aligned, 2,000 camera poses. Final map has 4,498,964 Gaussians. params.ply and seg_params.ply are nonempty, each has 4,498,964 vertices; hashes are d4613f5dd81fca9ad676fcbdd6484dafde2f9d17eb902d596031674f9416c082 and 9381a9be2b816601f2010b2f1248e2c907d1861a5a3ae4153aba147eface3a8c.

The final BCGM record immediately after insertion has 4,498,991 Gaussians; saved checkpoint has 4,498,964, 27 fewer. This is consistent with post-insertion mapping pruning: BCGM event is emitted at scripts/slam.py:504-508; pruning occurs at scripts/slam.py:1038-1040. Pruning is separate from admission and is not a cap violation.

## Metrics and manifest

Six saved evaluator arrays each have 401 finite values at IDs 0, 4, 9, ..., 1999. Exact means/definitions are in PHASE7_R1_FULL_SCENE_METRIC_TABLE.md. Offline ATE uses all 2,000 poses; method: Horn rigid SE(3) on W2C translation columns, no scale fit. The console ATE RMSE label is mean residual; rmse.txt equals l1.txt and is not true Depth RMSE.

The original artifact_manifest.json has 1,629 records; all paths exist and all recorded sizes/SHA256 match. It was not modified. Offline ATE JSON/Markdown were generated separately, absent from that original manifest, and are listed with hashes in PHASE7_R1_OFFLINE_ATE_INTEGRITY_MANIFEST.json.
