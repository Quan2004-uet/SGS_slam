# GPU/VRAM architecture

This is a static allocation model, not a measurement.

## Categories

| Category | Allocation/lifetime | Scaling |
|---|---|---|
| A Gaussian state | `initialize_params`, append/densify; whole run | `O(N)` |
| B gradients/Adam | backward and stage optimizer | `O(N)` plus `O(T)` cameras |
| C camera state/settings | pose arrays and raster camera objects | `O(T)` plus small constants |
| D keyframes | GPU image/depth/semantic dictionaries | `O(KHW)` |
| E current/dataset tensors | `__getitem__` directly returns GPU tensors | `O(HW)` per live view |
| F semantics | per-Gaussian RGB+ID, per-frame ID+RGB, third render | `O(N)+O(KHW)+O(HW)` |
| G renderer buffers | external CUDA forward/backward | unknown; expected `N`, visible splats, tiles, pixels **[INFERRED]** |
| H autograd | three render graphs and transforms per iteration | `O(N)+renderer-dependent` |
| I mapping temporaries | transformed points, masks, images, resize copies | `O(N)+O(HW)`; append/prune can transiently duplicate |
| J evaluation/viz | render outputs, LPIPS/MS-SSIM, plots | resolution/model dependent |

## Per-Gaussian lower-bound accounting

With semantics and float32, persistent map parameters hold 15 trainable floats (center 3 + RGB 3 + quaternion 4 + opacity 1 + scale 1 + semantic RGB 3) plus one semantic-ID float: about 64 bytes/Gaussian. Four auxiliary floats add about 16 bytes. Gradients for all trainable values add up to 60 bytes when materialized. Adam's two moment tensors add about 120 bytes after state is initialized. Thus a mapping-time tensor-only lower bound is roughly 260 bytes/Gaussian, excluding PyTorch objects, allocator rounding, temporary transformed/tiled tensors, and renderer buffers. **[INFERRED FROM VERIFIED SHAPES]**

The `N×1` scale is tiled to `N×3` for every render pass, and each loss uses separate render dictionaries/passes. Temporary memory can therefore materially exceed the persistent lower bound. **[VERIFIED FROM SOURCE; INFERRED]**

## Stage-specific pressure

Tracking nominally freezes the map through zero LR, but RGB/rotation/opacity/scale/semantic values remain in the graph. Their gradients can cause lazy Adam moments even for zero-LR groups. The optimizer is recreated each frame. **[VERIFIED FROM SOURCE]**

Online mapping recreates Adam each map event; its state grows with Gaussian count. Pixel append constructs concatenated replacement tensors while the previous tracking optimizer may still reference old map tensors, giving possible transient duplication. Pruning/densification similarly concatenate/filter parameter and moment arrays. **[INFERRED]**

Keyframes are a clear frame-count-dependent resident allocation: RGB `3HW`, depth `HW`, semantic ID `HW`, semantic RGB `3HW` plus pose, all on GPU. With float RGB/depth/semantic color and commonly int64 semantic IDs, semantics make this especially expensive. Actual semantic-ID dtype must be measured per loader/image backend. **[VERIFIED FROM SOURCE; UNKNOWN / NEEDS RUNTIME VERIFICATION]**

Post-opt intentionally preloads all selected frames and one raster camera object per frame onto GPU, so it scales as `O(FHW)` rather than online `O(KHW)`. **[VERIFIED FROM SOURCE]**

`torch.cuda.empty_cache()` is called after each online frame and in resize helpers, but it only releases unused cached blocks; it cannot release tensors retained by Python lists, optimizers, or graphs. No explicit deletion of keyframes or old optimizers is present. **[VERIFIED FROM SOURCE]**

## Conceptual equation

```text
VRAM_total ≈ Gaussian parameters + gradients + Adam moments
           + per-Gaussian auxiliaries and transformed/tiled values
           + camera/keyframe/current-frame tensors
           + semantic tensors
           + rasterizer forward/backward buffers
           + autograd graph
           + append/prune/densify transient copies
           + evaluation/LPIPS/visualization allocations
```

Peak values, allocator fragmentation, actual visible-splat buffers, and whether three render graphs overlap until backward are **[UNKNOWN / NEEDS RUNTIME VERIFICATION]**.
