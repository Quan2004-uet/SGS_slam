# Gates 2A–2C — CUDA Renderer

## Source audit

- Repository: `https://github.com/JonathonLuiten/diff-gaussian-rasterization-w-depth.git`
- Required and checked-out revision:
  `cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110`
- Temporary source path:
  `/tmp/sgs_renderer_cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110`
- Python import: `diff_gaussian_rasterization`
- Required symbols: `GaussianRasterizer`, `GaussianRasterizationSettings`
- Build: setuptools `CUDAExtension` with PyTorch `BuildExtension`; CUDA/C++
  sources are `rasterizer_impl.cu`, `forward.cu`, `backward.cu`,
  `rasterize_points.cu`, and `ext.cpp`; GLM is included from `third_party/glm`.
- SGS-SLAM consumers include `scripts/slam.py`, `scripts/post_slam_opt.py`,
  `utils/eval_helpers.py`, and `utils/gs_helpers.py`.

The audited fork returns RGB, radii, and depth. It was not replaced by upstream
or another fork.

## Build

Compatibility tuple captured immediately before build:

```text
PyTorch: 2.0.1
torch.version.cuda: 11.8
nvcc: 11.8.89
gcc/g++: 11.4.0
NVIDIA driver: 580.178.04
GPU: GTX 1650 Ti, SM 7.5
```

Exact command:

```bash
CUDA_HOME=/home/quan/miniconda3/envs/sgs_slam_baseline \
TORCH_CUDA_ARCH_LIST=7.5 \
MAX_JOBS=2 \
conda run -n sgs_slam_baseline python -m pip install --no-build-isolation \
  /tmp/sgs_renderer_cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110
```

Result:

```text
Successfully built diff_gaussian_rasterization
Successfully installed diff_gaussian_rasterization-0.0.0
Wheel: diff_gaussian_rasterization-0.0.0-cp39-cp39-linux_x86_64.whl
Build wheel SHA-256: 9c8a033dc2c78883178cd89740c239e4d8dcc9a1a48b5b492b6967092c1f991f
```

The pip wheel cache was ephemeral; the authoritative reproducibility identity is
the Git revision plus build command. No kernel source was edited.

Gate 2A: **PASS**.

## Import

```text
module /home/quan/miniconda3/envs/sgs_slam_baseline/lib/python3.9/site-packages/diff_gaussian_rasterization/__init__.py
GaussianRasterizer <class 'diff_gaussian_rasterization.GaussianRasterizer'>
GaussianRasterizationSettings <class 'diff_gaussian_rasterization.GaussianRasterizationSettings'>
```

No undefined symbol or shared-library error occurred. Gate 2B: **PASS**.

## Synthetic forward/backward test

The temporary script `/tmp/sgs_renderer_smoke.py` used the repository's
`utils.recon_helpers.setup_camera` with a 16x16 camera and one Gaussian at
`[0, 0, 2]`. Inputs matched the production API: leaf tensors for means3D,
means2D, precomputed RGB, opacity, anisotropic scale, and scalar-first identity
quaternion. It asserted finite RGB/depth, positive radius, nonzero rendering, and
finite nonzero gradients. `torch.cuda.synchronize()` followed both forward and
backward.

Command:

```bash
PYTHONPATH=/home/quan/research/SGS-SLAM \
conda run -n sgs_slam_baseline python /tmp/sgs_renderer_smoke.py
```

Raw output:

```text
renderer_forward=PASS
image_shape (3, 16, 16)
radii_shape (1,) radius [5]
depth_shape (1, 16, 16)
image_sum 9.5834321975708
depth_sum 3775.0
renderer_backward=PASS
colors_grad [[8.712209701538086, 8.712209701538086, 8.712209701538086]]
means3d_grad [[2.5331974029541016e-07, -1.6093254089355469e-06, -7.761103630065918]]
peak_cuda_bytes 8546816
```

Gate 2C: **PASS**. This validates the compiled extension, not SLAM numerical
correctness or full-resolution memory capacity.
