# Gate 0 — Host Inventory

## Pre-flight

```text
$ git rev-parse HEAD
e4183986204242a8bb422624618af07780a49d26

$ git branch --show-current
main

$ git status --short
?? 2402.03246v6.pdf
?? AGENTS.md
?? docs/
```

HEAD matched the expected audit baseline, so recovery continued. There were no
tracked source/config changes. The three untracked entries predated Phase 3A.

## OS and capacity

```text
Ubuntu 22.04.5 LTS (Jammy Jellyfish)
Linux 6.8.0-138-generic
x86_64
RAM: 23 GiB total, 17 GiB available at inventory
Swap: 2.0 GiB
Disk: 457 GiB total, 339 GiB available on repository and /tmp filesystem
```

## GPU and CUDA

An initial sandboxed `nvidia-smi` failed because no `/dev/nvidia*` devices were
exposed there. PCI inspection still found the NVIDIA GPU and loaded driver. The
same command outside the device-restricted sandbox returned:

```text
NVIDIA-SMI 580.178.04
Driver Version: 580.178.04
CUDA Version: 13.0
GPU 0: NVIDIA GeForce GTX 1650 Ti
Memory: 4096 MiB
Compute capability: 7.5
```

The `13.0` value is the maximum CUDA compatibility reported by the driver; it is
not the compiler toolkit. No system `nvcc` was present. After isolated environment
creation, the environment-local toolkit reported:

```text
Cuda compilation tools, release 11.8, V11.8.89
```

Kernel driver modules were loaded; `/proc/driver/nvidia/version` reported kernel
module 580.178.04. GPU runtime commands in this audit were therefore executed
outside the device-restricted sandbox.

## Compiler and tools

```text
gcc (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0
g++ (Ubuntu 11.4.0-1ubuntu1~22.04.3) 11.4.0
System python3: 3.10.12
System python command: absent
Conda: 26.7.1 at /home/quan/miniconda3/condabin/conda
System pip: 22.0.2 for Python 3.10
Mamba: absent
```

## Compatibility matrix

| Component | Required candidate | Host/runtime | Status |
|---|---|---|---|
| NVIDIA driver | Must support CUDA 11.8 | 580.178.04, compatibility up to CUDA 13.0 | COMPATIBLE |
| CUDA toolkit | 11.8 | No system toolkit; isolated toolkit 11.8.89 installed | COMPATIBLE |
| GCC/G++ | CUDA 11.8-compatible compiler | 11.4.0 | LIKELY COMPATIBLE before build; build PASS confirmed |
| Python | 3.9 | Isolated Python 3.9.25 | COMPATIBLE |
| Conda | Available | 26.7.1 | COMPATIBLE |
| GPU architecture | Renderer/PyTorch CUDA target | SM 7.5 | COMPATIBLE; wheel built with `TORCH_CUDA_ARCH_LIST=7.5` |
| VRAM | Smoke test only in Phase 3A | 4096 MiB | COMPATIBLE for Phase 3A; full baseline capacity UNKNOWN |

Gate 0: **PASS**. The 4 GiB GPU is a material future capacity risk and must not
be interpreted as sufficient for full-resolution room0.
