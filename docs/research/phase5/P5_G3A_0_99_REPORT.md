# SGS-SLAM Phase 5 — P5-G3A Bounded Profiling Report

Status: `BLOCKED_P5_G3A`

## Contract

- Scene: Replica `room0`
- Frame horizon: `0–99` inclusive, 100 frames
- Seed: `0`
- Conditions: C0 `off`, C1 `light`, C2 `detailed`
- P5-G2 implementation commit: `0118d2cf99bf1fe089f34dea20696ac71101b30d`
- Phase 4 reference commit: `37522db553ff18b96592073f9de699db7fa48600`

## Preflight result

The pre-run snapshot was recorded at:

`results/runtime_artifacts/phase5_profiling/p5_g3a_room0_0_99/comparison/pre_run_system_state.log`

It reports:

- Python 3.10.22
- PyTorch `2.7.1+cu128`
- PyTorch CUDA build `12.8`
- `torch.cuda.is_available() == False`
- `torch.cuda.is_initialized() == False`
- `torch.cuda.device_count() == 0`
- `nvidia-smi`: failed to communicate with the NVIDIA driver

No condition was launched. This avoids treating a CPU fallback or an unavailable CUDA runtime as bounded GPU validation.

## Gate decision

`BLOCKED_P5_G3A`: the required CUDA runtime is unavailable before C0, so C0/C1/C2 cannot be compared under the specified hardware contract. No runtime, Gaussian, keyframe, memory, H2D, equivalence, or overhead result exists for this gate.

The blocker evidence and immutable source/config hashes are in:

- `results/runtime_artifacts/phase5_profiling/p5_g3a_room0_0_99/comparison/blocker.json`
- `results/runtime_artifacts/phase5_profiling/p5_g3a_room0_0_99/comparison/source_hashes.json`

The per-condition directories and immutable configs were created, but contain no SLAM outputs because no run was started. No frame beyond 99 was processed.

## Required recovery

Restore the compatible NVIDIA driver/GPU runtime, rerun the preflight snapshot, confirm `torch.cuda.is_available() == True` and a stable device count, then execute fresh unique C0/C1/C2 run IDs. Do not reuse this blocked run directory or infer profiling validity from it.
