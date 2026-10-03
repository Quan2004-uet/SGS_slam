# Gates 1A/1B — Dependency Verification

## PyTorch and CUDA raw evidence

Final verification output:

```text
torch 2.0.1
torchvision 0.15.2
torchaudio 2.0.2
torch_cuda 11.8
cuda_available True
device_count 1
device_name NVIDIA GeForce GTX 1650 Ti
capability (7, 5)
cuda_tensor tensor([1.], device='cuda:0', requires_grad=True)
cuda_grad tensor([3.], device='cuda:0')
```

Environment-local compiler output:

```text
nvcc: NVIDIA (R) Cuda compiler driver
Cuda compilation tools, release 11.8, V11.8.89
```

Gate 1A: **PASS**. Import, device enumeration, allocation, a scalar operation,
backward, and explicit synchronization completed.

## Dependency imports

```text
No broken requirements found.
numpy 1.26.4
scipy 1.12.0 interpolate_ok
open3d 0.16.0
sklearn 1.6.1
cv2 4.11.0
kornia 0.8.2
imageio 2.37.2
matplotlib 3.9.4
tqdm 4.65.0
wandb 0.26.1
lpips imported
pytorch_msssim imported
pandas 2.3.3
plyfile imported
yaml 6.0.3
torchmetrics 1.8.2
cyclonedds imported
```

Optional side-effect-free repository imports also passed:

```text
core_helpers_import=PASS
ReplicaDataset_import=PASS
```

This covered `utils.slam_helpers`, `utils.slam_external`,
`utils.keyframe_selection`, and the `ReplicaDataset` class. `scripts/slam.py` was
not imported or executed; no W&B run or dataset load was initiated.

## Role classification

| Dependency group | Packages | Result |
|---|---|---|
| CORE REQUIRED | PyTorch, torchvision, NumPy, SciPy, OpenCV, Kornia, imageio, natsort, PyYAML, tqdm, renderer | PASS |
| EVALUATION REQUIRED | torchmetrics, LPIPS, pytorch-msssim, matplotlib, pandas | PASS |
| SUPPORT / POST-OPT / VISUALIZATION | Open3D 0.16.0, plyfile, cyclonedds, scikit-learn | PASS |
| LOGGING | W&B | Import PASS; initialization intentionally not tested |
| UNKNOWN / NOT ON VERIFIED ONLINE PATH | FAISS GPU | Not installed; not a Phase 3A gate |

Gate 1B: **PASS** after the documented environment-only recoveries.
