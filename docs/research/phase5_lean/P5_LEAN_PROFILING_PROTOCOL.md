# P5-LEAN Profiling Protocol

## Required matched measurements

- End-to-end online wall time; tracking and mapping wall time.
- Configured and executed mapping iterations per event and total.
- Peak PyTorch GPU allocated/reserved, process RSS/HWM.
- CPU archive logical bytes, H2D event count/cumulative bytes.
- Final/per-sampled-frame Gaussian count, keyframe count, completion/OOM/non-finite status.
- Run ID, source/config hashes, environment, GPU, seed and exact horizon.

## Trust boundary

**VALIDATED ENOUGH FOR LEAN USE:** existing CPU `perf_counter` tracking/mapping spans, archive/staging byte counters, Gaussian/keyframe counters, `/proc` RSS/HWM, and PyTorch allocated/reserved sampling have produced structurally valid LIGHT output over 0–99 with zero event drops. They still need one short matched integration check after BAM implementation.

**NOT_VALIDATED FOR REQUIRED DECISIONS:** comprehensive DETAILED component CUDA timing. Retry1 dropped spans and FIX1 was synthetic-only. Comprehensive DETAILED profiling remains deferred; CUDA component timing is optional diagnostic evidence, not a prerequisite.

Use the same LIGHT configuration for V0/V-FIXED/V-A. OFF runs may establish correctness but are not runtime-comparable to LIGHT. Do not sum nested H2D/component spans into total mapping wall time.

Minimal next measurement test: one separately authorized 0–10 V0 LIGHT run and one V-A LIGHT run after CPU tests, verifying schema, horizon, counters, no event loss, and plausible executed-budget telemetry. No DETAILED run is required.
