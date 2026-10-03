# Phase 3B-R Dataset Recovery and Provenance Verification

## Result

**Phase 3B-R Status: PASS**

**Final provenance conclusion: AUTHOR-DISTRIBUTED DATASET RECOVERED**

The current maintainer-provided Google Drive distribution was recovered on
2026-10-02. `Replica_data.zip` is the maintainer-identified 2,000-frame
distribution and its `room0` content matches the active loader/config contract.
It was extracted without renaming or converting files to the ignored path
`data/Replica`.

The actual `ReplicaDataset` constructor accepts all paths, counts, and poses and
reports length 2,000. Frame-0 `__getitem__` is not yet a runtime PASS: it stops in
the environment's `cv2.resize` before returning tensors. A standalone
`cv2.resize` call on a newly allocated NumPy array fails identically, so this is
runtime evidence of an OpenCV/NumPy binding problem rather than a dataset
structure or image-decoding mismatch. No environment, source, or config change
was made in this task.

## Pre-flight

`RUNTIME VERIFIED` on 2026-10-02:

- branch: `main`;
- HEAD: `e4183986204242a8bb422624618af07780a49d26`, exactly the expected audit
  commit;
- pre-existing untracked entries: `2402.03246v6.pdf`, `AGENTS.md`, and `docs/`;
- no source/config edit was authorized or made;
- `/data/` is ignored by `.gitignore:3`.

Required documentation and the active Replica config/loader path were inspected
before external candidate acquisition.

## Original distribution and authoritative evidence

The current README is internally stale but preserves both authoritative links:

- `README.md:13` links the header label **Replica Dataset** to the public Google
  Drive folder
  `1-o4iFl53QeYD907azv_e8rI4aVDDvLwT`;
- `README.md:83` still links the prose **this link** to the older Dropbox folder.

`RUNTIME VERIFIED`: the Dropbox folder is reachable but displays `This folder
is empty`; its folder-download endpoint returns only a 118-byte empty ZIP. This
is the unavailable original link recorded during Phase 3B.

`VERIFIED FROM REPOSITORY HISTORY`: commit
`e4183986204242a8bb422624618af07780a49d26` (`Update data download link`, authored
2025-11-20) replaced the header's Dropbox URL with the Google Drive URL. The
commit did not update the duplicate link in the download prose.

`VERIFIED FROM MAINTAINER STATEMENT`: in
[SGS-SLAM issue #14](https://github.com/ShuhongLL/SGS-SLAM/issues/14#issuecomment-3556515971),
repository owner `ShuhongLL` stated on 2025-11-20 that the README link had
recently expired, supplied the same Google Drive folder, and identified
`Replica_data.zip` as the commonly used 2,000-frame sequence and
`Replica_data_900.zip` as the 900-frame sequence. An earlier owner comment in
the same issue stated that the intended package contains `traj.txt` and included
a directory screenshot. Community reports in that issue are distribution
failure reports, not authoritative replacement links.

The public Google Drive folder was accessible without login, CAPTCHA, access
request, or license-bypass behavior. It exposed these two files:

| File | Provider metadata size | Provider modified time | Maintainer meaning |
|---|---:|---|---|
| `Replica_data.zip` | 13,221,213,627 bytes | 2024-03-01 14:44:16 UTC | 2,000-frame, commonly used |
| `Replica_data_900.zip` | 4,636,461,280 bytes | 2024-04-17 06:35:03 UTC | 900-frame |

## Dataset URL history

| Commit | Author date | Dataset URL/instruction | Interpretation |
|---|---|---|---|
| `f430eb330ff5ec1557fc657ceada91b86930ad7d` | 2023-12-16 | `bash_scripts/download_replica.sh` downloaded `https://cvg-data.inf.ethz.ch/nice-slam/data/Replica.zip`; script also named a Caiyun mirror | Inherited iMAP/NICE-SLAM RGB-D distribution; not sufficient evidence for the later SGS-SLAM semantic package |
| `7753e19e5b0c371d3312fca6b823e9ace8bb2fc4` | 2024-09-28 | Dropbox folder `a93xhcpsteumsmw8oq4jc` | SGS-SLAM semantic package introduced; old download script deleted; loader changed to current JPG and `semantic_*` layout |
| `e4183986204242a8bb422624618af07780a49d26` | 2025-11-20 | Header changed to Google Drive folder `1-o4iFl53QeYD907azv_e8rI4aVDDvLwT`; prose retained Dropbox | Maintainer replacement source; corroborated by the owner comment in issue #14 |

The repository has one remote branch (`main`), no tags, and no GitHub releases.
No separate dataset artifact was found there. GitHub Discussions was not
available for this repository.

## SGS-SLAM Replica dataset fingerprint

### Identity and layout

`VERIFIED FROM CONFIG`: `configs/replica/slam.py:4-10,48-59` selects scene
`room0`, root `./data/Replica`, `start=0`, `end=-1`, `stride=1`, full
680x1200 output, semantic loading, and 101 configured semantic classes. The
checked-in scene list contains `room0`, `room1`, `room2`, `office0` through
`office4`, plus apartment variants; the paper's standard results use the eight
room/office scenes.

`VERIFIED FROM SOURCE`: `datasets/gradslam_datasets/replica.py:31-69` and
`datasets/gradslam_datasets/basedataset.py:174-207` define this required
fingerprint:

```text
data/Replica/
└── room0/
    ├── frames/frame*.jpg
    ├── depths/depth*.png
    ├── semantic_ids/semantic_id*.png
    ├── semantic_colors/semantic_color*.png
    └── traj.txt
```

- all four image lists use natural sorting;
- RGB/depth counts must be equal and, with semantics enabled, both semantic
  counts must equal RGB;
- each trajectory line must contain 16 floating-point values reshaped to a 4x4
  camera-to-world matrix;
- current config consumes every frame from index 0 at stride 1;
- current source does not hard-code a frame count. Before acquisition it was
  correctly `UNKNOWN / NEEDS RUNTIME VERIFICATION`.

### Image, semantic, depth, and pose assumptions

`VERIFIED FROM CONFIG`: `configs/data/replica.yaml:1-10` specifies width 1200,
height 680, `fx=fy=600`, `cx=599.5`, `cy=339.5`, depth scale 6553.5, and no edge
crop. The recovered archive's `cam_params.json` independently contains the same
values.

`VERIFIED FROM SOURCE`:

- RGB is decoded HWC, resized bilinearly, converted to floating point, and later
  divided by 255 in the SLAM caller;
- depth is decoded from PNG, nearest-neighbor resized, expanded to one channel,
  and divided by 6553.5 to obtain meters;
- semantic ID is a one-channel integer label image and is nearest-neighbor
  resized;
- semantic color is a three-channel color image and is nearest-neighbor resized;
- raw poses are c2w; the base loader computes
  `inverse(c2w_frame0) @ c2w_frame_t`, so returned frame 0 should be identity;
- no preprocessing or conversion step is invoked between this on-disk layout
  and the current loader.

`VERIFIED FROM README`: the scenes originate from Meta Replica; the SGS-SLAM
authors generated the ground-truth semantic masks by referring to the
Semantic-NeRF preprocessing procedure, and the trajectories were captured using
iMAP. `VERIFIED FROM PAPER`: the paper only says that Replica ground-truth poses
and semantic maps are supplied by simulation; it does not identify an archive,
checksum, or exact file layout.

## Sources investigated

### Repository, history, issues, and project material

- Current README, all README commits, current and pre-semantic Replica loader,
  config, branches, tags, releases, and issues were inspected.
- Issue #14 contains the decisive owner replacement link and frame-count
  statement. Issue #18 contains an owner pointer to Semantic-NeRF's Habitat data
  generation for reproducing RGB frames from trajectories; it is provenance
  context, not an instruction to reconstruct the dataset in this task.
- Issue #5 discusses pseudo labels for user datasets, not the released Replica
  package.
- The paper and author publication page identify Replica and the official code
  but publish no independent dataset checksum or mirror.
- The official Meta Replica release supplies semantic meshes/assets, not this
  pre-rendered SGS-SLAM RGB/depth/semantic/trajectory layout.
- Semantic-NeRF's documented generation path renders RGB, depth, semantic, and
  instance images with Habitat-Sim from a supplied camera trajectory. This
  supports the README's stated preprocessing lineage but is not byte-level
  equivalence evidence.

### Archived and re-uploaded candidates

| Candidate | Source | Claimed origin/evidence | Structural match | Confidence/result |
|---|---|---|---|---|
| `Replica_data.zip` | Current SGS-SLAM maintainer Google Drive | Current README header, history, and owner issue #14 explicitly identify it as the usual 2,000-frame package | Exact current `room0` layout and metadata match | **HIGH — ACCEPTED** |
| `Replica_data_900.zip` | Same maintainer Google Drive | Owner identifies it as the 900-frame sequence | 900 RGB and depth files exist, but RGB is `frame*.png`; semantic directories/files use `semantics_id`, `semantics_color`, and `semantic_class*`, matching the older pre-2024-09-28 loader rather than current HEAD | **HIGH provenance, MISMATCH for current HEAD — REJECTED as baseline input** |
| Former Dropbox folder | Current README prose / prior header | Original SGS-SLAM semantic distribution link | Empty share and empty ZIP now | **HIGH provenance, unavailable — REJECTED** |
| NICE-SLAM/iMAP `Replica.zip` | Initial SGS-SLAM history and NICE-SLAM host | Original posed RGB-D lineage | Does not establish SGS-SLAM-authored per-frame semantic directories required by current HEAD | **REJECT** |
| Official Meta Replica v1 | Meta repository | Authoritative underlying scene meshes and semantic assets | Not the pre-rendered current loader layout and does not directly provide the iMAP sequence | **REJECT as direct baseline input; base data remains obtainable** |
| TGS-SLAM Google Drive | Separate 2026 research repository | Claims a preprocessed Replica dataset and documents the same five path patterns, but does not state that it is a copy of SGS-SLAM's package | Claimed layout match only; no checksum/origin link checked | **MEDIUM, not needed and not downloaded** |
| `voviktyl/Replica-SLAM` | Hugging Face community upload | No dataset card; 32,000 image rows / 12.5 GB | No evidence of SGS-SLAM semantic directories or provenance | **LOW — not downloaded** |
| SGS-SLAM forks/search-index copies | GitHub/community | Mostly inherit the project's README link | No independent archive/checksum provenance | **LOW — not downloaded** |

No Zenodo or institutional archive explicitly claiming to preserve the SGS-SLAM
semantic distribution was found. Because an author-distributed working source
was recovered, no community mirror was downloaded.

## Recovered archive

| Property | Runtime evidence |
|---|---|
| Provider | SGS-SLAM maintainer Google Drive folder |
| Acquisition date | 2026-10-02 (Asia/Ho_Chi_Minh) |
| Archive | `data/Replica_data.zip` |
| Size | 13,221,213,627 bytes |
| **LOCAL ARCHIVE SHA-256** | `1e4a71b656936f2b75a91fb938cde2b22d690175410fd9be32d0a198471bf041` |
| **VERIFIED AGAINST PUBLISHED CHECKSUM** | NO — no independently published checksum was found |
| Extracted path | `data/Replica` |
| Extracted apparent byte count | 13,605,757,388 bytes (`du -sb`) |
| Git handling | `data/` is ignored; archive and extracted dataset are untracked/ignored data, not source |
| Extraction | `unzip` completed with exit status 0; files were not renamed or converted |

The archive contains all eight standard scenes: `room0`, `room1`, `room2`, and
`office0` through `office4`. It also includes per-scene instance data and mesh
metadata that the current online loader does not read.

## Structural equivalence: `room0`

| Property | SGS-SLAM expectation | Candidate | Result |
|---|---|---|---|
| scene | `room0` | `data/Replica/room0` | MATCH |
| RGB path | `frames/frame*.jpg` | 2,000 files, `frame000000.jpg` through `frame001999.jpg` | MATCH |
| depth path | `depths/depth*.png` | 2,000 files, `depth000000.png` through `depth001999.png` | MATCH |
| semantic ID | `semantic_ids/semantic_id*.png` | 2,000 files, `semantic_id000000.png` through `semantic_id001999.png` | MATCH |
| semantic color | `semantic_colors/semantic_color*.png` | 2,000 files, `semantic_color000000.png` through `semantic_color001999.png` | MATCH |
| trajectory | `traj.txt`, 16 floats/line | 2,000 lines; all parse as finite 4x4 matrices | MATCH |
| resolution | 1200x680 | both inspected samples are 1200x680 for all modalities | MATCH |
| frame count | source unknown; maintainer says common package is 2,000 | 2,000 images and 2,000 poses | MATCH |
| indexing | natural-sort aligned from index 0, stride 1 | all four sets are contiguous six-digit indices 000000-001999 and exactly equal | MATCH |
| zero-byte files | none expected | none under `room0` | MATCH |
| calibration | 1200x680, 600/600/599.5/339.5, scale 6553.5 | root `cam_params.json` exactly matches checked-in YAML | MATCH |

## Semantic and image sample verification

`RUNTIME VERIFIED` with direct decoding, without regeneration or conversion:

| Sample | RGB | Depth | Semantic ID | Semantic color | Alignment evidence |
|---|---|---|---|---|---|
| frame 0 | `(680,1200,3)` `uint8`, range 0-255 | `(680,1200)` `uint16`, raw 0-32814; 0-5.007095 m after `/6553.5` | `(680,1200)` `uint8`; 18 unique IDs, range within configured 0-100 | `(680,1200,3)` `uint8`, range 0-224; 18 colors | identical spatial dimensions; each sampled ID maps to exactly one sampled RGB semantic color |
| frame 1000 | `(680,1200,3)` `uint8`, range 0-255 | `(680,1200)` `uint16`, raw 10073-37470; 1.537041-5.717556 m | `(680,1200)` `uint8`; 20 unique IDs, range within configured 0-100 | `(680,1200,3)` `uint8`, range 0-224; 20 colors | identical spatial dimensions; each sampled ID maps to exactly one sampled RGB semantic color |

This establishes the loader-required representation and sampled pixel-grid
alignment. It does not prove every pixel in all 2,000 frames is semantically
correct relative to the underlying 3D mesh.

## Trajectory verification

`RUNTIME VERIFIED`:

- `room0/traj.txt` exists and has exactly 2,000 lines;
- every line contains 16 parseable finite values and reshapes to 4x4;
- every homogeneous last row is `[0, 0, 0, 1]` within numerical tolerance;
- pose count equals all four modality counts;
- no pose transform was applied during verification.

The source interprets these matrices as c2w. Archive provenance plus structural
and numerical validity supports that interpretation, but this recovery task did
not rerender the mesh to independently prove geometric coordinate alignment.

## Actual loader frame-0 check

The unmodified `ReplicaDataset` was instantiated using
`configs/data/replica.yaml`, root `./data/Replica`, scene `room0`, full
680x1200 resolution, semantics enabled, and device `cuda:0`.

`RUNTIME VERIFIED`:

- constructor passed all count checks;
- all 2,000 trajectory matrices parsed;
- dataset length is 2,000;
- `dataset[0]` decoded the JPG into a contiguous `(680,1200,3)` NumPy array;
- it then failed at `basedataset.py:236` in `cv2.resize` with
  `src is not a numpy array, neither a scalar`.

The controlled minimum reproduced the same failure for both freshly allocated
`uint8` and `float64` NumPy arrays, with no dataset involved:

```text
Python 3.9.25
NumPy 1.26.4 (conda)
opencv-python 4.11.0.86 (pip)
cv2.resize(np.zeros(...)) -> same Bad argument / src is not a numpy array
```

OpenCV build information says its Python binding was built against NumPy 2.0.2,
while the baseline environment loads NumPy 1.26.4. This is evidence of a binary
binding incompatibility, but the precise compatible recovery action remains
`UNKNOWN / NEEDS RUNTIME VERIFICATION`. Per the Phase 3B-R boundary, the
environment was not changed and first-frame Gaussian initialization was not
called.

## Final provenance conclusion and remaining uncertainty

**AUTHOR-DISTRIBUTED DATASET RECOVERED**

The current README link, the commit that replaced the expired link, the
repository owner's issue statement, provider metadata, exact active-loader
layout, exact calibration match, semantic samples, and complete pose/count
checks together establish high-confidence provenance and structural equivalence
for the released 2,000-frame SGS-SLAM Replica package.

Remaining uncertainty:

- no author-published checksum exists, so the local SHA-256 cannot be compared
  with an independent digest;
- full semantic correctness and pose-to-render geometric alignment were not
  exhaustively re-derived from the Meta meshes;
- loader frame 0 is blocked by the newly runtime-observed OpenCV/NumPy binding
  incompatibility and has not returned tensors;
- no SLAM, tracking, mapping, evaluation, post-opt, or first-frame Gaussian
  initialization was run.

## Next action

Resume **Phase 3B — Gate 3A/3B Dataset Validation** by recovering the
OpenCV/NumPy compatibility of the existing baseline environment as a separately
recorded compatibility intervention, then rerun only the loader frame-0 check.
Do not begin first-frame Gaussian initialization until that gate passes, and do
not begin Phase 3C.
