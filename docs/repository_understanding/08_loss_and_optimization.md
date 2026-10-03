# Loss and optimizer audit

## Online losses

| Term | Tracking | Mapping | Gradient targets |
|---|---|---|---|
| depth | masked pixelwise L1 **sum** | valid-depth L1 **mean** | pose vs map geometry/opacity/scale |
| RGB | masked L1 **sum** | `0.8 mean L1 + 0.2(1-SSIM)` | pose vs map attributes |
| semantic | masked L1 **sum** | `0.8 mean L1 + 0.2(1-SSIM)` | pose vs semantic/map attributes |
| silhouette | not a direct loss | not a direct loss | tracking mask and append criterion only |
| uncertainty | no loss/weight | no loss/weight | detached; only finite-value mask |

**[VERIFIED FROM SOURCE]** There is no cross entropy, class balancing, Dice, feature contrastive loss, regularizer, explicit scale loss, pose smoothness, or direct opacity loss.

With shipped weights:

- Replica/ScanNet++ tracking: `L = 1.0 Ldepth + 0.5 Lrgb + 0.05 Lsemantic`.
- ScanNet tracking: same but semantic weight zero.
- Online mapping: `L = 1.0 Ldepth + 0.5 Lrgb + 0.1 Lsemantic`.
- Post-opt: same mapping weights, with its separate loss implementation.

**[VERIFIED FROM CONFIG]** `use_l1=False` would omit depth entirely, but shipped configs use true. Several config keys (`use_uncertainty_for_loss*`, `use_chamfer`) are never read by `scripts/slam.py`. **[VERIFIED FROM CONFIG; VERIFIED FROM SOURCE]**

## Optimizer architecture

| Stage | Optimizer/lifetime | Parameter groups |
|---|---|---|
| tracking | new default PyTorch Adam per tracked frame | every parameter except semantic IDs; Gaussian LR 0, camera LR nonzero |
| online mapping | new Adam per mapping event, `eps=1e-15` | same exclusions; Gaussian LR nonzero, camera LR 0 |
| post-opt | initialized then recreated per outer frame; only final one is stepped | saved map fields with keys in LR dict; camera LR 0 |

**[VERIFIED FROM SOURCE]** Adam moments are lazy: only parameters with gradients acquire state. Because renderer attributes are not fully detached during tracking, zero-LR Gaussian groups may still allocate moments. Mapping moments scale linearly with all trainable Gaussian values.

Prune/densify helpers replace Parameters in optimizer groups and preserve/filter/extend `exp_avg` and `exp_avg_sq`. Pixel append instead happens before mapping optimizer construction and performs raw concatenation. **[VERIFIED FROM SOURCE]**

There is no optimizer checkpoint persistence: NPZ stores tensors only. Resuming reconstructs fresh optimizer state and resets densification accumulators/timestamps (timestamps are set all zero in online checkpoint restore). **[VERIFIED FROM SOURCE]**

## BA loss

There is no executed `L_BA`. If the dormant `do_ba=True` branch were called, it would reuse exactly `get_loss` mapping terms with both camera and Gaussian-center gradient, but no current optimizer/caller activates it. **[VERIFIED FROM SOURCE]**
