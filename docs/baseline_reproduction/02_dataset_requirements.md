# Replica Dataset Requirements

## Expected source and layout

The README links a custom Replica download containing semantic data and separately
attributes trajectory files to iMAP. The repository does not contain the dataset,
and Phase 2 did not download it. `VERIFIED FROM README`; repository-tree absence
was `VERIFIED FROM SOURCE`.

For canonical scene `room0`, `ReplicaDataset` expects:

```text
data/Replica/
├── color_dict.json                 # visualization only
└── room0/
    ├── frames/frame*.jpg
    ├── depths/depth*.png
    ├── semantic_ids/semantic_id*.png
    ├── semantic_colors/semantic_color*.png
    └── traj.txt
```

This exact glob/layout is `VERIFIED FROM SOURCE` in
`datasets/gradslam_datasets/replica.py`; common preprocessing is in
`datasets/gradslam_datasets/basedataset.py`. A standard Replica RGB-D release
without both semantic directories does not satisfy the checked-in config.

The semantic source is precomputed dataset imagery, not an online segmentation
model. Each sample supplies semantic IDs and RGB semantic colors. Online map
optimization learns a three-channel `semantic_colors` value per Gaussian; the IDs
remain fixed metadata. `VERIFIED FROM SOURCE`

## Scene and calibration contract

- Checked-in scene names include `room0`, `room1`, `room2`, `office0`–`office4`
  plus several apartment scenes. Paper tables use the eight room/office scenes.
- YAML calibration: width 1200, height 680, `fx=fy=600`, `cx=599.5`,
  `cy=339.5`, depth scale `6553.5`, crop edge 0.
  `VERIFIED FROM CONFIG: configs/data/replica.yaml`
- `traj.txt` is parsed as one flattened 4x4 **camera-to-world** transform per
  line. `VERIFIED FROM SOURCE`
- With `relative_pose=True`, poses become
  `inverse(c2w_frame0) @ c2w_frame_t`; the SLAM loop inverts them to obtain w2c.
  `VERIFIED FROM SOURCE`
- RGB and semantic-color images enter through `imageio`, are resized bilinearly
  and converted to float tensors; the SLAM loop permutes HWC to CHW and divides
  by 255. `VERIFIED FROM SOURCE`
- Depth is read as integer data, resized with nearest-neighbor interpolation,
  given a singleton channel, and divided by `png_depth_scale` (6553.5 for
  Replica). `VERIFIED FROM SOURCE`
- Semantic IDs use nearest-neighbor resizing and remain a single-channel integer
  label image. Semantic colors also use nearest-neighbor resizing.
- Intrinsics are scaled if source and desired image sizes differ; the canonical
  Replica sizes agree, so no numerical resize should occur. `INFERRED`
- Dataset tensors are returned on the configured device (`cuda:0` here), not
  lazily retained only on CPU. `VERIFIED FROM SOURCE`

The dataset's exact frame count and raw PNG/JPG dimensions are `UNKNOWN / NEEDS
RUNTIME VERIFICATION` because no dataset is present locally.

## Disk-to-SLAM trace

```text
frame*.jpg / depth*.png / semantic_id*.png / semantic_color*.png / traj.txt
  -> ReplicaDataset.get_filepaths() and load_poses()
  -> GradSLAMDataset.__getitem__()
     resize, depth-scale conversion, K scaling, relative c2w pose, device move
  -> scripts/slam.py
     HWC->CHW, RGB/semantic-color /255, pose inversion, camera construction
  -> current-frame tensors used by tracking, addition, mapping, and evaluation
```

## Phase 3 integrity checklist

All checks are required before a multi-frame run:

- [ ] `data/Replica/room0` exists at the path resolved from repository root.
- [ ] Sorted counts of RGB and depth files are equal and nonzero.
- [ ] Sorted counts of semantic-ID and semantic-color files equal RGB count.
- [ ] `traj.txt` has at least one valid 16-number line per selected image.
- [ ] Frame ordering pairs the same index across all four modalities.
- [ ] Frame 0 loads at HxW = 680x1200 after preprocessing.
- [ ] RGB tensor is HxWx3, finite, and represents the expected 0–255 loader
  range before the SLAM loop's division.
- [ ] Depth tensor is HxWx1, finite, nonnegative, and plausibly in meters after
  division by 6553.5; report min/max/valid-pixel ratio.
- [ ] Semantic-ID tensor is HxWx1, integer-like, and label range is recorded.
- [ ] Semantic-color tensor is HxWx3 and palette consistency is sampled.
- [ ] Intrinsics equal or correctly scale from the YAML values.
- [ ] Frame-0 relative pose is identity within numerical precision; later poses
  are finite, invertible, and have valid homogeneous last rows.
- [ ] Dataset length after `start=0,end=-1,stride=1` is recorded.
- [ ] No actual frame count is inserted into the contract until measured.
