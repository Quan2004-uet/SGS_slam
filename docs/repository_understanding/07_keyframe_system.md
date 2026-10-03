# Keyframe system

## Capture lifecycle

A frame is stored when it is frame 0, every `keyframe_every` frames under `(time_idx+1)%interval==0`, or the penultimate frame, and its GT w2c contains neither Inf nor NaN. Stored fields are ID, detached estimated w2c, RGB, depth, and optionally semantic ID/color. All tensors remain on GPU. **[VERIFIED FROM SOURCE]**

The validity gate uses GT pose, not estimated-pose quality. There is no candidate score at capture time. Shipped configs use interval five. **[VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

## Mapping-window selection

For a mapping event:

1. Sample 1600 valid-depth pixels from the current frame, with replacement.
2. Back-project through current estimated pose.
3. Reproject them into each candidate keyframe except the most recent one.
4. Compute fraction inside a 20-pixel border and with positive z.
5. Keep every candidate with overlap strictly above zero, randomly permute, take up to `mapping_window_size-2`.
6. Always append the latest stored keyframe, if any, then append current frame.

**[VERIFIED FROM SOURCE]** The list therefore contains at most `mapping_window_size` views. Mapping samples uniformly over this list; geometric overlap magnitude is not used as a sampling weight.

## Paper/code discrepancy

The paper specifies geometric threshold `Tgeo=0.05`, semantic mIoU filtering around `Tsem=0.7`, and time uncertainty weighting. Active code uses only `percent_inside > 0.0`; semantic selection is commented and no uncertainty weight is passed to mapping loss. No matching config keys exist. **[VERIFIED FROM README/DOCUMENTATION; VERIFIED FROM SOURCE; VERIFIED FROM CONFIG]**

This is the largest paper-to-released-code gap found in the core algorithm. It means “semantic-guided keyframe selection” should not be described as an executed behavior of commit `e418398...`.

Checkpoint restore stores only keyframe indices, then rereads their image tensors and reconstructs stored estimated poses. Selection histories can optionally be written to CSV. **[VERIFIED FROM SOURCE]**
