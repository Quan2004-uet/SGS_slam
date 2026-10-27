# Phase 7 Gate 3 visualization reference audit

**Audit result:** reference viewpoints and renderer are identified and
verified. Rendering is currently blocked because this Codex environment
cannot access the NVIDIA driver required by the canonical renderer.

## Canonical Phase 4 reference

The authoritative full-map visualization is
`/home/robot/research/SGS_slam/results/runtime_artifacts/phase4_vb001_visualization/`.
Its `metadata/visualization_summary.md` records `PASS_V1_FINAL_RECONSTRUCTION_VISUALIZATION`
and `PASS_V2_FINAL_SEMANTIC_VISUALIZATION`, native anisotropic Gaussian
splatting, white background, 1600×900 images, and the views `overview`,
`oblique`, and `top_oblique`. The corresponding `cameras/*.json` files hold
the complete camera extrinsic, intrinsic, clipping, and framing values.

The paired RGB and learned-semantic outputs are under `reconstruction/`,
`semantic/`, and `paired/`. This V1/V2 convention renders `params.ply` and
`seg_params.ply` with identical Gaussian geometry and exact identical camera
parameters. The semantic output is the saved learned per-Gaussian semantic
color field; it is not categorical semantic-ID coloring.

Canonical camera SHA256 values:

| View | Phase 4 camera JSON SHA256 |
|---|---|
| `overview` | `c5e0029b1758788322538ce27e587c8cdfa5a3277aba331431e50d5ac80865bb` |
| `oblique` | `9846a224e93b3615afd45097b9106037c3550b5199b74d4e0550f328ad220120` |
| `top_oblique` | `0d865494919fb2066cf769ef654163ee3f1e262d5ebb4cf8b95681d6934ec196` |

## Phase 6 reference and exact camera correspondence

The initial Phase 6 `visualization/va2/` package used different camera JSONs
and is **not** the comparison reference. The validated
`/home/robot/research/SGS_slam/results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/`
package explicitly reuses the Phase 4 V1 JSON files. Direct byte comparison
confirms that all three camera files match Phase 4, including the hashes
above. Its `metadata/visualization_summary.md` records the same image size,
white background, native Gaussian renderer, and learned semantic-color
rendering.

Phase 6 also has an extended V3A family with exact Phase 4 V3A camera JSONs
and categorical semantic-ID diagnostics. That is a distinct visualization
family. For the Phase 7 full-map paired comparison, use the simpler V1 camera
family already shared exactly by Phase 4 and Phase 6. Do not mix V1 and V3A
views in a single matched panel.

## Renderer and conventions

The reusable renderer is
`/home/robot/research/SGS_slam/scripts/visualization/render_final_maps.py`,
SHA256 `b46eb61fee2f2cc40488bcc560dc10065b4074023808c2cc027c9a270095ade0`.
It accepts an explicit `--camera-dir`, validates the three view names and
resolution, copies camera JSONs without changing their bytes, renders both
maps with the native `diff_gaussian_rasterization` CUDA extension, and emits
camera/map metadata, paired PNGs, validation, and SHA256 manifest. It refuses
to overwrite nonmatching existing output artifacts. Renderer coordinate
convention is OpenCV-style world-to-camera (`+x` right, `+y` down, `+z`
forward); it uses PLY world coordinates directly and performs no geometry
transform.

The Phase 7 source PLYs are verified against the final checkpoint: both have
4,499,583 vertices, XYZ arrays exactly equal `params.npz::means3D`, and
decoded degree-0 color coefficients exactly equal the corresponding
`rgb_colors` or `semantic_colors`. All points are finite. CPU projection
against each authoritative camera verifies all Phase 7 Gaussian centers fit
inside all three views. No viewpoint inference or new framing is needed.

Phase 7 input hashes:

| Input | SHA256 |
|---|---|
| `params.npz` | `a02dd4b4ecfd9c982866cf4a4c38c187ef22c75049b8328e18eea20608944917` |
| `params.ply` | `409d1c3637e3f951f950d14bf066a88df66de8dc41a01762c312a0871ab300fc` |
| `seg_params.ply` | `98a41a36e69e113c7e7da8dcfcd8c279c08c25da8af7525e26dcbdb7df262b89` |

## Availability blocker

The current `nvidia-smi --query-gpu=...` call fails with “couldn't
communicate with the NVIDIA driver.” The canonical renderer explicitly checks
`torch.cuda.is_available()` and requires its compiled CUDA rasterizer. No
image was rendered, no alternative CPU renderer was substituted, and no
output directory was created. Re-run the read-only GPU check and the guarded
render command on the direct GPU host. This is an environment-visibility
blocker, not evidence that the host GPU is failed.
