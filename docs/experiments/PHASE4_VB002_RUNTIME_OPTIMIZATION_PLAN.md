# PHASE4-VB002 Runtime Optimization Plan

Date: 2026-10-11  
Repository: `/home/robot/research/SGS_slam`  
Planning branch: `phase4-vb-001-cpu-keyframe-offload`  
Planning HEAD: `ecb2ae67b073fe7002df6cda76999a18e603a901`  
Predecessor: `PHASE4-VB-001` — CPU offload of resident keyframe payloads

This is a source- and existing-evidence-only plan. No experiment, CUDA
workload, full scene, evaluation, source/config/algorithm edit, commit, or push
was performed while preparing it.

## 1. Current runtime problem

PHASE4-VB-001 solved the measured VRAM-capacity problem: the online Replica
`room0` loop completed frames 0–1999 with corrected classification
`PASS_RUNTIME_VALIDATOR_BUG`, zero persistent GPU archived-payload bytes, and
no OOM. However, the continuous run took **22,299.70758857 seconds**, or about
**6 h 11 m 39.708 s**.

That turnaround is too slow for routine repetition. The previous run also did
not preserve `params.npz`, the final map, camera trajectory, or a checkpoint,
so at least one output-saving full-scene run is still needed before evaluation.
Repeating six-hour runs to repair output handling, validate a runtime variant,
or prepare evaluation would be expensive and would make failures near the end
particularly costly.

The source-reported averages at full-scene completion were:

- tracking: 74.514 ms/iteration and 2.980 s/frame;
- mapping: 132.905 ms/iteration and 7.975 s/frame.

These aggregate timings place most elapsed time inside tracking and mapping,
with mapping the larger component. They do not isolate renderer, backward,
optimizer, pruning, transfer, or instrumentation time.

## 2. Runtime bottleneck hypotheses

| Hypothesis | Evidence classification | Assessment |
|---|---|---|
| Repeated synchronous CPU→GPU staging | **RUNTIME VERIFIED** for occurrence and volume; contribution to runtime is **UNKNOWN** | VB001 stages an archived payload after every archived-view selection inside the mapping loop. The full scene recorded 114,404 synchronous staging events and 2,987,317,248,000 transferred bytes. Transfer time was not separately measured. |
| Mapping loop: 60 iterations per frame | **RUNTIME VERIFIED** | The released config maps every frame for 60 iterations: 120,000 iterations over 2,000 frames. Average mapping time was 7.975 s/frame, about 15,949 s when multiplied by 2,000 frames. This aggregate includes staging, rendering, loss, backward, pruning, and optimizer work. |
| Renderer/autograd cost | **INFERRED** as a major cost; isolated share **UNKNOWN** | Every tracking/mapping iteration executes renderer-based loss work; optimization iterations also execute backward and optimizer updates. No stage-level CUDA profile or renderer-only timing exists. |
| Logging and JSON trace overhead | **RUNTIME VERIFIED** for instrumentation volume; runtime share **UNKNOWN** | The harness captured per-iteration losses, 120,000 prune-hook records, 114,404 stage records, optimizer snapshots, and per-frame tensor/residency checks. The final JSON is 85,779,475 B and the log is 12,615,625 B. Final JSON serialization occurs after the recorded run timer, but per-iteration Python bookkeeping and scalar extraction occur during it. |
| CPU archive/RSS pressure | **RUNTIME VERIFIED** for memory growth; slowdown **INFERRED/UNKNOWN** | Final CPU archive was 10,497,024,000 B; maximum RSS/HWM was 13,529,231,360 / 13,583,106,048 B. This can increase memory-bandwidth and page pressure, but no swap, page-fault, or CPU-memory-bandwidth profile was recorded. |
| Lack of GPU cache | **VERIFIED FROM SOURCE AND RUNTIME**; speed impact **INFERRED** | VB001 deliberately has no persistent GPU payload cache. Persistent GPU archived payload remained 0 B and repeated selection triggers repeated transfer. The actual cache speedup requires bounded measurement. |
| Lack of pinned memory and non-blocking transfer | **VERIFIED FROM SOURCE**; benefit **UNKNOWN** | Archival uses ordinary CPU tensors and staging explicitly uses `non_blocking=False`. Pinned memory and asynchronous copies could improve transfer overlap, but no transfer timing exists and they change the declared transfer semantics. |

The strongest actionable evidence is transfer repetition, not proof that PCIe
transfer alone dominates total runtime. Any speedup estimate must remain a
hypothesis until a bounded timing gate isolates it.

## 3. Evidence table

| Evidence | Gate 4, 0–499 | Gate 5, 0–999 | Full scene, 0–1999 |
|---|---:|---:|---:|
| Status | `PASS_FRAME_LIMIT` | `PASS_FRAME_LIMIT` | `PASS_RUNTIME_VALIDATOR_BUG` after audit; original harness says `FAIL_RUNTIME` |
| Runtime (s) | 2,564.527928634 | 7,183.993467400001 | 22,299.70758857 |
| Final Gaussians | 2,255,038 | 4,411,916 | 4,983,660 |
| Logical keyframes | 101 | 201 | 402 |
| CPU archive (B) | 2,637,312,000 | 5,248,512,000 | 10,497,024,000 |
| Persistent GPU archived payload (B) | 0 | 0 | 0 |
| Max GPU allocated (B) | 3,468,590,592 | 5,958,148,096 | 6,774,482,432 |
| Max GPU reserved (B) | 4,525,654,016 | 6,949,961,728 | 8,009,023,488 |
| Max RSS / HWM (B) | 5,101,789,184 / 5,115,858,944 | 7,905,923,072 / 7,957,504,000 | 13,529,231,360 / 13,583,106,048 |
| Mapping iterations | 30,000 | 60,000 | 120,000 |
| Staging events | 28,141 | 56,876 | 114,404 |
| Total staged bytes | 734,817,792,000 | 1,485,146,112,000 | 2,987,317,248,000 |
| Peak/single payload (B) | 26,112,000 | 26,112,000 | 26,112,000 |

The full-scene archived-view selection rate was 114,404 / 120,000 mapping
iterations, or approximately 95.34%. Thus almost every mapping iteration
performed one 26,112,000 B synchronous transfer in VB001.

### Offline trace projection for cache sizing

The saved full-scene ordered `stage_events` trace was replayed with a simple
read-only LRU simulation. This is **TRACE-DERIVED / NOT A RUNTIME
MEASUREMENT**. It preserves the recorded selection order and counts a transfer
only on a simulated cache miss.

| Cache entries | Nominal payload VRAM | Trace hits | Hit rate | Projected miss-transfer bytes |
|---:|---:|---:|---:|---:|
| 4 | 104,448,000 B (~99.6 MiB) | 20,747 | 18.13% | 2,445,571,584,000 B |
| 8 | 208,896,000 B (~199.2 MiB) | 39,143 | 34.21% | 1,965,215,232,000 B |
| 16 | 417,792,000 B (~398.4 MiB) | 68,523 | 59.90% | 1,198,044,672,000 B |
| 24 | 626,688,000 B (~597.7 MiB) | 80,773 | 70.60% | 878,172,672,000 B |

The same trace contains at most 23 archived views in a 24-view mapping window.
Pre-staging every selected archived view once per frame would have produced
44,734 payload stages, or 1,168,094,208,000 B, before accounting for views that
were selected into the window but never sampled. Staging only unique archived
views actually sampled per frame would be 41,364 stages, but knowing that set
in advance would require changing or precomputing the random draw sequence.

These projections show reuse opportunity. They do not predict wall-clock
speedup because renderer/autograd cost and transfer/compute overlap are not
isolated.

## 4. Candidate runtime variants

### A. Low-overhead output-save run

Purpose: obtain the missing final map and trajectory with the smallest
scientific change.

- Keep PHASE4-VB-001 source, config, synchronous one-payload staging, CPU
  authority, logical keyframes, RNG, and optimizer behavior unchanged.
- Replace the heavy diagnostic harness with sampled memory/residency records
  and essential failure guards. Avoid retaining every loss, prune call, stage
  event, optimizer snapshot, and full ordered trace when already established by
  the prior full-scene evidence.
- Block the real evaluator with a no-op boundary that returns to the released
  final metadata/save path, rather than raising before `save_params(...)`.
- Save and verify final `params.npz`, map/Gaussian state, semantic state,
  estimated camera trajectory, GT trajectory metadata, and keyframe indices.
- Review whether PLY generation is required; output policy must be explicit and
  must not silently alter numerical state.
- Expected speedup: **UNKNOWN, low-to-medium**. The harness does substantial
  per-iteration bookkeeping, but the renderer/mapping workload remains.
- Risk: **low**. The principal risk is an incorrect save/evaluation boundary,
  not an algorithm change.

This remains VB001 if only harness validation/logging and output handling are
changed and the executed online algorithm is unchanged.

### B. Bounded GPU keyframe payload cache

Purpose: avoid repeat transfers while retaining the CPU archive as authority.

- Create a new research variant: **PHASE4-VB002**. A persistent GPU cache is
  explicitly outside VB001 invariants.
- Keep every logical keyframe and authoritative payload in the CPU archive.
- Perform the unchanged mapping-window construction and random selected-view
  draw first; use the exact selected keyframe ID as the cache key.
- On hit, reuse the cached GPU payload. On miss, synchronously stage that one
  payload and insert it into a bounded LRU. Do not add RNG calls.
- Do not alter archive IDs/order, candidate set, selected IDs, current-frame
  sentinel, keyframe cadence, losses, renderer, iteration counts, precision,
  pruning, or Gaussian lifecycle.
- Candidate capacities: 4, 8, 16, and 24 keyframes.
- Nominal payload cost is `cache_size × 26,112,000 B`, shown in the trace table.
  Allocator and renderer overlap mean actual peak must be measured rather than
  inferred by simple addition.
- Expected speedup: **potentially high if transfer is material**, with realized
  speedup currently **UNKNOWN**. The trace predicts 18.1–70.6% cache-hit rates.
- Risk: **medium**. Cache lifetime, eviction, device ownership, cleanup,
  memory peaks, and accidental semantic/RNG changes require explicit guards.

Capacity 16 is the recommended first design point: trace-derived hit rate is
about 59.9% for ~417.8 MB nominal payload VRAM. Capacity 24 adds ~208.9 MB over
capacity 16 for another ~10.7 percentage points of trace hit rate. This is a
planning tradeoff, not an acceptance result.

### C. Mapping-window pre-stage cache

Purpose: stage selected-window payloads once per mapping phase and reuse them
across its 60 iterations.

- Run the unchanged mapping-window selection first.
- Stage each selected archived payload once, retain it only for that frame's
  mapping phase, and free the complete window after mapping.
- Preserve the exact random index draws and selected IDs inside the 60-iteration
  loop. Do not precompute or reorder RNG draws merely to optimize staging.
- Mapping window size is 24: up to 23 archived views plus the current-frame
  sentinel. Worst-case payload residency is approximately
  `23 × 26,112,000 = 600,576,000 B`, excluding allocator overhead.
- Existing trace projection: 44,734 window payload stages and about 1.168 TB
  transferred if every selected archived view is staged once.
- Expected speedup: **potentially high**, realized speedup **UNKNOWN**.
- Risk: **medium/high**. It changes simultaneous staged-payload lifetime,
  stages views that may not be sampled, and can accidentally alter selection or
  RNG semantics if implemented carelessly.

This is a separate research variant or named VB002 subvariant, not VB001.

### D. Pinned memory plus non-blocking transfer

- Allocate archived payloads in pinned CPU memory and use non-blocking copies,
  with explicit stream/lifetime synchronization.
- Potential benefit: reduce copy latency or overlap transfer with compute.
- Expected speedup: **UNKNOWN** until transfer timing is isolated.
- Risk: **medium**. It changes transfer semantics, CPU memory behavior, and
  lifetime/synchronization requirements.
- Keep it as a separate variant. Do not combine it with the first cache test;
  otherwise cache and transfer-mode effects cannot be attributed.

### E. Larger-VRAM infrastructure

- Run the released residency model or a less aggressive offload policy on a
  GPU with sufficient VRAM.
- Algorithm risk: **low**; infrastructure cost and availability: **high**.
- Advantages: avoids cache design complexity and can provide a pure released
  baseline if the device fits the full scene.
- Limitations: hardware changes reduce direct runtime comparability with the
  RTX 5080 evidence, and capacity/speed must still be established by a
  separately authorized run.

### F. Algorithm-changing speedups

The following can reduce runtime but change the executed method:

- reduce mapping iterations;
- reduce tracking iterations;
- reduce image/depth/semantic resolution;
- disable or reduce semantic rendering;
- change keyframe cadence or mapping-window policy.

Risk: **high**. Do not use these before a saved-output evaluation baseline is
established. They require separate method IDs, controlled ablations, and new
metric validation; they are not runtime-equivalent VB001/VB002 optimizations.

## 5. Recommended next step

### Recommendation: option D — low-overhead output-saving run first

The safest near-term path is to design and audit the low-overhead output-saving
harness, then execute one separately authorized VB001 full-scene output-saving
run. This obtains the missing evaluation baseline while changing only
instrumentation and save-boundary behavior. It avoids evaluating a new cache
variant before any VB001 final map exists.

Expected tradeoff:

- speed: **unknown, likely low-to-medium improvement** because diagnostic
  bookkeeping is reduced but the 120,000-iteration mapping workload remains;
- GPU memory: approximately VB001 behavior, plus transient output-saving costs;
- scientific risk: low;
- result: a saved VB001 final state suitable for a later, separately authorized
  evaluation gate.

In parallel at the design level, prepare PHASE4-VB002 with a 16-entry bounded
LRU cache. Do not put that cache into the immediate VB001 output-saving run.
After the VB001 outputs exist, validate VB002 through R1–R5 before its own
full-scene output-saving R6. If the overriding priority becomes avoiding any
likely six-hour VB001 rerun rather than preserving a VB001 evaluation baseline,
option B is the alternative, but that produces VB002—not VB001—outputs.

Options A–D from the decision question are therefore ranked:

1. **D — low-overhead output-saving run first**: recommended.
2. **B — implement VB002 bounded GPU cache first**: best next runtime research
   path after, or instead of D only if turnaround outweighs baseline purity.
3. **C — rent a larger-VRAM GPU**: useful for pure-baseline infrastructure,
   but costly and not directly comparable to current-host timing.
4. **A — rerun the heavy VB001 harness unchanged**: not recommended; it
   repeats known validation overhead and the broken save boundary.

## 6. Validation gates for runtime optimization

### Gate R1 — static/source audit

- Name the variant and isolate its change from VB001.
- Prove CPU archive authority, cache key/eviction/lifetime rules, unchanged
  selection/RNG path, and unchanged config contract.
- Define output-save boundary and evaluator suppression separately.

### Gate R2 — dataset[0] plus cache invariants

- Verify payload equality before/after archive, cache miss, cache hit, eviction,
  and restaging.
- Verify dtype, shape, device, semantic IDs/colors, and `est_w2c` policy.
- Verify no added RNG calls and no logical keyframe mutation.

### Gate R3 — frames 0–99 timing/memory

- Compare VB001 and candidate using like-for-like lightweight instrumentation.
- Record cache hit/miss counts, transfer bytes/time if reliable, runtime,
  Gaussian/keyframe trajectory, peak GPU memory, RSS, finite state, and output
  cleanup.

### Gate R4 — frames 0–499 timing/memory

- Confirm material runtime trend and memory headroom at the established Phase
  3C-6 comparison boundary.
- Reject variants that alter logical keyframe IDs, iteration contract, or
  selected-view trace under controlled seed/order evidence.

### Gate R5 — frames 0–999 timing/memory

- Validate scaling, cache hit rate, CPU/GPU growth, finite state, and output
  policy against VB001 Gate 5.
- Select one cache capacity before full scene; do not choose retrospectively
  from full-scene results.

### Gate R6 — full-scene output-saving frames 0–1999

- Run exactly once after explicit authorization.
- Save and verify final params/map, semantic state, camera trajectory,
  keyframe IDs/indices, config/provenance, and checksums.
- Stop after output verification. Do not continue automatically to evaluation.

Evaluation is a separate gate and is prohibited until saved outputs exist and
are reviewed.

## 7. Acceptance criteria

- No CUDA OOM, NaN/Inf, residency violation, or source/config drift.
- Runtime is materially lower than the like-for-like VB001 gate. Define the
  numeric materiality threshold before R3; a provisional planning threshold is
  at least 20% wall-clock reduction at R4/R5, subject to measurement noise.
- GPU allocated/reserved memory remains below the predeclared safety threshold
  with renderer and cache peaks included. Do not accept nominal cache-size
  arithmetic as runtime proof.
- CPU archive remains authoritative for VB002; cache is bounded and fully
  auditable.
- Logical keyframe IDs/order/cadence, candidate set, selected IDs, current-frame
  sentinel, mapping window, tracking/mapping iteration counts, RNG policy,
  precision, resolution, renderer, losses, pruning, and Gaussian lifecycle are
  unchanged.
- Cache hit/miss/eviction counts and staged bytes are internally consistent;
  no stale or wrong-ID payload is used.
- No metric-equivalence or paper-result claim is made before the evaluation
  gate.
- An output-saving full-scene run must preserve and verify `params.npz` or an
  explicitly equivalent final map, camera trajectory, semantic state,
  keyframe indices, config, provenance, and checksums.

## 8. Decision summary

**Choose D: create and audit a low-overhead VB001 output-saving harness first.**
It has the lowest scientific risk and produces the missing baseline artifact.
Expect an unknown low-to-medium speed improvement with approximately VB001 GPU
memory behavior. Then pursue **PHASE4-VB002**, starting with a 16-entry bounded
GPU LRU cache, as the strongest evidence-backed runtime research candidate.
Its trace-projected tradeoff is ~417.8 MB nominal payload VRAM for ~59.9% cache
hits and a reduction in miss-transfer volume from ~2.987 TB to ~1.198 TB;
actual wall-clock speedup remains unknown until bounded gates run.

No evaluation or paper metrics are authorized or implied by this plan.
