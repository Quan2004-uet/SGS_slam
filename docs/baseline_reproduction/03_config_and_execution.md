# Configuration and Execution

All commands below assume the repository root as working directory. They are
documented only; none was executed in Phase 2.

## Canonical online config audit

Source read-sites are in `scripts/slam.py` unless noted. A key is called active
only when a read-site occurs on the canonical path.

| Area | Active values for Replica room0 | Source behavior |
|---|---|---|
| Schedule | `map_every=1`, `keyframe_every=5`, window 24 | Mapping condition at `time_idx==0` or `(time_idx+1)%map_every==0`; keyframe insertion condition reads the keyframe interval. |
| Tracking | 40 iterations; forward propagation; no GT pose | Creates a per-frame Adam; only camera quaternion/translation have nonzero LR. Failed depth loss can trigger an extra 80 iterations. |
| Tracking LRs | camera quaternion `4e-4`, translation `2e-3`; all Gaussian groups and semantic colors `0` | Read by `initialize_optimizer`. |
| Tracking loss | image 0.5, depth 1.0, semantic 0.05; L1; silhouette mask threshold 0.99 | Read by `get_loss`; semantic rendering is active because `load_semantics=True`. |
| Mapping | 60 iterations at each mapping event | Samples current frame plus selected stored keyframes, then optimizes map Adam. |
| Mapping LRs | means `1e-4`, RGB `2.5e-3`, rotation `1e-3`, opacity `5e-2`, scales `1e-3`, semantic RGB `2.5e-3`; camera LRs `0` | Camera arrays are in optimizer groups but frozen by zero LR. |
| Mapping loss | image 0.5, depth 1.0, semantic 0.1; L1; no silhouette loss | Read by `get_loss`. |
| Gaussian addition | enabled; silhouette threshold 0.5 | Pixel-driven append before mapping for frames after frame 0. |
| Pruning | enabled; iter 0/20 schedule, opacity threshold .005, no reset | `prune_gaussians` branch is active. |
| Clone/split densification | disabled | The densification dictionary exists but its guarded path is inactive online. |
| Checkpoints | enabled every 500 frame indices | Saves `params{time_idx}.npz` and keyframe index array; index 0 qualifies. |
| Evaluation | every 5 frames at final evaluation | Passed to `utils.eval_helpers.eval`. |
| W&B | enabled; entity is placeholder `my-project` | Active initialization path; an operational prerequisite/blocker. |
| Dataset | semantic Replica, all frames, stride 1, 680x1200 | Passed into `ReplicaDataset`; actual frame count comes from dataset length. |

All values are `VERIFIED FROM CONFIG`; source behavior/read-sites are `VERIFIED
FROM SOURCE`.

No `use_uncertainty_for_loss` or `use_chamfer` key participates in this checked-in
Replica config or verified online path. `do_ba` is a helper branch, not an active
caller. Do not add keys or enable these features during released-source
reproduction.

## Commands

### A. Online SLAM — baseline, required

```bash
python scripts/slam.py configs/replica/slam.py
```

- Provenance: exact README command; positional config loading verified in source.
- Dataset prerequisite: `./data/Replica/room0/` with the semantic layout.
- Output: `./experiments/Replica/room0_0/`.
- Stage: online tracking, Gaussian addition, keyframe mapping, final evaluation,
  and final save.
- W&B prerequisite: default config attempts W&B initialization with placeholder
  entity. Phase 3 must explicitly record whether credentials/entity are supplied
  or a separate reproduction config disables W&B. Do not silently edit the
  checked-in config.

### B. Post-SLAM optimization — baseline stage, conditional

```bash
python scripts/post_slam_opt.py configs/replica/post_slam_opt.py
```

- Provenance: exact README command; positional config loading verified in source.
- Input prerequisite: `./experiments/Replica/room0_0/params.npz`.
- Output: `./experiments/Replica_postopt/postopt_room0_0/`.
- Stage: 15,000-iteration offline Gaussian refinement with GT cameras, selected
  frame stride 20, eval stride 5, and gradient clone/split densification.
- Optional until the online run and its evaluation have been preserved.

### C. Standalone final training-view evaluation — baseline support

```bash
python scripts/eval_novel_view.py configs/replica/slam.py
```

- Provenance: CLI contract and default `use_train_split=True` verified in source.
- Input: `./experiments/Replica/room0_0/params.npz`.
- Output: `./experiments/Replica/room0_0/eval_train/`.
- Despite the script name, the checked-in Replica config has no
  `data.use_train_split`; source defaults it to `True`, so this command evaluates
  training views rather than novel views.
- This is redundant with the online script's final evaluation for many purposes,
  but it provides a reload/evaluator check.

### D. Novel-view evaluation — deferred, no canonical Replica command

Generic CLI:

```bash
python scripts/eval_novel_view.py <experiment_config_with_use_train_split_false>
```

`eval_nvs` is selected only when `data.use_train_split=False`. The checked-in
`configs/replica/slam.py` does not request that split, and the canonical loader is
`ReplicaDataset`, not necessarily a ReplicaV2 NVS layout. Therefore an exact
room0 NVS command/config is `UNKNOWN / NEEDS RUNTIME VERIFICATION` and is not
required for the first baseline. No config should be invented in Phase 2.

### E. Visualization — optional artifact check

```bash
python viz_scripts/online_recon.py configs/replica/slam.py
python viz_scripts/tk_recon.py configs/replica/slam.py
```

These README commands are optional visualization checks, not metric evaluation.
They must not gate online numerical reproduction.

## Post-opt config audit

- Input path is the online final `params.npz`; output is separate.
- Dataset train stride is 20; evaluation stride is 5.
- 15,000 mapping iterations optimize Gaussian means/color/rotation/opacity/scale
  and semantic RGB. Camera LRs are zero.
- Means LR decays from `3.2e-4` to `3.2e-6`, delay multiplier .01.
- Densification begins after 500, runs every 100, stops at 15,000, removes large
  Gaussians after 3,000, and resets opacity every 3,000.
- Loss weights are image .5, depth 1.0, semantic .1.
- W&B is disabled in this config.

These are `VERIFIED FROM CONFIG`; behavior is `VERIFIED FROM SOURCE`. Post-opt is not a substitute for the
online map and must retain input/output provenance.

## Bounded-run prerequisite

The scripts expose only the experiment-file positional argument; there is no CLI
override for frame limits. Phase 3 bounded gates therefore require a clearly
named, recorded **derived reproduction config** that changes only frame count/end
and, if necessary, W&B logging. Keep the checked-in config unchanged and record a
diff against it. Such a config is test instrumentation, not the full baseline;
full-scene acceptance returns to the checked-in algorithm settings.
