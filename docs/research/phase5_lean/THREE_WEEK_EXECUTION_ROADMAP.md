# Three-Week Execution Roadmap — 15 October to 5 November 2026

The final deadline is **November 5, 2026**.

## Week 1 — 15–21 October: implementation readiness

- Close P5-LEAN-001; authorize P6-BAM-001 separately.
- Implement the novelty-aware controller, disabled by default, with CPU tests and static integrity audit.
- Run only approved 0–10 smoke tests, then V0/V-FIXED/V-A 0–49 functional comparison.
- By 21 October: a functioning V-A with valid telemetry and acceptable short-horizon behavior, or invoke fallback.

## Week 2 — 22–28 October: bounded decision and freeze

- Run selected V0/V-FIXED/V-A at 0–99 under matched LIGHT mode.
- Freeze one V-A configuration; run V0/V-A at 0–499 for the 25 October go/no-go decision.
- If gates pass, authorize final room0 execution; prioritize one additional scene only if compute and data readiness allow.
- Freeze code, config, evaluator and run IDs by 28 October.

## Week 3 — 29 October–5 November: final evidence and thesis

- Complete matched final evaluation: ATE, PSNR, MS-SSIM, LPIPS, Depth L1, semantic mIoU, runtime and memory.
- Produce qualitative panels, ablation table, limitations, reproducibility record and thesis/presentation material.
- Start no new feature family. Final deadline: 5 November.

## Fallback

If V-A is not functional by 21 October, stop adaptive development. Complete a controlled fixed-budget study plus V0 evidence, explicitly describing it as a systems/parameter trade-off rather than a novel adaptive algorithm.

## Minimum viable thesis deliverables

Phase 4 CPU-offload contribution; one controlled mapping-budget study; matched room0 runtime/memory/quality results; fixed-budget control; failure and reproducibility disclosure; thesis tables, figures and artifact index.

## Stretch goals

Replica `office0` 0–499 as the prioritized additional-scene target, repeated medium runs, and bounded GPU keyframe reuse only after all core deliverables and V-A validation are secure.
