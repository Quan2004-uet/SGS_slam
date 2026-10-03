# Gaussian representation and differentiable rendering

## What exactly is a Gaussian here?

One online semantic Gaussian is an isotropic 3D primitive with center `means3D[3]`, RGB `rgb_colors[3]`, real-first quaternion `unnorm_rotations[4]`, opacity logit `[1]`, isotropic log scale `[1]`, fixed semantic class ID `[1]`, trainable semantic RGB `[3]`, and creation timestamp in `variables`. **[VERIFIED FROM SOURCE]**

It is not a spherical-harmonic representation (`sh_degree=0`, `colors_precomp` is passed), not a class-logit vector, and not a learned high-dimensional feature. **[VERIFIED FROM SOURCE]**

| Parameter | Renderer transform | Tracking update | Mapping update | Persistent |
|---|---|---|---|---|
| center | current w2c × homogeneous center | numerically frozen | yes | yes |
| RGB | direct precomputed color | LR 0 | yes | yes |
| quaternion | L2 normalize | LR 0 | yes | yes |
| opacity | sigmoid | LR 0 | yes | yes |
| scale | exp then tile `N×1→N×3` | LR 0 | yes | yes |
| semantic ID | not rendered | no | no | yes |
| semantic RGB | direct precomputed color in separate pass | LR 0 | yes | yes |

## Pixel → Gaussian initialization

For pixel `(u,v)` and depth `z`, `get_pointcloud` forms `[(u-cx)z/fx, (v-cy)z/fy, z]`, applies `c2w = inverse(w2c)`, and concatenates RGB plus semantic ID/color. Initial radius is `z / ((fx+fy)/2)` and stored as its log. Quaternion is identity and opacity logit is zero (`sigmoid=0.5`). Invalid depth pixels are excluded. **[VERIFIED FROM SOURCE]**

## Rendering passes

`setup_camera` builds `GaussianRasterizationSettings` with fixed image dimensions, FoV, background, transposed w2c/projection matrices, camera center, and SH degree zero. `transform_to_frame` explicitly moves world centers into the current relative camera frame; the renderer camera settings remain based on frame 0. **[VERIFIED FROM SOURCE]**

Each `get_loss` makes:

1. RGB pass: `colors_precomp=rgb_colors` → image, per-Gaussian radius, third undocumented extension output.
2. Depth/silhouette pass: per-Gaussian pseudo-color `[z,1,z²]` → expected depth, accumulated opacity/silhouette, expected squared depth; `z²-depth²` is computed as uncertainty but only NaN-tested.
3. Semantic pass when enabled: `colors_precomp=semantic_colors` → 3-channel semantic-color image.

**[VERIFIED FROM SOURCE]** All passes use the same external CUDA rasterizer and geometry/opacity/scale. Gradients return through the rasterizer to render inputs, then through sigmoid/exp/quaternion normalization and camera transform. `means2D.retain_grad()` provides screen-space center gradients for optional clone/split densification.

The compiled extension itself is not vendored, so its internal tile buffers, exact third return value, compositing implementation, and backward allocation sizes are **[UNKNOWN / NEEDS RUNTIME VERIFICATION]**. The dependency commit is `cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110` in requirements.
