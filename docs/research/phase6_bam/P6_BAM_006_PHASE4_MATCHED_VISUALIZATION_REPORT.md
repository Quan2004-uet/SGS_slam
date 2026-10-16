# P6-BAM-006 — Phase 4 Camera-Matched Visualization Export

Date: 2026-10-17
Status: `PASS_P6_BAM_006_PHASE4_MATCHED_VISUALIZATION`

## Result

A new Phase 6 visualization package was rendered from the already-saved P6-BAM-006 V-A2 model using the exact camera JSON files from the validated Phase 4 V1 final-map visualization. The earlier Phase 6 `visualization/va2/` package did **not** use the same cameras: all three camera-file hashes differed. The new `va2_phase4_matched/` package uses byte-identical copies of the Phase 4 files, the same native renderer, 1600×900 map images, and white background.

No SLAM, tracking, mapping, optimization, or evaluation was run. The only CUDA work was the explicitly requested offline visualization from saved model files.

## Sources and exact camera provenance

Phase 4 camera source: `results/runtime_artifacts/phase4_vb001_visualization/cameras/`. This is the package whose metadata records `PASS_V1_FINAL_RECONSTRUCTION_VISUALIZATION` and `PASS_V2_FINAL_SEMANTIC_VISUALIZATION`; its summary records 1600×900, white background, and `overview`, `oblique`, `top_oblique` views.

| View | Phase 4 camera JSON SHA256 | Prior Phase 6 `va2/` SHA256 | New output camera |
|---|---|---|---|
| overview | `c5e0029b1758788322538ce27e587c8cdfa5a3277aba331431e50d5ac80865bb` | `827a39e5529742421e710efab060cd2626bf9d886d3556e1cd9bf02760a1e96f` | byte-identical to Phase 4 |
| oblique | `9846a224e93b3615afd45097b9106037c3550b5199b74d4e0550f328ad220120` | `300ec0af073077f37a863bb9c24346cf5ba537473fcea7ab0beeb6b8d3d2fb7f` | byte-identical to Phase 4 |
| top_oblique | `0d865494919fb2066cf769ef654163ee3f1e262d5ebb4cf8b95681d6934ec196` | `8a295bc500684914897c0fb49117bf3734aed68fc7a458e6507fcf9c84f043d0` | byte-identical to Phase 4 |

Saved Phase 6 model inputs:

| File | SHA256 |
|---|---|
| `results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/params.npz` | `1193f5d5a854225d6e9fc68154d459b5eb026e056a91b5f00639b8da0facd0a5` |
| `results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/params.ply` | `dc10441cd383ad7861d27fb70a4f9a76fe9dd88a91e2bacc197b18bbe24cb50a` |
| `results/runtime_artifacts/phase6_bam/p6_bam_006_room0_0_1999_va2_r01/seg_params.ply` | `98676b4c3e6447681f99426153dfb112bee76882ac9f5d3a18cf11f4832fec21` |

The input hashes match the known post-P6-BAM-006 values; the renderer also recorded equal before/after hashes for both PLYs, and CPU validation verified the NPZ hash after rendering. No model input was modified.

## Renderer and output

The same repository entrypoint was used: `scripts/visualization/render_final_maps.py` (validated base renderer SHA256 `6c24f65dbac4960d681afd7be95995ca7649d4496a36d4d2b356ce17c5051d5f`; optional `--camera-dir` support was added for this export, resulting working-file SHA256 `b46eb61fee2f2cc40488bcc560dc10065b4074023808c2cc027c9a270095ade0`). The additive camera-input path loads the supplied Phase 4 JSONs and copies their bytes unchanged; the renderer continues to use its native Gaussian rasterizer. Rendering used 1600×900 per view and white background, matching the Phase 4 visualization summary. The copied JSONs preserve the original extrinsic, intrinsic, clipping, and image-framing parameters.

New isolated output root: `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2_phase4_matched/`

- `reconstruction/`: 3 PNGs (`overview`, `oblique`, `top_oblique`), each 1600×900.
- `semantic/`: 3 PNGs, same views and size, rendered from `seg_params.ply`.
- `paired/`: 3 side-by-side PNGs, each 3200×956 including renderer labels.
- `cameras/`: exact Phase 4 camera JSON copies.
- `metadata/`: visualization manifest, validation report, summary, and map metadata.
- `logs/`: successful renderer logs and preserved failed-preflight attempt logs.

CPU validation confirms all nine PNGs are present, nonzero and nonuniform; every map image has the expected dimensions; each required camera has reconstruction, semantic, and paired outputs; Phase 6 Gaussian centers fit inside each supplied view; and output camera files match Phase 4 byte-for-byte. Machine-readable details are in `metadata/visualization_manifest.json` and `metadata/validation_report.json`; the manifest lists and hashes 23 non-manifest output files.

`seg_params.ply` visualizes learned per-Gaussian semantic colors; it is **not** a categorical semantic-ID PLY. Semantic IDs remain in the saved NPZ.

## Scope and execution notes

The first renderer invocation was safely rejected by its no-overwrite guard before accessing model data. A subsequent restricted-context invocation copied the exact camera files but could not access CUDA and stopped before rendering. Those logs are retained. The successful host rendering used the same saved model and isolated target; it completed with 0 exit status (5.0 s renderer elapsed, approximately 2.01 GB peak host RSS). No SLAM rerun or evaluation was performed, and the Phase 4 and previous Phase 6 visualization directories were left intact.
