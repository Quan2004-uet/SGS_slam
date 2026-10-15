# P5-LEAN Variant and Ablation Plan

Variants: V0 = Phase 4 CPU offload with 60 mapping iterations; V-FIXED = identical system with a fixed reduced budget; V-A = novelty-aware tiered budget. V-B cache and V-A+B are conditional stretch work only.

| Horizon | Runs needed | Question / required evidence | Gate and stop rule | Estimated cost |
|---|---|---|---|---|
| 0–10 | V0, V-FIXED, V-A | Does each finish with correct budget telemetry, finite state, unchanged keyframes/tracking settings? | Stop on crash, OOM, invalid config, missing prune iteration 20, or schema failure | ~34 s/run historically, excluding setup/eval |
| 0–49 | V0, V-FIXED, V-A | Functional runtime and early quality; select one fixed budget and one V-A setting | Stop V-A if no iteration reduction or obvious quality/trajectory failure | ~3–4 min/run inferred from 0–99; growth may increase cost |
| 0–99 | V0, selected V-FIXED, selected V-A | Is adaptive allocation better than uniform reduction under matched LIGHT instrumentation? | Require provisional quality targets and useful runtime reduction | ~6.5 min/run observed for prior workload; single-run estimates only |
| 0–499 | V0 and V-A only; V-FIXED only if scientifically needed | Medium-horizon go/no-go for final run | Stop if quality margin fails, non-finite state/OOM occurs, or speedup is not material | Linear lower-bound ~32 min/run; actual cost may grow with scene |
| 0–1999 | Frozen V0 and V-A only if medium gate passes | Final matched thesis result | One immutable run per frozen condition; preserve failures; no retuning | Historical output-save V0 ~3.94 h; new matched time unknown |

Each run has one question, immutable ID, effective config, source/config hashes, stdout/stderr, telemetry summary, checkpoint policy and failure record. Researcher approval is required for every online horizon; 0–499 and 0–1999 require explicit go/no-go approval.

Do not run every hyperparameter at every horizon. Search `{30,45}` fixed budgets and one small set of novelty thresholds only through 0–49; freeze by 0–99. Optional V-B starts only after V-A full evidence and schedule review.
