# Environment Installation and Recovery

## Creation commands

The README-preferred candidate was attempted first, without editing repository
environment files:

```bash
conda create -n sgs_slam_baseline python=3.9 -y
conda install -n sgs_slam_baseline -c nvidia/label/cuda-11.8.0 cuda-toolkit -y
conda install -n sgs_slam_baseline pytorch==2.0.1 torchvision==0.15.2 \
  torchaudio==2.0.2 cudatoolkit=11.8 pytorch-cuda=11.8 \
  -c pytorch -c nvidia -y
```

Core/evaluation requirements were installed explicitly without the renderer so
the exact renderer source could be audited before compilation:

```bash
conda run -n sgs_slam_baseline python -m pip install \
  tqdm==4.65.0 Pillow opencv-python imageio matplotlib kornia natsort \
  pyyaml pandas wandb lpips plyfile open3d==0.16.0 torchmetrics \
  cyclonedds pytorch-msssim
```

FAISS was not installed: it is present only in the alternative Conda YAML and has
no verified canonical online read-site. W&B was imported but never initialized.

## Compatibility recoveries

| Problem and evidence | Change | Class | Algorithm behavior changed? |
|---|---|---|---|
| Resolver selected NumPy 2.0.x; PyTorch/torchvision 2.0.1 emitted `_ARRAY_API not found` and warned that binaries compiled for NumPy 1.x may crash. | Pin runtime NumPy to 1.26.4. | B — compatibility recovery | NO |
| Current unpinned OpenCV resolved to 5.0.0.93 and required/pulled NumPy 2.x. | Pin `opencv-python==4.11.0.86`, whose requirement accepts NumPy 1.26.4. | B | NO |
| Phase 3B loader testing showed that the 4.11.0.86 wheel was built with NumPy 2.0.2 headers and rejected every runtime NumPy 1.26.4 array passed to `cv2.resize`; duplicate providers and stale metadata were absent. | Replace only OpenCV with `opencv-python==4.9.0.80 --no-deps`; its NumPy-1.x-built wheel passes the same resize tests while retaining NumPy 1.26.4. See `09_opencv_numpy_recovery.md`. | B | NO |
| NumPy/MKL resolution upgraded MKL to 2025; `import torch` then failed with `libtorch_cpu.so: undefined symbol: iJIT_NotifyEvent`. | Pin `mkl<2024.1`; resolver selected MKL 2023.1.0. | B | NO |
| SciPy 1.13.1 + NumPy 1.26.4 failed importing `scipy.interpolate` at `_fitpack_impl.py` with bare `TypeError`; the same pair/traceback is recorded in SciPy issue #21014/#21650. | Pin `scipy==1.12.0`, which supports Python 3.9 and NumPy <2. | B | NO |
| `pip check` reported missing `typeguard`, `cmake`, and `lit`; CUDA extension build benefits from Ninja. | Install `typeguard`, `cmake`, `lit`, `ninja`. | A/B — dependency/build closure | NO |
| Conda+pip sequence left stale `numpy-2.0.2.dist-info` although runtime and active metadata were 1.26.4, causing incorrect Conda export. | Move only stale metadata to `/tmp/sgs_slam_numpy-2.0.2.dist-info.stale`; retain recoverably. | B — metadata consistency | NO |

Recovery commands:

```bash
conda install -n sgs_slam_baseline "mkl<2024.1" "numpy<2" -y
conda run -n sgs_slam_baseline python -m pip install \
  opencv-python==4.11.0.86 typeguard cmake lit ninja
conda run -n sgs_slam_baseline python -m pip install --force-reinstall \
  numpy==1.26.4 scipy==1.12.0
```

Subsequent Phase 3B-C recovery command:

```bash
conda run -n sgs_slam_baseline python -m pip install \
  --force-reinstall --no-deps opencv-python==4.9.0.80
```

No source, CUDA kernel, algorithm, or experiment config was patched.

## Snapshot

The exact mixed Conda/pip snapshot is in
`sgs_slam_baseline_environment.yml`. It was generated using:

```bash
conda export -n sgs_slam_baseline --format=environment-yaml \
  --file docs/baseline_reproduction/runtime/sgs_slam_baseline_environment.yml
```

The export includes build strings and pip packages. Renderer revision provenance
must still be read from `03_renderer_build_and_smoke_test.md`, because its wheel
metadata version is only `0.0.0`.
