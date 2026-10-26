# Phase 6 Room1 Gate 1 r02 Validator Diagnostic

Date: 2026-10-19  
Run: `p6_bam_ms_room1_gate1_0_49_r02`  
Frozen source: `002927f3b24dd69418c17da08bd4ae987bae9ee2`

## Root cause

**RUNTIME VERIFIED:** the original CPU validator failed at its PLY schema
assertion with this exact output and exit status:

```text
params.ply binary payload size/schema mismatch
exit code: 1
```

The validator required 18 float properties per vertex. The frozen PLY exporter
in `utils/convert_ply.py` constructs 17: xyz (3), normals (3), DC color
coefficients (3), opacity (1), scales (3), and rotations (4). Both
`params.ply` and `seg_params.ply` have 1,583,985 vertices and a binary payload
of 107,710,980 bytes, exactly `1,583,985 * 17 * 4`. The saved files therefore
match the frozen serializer; the expected property count in the validator was
wrong. This is a validator-side schema mismatch, not corrupted or incomplete
SLAM output.

## Minimal validator correction

Only the expected PLY float property count changed from 18 to 17 in the
untracked `tools/validate_phase6_room1_gate1_cpu.py`:

- Original validator SHA256: `94bb1b340f08991dd03beba8578eb8e9cf9874462daad13c0b04f9c6f97a69e4`
- Revised validator SHA256: `56e3ed967f4b71924bd6bd9313615c6b70f1a72f475eb47e047d422f198124d2`

The prior finite-value, Gaussian-count, pose-count, checkpoint, sidecar, and
binary payload integrity assertions remain enabled. The revised validator
returned exit 0, `PASS_CPU_INTEGRITY`, with 50 poses, 1,583,985 final
Gaussians, 12 final keyframes, and valid frame 0/49 checkpoint sidecars.

The original preparation checksum manifest is preserved unchanged. It passed
6/6 before this diagnostic correction; its validator entry records the
original validator hash. Source checksum verification remained 17/17, and the
frozen source and configuration were not changed.

## Saved artifact integrity

The following SHA256 values were recorded before the validator correction and
confirmed unchanged after CPU validation and offline evaluation:

| Artifact | SHA256 |
|---|---|
| `params.npz` | `56f2411a38b9ae44fe78c7da165f178b4b31a506dcb3ee9d163acc8e860dc425` |
| `params.ply` | `75f2fb92a6af7ec4bbbcdc8b029a32e33345738034d76e01766ca02306d7e8e5` |
| `seg_params.ply` | `189d04232c29a867dead52cb5493f6bbd2e6a064c0c2178b31d83b83bc508563` |
| `params0.npz` | `9b2cef7a37d470a79c1e1ec4b9628e38e7000e551bb9ceb4e628e594dbdcda51` |
| `params49.npz` | `053babcdb0818d72b0fbaec1ed7565da918198e6733cf8759b588758fdd9d73a` |
| `keyframe_time_indices0.npy` | `f6df0000bed676f0a4b777e2a1d915b6608dab452e11737f82c685cebf0e8ba7` |
| `keyframe_time_indices49.npy` | `29ab8caee75cf155be200c8e530285dc892f1721a588216e6855e69c757bc79f` |
| `effective_config.json` | `9916cd0cd8f3028580196a02c11c646451a451ce069a5dfa71b047da8ed42580` |

The run evidence inventory contains 63 entries and its recorded hashes verify.
The evaluation output has 54 artifacts plus its manifest; all 54 artifact
entries in `SHA256SUMS.txt` verify. The diagnostic directory also has a
four-entry checksum manifest for its four evidence files.

## Offline evaluation

After CPU validation passed, the approved saved-state evaluator rendered exactly
`[0,4,9,14,19,24,29,34,39,44,49]`. It evaluated the saved state only; SLAM
tracking and mapping were not called. A first invocation stopped before
evaluation because the Python import path omitted the frozen worktree root
(`ModuleNotFoundError: No module named 'datasets'`). It created no evaluation
output. The successful invocation supplied that root in `PYTHONPATH`.

| Metric | Result |
|---|---:|
| PSNR | 41.825503 dB |
| MS-SSIM | 0.995158 |
| LPIPS-Alex | 0.025577 |
| Depth L1 | 0.00140345 m |
| Semantic-color mIoU | 0.919817 |
| ATE Mean, 50 poses | 0.00121016 m |
| True ATE RMSE, 50 poses | 0.00170726 m |

Image metrics are the unweighted mean over the 11 selected views. ATE uses
Horn rigid rotation and translation alignment with no scale.

## Evidence locations and disposition

- Machine-readable diagnostic, original failure, CPU validator result, and
  diagnostic checksums:
  `results/runtime_artifacts/phase6_bam/validator_diagnostics/p6_bam_ms_room1_gate1_0_49_r02/`
- Evaluation renders, metric files, and checksum manifest:
  `results/runtime_artifacts/phase6_bam/evaluation/p6_bam_ms_room1_gate1_0_49_r02_offline/`
- Main gate report: [PHASE6_MULTISCENE_ROOM1_GATE1_REPORT.md](PHASE6_MULTISCENE_ROOM1_GATE1_REPORT.md)

**Gate 1: PASS. Gate 2: NO-GO pending separate authorization and review.** No
SLAM rerun, Gate 2, full-scene evaluation, commit, or push was performed.
