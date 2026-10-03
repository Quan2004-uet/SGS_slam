# Phase 3B-C OpenCV/NumPy Compatibility Recovery

## Result

**Phase 3B-C Status: PASS**

`RUNTIME VERIFIED` on 2026-10-02: the OpenCV/NumPy compatibility failure was
recovered by replacing only `opencv-python==4.11.0.86` with
`opencv-python==4.9.0.80`. NumPy remains 1.26.4. PyTorch 2.0.1, PyTorch CUDA
11.8, the pinned CUDA rasterizer, source, experiment config, algorithm, and
dataset contents were not changed.

The exact SGS-SLAM `ReplicaDataset` now loads `room0` frame 0 and returns all
six expected tensors on `cuda:0`. No frame after index 0 was accessed and no
Gaussian initialization function was called.

## Pre-flight

```text
environment  /home/quan/miniconda3/envs/sgs_slam_baseline
python       /home/quan/miniconda3/envs/sgs_slam_baseline/bin/python
version      Python 3.9.25
branch       main
HEAD         e4183986204242a8bb422624618af07780a49d26
```

Pre-existing untracked paths remained `2402.03246v6.pdf`, `AGENTS.md`, and
`docs/`. No reset or revert was performed.

## Original failure

Before changing the environment, this minimum reproduction failed:

```python
import cv2
import numpy as np

x = np.zeros((10, 10, 3), dtype=np.uint8)
cv2.resize(x, (5, 5))
```

`RUNTIME VERIFIED` output:

```text
cv2_version 4.11.0
numpy_version 1.26.4
type <class 'numpy.ndarray'>
dtype uint8
C_CONTIGUOUS True
cv2.error: OpenCV(4.11.0) ... Bad argument in function 'resize'
  src is not a numpy array, neither a scalar
  Expected Ptr<cv::UMat> for argument 'src'
```

Module paths were both inside the intended environment:

```text
cv2   /home/quan/miniconda3/envs/sgs_slam_baseline/lib/python3.9/site-packages/cv2/__init__.py
numpy /home/quan/miniconda3/envs/sgs_slam_baseline/lib/python3.9/site-packages/numpy/__init__.py
```

## Root-cause evidence and package ownership

`RUNTIME VERIFIED` before recovery:

- pip/Conda metadata listed only `opencv-python==4.11.0.86`; neither
  `opencv-python-headless`, `opencv-contrib-python`,
  `opencv-contrib-python-headless`, nor Conda `opencv` was installed;
- site-packages contained one `cv2/`, one
  `opencv_python-4.11.0.86.dist-info`, and one
  `numpy-1.26.4.dist-info`;
- no stale NumPy 2.x metadata remained in site-packages;
- `pip check` reported no broken requirements;
- OpenCV 4.11.0 build information reported NumPy headers 2.0.2, while the
  runtime intentionally loaded NumPy 1.26.4;
- the failure reproduced on newly allocated contiguous `uint8` and `float64`
  arrays, independent of dataset decoding.

Multiple OpenCV providers and stale metadata were therefore excluded. The
controlled replacement with a wheel built against NumPy 1.x immediately made
the same operation pass. This is runtime evidence of an OpenCV-wheel/NumPy ABI
compatibility failure, not an SGS-SLAM source or Replica-data defect.

Repository dependency files do not prescribe an exact version:

- `requirements.txt` lists unpinned `opencv-python`;
- `environment.yml` lists unpinned Conda `opencv`;
- `venv_requirements.txt` omits OpenCV;
- the paper does not state an OpenCV version.

The selected 4.9.0.80 wheel supports Python 3.9, predates NumPy 2, and reports
that it was built with NumPy 1.17 headers. It is a minimal compatibility pin,
not a claim about the authors' paper environment.

## Recovery intervention

Classification: **B — environment compatibility recovery**.

Algorithm behavior changed: **NO**.

```text
OLD: opencv-python 4.11.0.86; NumPy 1.26.4
NEW: opencv-python 4.9.0.80;  NumPy 1.26.4
```

Exact command:

```bash
python -m pip install --force-reinstall --no-deps opencv-python==4.9.0.80
```

`--no-deps` prevented pip from changing NumPy or any other package. No
`pip install -U`, PyTorch/CUDA change, renderer rebuild, or source/config edit
was performed.

## Minimal OpenCV verification

`RUNTIME VERIFIED` after recovery:

```text
cv2_version 4.9.0
numpy_version 1.26.4
uint8 resize  (10,10,3) -> (5,5,3), dtype uint8   PASS
float resize  (10,10)   -> (5,5),   dtype float32 PASS
```

OpenCV 4.9.0 build information reports Python limited ABI through its CPython
3.7 abi3 wheel and NumPy 1.17 build headers. Runtime imports remain from the
same Python 3.9 environment.

## Phase 3A regression checks

### PyTorch and CUDA

The default command sandbox could not communicate with the NVIDIA driver, so
the GPU check was repeated with host device access. This was a tool-isolation
effect: `nvidia-smi` and PyTorch both passed immediately outside that sandbox.

`RUNTIME VERIFIED`:

```text
PyTorch              2.0.1
torch.version.cuda   11.8
cuda available       True
device count         1
device               NVIDIA GeForce GTX 1650 Ti
gradient             tensor([2.], device='cuda:0')
CUDA backward        PASS
driver               580.178.04
```

### Dependency closure and renderer

```text
pip check: No broken requirements found.
GaussianRasterizer import: PASS
GaussianRasterizationSettings import: PASS
```

The rasterizer was not rebuilt. The OpenCV-only change did not touch its
PyTorch/CUDA ABI. A repeated synthetic rasterizer forward/backward was not
needed because the required exact import and PyTorch CUDA backward both passed.

## Replica frame-0 loader verification

The unmodified `ReplicaDataset` was instantiated with:

```text
config               configs/data/replica.yaml
root                 ./data/Replica
sequence             room0
range                start=0, end=-1, stride=1
desired resolution   680x1200
device               cuda:0
semantics            enabled
configured classes   101
```

`RUNTIME VERIFIED`:

```text
constructor          PASS
dataset length       2000
accessed index       0 only
sample tuple length  6
dataset[0]           PASS
```

### Frame-0 tensor schema

| Output | Type | Shape | Dtype | Device | Finite | Runtime range/details |
|---|---|---|---|---|---|---|
| color | `Tensor` | `(680, 1200, 3)` | `torch.float32` | `cuda:0` | YES | 0-255; loader output is not yet divided by 255 |
| depth | `Tensor` | `(680, 1200, 1)` | `torch.float32` | `cuda:0` | YES | 0-5.007095 m; minimum positive 1.205615 m |
| intrinsics | `Tensor` | `(4, 4)` | `torch.float32` | `cuda:0` | YES | `fx=fy=600`, `cx=599.5`, `cy=339.5` |
| pose | `Tensor` | `(4, 4)` | `torch.float32` | `cuda:0` | YES | relative c2w; identity within `1e-5` |
| semantic ID | `Tensor` | `(680, 1200, 1)` | `torch.int32` | `cuda:0` | YES | 18 unique IDs, min 0, max 98 |
| semantic color | `Tensor` | `(680, 1200, 3)` | `torch.float32` | `cuda:0` | YES | 0-224; loader output is not yet divided by 255 |

Depth statistics:

```text
total pixels                 816000
positive/valid pixels        815998
non-positive/invalid pixels  2
non-finite pixels            0
units                        meters after division by 6553.5
```

Semantic IDs present in frame 0:

```text
[0, 13, 18, 19, 29, 37, 40, 47, 59, 64, 76, 78, 79, 80, 91, 93, 97, 98]
```

The frame-0 pose contains only float-rounding residuals up to approximately
`1.19e-7` away from exact identity. `VERIFIED FROM SOURCE`: the loader returns
`inverse(c2w_0) @ c2w_t`, so its runtime convention is first-frame-relative
c2w. No pose values were modified.

## Loader-only GPU memory

Measured in a fresh process after dataset construction, `empty_cache`, CUDA
synchronization, and peak-stat reset:

| Boundary | Allocated bytes | Reserved bytes |
|---|---:|---:|
| Before `dataset[0]` | 0 | 0 |
| After `dataset[0]` | 26,113,024 | 65,011,712 |

Peak allocated during the load was **45,697,024 bytes**. This is only a loader
measurement for one full-resolution frame. It does not estimate first-frame
Gaussian initialization, rasterization, tracking, mapping, or full-SLAM memory.

## Stop boundary and conclusion

All Phase 3B-C pass criteria were met. Specifically, minimal resize, dependency
closure, PyTorch CUDA backward, exact rasterizer import, dataset construction,
dataset length, and `dataset[0]` all pass with source/config/algorithm unchanged.

The task stopped immediately after validating frame 0. The following were not
called: `initialize_first_timestep`, `get_pointcloud`, and `initialize_params`.
No SLAM, tracking, mapping, evaluation, post-opt, or frame 1+ operation ran.

Next action: **Resume Phase 3B — First-Frame Gaussian Initialization**.
