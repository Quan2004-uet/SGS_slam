# Phase 3C-3 Bounded Online Reproduction: Frames 0-49

## Result

**Phase 3C-3 Status: PASS**

`RUNTIME VERIFIED` on 2026-10-02: one continuous released SGS-SLAM online run
processed Replica `room0` frame indices 0 through 49 at 680 x 1200 on the
NVIDIA GeForce GTX 1650 Ti. The harness intercepted index 50 before delegating
it to `ReplicaDataset`.

All 1,960 tracking iterations and 3,000 mapping iterations completed. Every
observed weighted RGB, depth, semantic, and total loss was finite. Camera state,
all released per-Gaussian fields, and the requested semantic checkpoints were
finite and shape-consistent. No source, experiment config, algorithm,
environment, or dataset change was required.

## Pre-flight

```text
environment       /home/quan/miniconda3/envs/sgs_slam_baseline
python            /home/quan/miniconda3/envs/sgs_slam_baseline/bin/python
version           Python 3.9.25
branch            main
HEAD              e4183986204242a8bb422624618af07780a49d26
PyTorch           2.0.1
PyTorch CUDA      11.8
CUDA available    True
OpenCV            4.9.0
NumPy             1.26.4
renderer import   PASS
GPU               NVIDIA GeForce GTX 1650 Ti, 4096 MiB
```

The tracked source and configs were clean before the run. Pre-existing
untracked paths were `2402.03246v6.pdf`, `AGENTS.md`, and `docs/`.

## Released path, harness, and strict guard

`VERIFIED FROM SOURCE`: the released loop loads a frame, initializes the
camera, tracks, adds low-silhouette Gaussians, selects mapping views, creates a
fresh mapping optimizer, maps with pruning/densification hooks, and finally
stores a scheduled keyframe (`scripts/slam.py:727-1039`). In particular:

- tracking optimizer and loop: `scripts/slam.py:766-841`;
- pixel-driven addition: `scripts/slam.py:875-897`;
- mapping view selection and random sampling: `scripts/slam.py:899-960`;
- pruning, optional densification, and optimizer step: `scripts/slam.py:965-981`;
- keyframe append after mapping: `scripts/slam.py:1022-1039`.

The existing temporary harness `/tmp/sgs_phase3c1_bounded_online.py` was
extended only by setting `MAX_FRAME=49`, updating checkpoint indices, and
renaming temporary output/evidence paths. It still invokes released
`rgbd_slam()` and released stage functions. The dataset proxy retains
`len(dataset) == 2000`; therefore the released penultimate-frame condition is
not accidentally activated. Its exact delegated indices were `[0, ..., 49]`.
The next attempted access, index 50, raised the expected guard exception before
the real loader was called.

The temporary config copy changed output-only behavior:

```text
use_wandb        True -> False
save_checkpoints True -> False
workdir          ./experiments/Replica -> /tmp/sgs_phase3c3_output
run_name         room0_0 -> room0_frames_0_49_diagnostic
```

Two frame-0 `report_progress` calls were suppressed because this task forbids
evaluation/metric computation. Tracking/mapping iterations, LRs, loss weights,
resolution, cadence, addition, pruning, keyframes, semantic behavior, and seed
were unchanged.

Persistent, Git-ignored evidence:

```text
results/runtime_artifacts/phase3c3/phase3c3_results.json
results/runtime_artifacts/phase3c3/phase3c3_bounded_online.log
```

Temporary originals:

```text
/tmp/sgs_phase3c3_results.json
/tmp/sgs_phase3c3_bounded_online.log
/tmp/sgs_phase3c1_bounded_online.py
```

## Active baseline configuration and randomness

`VERIFIED FROM CONFIG`, `VERIFIED FROM SOURCE`, and executed at runtime:

| Setting | Runtime value |
|---|---:|
| Seed | 0 |
| Tracking iterations | 40 per frame 1-49 |
| Mapping iterations | 60 per frame 0-49 |
| Mapping cadence | every frame (`map_every=1`) |
| Keyframe cadence | frame 0, then every five frames |
| Mapping window size | 24 |
| Tracking weights | depth 1.0, RGB 0.5, semantic 0.05 |
| Mapping weights | depth 1.0, RGB 0.5, semantic 0.1 |
| Addition threshold | silhouette 0.5 |
| Pruning | enabled at mapping iterations 0 and 20 |
| Gradient clone/split | disabled |
| Opacity reset | disabled |

The released entry-point-equivalent path called `seed_everything(0)`. It did
not enable deterministic CUDA algorithms. The prior independent 20-frame run
ended at 937,970 Gaussians; this fresh continuous run ended frame 19 at 937,892
(-78). This small cross-run difference is retained as non-bit-exact
GPU/renderer evidence, not silently reconciled.

## Tracking and camera state

Frame 0 did not track. Frame 1 used previous-pose copy; frames 2-49 used the
released component-wise constant-velocity initialization. Every camera
quaternion and translation was finite. All frames 1-49 ran exactly 40
iterations, and all per-iteration weighted component and total losses were
finite.

| Frame | Initial loss | Final loss | Runtime | Finite |
|---:|---:|---:|---:|---|
| 1 | 76681.4688 | 10983.6924 | 8.827 s | YES |
| 9 | 15741.5547 | 7999.5117 | 8.318 s | YES |
| 19 | 9300.3125 | 8220.1592 | 9.116 s | YES |
| 29 | 9279.1670 | 8900.2969 | 9.729 s | YES |
| 39 | 12369.8291 | 8445.4004 | 10.456 s | YES |
| 49 | 10546.8145 | 8320.4072 | 10.696 s | YES |

Across all tracked frames, initial loss ranged from 9028.9248 (frame 28) to
76681.4688 (frame 1), while final loss ranged from 7862.5933 (frame 11) to
10983.6924 (frame 1). These are summed masked training losses, not evaluation
metrics.

## Gaussian growth and pruning

For every addition, selected valid new-point count, new point-cloud rows, and
appended Gaussian count agreed. New semantic colors were trainable, semantic
IDs were fixed, and all appended timestamps matched the current frame.

| Frame | N before | Added | Pruned | N after |
|---:|---:|---:|---:|---:|
| 0 | 815998 | 0 | 0 | 815998 |
| 1 | 815998 | 13073 | 0 | 829071 |
| 2 | 829071 | 12710 | 0 | 841781 |
| 3 | 841781 | 10755 | 23 | 852513 |
| 4 | 852513 | 8621 | 37 | 861097 |
| 5 | 861097 | 6318 | 42 | 867373 |
| 6 | 867373 | 4434 | 17 | 871790 |
| 7 | 871790 | 3138 | 14 | 874914 |
| 8 | 874914 | 1884 | 23 | 876775 |
| 9 | 876775 | 1639 | 21 | 878393 |
| 10 | 878393 | 1453 | 29 | 879817 |
| 11 | 879817 | 3678 | 27 | 883468 |
| 12 | 883468 | 4444 | 21 | 887891 |
| 13 | 887891 | 4879 | 11 | 892759 |
| 14 | 892759 | 5510 | 22 | 898247 |
| 15 | 898247 | 5669 | 26 | 903890 |
| 16 | 903890 | 6751 | 13 | 910628 |
| 17 | 910628 | 8038 | 30 | 918636 |
| 18 | 918636 | 9195 | 26 | 927805 |
| 19 | 927805 | 10106 | 19 | 937892 |
| 20 | 937892 | 10091 | 16 | 947967 |
| 21 | 947967 | 10993 | 15 | 958945 |
| 22 | 958945 | 11473 | 13 | 970405 |
| 23 | 970405 | 10818 | 21 | 981202 |
| 24 | 981202 | 10964 | 26 | 992140 |
| 25 | 992140 | 11673 | 34 | 1003779 |
| 26 | 1003779 | 11040 | 23 | 1014796 |
| 27 | 1014796 | 10806 | 31 | 1025571 |
| 28 | 1025571 | 9981 | 26 | 1035526 |
| 29 | 1035526 | 9615 | 17 | 1045124 |
| 30 | 1045124 | 8779 | 26 | 1053877 |
| 31 | 1053877 | 8107 | 26 | 1061958 |
| 32 | 1061958 | 6978 | 49 | 1068887 |
| 33 | 1068887 | 7163 | 48 | 1076002 |
| 34 | 1076002 | 5828 | 51 | 1081779 |
| 35 | 1081779 | 4695 | 33 | 1086441 |
| 36 | 1086441 | 3915 | 38 | 1090318 |
| 37 | 1090318 | 3227 | 40 | 1093505 |
| 38 | 1093505 | 2743 | 32 | 1096216 |
| 39 | 1096216 | 1933 | 30 | 1098119 |
| 40 | 1098119 | 1926 | 38 | 1100007 |
| 41 | 1100007 | 1568 | 30 | 1101545 |
| 42 | 1101545 | 2247 | 35 | 1103757 |
| 43 | 1103757 | 1501 | 50 | 1105208 |
| 44 | 1105208 | 1673 | 43 | 1106838 |
| 45 | 1106838 | 1915 | 47 | 1108706 |
| 46 | 1108706 | 2147 | 42 | 1110811 |
| 47 | 1110811 | 2418 | 57 | 1113172 |
| 48 | 1113172 | 2629 | 48 | 1115753 |
| 49 | 1115753 | 2878 | 41 | 1118590 |

```text
initial N                              815,998
final N                              1,118,590
net growth                             302,592 (37.0824%)
total additions, frames 1-49           304,019
mean / median additions                  6,204.47 / 5,669
minimum / maximum additions              1,453 (f10) / 13,073 (f1)
total pruning, frames 0-49               1,427
mean pruning per mapping frame               28.54
maximum pruning                            57 (f47)
```

| Segment | Added | Mean/frame | Pruned | Net |
|---|---:|---:|---:|---:|
| 1-9 | 62572 | 6952.44 | 177 | 62395 |
| 10-19 | 59723 | 5972.30 | 224 | 59499 |
| 20-29 | 107454 | 10745.40 | 222 | 107232 |
| 30-39 | 53368 | 5336.80 | 373 | 52995 |
| 40-49 | 20902 | 2090.20 | 431 | 20471 |

Growth is oscillatory across the whole prefix: it accelerated strongly in
frames 20-29, then decelerated in frames 30-49. The final ten-frame segment is
consistent with emerging local saturation, but is not enough to claim global
saturation for the scene.

Pruning executed at iterations 0 and 20 of every mapping event, including
zero-removal checks in frames 0-2. The JSON records all 100 events with
before/after N and per-event removal counts. Gradient clone/split and opacity
reset were **NOT EXECUTED**.

## Semantic state

At every frame boundary all Gaussian fields were finite and had leading
dimension N. Requested checkpoints were:

| Frame | N | `semantic_colors` | Trainable/finite | `semantic_ids` | Trainable/excluded/finite |
|---:|---:|---:|---|---:|---|
| 0 | 815998 | `(815998,3)` | YES / YES | `(815998,)` | NO / YES / YES |
| 9 | 878393 | `(878393,3)` | YES / YES | `(878393,)` | NO / YES / YES |
| 19 | 937892 | `(937892,3)` | YES / YES | `(937892,)` | NO / YES / YES |
| 29 | 1045124 | `(1045124,3)` | YES / YES | `(1045124,)` | NO / YES / YES |
| 39 | 1098119 | `(1098119,3)` | YES / YES | `(1098119,)` | NO / YES / YES |
| 49 | 1118590 | `(1118590,3)` | YES / YES | `(1118590,)` | NO / YES / YES |

## Keyframe residency and mapping views

Each resident keyframe referenced RGB, depth, semantic ID, semantic color, and
estimated `w2c` tensors on CUDA. Unique tensor payload was 26,112,064 bytes per
keyframe; this is not total process memory.

| New keyframe frame | Stored IDs after frame | Count | Payload bytes |
|---:|---|---:|---:|
| 0 | `[0]` | 1 | 26112064 |
| 4 | `[0,4]` | 2 | 52224128 |
| 9 | `[0,4,9]` | 3 | 78336192 |
| 14 | `[0,4,9,14]` | 4 | 104448256 |
| 19 | `[0,4,9,14,19]` | 5 | 130560320 |
| 24 | `[0,4,9,14,19,24]` | 6 | 156672384 |
| 29 | `[0,4,9,14,19,24,29]` | 7 | 182784448 |
| 34 | `[0,4,9,14,19,24,29,34]` | 8 | 208896512 |
| 39 | `[0,4,9,14,19,24,29,34,39]` | 9 | 235008576 |
| 44 | `[0,4,9,14,19,24,29,34,39,44]` | 10 | 261120640 |
| 49 | `[0,4,9,14,19,24,29,34,39,44,49]` | 11 | 287232704 |

Because only ten keyframes existed before mapping frame 49 and the overlap
quota is `mapping_window_size - 2 = 22`, every resident keyframe remained in
the effective window, together with the current frame. The runtime-selected
frame-49 order was `[9,24,39,14,34,4,0,29,19,44,49]`; 60 random draws were
distributed across all eleven views. Full window orders and draw counts for all
frames are retained in the JSON/log.

## Mapping

Mapping ran for exactly 60 iterations on all 50 frames. All component and total
losses were finite.

| Frame | Initial loss | Final loss | Runtime | Finite |
|---:|---:|---:|---:|---|
| 0 | 0.039199 | 0.006249 | 15.190 s | YES |
| 9 | 0.007291 | 0.006064 | 14.142 s | YES |
| 19 | 0.008666 | 0.006106 | 15.185 s | YES |
| 29 | 0.007408 | 0.006716 | 16.365 s | YES |
| 39 | 0.007691 | 0.005868 | 17.320 s | YES |
| 49 | 0.007309 | 0.006181 | 17.696 s | YES |

Frames 35 and 40 ended with a total loss above their initial iteration, but
the iterations sampled different mapping views and every component remained
finite. Monotonicity is neither required nor expected for this stochastic
multi-view loop.

## Optimizer state

Tracking and mapping each created a fresh Adam optimizer per applicable frame.
State was initialized lazily on the first step. Bytes below are the final
snapshot after the stage, not the zero-byte creation snapshot.

| Frame | Tracking Adam-state bytes | N at creation |
|---:|---:|---:|
| 1 | 78447836 | 815998 |
| 9 | 84282428 | 876775 |
| 19 | 89181308 | 927805 |
| 29 | 99522524 | 1035526 |
| 39 | 105348764 | 1096216 |
| 49 | 107224316 | 1115753 |

Tracking created state for zero-LR `rgb_colors`, `unnorm_rotations`,
`logit_opacities`, `log_scales`, and `semantic_colors`, because those tensors
received gradients. `means3D` had no tracking Adam state. Camera quaternion and
translation groups had nonzero LRs and state.

| Frame | Mapping Adam-state bytes after pruning | N at creation |
|---:|---:|---:|
| 0 | 97919784 | 815998 |
| 9 | 105407184 | 878414 |
| 19 | 112547064 | 937911 |
| 29 | 125414904 | 1045141 |
| 39 | 131774304 | 1098149 |
| 49 | 134230824 | 1118631 |

Mapping state existed for all trainable Gaussian groups. Camera groups had LR
zero and no mapping state. The frame-49 optimizer started with 1,118,631
Gaussians after addition; pruning migrated/replaced state to the final
1,118,590 rows.

## CUDA memory

`RUNTIME MEASUREMENT`; MiB values use 1,048,576 bytes.

| Frame | Final N | KFs | Post alloc MiB | Reserved MiB | Peak alloc MiB | Peak reserved MiB |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 815998 | 1 | 281.77 | 404 | 1307.79 | 1498 |
| 4 | 861097 | 2 | 432.82 | 808 | 1595.02 | 1652 |
| 9 | 878393 | 3 | 456.97 | 884 | 1690.61 | 1864 |
| 14 | 898247 | 4 | 488.25 | 952 | 1744.96 | 2106 |
| 19 | 937892 | 5 | 527.51 | 978 | 1818.23 | 2228 |
| 24 | 992140 | 6 | 590.44 | 1040 | 1936.63 | 2278 |
| 29 | 1045124 | 7 | 627.33 | 1106 | 2015.75 | 2362 |
| 34 | 1081779 | 8 | 666.02 | 1122 | 2089.02 | 2420 |
| 39 | 1098119 | 9 | 698.98 | 1170 | 2137.27 | 2682 |
| 44 | 1106838 | 10 | 728.42 | 1208 | 2178.53 | 2634 |
| 49 | 1118590 | 11 | 761.14 | 1292 | 2228.16 | 2688 |

Maximums across all frames:

```text
peak allocated       2,340,127,232 B = 2,231.72 MiB (frame 48)
peak reserved        3,040,870,400 B = 2,900.00 MiB (frame 42)
nvidia-smi sample          1,416 MiB                 (frame 43, after frame)
```

The allocator peak is a within-frame high-water mark; the `nvidia-smi` value
is a boundary sample, so they are not expected to coincide.

Frame 19 to frame 49 changes:

```text
Gaussians             +180,698
keyframe payload      +156,672,384 B
post-frame allocated  +244,979,712 B
post-frame reserved   +329,252,864 B
peak allocated        +429,850,112 B
peak reserved         +482,344,960 B
tracking Adam state    +18,043,008 B
mapping Adam state     +21,683,760 B
```

**Is 4 GiB VRAM sufficient through frame 49? YES.** This statement applies
only to this measured prefix and does not establish full-scene sufficiency.

## Diagnostic timing

`DIAGNOSTIC TIMING — NOT BENCHMARK FPS`. Statistics cover frames 1-49 and use
the nearest-rank p90.

| Stage | Mean | Median | p90 |
|---|---:|---:|---:|
| Tracking | 9.447 s | 9.501 s | 10.529 s |
| Mapping | 15.831 s | 15.990 s | 17.585 s |
| Total frame | 25.598 s | 25.777 s | 28.444 s |

## Integrity and next bounded gate

No tracked SGS-SLAM source/config, environment package, dataset, or algorithm
was modified. The temporary harness and output-only overrides are diagnostic
artifacts.

The recommended next gate is **Phase 3C-4 — 100-frame bounded reproduction**.
At frame 49 the map held 1,118,590 Gaussians and 11 keyframes; late additions
fell to 20,902 total in frames 40-49, Adam-state growth from frame 19 was
bounded, and maximum reserved memory was 2,900 MiB on the 4,096 MiB device.
These measurements leave a meaningful but not guaranteed margin, so 100 frames
is the next risk-controlled test rather than a full-scene run.
