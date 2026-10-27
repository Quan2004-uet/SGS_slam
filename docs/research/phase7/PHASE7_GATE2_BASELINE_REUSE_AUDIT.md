# Phase 7 Gate 2 — Phase 4 baseline reuse audit

**Date:** 2026-10-27
**Session:** `SESSION_005` — ACTIVE
**Decision:** Phase 4 Gate 4 may be reused as a contextual 0–499 CPU Keyframe
Offload reference for runtime, memory, and Gaussian count. It cannot serve as
a matched quality comparison because evaluation, saved parameters, and the
estimated trajectory are absent. No Phase 4 rerun is scheduled by this audit.

## 1. Artifact discovery and identity

The requested path exists and contains:

- `results/runtime_artifacts/phase4_vb001_gate4_0_499/PHASE4_VB001_GATE4_SUMMARY.md`
- `results/runtime_artifacts/phase4_vb001_gate4_0_499/phase4_vb001_gate4_0_499.log`
- `results/runtime_artifacts/phase4_vb001_gate4_0_499/phase4_vb001_gate4_0_499_results.json`

Current SHA256 values:

| Artifact | SHA256 |
|---|---|
| Summary | `494bb6f6193efdf998c86a85b4b3888e43171c3cffc975a693fafded1255a294` |
| Log | `f68bbf00c57c8e7479b04061974f1922850816eb276b81173b6e0a6084ffb6e1` |
| Results JSON | `34020162de8529fdc9950b10747673dac524e15ee02775a89946f7aa0bed7709` |

No `experiments/Replica` output directory for this Gate 4 run was found. Its
runtime overrides say `save_checkpoints=false`, `workdir=/tmp/...`, and
`report_progress` suppressed to prohibit evaluation/rendering metrics. The
temporary harness path recorded in the JSON is no longer present. The
separate Phase 4 full-scene output-save artifact
`experiments/Replica/room0_phase4_vb001_minimal_output_save_full_0_1999/`
contains a 0–1999 checkpoint and is not this 0–499 run; it is not substituted
for Gate 4 metrics or copied into Gate 2.

### Source identity

**VERIFIED FROM RUN RECORD:** Gate 4 ran on branch
`phase4-vb-001-cpu-keyframe-offload`, HEAD
`443d3d3251f0ac8d3e0e5489507fe13b506110a4`, with an uncommitted
`scripts/slam.py` diff whose recorded SHA256 is
`d0ac4ffa33768189d6889db78444caea992cc4c9082c733e5c7961355c1c6e5c` and whose
scope was classified by that run's harness as PHASE4-VB-001 only. It recorded
no config changes.

The frozen Phase 4 worktree currently points to
`68f9060f7ff4d8d141be1d5f71339401327edd06`; its `scripts/slam.py` SHA256 is
`a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3` and base
Replica config SHA256 is
`08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3`.
The Gate 4 run did not record the complete effective `scripts/slam.py` file
hash, and its original temporary harness is unavailable. Thus the run is
verified as the CPU-offload variant, but exact byte-for-byte equivalence of
its effective online source to the frozen Phase 4 source is
`COMPARABLE_WITH_LIMITATIONS`, not established. Preserve both identities in
any comparison; do not relabel Gate 4 as unmodified Phase 4.

Phase 7's current online source and BCGM module identities are unchanged from
Gate 1B: `scripts/slam.py`
`ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999`,
`utils/bcgm.py`
`8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400`. Gate 2
will use this Phase 7 source, which carries the CPU Keyframe Offload helpers,
plus the unchanged BCGM admission algorithm.

## 2. Dataset, interval, and scientific settings

Gate 4 JSON records `ReplicaDataset`, sequence `room0`, 2,000-frame dataset,
resolution 1200×680, seed 0, and processed indices exactly 0–499. The loader
guard intercepted index 500 before real dataset loading. Initial Gaussian
count was 815,998; final frame-499 count was 2,255,038. The effective settings
recorded in the JSON include `map_every=1`, `keyframe_every=5`, mapping window
24, tracking iterations 40, mapping iterations 60, semantic loading on,
pixel-driven Gaussian addition on, pruning on, and gradient clone/split
densification off. Runtime totals were 19,960 tracking iterations and 30,000
mapping iterations. The Phase 4 CPU archive held 2,637,312,000 bytes
(2.456 GiB); persistent GPU archived keyframe payload was 0 bytes. These
records verify the requested Phase 4 CPU-offload behavior over this prefix.

The JSON preserves source-reconstructed scientific settings and states that
config changes were not detected, but it does not preserve a complete copied
effective config or config-file hash. Dataset images are not individually
hashed in this Gate 4 bundle. The exact effective settings are therefore
`COMPARABLE_WITH_LIMITATIONS` rather than a complete config/dataset lock.

## 3. Metric availability and comparability

Labels below distinguish artifact presence from suitability as a matched
Gate 2 comparison.

| Quantity | Gate 4 evidence | Classification for Gate 2 comparison |
|---|---|---|
| Dataset/frame IDs | `room0`, processed 0–499, guard stopped before loading 500 | `VERIFIED_COMPARABLE` for scene and interval; input-file byte identity is not locked by this bundle |
| Seed/scientific settings | Seed 0; 1200×680; 40 tracking / 60 mapping iterations; keyframe 5; window 24; semantic and pixel insertion on; pruning on; densification off | `COMPARABLE_WITH_LIMITATIONS`; telemetry records settings, but no full effective config snapshot/hash |
| Frozen source identity | Runtime HEAD 443d3d… plus recorded PHASE4-VB-001 diff SHA; current frozen source at 68f906… | `COMPARABLE_WITH_LIMITATIONS`; effective runtime file SHA is absent |
| Completion/validator | `PASS_FRAME_LIMIT`; exactly 500 processed frames, final 499, index 500 intercepted pre-loader; not full-scene completion | `VERIFIED_COMPARABLE` as a bounded 500-frame result |
| Final Gaussian count | 2,255,038 at frame 499; from per-frame telemetry | `COMPARABLE_WITH_LIMITATIONS`; useful baseline count, but source provenance differs as above and BCGM changes insertion |
| Continuous runtime / derived throughput | 2,564.527929 s; 500 / runtime = 0.194968 frames/s | `COMPARABLE_WITH_LIMITATIONS`; Gate 4 disabled evaluation/save and recorded a continuous-run timer. It is not Gate 2's worker process wall/E2E scope; archived timer harness is unavailable |
| Tracking FPS | No aggregate tracking frame time/FPS in the JSON or log | `NOT_MEASURED` |
| Mapping FPS | No aggregate mapping frame time/FPS in the JSON or log | `NOT_MEASURED` |
| CUDA peak allocated | 3,468,590,592 B = 3,307.91 MiB | `COMPARABLE_WITH_LIMITATIONS`; allocator telemetry exists, but only same-scoped allocator values should be contrasted |
| CUDA peak reserved | 4,525,654,016 B = 4,316 MiB | `COMPARABLE_WITH_LIMITATIONS`; distinct from allocated and NVML |
| NVML sampled peak VRAM | No NVML samples/peak in report, log, or result JSON | `NOT_MEASURED` |
| BCGM candidate/admission/Event Cap counts | Gate 4 is BCGM-free Phase 4; no BCGM candidate stream | `NOT_COMPARABLE`; Gate 1B supplies bounded BCGM behavior evidence instead |
| RGB PSNR / MS-SSIM / LPIPS | Evaluation/rendering hooks suppressed; no `eval/` arrays or model output for this run | `NOT_MEASURED` |
| Depth L1 | No depth evaluation arrays; saved evaluator not run | `NOT_MEASURED` |
| Semantic mIoU | No semantic evaluation arrays; finite semantic tensors are not mIoU | `NOT_MEASURED` |
| Estimated trajectory / ATE | No estimated-pose/checkpoint artifact for Gate 4 and ATE hook not entered | `NOT_MEASURED` |

The Gate 4 run therefore cannot support Gate 2 claims about RGB/depth/semantic
quality or trajectory accuracy, nor direct process-wall comparison. Gate 1B
provides 100-frame saved-evaluator metrics and BCGM-off parity evidence only;
those values are not a substitute for 500-frame Phase 4 quality metrics.

## 4. Gate 1B evidence reused (no rerun)

Read and retained as final `PASS_WITH_LIMITATIONS`:

- `PHASE7_GATE1B_FINAL_VALIDATION_REPORT.md`
- `PHASE7_GATE1B_METRIC_COMPARISON.md`
- `PHASE7_GATE1B_EVIDENCE_MANIFEST.json`
- `PHASE7_GATE2_READINESS_REPORT.md`

The Gate 1B manifest was previously verified 322/322 entries against file
hashes and sizes. Its three 0–99 runs remain untouched. BCGM-on used Event Cap
9,000 and Global Cap 4,500,000; Event Cap activated 14 times and rejected
35,201 of 599,547 valid candidates. Global Cap activated zero times. BCGM-off
was empirically close to the P4 arm at 100 frames, but the one-run-per-arm
design does not establish statistical equivalence or 500-frame parity.

## 5. Reuse decision

**Decision:** reuse Gate 4 for contextual runtime, CUDA allocator memory,
Gaussian-count, and CPU-offload reference only. Combine with Gate 1B for
short-horizon quality/parity context. Prepare exactly one new 500-frame
BCGM-on run. Do not run new P4 or BCGM-off arms unless the researcher later
decides that same-horizon controlled deltas are essential.

**Final classification:** `PASS_GATE2_WITH_COMPARISON_LIMITATIONS`.

Related records: [minimal run contract](PHASE7_GATE2_MINIMAL_RUN_CONTRACT.md),
[minimal preflight report](PHASE7_GATE2_MINIMAL_PREFLIGHT_REPORT.md),
[Gate 1B final validation](PHASE7_GATE1B_FINAL_VALIDATION_REPORT.md),
[Gate 1B metric comparison](PHASE7_GATE1B_METRIC_COMPARISON.md),
[Gate 1B evidence manifest](PHASE7_GATE1B_EVIDENCE_MANIFEST.json), and
[Gate 2 readiness report](PHASE7_GATE2_READINESS_REPORT.md).
