# P6-BAM-006 — 3D Visualization Inventory

Run ID: `p6_bam_006_room0_0_1999_va2_r01`\
Visualization root: `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/visualization/va2/`

The existing `scripts/visualization/render_final_maps.py` workflow completed from the saved model. Validation records `PASS_V1_FINAL_RECONSTRUCTION_VISUALIZATION` and `PASS_V2_FINAL_SEMANTIC_VISUALIZATION`; three fixed camera views were rendered at 1600×900. The renderer did not run SLAM, tracking, mapping, optimization, or evaluation, and it did not modify the source PLY files.

| Product | Location | Meaning |
|---|---|---|
| RGB Gaussian 3D map views | `reconstruction/` | Rendered views of the saved RGB Gaussian model |
| Learned semantic-color 3D map views | `semantic/` | Same Gaussian geometry rendered with learned per-Gaussian semantic colors |
| Paired RGB/semantic views | `paired/` | Matched camera presentation for the three fixed views |
| Camera definitions | `cameras/` | `overview.json`, `oblique.json`, `top_oblique.json` |
| Metadata and validation | `metadata/` | map metadata, exact source hashes, validation report, manifest and summary |
| Renderer log | `logs/visualization.log` | Offline visualization execution evidence |

The authoritative model is the run's `params.npz`; `params.ply` stores RGB Gaussian attributes and `seg_params.ply` stores learned semantic colors. Per-Gaussian categorical semantic IDs remain in NPZ. `seg_params.ply` is **not** a categorical-ID PLY. Evaluation camera-view RGB/depth/semantic images are separately stored at the run's `eval/rendered_rgb`, `eval/rendered_depth`, and `eval/rendered_seg` paths; they are not the 3D map views.

Integrity: visualization validation confirms the RGB and semantic PLY source hashes are unchanged before/after rendering, the same camera parameters were used for both maps, all map Gaussian centers are represented in the views, images are nonempty/nonuniform, and the workflow is offline-only. The artifact manifest and SHA256 list are in `results/runtime_artifacts/phase6_bam/p6_bam_006_comparison/`.

Status: RGB 3D map `PASS`; learned semantic-color 3D map `PASS`; categorical semantic-ID PLY export `NOT_IMPLEMENTED` (IDs retained in NPZ).
