# Phase 3C-2 Bounded Online Reproduction: Frames 0-19

## Result

**Phase 3C-2 Status: PASS**

`RUNTIME VERIFIED` on 2026-10-02: one continuous released SGS-SLAM online run
processed Replica `room0` frame indices 0 through 19 at 680 x 1200 on the
NVIDIA GeForce GTX 1650 Ti. Index 20 was intercepted before the underlying
`ReplicaDataset` loaded it.

All 760 tracking iterations, 1,200 mapping iterations, their RGB/depth/semantic
components, camera states, and checked Gaussian fields remained finite. Pixel
addition, keyframe residency, mapping view selection, Adam state creation, and
pruning executed without a source/config/algorithm repair. No evaluation,
final save, post-opt, or frame 20+ operation ran.

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

The tracked source and configs were clean. Pre-existing untracked paths were
`2402.03246v6.pdf`, `AGENTS.md`, and `docs/`.

## Harness, guard, and runtime-only controls

Phase 3C-2 extended the non-cyclic Phase 3C-1 harness at
`/tmp/sgs_phase3c1_bounded_online.py`. It continued to invoke the released
`rgbd_slam()` control flow and released stage functions; it did not reimplement
tracking, mapping, addition, pruning, loss, or keyframe logic.

The proxy retained `len(dataset) == 2000`, preventing a false penultimate-frame
keyframe trigger. The exact delegated indices were:

```text
[0, 1, 2, 3, 4, 5, 6, 7, 8, 9,
 10, 11, 12, 13, 14, 15, 16, 17, 18, 19]
```

The next request, index 20, raised the expected guard exception before
delegation to `ReplicaDataset`.

The temporary config copy differed from the checked-in config only in
output-only behavior:

```text
use_wandb       True -> False
save_checkpoints True -> False
workdir         ./experiments/Replica -> /tmp/sgs_phase3c2_output
run_name        room0_0 -> room0_frames_0_19_diagnostic
```

Two frame-0 `report_progress` hooks were suppressed because the task prohibited
evaluation/metric reporting. Tracking/mapping iterations, resolution, losses,
LRs, cadence, thresholds, semantics, addition, and pruning were unchanged.
The temporary output directory contains only an empty `eval/` directory.

Machine-readable evidence:

```text
/tmp/sgs_phase3c2_results.json
/tmp/sgs_phase3c2_bounded_online.log
```

## Baseline configuration and randomness

`VERIFIED FROM CONFIG`, `VERIFIED FROM SOURCE`, and executed at runtime:

| Setting | Value |
|---|---:|
| Seed | 0 |
| Tracking iterations | 40 per frame 1-19 |
| Mapping iterations | 60 per frame 0-19 |
| Mapping cadence | every frame (`map_every=1`) |
| Keyframe cadence | every five frames (`keyframe_every=5`) plus frame 0 |
| Mapping window | 24 |
| Tracking weights | depth 1.0, RGB 0.5, semantic 0.05 |
| Mapping weights | depth 1.0, RGB 0.5, semantic 0.1 |
| Tracking camera LRs | quaternion 0.0004, translation 0.002 |
| Addition | enabled, silhouette threshold 0.5 |
| Pruning | enabled, checks at mapping iterations 0 and 20 |
| Gradient clone/split | disabled |
| Opacity reset | disabled |

The entry-point-equivalent harness called `seed_everything(0)`, which seeds
Python, NumPy, and PyTorch. Random mapping view sampling was retained and its
actual frequency is recorded below. Deterministic-algorithm enforcement is not
part of the released entry point.

The independent Phase 3C-1 run ended frame 4 with 861,070 Gaussians; this
continuous Phase 3C-2 run had 861,076 at the same boundary, a difference of six
despite the same configured seed. This small runtime discrepancy is preserved
as evidence of non-bit-exact GPU/renderer execution and is not silently
reconciled.

## Tracking

Frame 0 did not enter tracking. Frame 1 used previous-pose copy. Frames 2-19
used the released component-wise constant-velocity initialization. All camera
quaternions and translations were finite after tracking.

| Frame | Initial loss | Final loss | Runtime | Finite |
|---:|---:|---:|---:|---|
| 1 | 76,676.84 | 10,985.33 | 8.812 s | YES |
| 2 | 15,226.56 | 8,230.93 | 8.389 s | YES |
| 3 | 16,805.67 | 8,216.26 | 8.278 s | YES |
| 4 | 19,576.08 | 7,960.53 | 8.228 s | YES |
| 5 | 17,806.54 | 8,144.64 | 8.208 s | YES |
| 6 | 16,897.26 | 7,931.07 | 8.234 s | YES |
| 7 | 16,393.93 | 8,109.34 | 8.215 s | YES |
| 8 | 15,407.16 | 8,021.31 | 8.272 s | YES |
| 9 | 15,746.02 | 8,001.92 | 8.363 s | YES |
| 10 | 15,767.97 | 8,134.92 | 8.401 s | YES |
| 11 | 15,640.74 | 7,864.94 | 8.430 s | YES |
| 12 | 14,312.49 | 7,960.23 | 8.515 s | YES |
| 13 | 14,082.03 | 8,084.19 | 8.596 s | YES |
| 14 | 12,329.07 | 8,126.65 | 8.689 s | YES |
| 15 | 11,868.82 | 8,224.93 | 8.838 s | YES |
| 16 | 12,102.25 | 8,224.80 | 8.816 s | YES |
| 17 | 11,288.69 | 8,189.77 | 9.054 s | YES |
| 18 | 10,461.35 | 8,129.85 | 9.094 s | YES |
| 19 | 11,070.73 | 8,065.73 | 9.045 s | YES |

Every weighted depth, RGB, semantic, and total component was finite. Losses are
summed over masks in tracking; they are runtime validity evidence, not metrics.

## Gaussian growth

| Frame | N before | Added/new mask | Pruned | N after |
|---:|---:|---:|---:|---:|
| 0 | 815,998 | 0 | 0 | 815,998 |
| 1 | 815,998 | 13,067 | 0 | 829,065 |
| 2 | 829,065 | 12,701 | 0 | 841,766 |
| 3 | 841,766 | 10,749 | 22 | 852,493 |
| 4 | 852,493 | 8,623 | 40 | 861,076 |
| 5 | 861,076 | 6,307 | 33 | 867,350 |
| 6 | 867,350 | 4,432 | 33 | 871,749 |
| 7 | 871,749 | 3,116 | 14 | 874,851 |
| 8 | 874,851 | 1,892 | 19 | 876,724 |
| 9 | 876,724 | 1,642 | 23 | 878,343 |
| 10 | 878,343 | 1,479 | 30 | 879,792 |
| 11 | 879,792 | 3,675 | 36 | 883,431 |
| 12 | 883,431 | 4,449 | 24 | 887,856 |
| 13 | 887,856 | 4,948 | 22 | 892,782 |
| 14 | 892,782 | 5,750 | 20 | 898,512 |
| 15 | 898,512 | 5,827 | 19 | 904,320 |
| 16 | 904,320 | 6,772 | 23 | 911,069 |
| 17 | 911,069 | 8,114 | 16 | 919,167 |
| 18 | 919,167 | 8,691 | 28 | 927,830 |
| 19 | 927,830 | 10,153 | 13 | 937,970 |

For every addition, the final valid new-point mask count equaled both the new
point-cloud row count and appended Gaussian count. New semantic colors were
trainable; new semantic IDs were fixed; all new timestamps matched the source
frame.

Growth summary:

```text
initial N                         815,998
final N                           937,970
absolute net growth               121,972
percentage net growth             14.9476%
total additions, frames 1-19      122,387
mean additions/frame, frames 1-19 6,441.42
maximum addition                  13,067 (frame 1)
minimum addition                  1,479 (frame 10)
total pruned, frames 0-19         415
mean pruned/mapping frame         20.75
```

No full-scene extrapolation is made.

## Semantic and Gaussian state

At the end of every frame, all released per-Gaussian fields had leading
dimension N and were finite. Selected semantic checkpoints were:

| Frame | N | `semantic_colors` | Trainable/finite | `semantic_ids` | Trainable/excluded/finite |
|---:|---:|---:|---|---:|---|
| 0 | 815,998 | `(815998,3)` | YES / YES | `(815998,)` | NO / YES / YES |
| 4 | 861,076 | `(861076,3)` | YES / YES | `(861076,)` | NO / YES / YES |
| 9 | 878,343 | `(878343,3)` | YES / YES | `(878343,)` | NO / YES / YES |
| 14 | 898,512 | `(898512,3)` | YES / YES | `(898512,)` | NO / YES / YES |
| 19 | 937,970 | `(937970,3)` | YES / YES | `(937970,)` | NO / YES / YES |

## Keyframe residency

Each keyframe retained RGB, depth, semantic ID, semantic color, and estimated
`w2c` tensors on `cuda:0`. One keyframe payload referenced 26,112,064 bytes.

| Frames after processing | Stored IDs | Count | Approximate payload |
|---|---|---:|---:|
| 0-3 | `[0]` | 1 | 26,112,064 B |
| 4-8 | `[0,4]` | 2 | 52,224,128 B |
| 9-13 | `[0,4,9]` | 3 | 78,336,192 B |
| 14-18 | `[0,4,9,14]` | 4 | 104,448,256 B |
| 19 | `[0,4,9,14,19]` | 5 | 130,560,320 B |

The payload is distinct from total CUDA allocation/reservation.

## Mapping and actual view sampling

Mapping ran exactly 60 iterations on every frame. All weighted depth, RGB,
semantic, and total loss values were finite.

| Frame | Initial loss | Final loss | Runtime | Finite |
|---:|---:|---:|---:|---|
| 0 | 0.039199 | 0.006248 | 15.121 s | YES |
| 1 | 0.008181 | 0.004980 | 14.484 s | YES |
| 2 | 0.011310 | 0.004557 | 14.183 s | YES |
| 3 | 0.010820 | 0.004708 | 14.031 s | YES |
| 4 | 0.010781 | 0.005012 | 13.895 s | YES |
| 5 | 0.007464 | 0.004862 | 14.041 s | YES |
| 6 | 0.011026 | 0.005378 | 13.836 s | YES |
| 7 | 0.007567 | 0.005734 | 13.947 s | YES |
| 8 | 0.007796 | 0.005653 | 13.960 s | YES |
| 9 | 0.007303 | 0.006071 | 14.068 s | YES |
| 10 | 0.006399 | 0.006225 | 14.202 s | YES |
| 11 | 0.007261 | 0.005820 | 14.262 s | YES |
| 12 | 0.007331 | 0.005960 | 14.421 s | YES |
| 13 | 0.007292 | 0.006296 | 14.416 s | YES |
| 14 | 0.007875 | 0.006593 | 14.604 s | YES |
| 15 | 0.010570 | 0.006575 | 14.761 s | YES |
| 16 | 0.008486 | 0.006367 | 14.873 s | YES |
| 17 | 0.008149 | 0.005801 | 15.185 s | YES |
| 18 | 0.006860 | 0.006951 | 15.052 s | YES |
| 19 | 0.008466 | 0.006185 | 15.215 s | YES |

The effective selected mapping windows and actual random draws across each 60
iterations were:

```text
0:  [0]                 draws {0:60}
1:  [0,1]               draws {0:24, 1:36}
2:  [0,2]               draws {0:33, 2:27}
3:  [0,3]               draws {0:28, 3:32}
4:  [0,4]               draws {0:36, 4:24}
5:  [0,4,5]             draws {0:18, 4:24, 5:18}
6:  [0,4,6]             draws {0:18, 4:26, 6:16}
7:  [0,4,7]             draws {0:26, 4:17, 7:17}
8:  [0,4,8]             draws {0:21, 4:20, 8:19}
9:  [0,4,9]             draws {0:25, 4:19, 9:16}
10: [4,0,9,10]          draws {0:15, 4:13, 9:12, 10:20}
11: [4,0,9,11]          draws {0:16, 4:9,  9:20, 11:15}
12: [4,0,9,12]          draws {0:13, 4:19, 9:18, 12:10}
13: [4,0,9,13]          draws {0:20, 4:8,  9:17, 13:15}
14: [0,4,9,14]          draws {0:15, 4:17, 9:16, 14:12}
15: [9,4,0,14,15]       draws {0:18, 4:9,  9:10, 14:9,  15:14}
16: [0,4,9,14,16]       draws {0:11, 4:10, 9:12, 14:10, 16:17}
17: [9,0,4,14,17]       draws {0:11, 4:8,  9:17, 14:12, 17:12}
18: [0,9,4,14,18]       draws {0:11, 4:13, 9:15, 14:11, 18:10}
19: [9,0,4,14,19]       draws {0:13, 4:10, 9:9,  14:19, 19:9}
```

These are observed stochastic selections, not quality rankings. The inactive
semantic-mIoU keyframe filter was not restored.

## Pruning, densification, and opacity reset

Pruning was called by the released mapping loop and its configured removal
checks executed at iterations 0 and 20:

| Frame | Iteration 0: before - removed -> after | Iteration 20: before - removed -> after |
|---:|---|---|
| 0 | 815,998 - 0 -> 815,998 | 815,998 - 0 -> 815,998 |
| 1 | 829,065 - 0 -> 829,065 | 829,065 - 0 -> 829,065 |
| 2 | 841,766 - 0 -> 841,766 | 841,766 - 0 -> 841,766 |
| 3 | 852,515 - 9 -> 852,506 | 852,506 - 13 -> 852,493 |
| 4 | 861,116 - 27 -> 861,089 | 861,089 - 13 -> 861,076 |
| 5 | 867,383 - 17 -> 867,366 | 867,366 - 16 -> 867,350 |
| 6 | 871,782 - 21 -> 871,761 | 871,761 - 12 -> 871,749 |
| 7 | 874,865 - 9 -> 874,856 | 874,856 - 5 -> 874,851 |
| 8 | 876,743 - 12 -> 876,731 | 876,731 - 7 -> 876,724 |
| 9 | 878,366 - 8 -> 878,358 | 878,358 - 15 -> 878,343 |
| 10 | 879,822 - 18 -> 879,804 | 879,804 - 12 -> 879,792 |
| 11 | 883,467 - 19 -> 883,448 | 883,448 - 17 -> 883,431 |
| 12 | 887,880 - 17 -> 887,863 | 887,863 - 7 -> 887,856 |
| 13 | 892,804 - 12 -> 892,792 | 892,792 - 10 -> 892,782 |
| 14 | 898,532 - 7 -> 898,525 | 898,525 - 13 -> 898,512 |
| 15 | 904,339 - 6 -> 904,333 | 904,333 - 13 -> 904,320 |
| 16 | 911,092 - 11 -> 911,081 | 911,081 - 12 -> 911,069 |
| 17 | 919,183 - 8 -> 919,175 | 919,175 - 8 -> 919,167 |
| 18 | 927,858 - 9 -> 927,849 | 927,849 - 19 -> 927,830 |
| 19 | 937,983 - 5 -> 937,978 | 937,978 - 8 -> 937,970 |

```text
gradient clone/split: NOT EXECUTED
opacity reset:        NOT EXECUTED
```

## Optimizer state

Tracking Adam had eight groups. Only camera groups had nonzero tracking LRs,
but `rgb_colors`, `unnorm_rotations`, `logit_opacities`, `log_scales`, and
`semantic_colors` also acquired Adam state because they received gradients.
`means3D` was detached during tracking and had no state. Camera groups did have
state.

| Frame | Tracking Adam-state bytes |
|---:|---:|
| 1 | 78,447,836 |
| 4 | 81,951,356 |
| 9 | 84,277,532 |
| 14 | 85,819,100 |
| 19 | 89,183,708 |

Mapping Adam also had eight groups. Its six Gaussian groups had state;
zero-LR detached camera groups did not. Pruning at iteration 0 replaced
Parameters after backward, so state remained empty after step 1 and was lazily
created at step 2. Iteration-20 pruning migrated/filter-adjusted existing state.

| Frame | N at mapping creation | Optimizer elements | State after step 2 | Final state bytes |
|---:|---:|---:|---:|---:|
| 0 | 815,998 | 12,253,970 | 97,919,784 | 97,919,784 |
| 4 | 861,116 | 12,930,740 | 103,330,704 | 103,329,144 |
| 9 | 878,366 | 13,189,490 | 105,402,984 | 105,401,184 |
| 14 | 898,532 | 13,491,980 | 107,823,024 | 107,821,464 |
| 19 | 937,983 | 14,083,745 | 112,557,384 | 112,556,424 |

## GPU memory trend

`RUNTIME MEASUREMENT`: CUDA peak counters were reset before each online frame.
`Reserved` below is the post-frame value after the released `empty_cache()`;
`peak reserved` is the actual per-frame maximum, not merely a boundary sample.

| Frame | Final N | Keyframes | Post-frame allocated | Reserved | Peak allocated | Peak reserved |
|---:|---:|---:|---:|---:|---:|---:|
| 0 | 815,998 | 1 | 295,453,696 | 465,567,744 | 1,371,315,200 | 1,570,766,848 |
| 1 | 829,065 | 1 | 423,382,016 | 813,694,976 | 1,653,588,992 | 1,795,162,112 |
| 2 | 841,766 | 1 | 434,760,704 | 872,415,232 | 1,714,781,696 | 1,803,550,720 |
| 3 | 852,493 | 1 | 449,586,176 | 845,152,256 | 1,718,282,752 | 2,011,168,768 |
| 4 | 861,076 | 2 | 450,799,616 | 746,586,112 | 1,664,711,680 | 1,738,539,008 |
| 5 | 867,350 | 2 | 478,152,192 | 845,152,256 | 1,758,671,360 | 1,839,202,304 |
| 6 | 871,749 | 2 | 479,327,744 | 859,832,320 | 1,764,183,040 | 1,818,230,784 |
| 7 | 874,851 | 2 | 478,427,648 | 887,095,296 | 1,764,690,944 | 1,990,197,248 |
| 8 | 876,724 | 2 | 478,389,248 | 910,163,968 | 1,764,058,112 | 2,181,038,080 |
| 9 | 878,343 | 3 | 477,568,000 | 901,775,360 | 1,767,190,528 | 1,969,225,728 |
| 10 | 879,792 | 3 | 505,810,944 | 1,012,924,416 | 1,796,907,008 | 1,973,420,032 |
| 11 | 883,431 | 3 | 507,235,840 | 996,147,200 | 1,803,007,488 | 2,195,718,144 |
| 12 | 887,856 | 3 | 510,119,424 | 989,855,744 | 1,811,038,208 | 2,212,495,360 |
| 13 | 892,782 | 3 | 510,700,544 | 1,052,770,304 | 1,819,089,408 | 1,988,100,096 |
| 14 | 898,512 | 4 | 513,591,296 | 1,042,284,544 | 1,828,360,192 | 2,235,564,032 |
| 15 | 904,320 | 4 | 543,114,752 | 1,031,798,784 | 1,868,974,080 | 2,084,569,088 |
| 16 | 911,069 | 4 | 544,317,952 | 1,000,341,504 | 1,869,874,688 | 2,294,284,288 |
| 17 | 919,167 | 4 | 547,893,248 | 1,080,033,280 | 1,881,136,128 | 2,153,775,104 |
| 18 | 927,830 | 4 | 552,316,928 | 1,098,907,648 | 1,888,363,520 | 2,332,033,024 |
| 19 | 937,970 | 5 | 554,376,192 | 1,161,822,208 | **1,905,219,584** | **2,355,101,696** |

Memory maxima:

```text
maximum allocated peak        1,905,219,584 B (1,816.96 MiB), frame 19
maximum reserved peak         2,355,101,696 B (2,246.00 MiB), frame 19
maximum sampled nvidia-smi    1,224 MiB, after frame 19
```

From frame 4 to frame 19 in this continuous run:

```text
N                       +76,894 (+8.93%)
stored keyframes         2 -> 5 (+78,336,192 payload bytes)
post-frame allocation    +103,576,576 B (+22.98%)
per-frame allocated peak +240,507,904 B (+14.45%)
```

**Is 4 GiB VRAM sufficient for released baseline processing through frame 19?
YES.** This conclusion applies only to measured frames 0-19 and does not claim
full-Replica sufficiency.

## Diagnostic timing

For frames 1-19:

```text
mean tracking time    8.551 s
median tracking time  8.430 s
mean mapping time     14.391 s
median mapping time   14.262 s
mean total frame time 23.238 s
median total time     23.027 s
```

These are synchronized **DIAGNOSTIC TIMING — NOT BENCHMARK FPS** values. No
paper-runtime comparison is made.

## Integrity and next bounded horizon

```text
source changed             NO
config changed             NO
environment changed        NO
algorithm changed          NO
dataset changed            NO
temporary harness created  YES (/tmp only; existing C1 harness extended)
```

The next appropriate Phase 3C-3 horizon is **50 frames**, not a full scene.
Through frame 19, five keyframes occupy about 124.5 MiB, N grew 14.95%, and the
largest reserved peak reached about 2.19 GiB on a 4 GiB GPU. Extending to frame
49 is large enough to observe six additional keyframe captures and longer map
growth while retaining a bounded stop before committing to 100 or 2000 frames.
This is a risk-controlled next gate, not a prediction that frame 49 will pass.
