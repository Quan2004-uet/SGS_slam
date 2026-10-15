# P5-G2 CPU and Static Test Report

Status: `PASS_P5_G2_CPU_STATIC`

## Environment and command

The first attempted invocation used system Python and collected no tests because that interpreter lacks PyTorch. No dependency was installed. Tests were then run with the Phase 4 environment while hiding all GPUs:

```bash
CUDA_VISIBLE_DEVICES='' /home/robot/miniconda3/envs/sgs_slam_5080/bin/python \
  -m unittest -v tests.test_performance_profiler
```

Final result: **20 tests run, 20 passed, 0 failed**, approximately 0.009 s. `torch.cuda.is_initialized()` was false. Python compilation also passed for the profiler, SLAM integration, profiling config and test module.

## Covered contracts

1. Missing profiling section produces the OFF/null profiler without even querying CUDA.
2. OFF creates no output and records nothing.
3. Valid mode parsing and invalid mode/interval rejection.
4. JSONL record schema validation.
5. JSONL streaming/readback and summary aggregation.
6. Deterministic index-based sampling.
7. CPU tensor storage de-duplication across aliases/views.
8. Python/NumPy/PyTorch RNG states unchanged.
9. Input profiling config not mutated.
10. Run metadata integrity and explicit pending-CUDA label.
11. Bounded write buffer and summary reservoir.
12. Safe context cleanup and failed status after exception.
13. Existing output directory cannot be overwritten.
14. Archive/staging counters, state sampling, RSS and metadata estimate.
15. Released Replica config and active keyframe-selection source hashes unchanged.
16. CUDA remains uninitialized.
17. Summary schema validation.
18. Run-metadata schema validation.
19. Profiling config wrapper preserves all base hyperparameters and defaults OFF.
20. Git/config reproducibility metadata generation without config mutation.

## Static source integrity

- `git diff --check`: pass.
- `scripts/slam.py`: instrumentation imports, optional arguments and surrounding hooks only.
- `configs/replica/slam.py`: unchanged.
- `utils/keyframe_selection.py`: unchanged.
- `utils/slam_external.py`: unchanged.
- No Phase 4 artifact/checkpoint/result file modified.
- `vds` hash remains `14579ca54c2c25514b385cf48beb5b68d6869a5418d27e3386ee840efbc2e92e`.

## Explicitly unvalidated

- `PENDING_P5_G3_CUDA_VALIDATION`: CUDA event accuracy and stream ordering.
- `PENDING_P5_G3_CUDA_VALIDATION`: OFF/light/detailed numerical and selected-keyframe trace equivalence under online execution.
- `PENDING_P5_G3_CUDA_VALIDATION`: instrumentation overhead and telemetry volume.
- `PENDING_P5_G3_CUDA_VALIDATION`: GPU allocator attribution and deferred-event lifetime in practice.

CPU mocks/static inspection do not constitute runtime validation.
