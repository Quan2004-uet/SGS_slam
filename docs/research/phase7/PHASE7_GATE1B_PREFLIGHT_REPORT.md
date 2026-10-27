# Phase 7 Gate 1B — Bounded GPU experiment preflight

**Decision:** `PASS_PHASE7_GATE1B_PREFLIGHT_READY` for preparation only. **No experiment was executed.**<br>
**Contract:** `PHASE7_GATE1B_RUN_CONTRACT.md`.<br>
**Audit date:** 2026-10-27.

## Verified source and controls

- Phase 7 worktree is on `phase7-bcgm` at frozen parent HEAD `68f9060f7ff4d8d141be1d5f71339401327edd06`. Its Gate 1A `scripts/slam.py` is modified and `utils/bcgm.py` is untracked; exact SHA256 values are in the contract. The Gate 1A report records 9/9 CPU tests. This preflight inspected the actual `add_new_gaussians`, `get_pointcloud`, config validator and online call path, rather than relying on report line numbers.
- Phase 4 source is the detached `/home/robot/research/SGS_slam_phase4_multiscene` worktree at the same frozen commit. Its tracked worktree is clean. Both base Replica config copies have the same SHA256. No Phase 4 file was edited.
- The actual entry point remains `scripts/slam.py::rgbd_slam`. The guarded runner uses the frozen Phase 4 source for `p4` and the Gate 1A source for `off`/`on`, with the same worker wrapper and pinned interpreter. `--execute` is required to start a run.
- Effective arm configs were loaded in separate CPU-only processes. Removing only `run_name` and `bcgm` yields the same canonical SHA256 `21fe6546fec201254f320f090cdac4b5d3a00f54c666834075834968df859935` for all three arms. Seed, frame range, camera file, resolution, map/keyframe cadence, mapping window, 40/60 tracking/mapping iterations, losses/semantics inherited from the identical base config, `eval_every=5`, baseline pruning and disabled gradient densification are matched.

## Dataset and environment preflight

Replica room0 contains 2,000 RGB JPEGs, 2,000 16-bit depth PNGs, 2,000 semantic-ID PNGs, 2,000 semantic-color PNGs and 2,000 trajectory lines. All four input classes have nonempty files for indices 0–99. First-frame file headers show 1200×680 RGB, depth, semantic IDs and semantic color. The dataset loader slices `start:end:stride`; `end=100` is exclusive, so the proposed horizon is exactly frames 0–99. The trajectory hash and camera-config hash are locked in the run contract.

The pinned interpreter reports Python 3.10.22 and PyTorch 2.7.1+cu128; the installed `diff_gaussian_rasterization` Python package imports with CUDA hidden. This is an import check, not a renderer-kernel smoke test. A read-only `nvidia-smi` query outside the sandbox reported RTX 5080, 16,303 MiB total, 818 MiB used, 0% GPU utilization and driver 580.167.08. The compute-process query listed only `/usr/libexec/gnome-remote-desktop-daemon` (PID 7710, 264 MiB); no active SLAM/Python compute process was observed at the query time. The sandboxed `nvidia-smi` call could not communicate with the driver; the direct-host read-only query succeeded. Recheck live GPU state immediately before each arm.

The output filesystem had approximately 29 GiB free (97% used). The guarded runner refuses execution below 10 GiB free. This threshold is a stop guard, not a guaranteed capacity estimate for all three runs.

## Arm preflight results

| Arm | Dry preflight | Effective config SHA256 | Output collision | Experiment result |
|---|---|---|---|---|
| Frozen Phase 4 (`p4`) | PASS with pinned Python | `e5c921af2c53d21a8779943ebc7da87c441089be2a62696beb7139d2977e14bc` | None | `NOT_RUN` |
| BCGM-off (`off`) | PASS with pinned Python | `d0777bb180d135d4c38e424b73605f4df41d99dcd28af8fce804c32f55f20291` | None | `NOT_RUN` |
| BCGM-on (`on`) | PASS with pinned Python | `c5b76b26ae0f7c6e6c60b18d258e8ae34e27c40811e17fbf13ad1766a74a5c79` | None | `NOT_RUN` |

An initial `off` dry preflight with system `python3` failed because that interpreter lacks `torch`; rerunning all three dry preflights with the pinned research interpreter passed. No SLAM or CUDA workload was started by either attempt. Model and evidence output directories are still absent. The exact config paths, run IDs and directories are listed in the contract.

## Measurement readiness and interpretation

The host runner records complete worker process wall time and one-second device-wide NVML samples. The worker resets/read PyTorch allocated/reserved peaks around `rgbd_slam`, records per-event Gaussian counts for all arms, reads final checkpoint count/100-pose horizon if available, and preserves input/runtime effective configs. Source-reported tracking/mapping average times are parsed separately. If a value is absent, the future summary uses `null`/`NOT_MEASURED`; no Gate 1B metric exists yet.

The BCGM selector performs two stable candidate sorts when the event cap binds. This can add nontrivial GPU sorting and synchronization cost. The worker records unsynchronized host call time for the whole insertion function on all arms; process wall captures the overall impact. Source mapping FPS excludes the preceding insertion, so a mapping-FPS improvement alone cannot establish a BCGM speedup. CUDA allocated/reserved peaks and sampled NVML device memory have different scopes.

Historical Phase 4 evidence predicts an informative event cap: 16/99 frame-1–99 insertion events exceeded 9,000 additions, while frame 99 had about 1.406 million Gaussians, well below 4.5 million. The exact treatment activation is `NOT_VERIFIED` until the BCGM-on run. The historical detailed trace retains a `FAIL_RUNTIME` label from its validator defect; the separate final output-save report records `PASS_FULL_OUTPUT_SAVE_TELEMETRY` and explicitly excluded evaluation. Neither record is represented as a completed 0–99 matched comparison.

## Limitations and authorization boundary

- Renderer kernel execution, CUDA runtime behavior, per-arm peak memory, FPS, final counts and quality are `NOT_VERIFIED` until execution. The 9/9 Gate 1A CPU result establishes only its tested function-level contract.
- The released evaluator's `rmse` output is Depth L1 and its ATE scalar is mean aligned translation error. Conventional Depth RMSE and true ATE RMSE remain `NOT_MEASURED` without a separately approved matched supplementary evaluation. The proposed 100-frame evaluation would use 21 sampled training views, not a held-out/full-scene benchmark.
- The Phase 7 source is uncommitted. Its SHA256 locks provide a reproducible local identity, but this is not remote preservation. Source/config drift will fail the runner preflight.
- The GPU occupancy and free disk observations are time-specific. The runner checks them again at execution; output directories must still be absent. Any failed arm retains its partial evidence and blocks automatic progression to the next arm.
- No current Phase 4/5/6 checkpoint, dataset or artifact path is an output target. Phase 4 tracked source and Phase 5 worktree state were not changed during preparation.

**Next action:** researcher reviews the run contract and this preflight, then separately authorizes bounded Gate 1B execution. Run `p4`, inspect evidence, then `off`, inspect parity, then `on`. Do not infer a benefit from the proposed caps before those measurements.
