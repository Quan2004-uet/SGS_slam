# R1-Gate 0 — Preflight and Baseline Audit

> Pre-execution snapshot from 2026-10-27. Its then-current HOST_EXECUTION_REQUIRED status was later cleared by the saved direct-host preflight PASS. Current R1 status is Gate 0 PASS, Gate 1 complete, Gate 2 PASS_WITH_LIMITATIONS; see PHASE7_R1_GATE2_FINAL_EVIDENCE_CLOSURE.md.

**Status:** `HOST_EXECUTION_REQUIRED`<br>
**Run:** `p7_bcgm_r1_full_room1_on_0_1999_r01`; no SLAM/CUDA run has started.<br>
**Search:** no earlier Phase 7 room1 Gate 0 report was found. Existing Phase 4/6 room1 records were audited directly.

## Dataset — PASS

`/home/robot/research/SGS_slam/data/Replica/room1` contains exactly 2,000 files in each of `frames`, `depths`, `semantic_ids`, `semantic_colors`, IDs 000000–001999. CPU decode of every file passed: RGB `(680,1200,3)` uint8; depth `(680,1200)` uint16 with finite positive values; semantic ID `(680,1200)` uint8; semantic color `(680,1200,3)` uint8. The files are aligned by the same numeric frame IDs. `traj.txt` has 2,000 finite 4×4 transforms with valid homogeneous rows and rotation orthogonality/determinant within 0.002. Its SHA256 is `5c650f90192da13b628308a6cbaf68fa6e048cfaa8f1870c5e66572296cc5c7d`. Root `data/Replica/cam_params.json` and pinned `configs/data/replica.yaml` agree at 1200×680, fx/fy 600, cx 599.5, cy 339.5, depth scale 6553.5. Camera JSON SHA256 `ffbefdeb53755e1490d6936dffdee253510e68d5e443e1ba91e60202addc1a0a`; YAML SHA256 `4c1e33544bef24c146c4ec9a622bb3ad7a314168db8d192c191db08bad3edf58`.

## Historical room1 baselines — PASS with protocol distinctions

**Phase 4:** `p4_vb001_room1_full_0_1999_r01`, source SHA `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3`, base commit `68f9060f7ff4d8d141be1d5f71339401327edd06`. Run metadata reports 2,000/2,000 frames, exit 0, `CORE_ARTIFACTS_VALIDATED`; checkpoint ZIP CRC PASS, 6,663,167 Gaussians, 2,000 poses, checkpoint SHA `3ab49193b0a1160405ff90ee6387a8e06c713c127c1e2bf2f1ca9cdf1b0443f4`. All 401 per-frame image metric rows finite, indices 0–1999 by `{0} union {5k-1}`. Offline evaluation status is `PARTIAL_OFFLINE_EVALUATION` only because standard Depth RMSE is unavailable; PSNR/MS-SSIM/LPIPS/Depth L1/mIoU and 2,000-pose trajectory metrics completed with exit 0. See Phase 4 `performance_summary.json`, `checkpoint_validation.json`, `artifact_manifest.json`, `evaluation_metrics.json`, `evaluation_protocol.json`, `trajectory_metrics.json`.

Phase 4 reference metrics: PSNR 33.93622684716584 dB; MS-SSIM 0.9699054904412153; LPIPS 0.09743846615223664; Depth L1 0.00436371473823105 m; semantic mIoU 0.9236634195237521; ATE Mean 0.004262120556727725 m; true ATE RMSE 0.004411847720561559 m. Runtime 18,472.333261692 s; E2E FPS 0.1082700259; tracking 0.2555125699 FPS; mapping 0.1931999681 FPS; CUDA peak allocated/reserved 8,066,530,816 / 10,626,269,184 B; sampled NVML 11,341 MiB over 17,917 samples. Evaluation separately took 370.505805 s; its runtime NVML sample peak was 4,497 MiB. Do not combine these scopes without labeling.

**Phase 6:** `p6_bam_ms_room1_gate3_0_1999_r01`, room1 frames 0–1999, exit 0; 401 views. Metrics: PSNR 34.096186264494705 dB; MS-SSIM 0.9714362002964924; LPIPS 0.09135246086410453; Depth L1 0.004393707946328413 m; semantic mIoU 0.9265354206849918; ATE Mean 0.004655330867990601 m; true ATE RMSE 0.004802019103114381 m. It enables Phase 6 BAM/adaptive mapping budget and has different source commit/config; use only as a distinct-method context, not an isolated BCGM baseline.

Two Phase 4 historical preflight attempts stopped because GNOME remote desktop appeared as an unclassified GPU process; a later Phase 4 full-scene run completed. This is historical, not current GPU process evidence.

## Config, output, resource checks

R1 config is derived from room0 Gate 3 config; expected config diff is only run/output identity plus scene metadata (`run_name`, `data.sequence`, `viz.scene_name`, disabled `wandb.name`). Hash `3c0d43c4e6ba4a3260815daa9f2d64f468802ab49f60686135df40b22f61bd10`. BCGM source/config/caps remain locked. R1 model and evidence paths did not exist during preflight. Current Codex-visible filesystem has 26,455,846,912 B available (98% used), 56,619,636 free inodes, 117 GiB MemAvailable; 6 GiB estimated output budget and 20 GiB minimum free space pass at this observation. No SLAM process appeared in the visible process list.

## Blocker to readiness PASS

Current Codex `nvidia-smi` cannot communicate with the NVIDIA driver. Therefore direct-host GPU model/free VRAM, active compute processes, CUDA availability and native dependencies at execution time are **NOT_VERIFIED**. This does not indicate host GPU failure. Overall R1 Gate 0 remains `HOST_EXECUTION_REQUIRED`, not `PASS_READY_FOR_FULL_SCENE`. Run the read-only R1 runner command on the direct host; execute only if it returns `preflight=PASS`.
