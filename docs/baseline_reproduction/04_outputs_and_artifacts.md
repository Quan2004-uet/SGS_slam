# Outputs and Artifacts

## Artifact contract

| Stage | Artifact | Expected path/pattern | Required? |
|---|---|---|---|
| Online startup | Copied experiment config | `experiments/Replica/room0_0/config.py` | Yes, provenance |
| Online checkpoint | Parameters | `experiments/Replica/room0_0/params{frame}.npz` | Expected when checkpoint condition is reached; frame 0 qualifies |
| Online checkpoint | Keyframe indices | `experiments/Replica/room0_0/keyframe_time_indices{frame}.npy` | Expected with each checkpoint |
| Online evaluation | Evaluation root | `experiments/Replica/room0_0/eval/` | Yes |
| Online evaluation | Per-frame arrays | `eval/{psnr,rmse,l1,ssim,lpips,miou}.txt` | Yes for semantic run |
| Online evaluation | Summary plot | `eval/metrics.png` | Yes |
| Online evaluation | Rendered frames | `eval/rendered_rgb/`, `rendered_depth/`, `rendered_seg/`, plus plots | Expected because `save_frames=True` |
| Online final | Serialized map/state | `experiments/Replica/room0_0/params.npz` | Yes; post-opt input |
| Online final | RGB PLY | `experiments/Replica/room0_0/params.ply` | Yes |
| Online final | Semantic PLY | `experiments/Replica/room0_0/seg_params.ply` | Yes |
| Online logging | Console and optional W&B records | External/run capture | Yes as provenance; W&B itself may be disabled only in a recorded derived config |
| Standalone eval | Reloaded train-view evaluation | `experiments/Replica/room0_0/eval_train/` | Optional confirmation |
| Post-opt startup | Copied post-opt config | `experiments/Replica_postopt/postopt_room0_0/config.py` | Yes if post-opt runs |
| Post-opt intermediate | Evaluation plots/logs | `.../eval_7k/` | Expected at iteration 7,000 |
| Post-opt final | Evaluation plots/logs | `.../eval/` | Yes if post-opt runs |
| Post-opt final | NPZ and PLYs | `.../{params.npz,params.ply,seg_params.ply}` | Yes if post-opt runs |

Paths are `VERIFIED FROM CONFIG`; save behavior is `VERIFIED FROM SOURCE`.

## Important qualifications

- Final online `params.npz` contains Gaussian arrays, camera pose arrays,
  per-Gaussian timestep, intrinsics, first-frame w2c, original dimensions,
  ground-truth w2c sequence, and keyframe indices. It is both a reconstruction
  artifact and a state/provenance container. `VERIFIED FROM SOURCE`
- Checkpoint NPZs are written before final metadata is appended and are not
  identical in schema to final `params.npz`. `VERIFIED FROM SOURCE`
- No dedicated estimated trajectory text file is written; estimated pose arrays
  are inside `params.npz`, while ATE is printed/logged during evaluation.
- `utils.eval_helpers.eval` used online saves metric arrays and `metrics.png`.
- `utils.gs_helpers.eval` used by post-opt currently has metric `np.savetxt` and
  aggregate plot code commented. Its guaranteed static artifacts are per-frame
  plots plus console/W&B aggregate values, not the online metric text schema.
  `VERIFIED FROM SOURCE`
- Post-opt writes a separate directory by default and does not overwrite online
  output. Preserve that separation; never relabel post-opt metrics as online.
- Running a stage again with the same run name can overwrite same-named artifacts.
  Archive or select a new, recorded output location in Phase 3 before reruns.
  `INFERRED`

## Completion checklist

An online run is not accepted merely because `params.npz` exists. Confirm:

- config copy and captured environment/commit metadata;
- bounded/full-run logs contain no silent early termination;
- checkpoint pair consistency where expected;
- final NPZ opens and required keys have consistent Gaussian/frame dimensions;
- PLYs exist and are nonempty;
- evaluation arrays have matching sample counts and finite values;
- `metrics.png` and saved renders correspond to the intended run;
- stage (`online`, `post-opt`, or standalone eval) is explicit in every report.
