# P5-LEAN Evaluation Protocol

All comparisons must match dataset/scene, inclusive frame range, seed, RTX 5080 environment, resolution, output-saving policy, LIGHT profiler settings, evaluation frames, and evaluator implementation.

## Metrics

- Tracking: released ATE Mean, supplementary true ATE RMSE, complete horizon and tracking failures.
- Mapping: PSNR, MS-SSIM (not generic SSIM), LPIPS-Alex, Depth L1, final Gaussian count and fixed-camera qualitative panels.
- Semantic: semantic-color mIoU under the existing GT-palette-assisted Phase 4 protocol.
- Resources: online wall, tracking/mapping wall, mapping iterations, peak allocated/reserved, RSS/HWM, archive bytes, H2D count/bytes, OOM/non-finite status.

## Non-inferiority policy

Bit-exact Gaussian equality is not required: R2 observed 644-Gaussian OFF-vs-OFF variation (0.0732%) over 0–10. Structural invariants, complete horizon, finite state, unchanged keyframes/schedule outside the controller, and matched evaluator inputs remain mandatory.

Pre-registered **provisional research targets**, not validated margins:

- runtime: at least 20% lower matched online wall time for V-A versus V0;
- ATE RMSE: no more than 10% relative or 1 mm absolute degradation, whichever is larger;
- PSNR: no more than 0.5 dB decrease;
- MS-SSIM: no more than 0.01 decrease;
- LPIPS: no more than 0.02 increase;
- Depth L1: no more than 10% increase;
- semantic mIoU: no more than 0.02 absolute decrease;
- no new failure/OOM and no loss of frame completion.

These targets are design choices, not inferred from current evidence. Before the 0–499 decision, freeze them and report V0 repeat variability where affordable. If short calibration shows baseline noise exceeds a margin, disclose it and revise prospectively before medium/full runs—never after seeing final variant results.

Primary scene is Replica `room0`. The high-priority generalization target is `office0` 0–499 because the earlier dataset audit verified its 2,000-frame structural layout and selected it for geometry/semantic variation; runtime validity remains unverified. Attempt it only after V-A passes room0 medium horizon. If omitted, claims remain room0-specific.
