# P5-G3A-R2 — Numerical equivalence

Classification: **`INCONCLUSIVE / BLOCKED`**.

OFF-A and OFF-B matched the frame horizon, keyframe insertion indices,
observable mapping-selection lists, seed, configuration family, and iteration
schedule. They did not match final Gaussian count: 879,862 versus 879,218
(difference 644; relative to OFF-A approximately 0.0732%). Final camera
translation arrays also differed (maximum absolute difference approximately
`4.645e-4`).

No per-frame Gaussian trace exists in OFF mode, so the first divergence frame
is unknown. The result cannot distinguish existing CUDA nondeterminism from
threshold-sensitive pruning/append behavior. No tolerance was chosen after
observing the result, and LIGHT/DETAILED were intentionally not executed.
