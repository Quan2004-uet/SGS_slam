# Environment Authority Audit

## Conflicting environment records

| Component | README | `environment.yml` | Requirements files | Paper | Audit conclusion |
|---|---|---|---|---|---|
| Python | 3.9 | 3.10 | Unpinned | Not stated | Prefer 3.9 candidate; 3.10 is alternative. |
| PyTorch | 2.0.1 | 1.12.1 | Unpinned | Not stated | Prefer 2.0.1 candidate; renderer compatibility remains unverified. |
| CUDA | Toolkit/PyTorch CUDA 11.8 | `cudatoolkit=11.6` | Not stated | A100 GPU only | Prefer 11.8 candidate; do not mix the two stacks. |
| torchvision | 0.15.2 | 0.13.1 | Unpinned | Not stated | Use version paired with selected PyTorch. |
| torchaudio | 2.0.2 | 0.12.1 | Unpinned | Not stated | Not on the verified core path, but preserve stack pairing. |
| Open3D | Via requirements | pip `open3d==0.16.0` | `0.16.0` in `requirements.txt`; absent from `venv_requirements.txt` | Not stated | 0.16.0 is the only pinned repository version. |
| Kornia | Via requirements | Conda package | Unpinned in both requirements files | Not stated | Required by dataset geometry utilities; exact version unknown. |
| FAISS | Not named | `faiss-gpu` | Absent | Not stated | Environment artifact only; no verified canonical online read-site. |
| Rasterizer | Installed through requirements | malformed-looking `/tree/<commit>` VCS URL | Git VCS URL pinned to `cb65e4b...` | Gaussian rasterization described, software revision not stated | `requirements.txt` pin is the usable static authority candidate. |

Table evidence: `VERIFIED FROM README`, `VERIFIED FROM CONFIG`, and `VERIFIED
FROM PAPER`. “Prefer” is an audit conclusion, not runtime validation.

## Candidate decision

**Preferred candidate:** follow the current README recipe: Conda Python 3.9,
PyTorch 2.0.1, torchvision 0.15.2, torchaudio 2.0.2, PyTorch CUDA 11.8, CUDA
toolkit 11.8, then `requirements.txt`. The README contains the most explicit
current installation sequence, while `requirements.txt` contains a syntactically
normal pinned renderer URL. `INFERRED FROM REPOSITORY PROVENANCE`

**Alternative candidate:** create the stack specified by `environment.yml`
(Python 3.10, PyTorch 1.12.1, torchvision 0.13.1, torchaudio 0.12.1, CUDA 11.6),
but install the renderer from the pin in `requirements.txt` if the environment
file's `/tree/<commit>` line cannot be resolved. Changing that line would be a
documented compatibility recovery, not an algorithm change. `VERIFIED FROM
CONFIG`; actual feasibility is unknown.

**Unknown until runtime:** which candidate successfully builds the pinned
rasterizer and reproduces metrics; driver compatibility; compiler compatibility;
whether unpinned packages still resolve to mutually compatible releases.

Do not “solve” this conflict by selecting current/latest packages. Phase 3 must
test the preferred candidate first and record any recovery change explicitly.

## CUDA renderer contract

- Distribution source: `https://github.com/JonathonLuiten/diff-gaussian-rasterization-w-depth.git`.
- Pinned revision: `cb65e4b86bc3bd8ed42174b72a62e8d3a3a71110`.
- Install record: pip VCS entry in `requirements.txt` and
  `venv_requirements.txt`. `VERIFIED FROM CONFIG`
- Import name: `diff_gaussian_rasterization`; `GaussianRasterizer` is imported as
  `Renderer`. `VERIFIED FROM SOURCE`
- Direct consumers include `scripts/slam.py`, `scripts/post_slam_opt.py`,
  `utils/slam_helpers.py`, `utils/eval_helpers.py`, and `utils/gs_helpers.py`.
- The external repository is not vendored and its build scripts were not audited
  locally. A native CUDA extension build through pip is expected, but its exact
  build mechanism is `UNKNOWN / NEEDS RUNTIME VERIFICATION`.
- PyTorch, CUDA toolkit, driver, C++ compiler, and GPU architecture compatibility
  are ABI-sensitive for a compiled extension. `INFERRED`

No renderer was built or imported during Phase 2.

## Other dependency roles

| Dependency | Static role | Status |
|---|---|---|
| PyTorch | tensors, autograd, Adam, CUDA | Core runtime; source verified |
| Kornia | pose/geometry conversion in dataset modules | Core dataset path; source verified |
| `pytorch-msssim` | evaluation MS-SSIM | Required by online evaluator; requirements verified |
| `torchmetrics` | AlexNet LPIPS | Required by online evaluator; requirements/source verified |
| OpenCV | image output and evaluation helpers | Evaluation/support; source verified |
| Open3D 0.16.0 | PLY/geometry utilities imported by post-opt helper path | Post-opt/support; source verified |
| W&B | default online experiment logging | Active by default for Replica online config |
| FAISS GPU | present in Conda environment | No active canonical path verified |

`venv_requirements.txt` is an incomplete alternative relative to the main
requirements: it omits packages such as Open3D, OpenCV, pandas, and plyfile. Do
not treat it as a standalone authoritative environment without import auditing.

## Phase 3 system checklist

Record, do not silently alter:

- NVIDIA GPU model, compute capability, and available VRAM.
- NVIDIA driver version and its supported CUDA runtime.
- `nvcc`/CUDA toolkit version (preferred candidate 11.8).
- Python, Conda, pip, PyTorch, torchvision, and torchaudio versions.
- GCC/G++ versions and compatibility with the selected CUDA toolkit.
- Native build tools needed by PyTorch C++/CUDA extensions (compiler, linker,
  headers; Ninja if the extension requests it).
- Successful import and device identity for PyTorch.
- Successful import plus bounded forward/backward test for the pinned renderer.
- Exact resolved versions of unpinned dependencies.
- At least the paper's stated typical memory envelope should be considered: the
  paper reports experiments on an A100 40 GB and says typical usage is below
  12 GB. This is not a guarantee for this source/config/hardware combination.
