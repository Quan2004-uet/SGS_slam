# P5-LEAN Bottleneck Assessment

## Evidence-backed observations

- **OBSERVED:** Retry1 DETAILED recorded 149.24 s tracking wall and 231.11 s mapping wall over 100 frames. Mapping is the largest observed stage and therefore the best three-week optimization target.
- **OBSERVED:** H2D staging recorded 10.44 s wall, 0.661 s sampled GPU-event time, 135.52 GB and 5,190 events. H2D is nested inside mapping; these values must not be added to mapping time as an independent category.
- **OBSERVED:** LIGHT and DETAILED online progress were about 385–386 s, while profiler wall summaries were about 408–409 s. These are single-run, differently bounded clocks, not a stable overhead estimate.
- **OBSERVED:** Mapping selection averaged about 2.10 ms per frame in the old diagnostic summary, far below total mapping wall time. This does not prove that every selected observation is useful.
- **OBSERVED:** CPU archive reached 574.464 MB at 22 keyframes by frame 99. Phase 4 full-scene archive reached 10.497 GB.
- **NOT_VALIDATED:** Incomplete DETAILED CUDA spans cannot support a complete render/loss/backward/optimizer percentage breakdown.

## Decision

Prioritize reducing mapping iterations while leaving tracking, keyframe policy, CPU offload, Gaussian append, losses, and learning rates unchanged. Transfer optimization is optional future work: the existing evidence shows large traffic but does not show that transfer dominates runtime.

The preferred initial method is novelty-aware mapping budget allocation using the already-produced Gaussian append count. It avoids new renders and avoids reading a CUDA loss scalar every iteration. A fixed-budget variant is mandatory as the control.

This is a **HYPOTHESIS**, not an observed speedup or quality result.
