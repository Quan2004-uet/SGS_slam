# Phase 7 Gate 2 — final validation report

**Run ID:** `p7_bcgm_g2_room0_on_0_499_r01`<br>
**Session:** `SESSION_005` — ACTIVE<br>
**Gate 1B:** `PASS_WITH_LIMITATIONS`<br>
**Final status:** `PASS_GATE2_WITH_COMPARISON_LIMITATIONS`

## Execution and checkpoint

**RUNTIME VERIFIED:** `run_summary.json` reports `COMPLETE`, process exit
code 0, frame range 0–499, 500 saved poses, and 499 insertion events. The
saved log ends with normal worker metrics and evaluator output. No run was
repeated for this closure.

`params.npz` independently passed ZIP CRC (`testzip() == None`), NumPy loading
with `allow_pickle=False`, and finite numeric checks. All Gaussian fields are
row-aligned at 2,198,608 rows. Camera slots and ground-truth poses each contain
500 frames. The checkpoint contains estimated camera rotation/translation,
ground-truth poses, and keyframe indices. The six saved evaluation arrays
(`psnr`, `ssim`, `lpips`, `l1`, `rmse`, `miou`) each contain 101 finite values;
`rmse.txt` equals `l1.txt` element-for-element.

## BCGM admission validation

The 499 `BCGM_INSERTION` records in the saved stdout were checked against the
499 rows of `insertion_counts.jsonl`:

- Frames are 1–499, one record each; all before/after transitions match.
- Valid candidates: 1,562,329; admitted: 1,478,249; rejected: 84,080.
- Every record satisfies `valid_candidates = admitted + rejected`,
  `after - before = admitted`, `admitted <= 9,000`, and `after <= 4,500,000`.
- `event_saturated` is true for 41 events; maximum admitted is 9,000.
- `global_saturated` is true for zero events. The Global Cap did not activate
  and is not runtime-validated.

The check deliberately uses `event_saturated` for Event Cap and
`global_saturated` for Global Cap. `budget_saturated` is not interpreted as a
Global Cap indicator.

## Identity and metrics

Saved summary identities match current source/config/worker files:

| Input | SHA256 | Result |
|---|---|---|
| `scripts/slam.py` | `ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999` | Match |
| `utils/bcgm.py` | `8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400` | Match |
| Gate 2 config | `ff025785249c1811c9ee3b3359cd4656b1992e78d9465b610bfe840ea2026b49` | Match; copied `config.py` also matches |
| Reused worker | `9a449ef10506ebbe6ccd0616d29aa02e9183554b333d605c9440ec07e09ad40b` | Match |

Process wall is 2,370.501740 s and E2E FPS is 0.21092581. Tracking and mapping
FPS, process-wide CUDA allocator peaks, recovered device-wide NVML peak,
Gaussian count, and saved quality/trajectory metrics are summarized in
`PHASE7_GATE2_METRIC_COMPARISON.md`.

The summary's NVML aggregate is incorrect (`0` samples, null peak). The
original CSV independently yields 2,334 valid samples, peak 4,877 MiB at
`2026-10-27T04:16:03.322036+00:00`, GPU 0, and maximum sampled utilization
98%. The parser mismatch and separate recovered sidecar are documented in
`PHASE7_GATE2_NVML_RECOVERY_REPORT.md`.

## Comparison limits and gate state

Phase 4 Gate 4 is a historical context for runtime, CUDA allocator peaks, and
final Gaussian count only. Its evaluation/save path was suppressed, its timing
scope differs, and its effective runtime source hash is incomplete. It did
not measure NVML, image/depth/semantic quality, or trajectory. Do not claim a
matched 500-frame speedup, quality retention, NVML improvement, or statistical
significance from this one-arm run.

**Gate 2:** `PASS_GATE2_WITH_COMPARISON_LIMITATIONS`<br>
**Gate 3 full scene:** `NOT_STARTED`<br>
**No SLAM/CUDA workload, rerun, algorithm/source/config change, deletion,
commit, push, or upload was performed during this evidence-closure task.**
