# Phase 7 Gate 4 — Final Metric Table (Chapter 4 ready)

**Run:** `p7_bcgm_g3_room0_on_0_1999_r01`, Replica `room0`, frames 0–1999, seed 0.
**Regime:** online SLAM; evaluation arrays saved by repository evaluator over 401 training-view samples.
**Source:** Phase 7 branch `phase7-bcgm`, HEAD `68f9060f7ff4d8d141be1d5f71339401327edd06`; current run/source/config hashes are in the Gate 4 manifest. Values are arithmetic means except explicit count/peak/time values.

## Final Phase 7 measurements

| Category | Metric | Result | Unit / scope | Interpretation |
|---|---|---:|---|---|
| RGB | PSNR | 32.444045252336 | dB; 401 evaluator views | Saved `psnr.txt` mean |
| RGB | MS-SSIM | 0.975780536409 | unitless; 401 views | Saved `ssim.txt` is MS-SSIM |
| RGB | LPIPS | 0.076533443729 | unitless; 401 views | Saved `lpips.txt` mean |
| Depth | Depth L1 | 0.005907558010 | m; 401 views | `rmse.txt` equals `l1.txt`; not true Depth RMSE |
| Semantic | mIoU | 0.913442026372 | unitless; 401 views | Saved `miou.txt` mean |
| Trajectory | ATE Mean | 0.002489759244 | m; 2,000 poses | Horn-aligned mean Euclidean translation residual |
| Trajectory | ATE RMSE | 0.003249278229 | m; 2,000 poses | Independently computed offline; `sqrt(mean(e_i^2))` |
| Trajectory | ATE Median | 0.001541667416 | m; 2,000 poses | Offline per-pose residual median |
| Trajectory | ATE Max | 0.009684450578 | m; 2,000 poses | Offline maximum per-pose residual |
| Completion | Process exit / status | 0 / COMPLETE | full run | Normal worker return |
| Completion | Poses / insertion events | 2,000 / 1,999 | full run | Frames 0–1999 inclusive |
| Map | Final Gaussian count | 4,499,583 | checkpoint rows | Post-run map; pruning is separate from admission |
| BCGM | Valid / admitted / rejected | 8,698,235 / 4,363,012 / 4,335,223 | all insertion events | Per-event invariants checked across 1,999 records |
| BCGM | Event / Global Cap activations | 104 / 789 | event counts | Uses `event_saturated` / `global_saturated` |
| Performance | Process wall | 14,165.030217954074 | s | Guarded process wall scope from summary |
| Performance | End-to-end FPS | 0.1411927803348428 | frames/s | 2,000 / process wall; whole-run throughput |
| Performance | Tracking FPS | 0.347069322852072 | frames/s | Stage reciprocal; not end-to-end FPS |
| Performance | Mapping FPS | 0.2567925871385077 | frames/s | Stage reciprocal; not end-to-end FPS |
| Memory | CUDA peak allocated | 5,442,630,656 | B | Process PyTorch allocator, summary scope |
| Memory | CUDA peak reserved | 6,784,286,720 | B | Process PyTorch allocator; distinct from allocated |
| Memory | NVML sampled peak | 7,684 | MiB | Device-wide sampled CSV peak, not allocator peak |
| Memory | NVML valid samples | 13,941 | samples | 0 invalid, 0 error rows; interval 1 s |

## Comparison eligibility (Phase 4 / Phase 6)

| Metric family | Phase 4 full-scene reference | Classification | Phase 6 | Claim allowed |
|---|---:|---|---|---|
| Runtime | 14,173.475159 s | `COMPARABLE_WITH_LIMITATIONS` | No matched Replica room0 0–1999 record established | Context only; no matched speedup/statistical claim |
| CUDA allocated | 5,817,509,888 B | `COMPARABLE_WITH_LIMITATIONS` | No comparable matched measurement | Context only; scopes/harness differ |
| CUDA reserved | 7,189,037,056 B | `COMPARABLE_WITH_LIMITATIONS` | No comparable matched measurement | Context only; scopes/harness differ |
| Final Gaussians | 4,956,467 | `COMPARABLE_WITH_LIMITATIONS` | No same-scene/protocol metric | Descriptive map-size context; not causal or quality proof |
| NVML peak | Not measured | `NOT_MEASURED` | Not established as matched | No comparative claim |
| PSNR/MS-SSIM/LPIPS | Not measured | `NOT_MEASURED` | No matched room0 protocol evidence | No quality-retention claim |
| Depth L1 | Not measured | `NOT_MEASURED` | No matched room0 protocol evidence | No depth-quality delta |
| ATE | Not measured | `NOT_MEASURED` | No matched room0 protocol evidence | No trajectory delta |
| Semantic mIoU | Not measured | `NOT_MEASURED` | No matched room0 protocol evidence | No semantic-quality delta |

Phase 4 row provenance and harness limitations are detailed in `PHASE7_GATE3_BASELINE_REUSE_AUDIT.md`; Phase 6 scenes/visualization artifacts are not substituted for a matched Replica room0 quantitative run. The raw numerical difference in historical runtime or memory is not a controlled BCGM effect estimate.

## Metric definitions and limitations

- Evaluator source: `utils/eval_helpers.py`; six arrays each contain 401 finite values. `ssim.txt` is MS-SSIM. The saved `rmse.txt` is byte-identical to `l1.txt`; report Depth L1 only.
- The original evaluator's console label `Final Average ATE RMSE` reports `100 × mean(e_i)` cm. The offline ATE artifact reports both mean and true RMSE after Horn SE(3) alignment of W2C translation columns, with no scale fitting and all 2,000 poses.
- RGB/depth/semantic values are training-view metrics. They do not establish held-out novel-view quality.
- CUDA allocated/reserved are PyTorch allocator quantities. NVML is a 1 Hz device-wide sampled observation; no unsampled absolute peak is claimed.
- Tracking/Mapping FPS are stage measures and must not be presented as overall FPS.
