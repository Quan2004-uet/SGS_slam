# Semantic pipeline

## End-to-end trace

```text
precomputed semantic_id PNG + semantic_color PNG
  → dataset nearest-neighbor resize
  → GPU ID (integer) and RGB color (float 0..255)
  → slam normalization: semantic color / 255
  → per-pixel initial/new Gaussian semantic ID + semantic RGB
  → separate rasterizer pass using semantic RGB as colors_precomp
  → tracking L1 or mapping L1+DSSIM against semantic-color image
  → gradients update pose (tracking) or Gaussian semantic/geometry attributes (mapping)
  → nearest-palette recoloring → color-based mIoU
```

**[VERIFIED FROM SOURCE]** Inputs are precomputed by the dataset; no segmentation network is invoked. ScanNet preprocessing maps raw IDs to a fixed RGB palette. Replica/ScanNet++ loaders expect both ID and color directories.

The semantic representation has two parallel values:

- `semantic_ids`: one fixed class ID per Gaussian, used for object selection/filtering in visualization/evaluation utilities; not rasterized or optimized.
- `semantic_colors`: a trainable 3-vector per Gaussian, rasterized exactly like RGB.

It is therefore a semantic RGB regression representation, not one-hot labels, logits, probabilities, or embeddings. Dataset loaders contain unused generic embedding support, but `scripts/slam.py` never enables or consumes it. **[VERIFIED FROM SOURCE]**

Tracking semantic loss is masked summed L1 when semantics are enabled. Mapping semantic loss is `0.8 mean-L1 + 0.2(1-SSIM)`. Geometry, opacity, and scale also participate in the semantic render graph, so semantic supervision can influence them during mapping; tracking map LRs are zero while camera receives pose gradient through transformed centers. **[VERIFIED FROM SOURCE]**

Evaluation snaps every rendered semantic RGB pixel to the nearest unique color present in that frame's GT semantic image, excludes black GT pixels, and computes IoU per remaining unique color. Thus the evaluated label palette is derived per GT frame, not directly from `semantic_ids` or global class logits. **[VERIFIED FROM SOURCE]**

`num_semantic_classes` is passed into datasets and stored but does not determine the online representation dimension or loss. **[VERIFIED FROM SOURCE]**

Paper statements that semantic maps filter keyframes are not realized by active code: an mIoU block exists only commented out. **[VERIFIED FROM README/DOCUMENTATION; VERIFIED FROM SOURCE]**
