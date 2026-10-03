# Durable Decisions

- **D-001:** Preserve the released baseline during Phase 3; separate compatibility recovery from algorithm changes.
- **D-002:** Use the runtime-verified environment at `/home/quan/miniconda3/envs/sgs_slam_baseline`.
- **D-003:** Retain NumPy 1.26.4 with `opencv-python` 4.9.0.80 unless explicit evidence requires a change. See [compatibility recovery](../baseline_reproduction/runtime/09_opencv_numpy_recovery.md).
- **D-004:** Use the recovered, maintainer-distributed Replica package. See [provenance record](../baseline_reproduction/runtime/08_dataset_recovery.md).
- **D-005:** Use continuous bounded prefixes before full `room0`; choose the next horizon from measured results.
- **D-006:** Preserve runtime JSON and logs outside `/tmp`; the Phase 3C-3 pair is under `results/runtime_artifacts/phase3c3/`.
- **D-007:** Fast instrumentation may reduce logging overhead but must preserve algorithmic settings.
- **D-008:** Do not optimize memory, optimizer behavior, or keyframes during baseline reproduction.
