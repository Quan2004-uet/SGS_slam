# Current Session Handoff

> **CURRENT OPERATIONAL HANDOFF AUTHORITY.** Use `PROJECT_STATUS.md` for project-wide state. Repository/runtime evidence overrides either document.

Last reconciled: 2026-10-14.

## Session and Git State

- Session ID: `SESSION_005`.
- Title: Phase 4 Final Experimental Synthesis and Closure.
- Status: `CLOSED`.
- Started/closed: 2026-10-14.
- Branch: `phase4-vb-001-cpu-keyframe-offload`.
- Experimental evidence / pre-closure-commit HEAD: `507aea652a5da15c92d358c19b8d6705c510242b`.
- Closure status: `PASS_PHASE4_CLOSURE`.
- Closure package: `results/runtime_artifacts/phase4_closure/`.
- No commit, push, tag, checkout, reset, stash, experiment, renderer evaluation, metric recomputation, or source/config change was performed by closure.

The worktree contains the intentionally uncommitted Phase 4 documentation and visualization artifacts. The unrelated untracked `vds` entry was not touched. Inspect `git status --short` before any later work.

## Closed Boundary

Phase 4 — CPU Keyframe Offload / Reproducible Memory Baseline Variant is **COMPLETE**. `PHASE4-VB-001` and all visualization gates V1, V2, V3A, V3B, and V3C are complete. The next phase is **PLANNED / NOT STARTED**.

The unchanged Phase 3 baseline OOMed during mapping at frame 1294 after completing frames 0–1293. PHASE4-VB-001 completed frames 0–1999 on the tested RTX 5080 by moving archived `color`, `depth`, `semantic_id`, and `semantic_color` payload ownership to CPU while retaining `est_w2c` on GPU and synchronously staging selected observations.

## Authoritative Final State

- Checkpoint: `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.npz`.
- RGB PLY: `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/params.ply`.
- Semantic PLY: `experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/seg_params.ply`.
- Checkpoint SHA256: `dc6f94cf24ff2ed4d3f8220d05586d321dbc5ad425cb5d5cba73a31aa90f88f2`.
- RGB PLY SHA256: `d9b4d22ba11c73f8c1d6d0ea5f874bbb5d3254f25b333362a502a5940f604502`.
- Semantic PLY SHA256: `6cd5a258a8147fe0c0515d04ea702d618f82c2411fc464ab9bfebd2fc2f3b726`.

Detailed memory run: peak GPU allocated/reserved 6,774,482,432 / 8,009,023,488 B; final CPU archive 10,497,024,000 B; persistent archived GPU payload 0 B; 402 keyframes; 2,000 frames; runtime 22,299.70758857 s.

Separate output-save run: runtime 14,173.47515856901 s; peak GPU allocated/reserved 5,817,509,888 / 7,189,037,056 B; final 4,956,467 Gaussians. Do not combine metrics between these independently instrumented runs without attribution.

## Final Quality Evidence

- E4: `results/runtime_artifacts/phase4_vb001_eval_e4_full_released/`.
- PSNR 33.313067015269745 dB; MS-SSIM 0.9794702553689628; LPIPS-Alex 0.06755526393577642.
- Depth L1 0.004951576771391114 m.
- Semantic-color mIoU 0.9165854801076707 under released GT-palette-assisted recoloring.
- Released Horn-aligned mean error 0.002740748680388891 m; supplementary true RMSE 0.003398270593244735 m.
- V2 is observed-camera qualitative evidence. V3A–V3C package virtual diagnostics and presentation figures; they do not establish novel-view accuracy.

## Closure Records

Read these first if Phase 4 evidence is needed:

```text
results/runtime_artifacts/phase4_closure/PHASE4_CLOSURE_REPORT.md
results/runtime_artifacts/phase4_closure/FINAL_EVIDENCE_INDEX.md
results/runtime_artifacts/phase4_closure/FINAL_METRICS_SUMMARY.md
results/runtime_artifacts/phase4_closure/BASELINE_VS_VARIANT_TABLE.csv
results/runtime_artifacts/phase4_closure/FINAL_LIMITATIONS.md
results/runtime_artifacts/phase4_closure/NEXT_PHASE_RECOMMENDATION.md
results/runtime_artifacts/phase4_closure/metadata/closure_manifest.json
```

## Next Authorized Work

No next phase has started. On explicit authorization, open a new session and select one isolated objective. Recommended first gate: multi-scene validation of unchanged PHASE4-VB-001 using the same memory and quality protocols. Transport optimization should follow as a separate systems experiment with isolated staging latency, wall time, GPU memory, CPU archive, completion, and quality checks.

## STOPPED HERE

Stop at `PASS_PHASE4_CLOSURE`. Do not rerun Phase 4, begin Phase 5, modify the checkpoint, or implement the recommended optimizations automatically.
