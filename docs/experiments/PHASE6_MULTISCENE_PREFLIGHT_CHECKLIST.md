# Phase 6 Multi-Scene Preflight Checklist

Use this checklist when preparing bounded Replica scenes such as `room1`,
`room2`, or `office`. Keep each run identity and all output leaves unique.

## Before preparing a run

- [ ] Read the current scene's preparation and prior gate report.
- [ ] Select the approved frozen commit and an existing worktree at that exact
  commit; verify its resolved path and `git status`.
- [ ] Confirm the source checksum manifest and preserve previous evidence.
- [ ] Choose a fresh run ID, scene, exact start/end/stride, and frame count.
- [ ] Confirm the scene loader, dataset root, and required RGB, depth, semantic
  ID, and semantic color modalities for that dataset.
- [ ] Record the approved V-A2 identity and scientific settings. For the
  current Phase 6 contract: seed 0, tracking 40, adaptive mapping 45/60/60,
  thresholds 0.01/0.05, LIGHT telemetry, CPU Keyframe Offload, and
  checkpoint-first finalization.
- [ ] Set checkpoint cadence so frame 0 and the terminal frame are saved; set
  the bounded offline view schedule and full pose horizon explicitly.

## Static preparation

- [ ] Derive the runner's root from its own resolved script path. Assert the
  expected worktree and actual `cwd`; never construct a worktree path by
  substituting scene/gate text into a different path.
- [ ] Validate the runner's actual `cd`, Python executable, config path and
  `scripts/slam.py` entrypoint.
- [ ] Load the config statically; verify scene identity, exact frame horizon,
  method settings and output paths.
- [ ] Generate canonical effective JSON with the agreed encoding, ordering,
  indentation, and final newline; compare it byte-for-byte with the reviewed
  SHA256 lock.
- [ ] Verify all four output destinations: model, evidence, offline evaluation,
  and telemetry. Each must be absent, unique, and confined to approved roots.
- [ ] Verify dataset and artifact symlinks resolve to approved canonical
  repository paths.
- [ ] Verify the CPU validator matches the frozen PLY serializer schema and
  checks final state, endpoint checkpoints/sidecars, finite Gaussian fields,
  and pose horizon.
- [ ] Import the offline evaluator with the frozen worktree on `PYTHONPATH`;
  verify its exact view IDs, render count, metric count, and full ATE pose
  horizon without initializing CUDA.
- [ ] Run source and preparation SHA256 manifests, shell syntax checks, and
  Python syntax checks. The preparation manifest should lock the runner,
  shared preflight, config, effective-config lock, validator, evaluator, and
  source manifest.
- [ ] Run the reusable `phase6_multiscene_preflight.py --mode static` from the
  frozen worktree. Require every line to pass and the final
  `READY_FOR_STATIC_PREFLIGHT` result.

## Host dry run and execution boundary

- [ ] Obtain explicit approval before running the host-only preflight outside
  the Codex sandbox.
- [ ] Invoke the runner with `--preflight-only`. Require separate PASS/FAIL
  results for NVIDIA nodes, `nvidia-smi`, free VRAM, available RAM, disk,
  permissions, Python/CUDA, and the CUDA rasterizer.
- [ ] Confirm dry-run leaves all reserved output destinations absent and ends
  with `READY_FOR_HOST_PREFLIGHT`. It must not reserve the run ID or launch
  SLAM.
- [ ] Preserve the host preflight output. Stop on any failed check; do not
  bypass hashes, config locks, path checks, or collision checks.
- [ ] Request distinct explicit authorization before invoking the normal
  runner. Do not automatically proceed from a passing dry run to SLAM.
- [ ] After execution, preserve logs, telemetry, manifests and partial output
  on failure; do not rerun an immutable run ID without a new approved
  preparation.
- [ ] Run the CPU validator before requesting approval for bounded offline
  evaluation. Keep offline rendering and metrics separate from online
  tracking/mapping.
