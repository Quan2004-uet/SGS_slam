# Phase 3 Baseline Closure — 2026-10-10

## Decision

Close Phase 3 baseline runtime reproduction on RTX 5080 16GB with a
documented memory limitation.

## Evidence summary

- Destination-host validation on RTX 5080: PASS.
- Phase 3C-4 bounded online reproduction 0–99: PASS.
- Phase 3C-6 bounded online reproduction 0–499: PASS.
- Full-scene baseline attempt 0–1999: `CUDA_OOM`; completed only 0–1293,
  with OOM during mapping around frame 1294.
- Runtime-only allocator/low-overhead attempt: `CUDA_OOM_ALLOCATOR_OPT`;
  completed only 0–1332, with OOM during mapping around frame 1333.
- Allocator-only optimization improved the completed horizon by about 39
  frames but did not complete the full scene.
- Released source/config/algorithm remained unchanged.
- No evaluation, ATE, rendering metrics, post-SLAM optimization, or
  paper-metric comparison was run.

Primary evidence:

- `results/runtime_artifacts/server_validation_2026-10-09/`
- `results/runtime_artifacts/phase3c4/`
- `results/runtime_artifacts/phase3c6/`
- `results/runtime_artifacts/full_scene_room0/`
- `results/runtime_artifacts/full_scene_room0_allocator_opt_fast/`
- `docs/experiments/FULL_SCENE_MEMORY_OPTIMIZATION_LOG.md`
- `docs/experiments/PHASE3_RUNTIME_CONCLUSION_2026-10-10.md`

The runtime records were produced at Git HEAD
`dd8caa772bd9511c018d298e38c081a679de2c72`. At closure-document creation,
the repository was on `main` at HEAD
`108d73e7367059a85010e2c19f48419cb3a2741f` with a clean worktree. A scoped
comparison against released baseline commit
`e4183986204242a8bb422624618af07780a49d26` found no changes under
`scripts/`, `utils/`, `datasets/`, or `configs/`.

## Conclusion

- Released SGS-SLAM online baseline is runtime-verified on this server through
  bounded prefixes up to 0–499.
- Released full Replica `room0` 0–1999 baseline did not complete on RTX 5080
  16GB.
- Runtime-only allocator optimization is insufficient to complete full
  `room0` on this 16GB GPU.
- Full-scene completion likely requires either larger VRAM or an explicitly
  authorized memory-management research variant.
- Any CPU offload, bounded GPU keyframe residency, optimizer-state offload,
  keyframe eviction, reduced resolution, reduced iterations, changed keyframe
  policy, or modified renderer behavior must be classified as a new research
  variant, not pure baseline reproduction.

## What remains unproven

- Paper metrics are not reproduced.
- Full-scene PASS is not achieved on RTX 5080 16GB.
- Evaluation, post-SLAM optimization, and paper comparison have not been run.
- A memory-management variant has not yet been validated.

## Next state

- Baseline runtime reproduction is closed with memory limitation.
- Next recommended phase: Phase 4 memory-management analysis and variant
  design, if authorized.
