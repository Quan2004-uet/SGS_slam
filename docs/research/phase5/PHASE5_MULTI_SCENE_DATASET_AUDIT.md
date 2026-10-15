# Phase 5 Multi-Scene Dataset Readiness Audit

Status: `VERIFIED STRUCTURAL READINESS`; image contents were not decoded and no data were modified.
Audit method: bounded directory inventories, filename endpoints, zero-byte checks, trajectory line/field counts, config/loader inspection.

## Loader contract

`ReplicaDataset` expects `frames/frame*.jpg`, `depths/depth*.png`, `semantic_ids/semantic_id*.png`, `semantic_colors/semantic_color*.png`, and `traj.txt` (`datasets/gradslam_datasets/replica.py:13-69`). The base class requires equal RGB/depth counts and, when semantics are enabled, equal semantic counts (`basedataset.py:174-202`). Each trajectory line is parsed as 16 floats into a 4x4 c2w pose. Shared intrinsics are 1200x680, fx=fy=600, cx=599.5, cy=339.5 and depth scale 6553.5 (`configs/data/replica.yaml`).

## Local inventory

`data/Replica` occupies approximately 13 GiB. All listed local scenes have index endpoints 000000..001999, no zero-byte modality files, 2,000 trajectory lines, and 16 fields per pose line.

| Scene | RGB | Depth | Semantic ID | Semantic color | Poses | Approx. disk | Structural status |
|---|---:|---:|---:|---:|---:|---:|---|
| room0 | 2000 | 2000 | 2000 | 2000 | 2000 | 2.0G | `VERIFIED COMPLETE LAYOUT`; runtime validated in Phase 4 |
| room1 | 2000 | 2000 | 2000 | 2000 | 2000 | 1.7G | `VERIFIED COMPLETE LAYOUT`; not runtime validated |
| room2 | 2000 | 2000 | 2000 | 2000 | 2000 | 1.7G | same |
| office0 | 2000 | 2000 | 2000 | 2000 | 2000 | 1.6G | same |
| office1 | 2000 | 2000 | 2000 | 2000 | 2000 | 1.5G | same |
| office2 | 2000 | 2000 | 2000 | 2000 | 2000 | 1.6G | same |
| office3 | 2000 | 2000 | 2000 | 2000 | 2000 | 1.8G | same |
| office4 | 2000 | 2000 | 2000 | 2000 | 2000 | 1.5G | same |

The checked-in Replica config also lists `apartment_0`, `apartment_1`, `apartment_2`, `frl_apartment_0`, and `frl_apartment_4` (`configs/replica/slam.py:4-6`); these directories are `MISSING` locally. No local ScanNet or ScanNet++ dataset directory was found.

“Complete layout” does not prove all images decode correctly or contain scientifically valid aligned content. P5-G2 may add a CPU-only manifest validator; P5-G3 should detect decode errors during bounded runs. Do not relabel unrun scenes as validated.

## Config readiness

The loader and shared data config are compatible with all eight local layouts. The sole checked-in online Replica experiment config hard-codes `scene_name="room0"` and default full horizon (`configs/replica/slam.py:10,48-59`). There are no checked-in per-scene immutable experiment configs. P5-G2/P5-G3 must create provenance-preserving profiling configs or a non-mutating override mechanism; it must not edit `configs/replica/slam.py` in place. Each run must save its exact config and SHA-256. Current hashes are:

- `scripts/slam.py`: `a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3`
- `configs/replica/slam.py`: `08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3`
- `configs/data/replica.yaml`: `4c1e33544bef24c146c4ec9a622bb3ad7a314168db8d192c191db08bad3edf58`

## Proposed controlled workload matrix

| Workload | Scene / frames | Purpose | Readiness | Expansion rule |
|---|---|---|---|---|
| W1 short reference | room0 0-99 | Instrumentation correctness, overhead, trace equivalence against known path | Ready after P5-G2 | Must pass before W2 |
| W2 medium reference | room0 0-499 | Growth curves and preliminary component shares on the Phase 4 scene | Ready after W1 | Must pass numerical/trace gate |
| W3 geometry/semantic variation | office0 0-499, then 0-1999 only after bounded pass | Different office geometry and semantics while preserving format/resolution | Structurally ready; runtime unverified | Stop on bounded failure; do not jump to full scene |
| W4 longest available | room1 0-1999 | A second full 2,000-frame room candidate | Structurally ready; runtime unverified | Execute only in P5-G4 after W1-W3 gates |

Scene choice is provisional until a CPU-only content summary confirms meaningful class/geometry variation without scanning all pixels. `office0` is chosen by scene category, not by an unverified claim of difficulty.

## Large-scene readiness

`BLOCKED`: no local 10k-50k-frame sequence is present. Eight independent 2,000-frame scenes support multi-scene generalization, not long-horizon or physically large-scale validation. Concatenating or repeating room0 frames would not constitute large-scene evidence and is prohibited as a scalability claim.

Potential future candidates are ScanNet/ScanNet++ because loaders/config families already exist, but readiness is not established: data are absent; licensing/download is external; directory/semantic preprocessing, split selection, intrinsics/poses, resolution, class mapping and evaluator compatibility need a separate adapter/data gate. Multi-room or long-sequence datasets without the repository's semantic-color contract would additionally require a named loader/semantic-adaptation effort. No data download or adapter work is authorized in P5-G1.

## Dataset blockers

1. No immutable per-scene profiling configs yet (P5-G2 deliverable, not a data corruption).
2. Image decodability/alignment for seven unrun scenes is not runtime verified.
3. No 10k-50k or demonstrably large-scale sequence is locally available.
4. Host capacity must be budgeted before full scenes: room0 V0 used 10.497 GB logical archive and approximately 13.58 GB process HWM in the detailed run.
