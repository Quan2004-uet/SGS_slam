# Phase 7 Gate 2 Readiness Report

**Date:** 2026-10-27 (Asia/Tokyo); **Session:** `SESSION_005` — ACTIVE
**Scope:** Session initialization and readiness planning only.

## 1. Session and source identity

- Current session: `SESSION_005` (created as the next unused local ledger ID;
  local records contain `SESSION_001`–`SESSION_004`; `SESSION_004` is CLOSED).
- Worktree: `/home/robot/research/SGS_slam_phase7_bcgm`.
- Branch: `phase7-bcgm`.
- HEAD and frozen Phase 4 base: `68f9060f7ff4d8d141be1d5f71339401327edd06`.
- `scripts/slam.py` SHA256: `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999`.
- `utils/bcgm.py` SHA256: `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400`.
- Evidence Manifest dependency hashes for these source files and Gate 1B
  configs match the recorded SHA256 values. The three Gate 1B effective input
  configs are preserved in the manifest; no Gate 2 config has been created.

Git currently shows 4 tracked modified paths (`project_management/CHANGELOG.md`,
`project_management/PROJECT_STATUS.md`, `project_management/SESSION_HANDOFF.md`,
`scripts/slam.py`) and 13 pre-existing untracked Phase 7 paths. The BCGM source
and Gate 1B changes predate this initialization and remain uncommitted. This
task adds a session record and this readiness report; source and scientific
configuration were not changed.

## 2. Gate 1B closure verification

**VERIFIED FROM ARTIFACTS:** `PASS_WITH_LIMITATIONS`. The Gate 1B evidence
manifest was read and every one of its 322 dependency and run-file entries was
checked for existence, SHA256, and byte size: 322 matched, none missing or
mismatched (1,105,339,776 bytes hashed). The three run IDs remain present:

- `p7_bcgm_g1b_room0_p4_0_99_r01`
- `p7_bcgm_g1b_room0_off_0_99_r01`
- `p7_bcgm_g1b_room0_on_0_99_r01`

Gate 1B remains a single 0–99 run per arm, not a statistical or full-scene
claim. The report and metric comparison document 100 saved poses and 99
insertion events per arm, and BCGM admission invariants 7/7 PASS. Event Cap
activated 14/99 times; Global Cap activated 0 times and remains
`NOT_RUNTIME_VERIFIED`.

## 3. Gate 2 objective and proposed experiment scope

**Objective:** medium-horizon validation of BCGM with Phase 4 CPU Keyframe
Offload for Replica `room0`, frames 0–499 inclusive (500 frames), seed 0.

**Proposed matched arms, sequential:**

| Arm | Proposed unique Run ID | BCGM |
|---|---|---|
| Phase 4 CPU Keyframe Offload reference | `p7_bcgm_g2_room0_p4_0_499_r01` | absent |
| CPU Keyframe Offload, BCGM off | `p7_bcgm_g2_room0_off_0_499_r01` | disabled |
| CPU Keyframe Offload, BCGM on | `p7_bcgm_g2_room0_on_0_499_r01` | Event Cap 9,000; Global Cap 4,500,000 |

These are proposed names only. A read-only search found no collision with the
existing Gate 1B IDs; confirm again and create isolated output directories
only during separately authorized run preparation.

Hold seed, scene, frame range, resolution, renderer, losses, optimizer,
tracking/mapping schedules, keyframe policy, evaluator and CPU offload policy
constant. Preserve pixel-driven insertion. Keep gradient clone/split
densification off. Do not combine Phase 6 BAM. Use the same 500-frame quality
sampling/evaluation protocol across all arms and archive the exact config and
source hashes.

Record process wall and end-to-end FPS separately from stage tracking FPS and
mapping FPS. Mapping FPS excludes pixel insertion. Collect Gaussian counts by
frame from the insertion trace and final checkpoint, distinguish CUDA peak
allocated, CUDA peak reserved and sampled device-wide NVML VRAM, and record
Event Cap activation counts/frames. If Global Cap never activates, state
explicitly that it was not runtime-verified.

Quality reporting should follow the same saved evaluator protocol as Gate 1B
for RGB PSNR, MS-SSIM, LPIPS, depth, semantic mIoU, and trajectory. Preserve
the actual definitions: saved `rmse`/displayed “Depth RMSE” is Depth L1;
`evaluate_ate()` reports aligned mean translation error, not conventional ATE
RMSE. Do not relabel them. No new supplementary metric protocol is authorized
by this readiness task.

### Selection/sorting measurement condition

**VERIFIED FROM SOURCE:** `utils/bcgm.py` uses `torch.argsort` for candidate
ordering, while the Gate 1B worker's insertion host-call timer is
unsynchronized and wraps the broader `add_new_gaussians` call. Existing
tracking/mapping stage averages do not include this selection work in the
mapping FPS. Therefore selection/sorting cost cannot be reported as isolated
from the current logs. Before Gate 2, define a measurement-only timing method
(including synchronization/profiler overhead and its scope) or report only a
clearly named aggregate BCGM insertion overhead. Do not infer sorting cost
from mapping FPS.

## 4. Storage and GPU readiness

- **Storage, runtime observation:** `df -h .` showed a 916G filesystem with
  28G available (97% used). Existing Gate 1B model/evaluation directories
  occupy approximately 353 MiB (P4), 353 MiB (off), and 348 MiB (on) for 100
  frames each. Linear scaling of these outputs to 500 frames suggests about
  5.2 GiB total for three runs. This is an extrapolation only; Gaussian map
  growth, plots/checkpoints, logs and temporary files can change it. Current
  space appears adequate for the estimate but has a small safety margin
  relative to the nearly full filesystem. Recalculate a conservative budget,
  reserve space, and recheck immediately before execution.
- **Direct SSH host evidence (researcher supplied):** the query
  `nvidia-smi --query-gpu=index,name,memory.total,memory.used,utilization.gpu --format=csv,noheader`
  returned `0, NVIDIA GeForce RTX 5080, 16303 MiB, 818 MiB, 0 %`. The reported
  compute-process listing contains `7710, /usr/libexec/gnome-remote-desktop-daemon,
  264 MiB`. Record host GPU status as
  `HOST_VERIFIED_AT_OBSERVATION_TIME`. The observation timestamp was not
  included with the supplied output.
- **Sandboxed Codex evidence:** the earlier Codex `nvidia-smi` invocation
  could not communicate with the NVIDIA driver. Codex execution-environment
  GPU access remains `NOT_VERIFIED`; the host SSH observation does not prove
  GPU visibility from this sandbox.
- Disk was also reported from the SSH terminal as
  `/dev/sda2 916G 842G 28G 97% /`, consistent with the readiness check.
- No CUDA workload was created or run for this reconciliation. The direct
  host observation alone does not make Gate 2 execution ready.

## 5. Risks and blockers

1. Host GPU was verified at the supplied SSH observation time, but Codex
   execution-environment GPU access remains `NOT_VERIFIED`. Verify access from
   the actual execution environment and recheck device/process state before
   any experiment; do not treat the SSH observation alone as Gate 2 readiness.
2. Disk is 97% used. The 5.2 GiB projection is only approximate; ensure a
   conservative reserve and verify target output paths are distinct and
   writable without touching existing results.
3. Selection/sorting cost is not isolated by current instrumentation; define
   a timing protocol before claiming that metric.
4. BCGM Global Cap did not activate in Gate 1B and is expected to remain
   inactive in 500 frames. Gate 2 cannot establish its effect unless it
   actually binds.
5. Source and scientific changes remain uncommitted. Preserve the current
   worktree inventory and record hashes/config snapshots for each future run.
6. Gate 1B metric limitations persist: one run per arm; no statistical
   significance; no conventional Depth RMSE or true ATE RMSE.

## 6. Proposed next Codex action

Prepare the Gate 2 run contract only after checking GPU visibility in the
intended Codex execution environment, confirming environment identity,
conservative disk budgeting, source/config identity, output-path collisions,
and selection/sorting measurement design. Then stop for review before any
CUDA workload or run-directory creation.

**Gate 1B:** `PASS_WITH_LIMITATIONS`; **Gate 2:** `NOT_STARTED`
**GATE2_EXECUTION_NOT_STARTED**
