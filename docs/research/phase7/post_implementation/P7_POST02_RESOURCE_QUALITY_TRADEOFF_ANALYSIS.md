# P7-POST-02 — Phân tích trade-off resource / quality

## Quan sát được

Room1 so với Phase4 room1 có ít hơn 2,164,203 Gaussian (−32.48%), CUDA allocated thấp hơn 30.22%, reserved thấp hơn 26.96%; NVML sampled peak giảm 986MiB (−8.69%). Nhưng LPIPS xấu hơn 10.21%, Depth L1 xấu hơn 26.32%, ATE Mean xấu hơn 29.93%, ATE RMSE xấu hơn 28.62%. Các chênh lệch chất lượng này vượt mục tiêu dung sai xấp xỉ 10% đã ghi ở giai đoạn thiết kế. Runtime quan sát thấp hơn 21.15%, nhưng evaluation/save boundary khác nên không phải matched speedup. P7 room0 có kết quả khác room1; đây không phải cặp lặp cùng scene.

## Các giả thuyết cần phân biệt

| Giả thuyết | Bằng chứng hỗ trợ | Thiếu/mâu thuẫn | Tin cậy về nguyên nhân | Thí nghiệm cần để khẳng định |
|---|---|---|---|---|
| Bounded rejection bỏ mất geometry hữu ích | R1 từ chối 29,515,493/33,408,344 candidate; source xếp theo depth residual/silhouette, không có utility label/semantic diversity | Không có counterfactual map cùng frame/pose với toàn bộ candidates; không biết candidate nào giảm sai số | Thấp; cơ chế hợp lý nhưng chưa nhân quả | matched ablation cùng scene/seed: baseline admission vs BCGM, log per-candidate accepted/rejected và offline replay |
| Global Cap làm suy giảm chất lượng | `global_saturated` 1,251 events; 1,250 events cap thật sự giới hạn admission; final map sát cap | Event cap đồng thời/sequence, pruning, optimization thay đổi map; không có run không global cap | Thấp–trung bình rằng pressure xảy ra, thấp về quality causality | factorial ablation Event-only / Global-only / both, cùng deterministic inputs |
| Event Cap tạo pressure | Event Cap 294 activations R1; max 9,000/event; source limits event additions | Không có per-frame error attribution; 1,999 events, many below limit | Trung bình về exposure, thấp về quality cause | Event cap sweep with fixed global cap, repeated seeds |
| Scene complexity explains room0/room1 differences | R1 had 33.4M valid vs room0 8.7M candidates and NVML peak 10.36 vs 7.68GiB | Scene differences and trajectories are confounded; candidate totals can reflect observed masks, not intrinsic complexity alone | Low/medium descriptive | Same-scene repeated baseline and complexity descriptors |
| Pruning explains count gaps | Source prunes after insertion; R1 last insertion 4,498,991 vs final checkpoint 4,498,964 (−27) | Does not explain multi-million gap to Phase4, which reflects whole run/history | High for 27-row final delta only; low for broader quality | Track per-iteration prune deltas; already not needed for cap correctness |
| Keyframe overlap affects coverage/quality | overlap policy samples 1,600 depth pixels and randomizes selected overlap; semantic filter commented | no saved coverage/error breakdown per keyframe; policy inherited | Low | controlled keyframe schedule/overlap study, outside BCGM-only scope |
| Lower map count improves resource use | fewer final Gaussian and lower allocator peaks vs P4 R1; source limits selected point construction | timing and background memory scopes differ; allocator peak may be caused by more than map | Moderate association, not causality | repeated paired runs and per-stage memory/profile instrumentation |
| Candidate sorting overhead offsets savings | selector uses two stable argsorts over candidates when capped (`bcgm.py:81-85`); insertion happens before mapping stage timer | no isolated GPU profiling; total runtime not matched | High that sorting exists; unknown magnitude | bounded CPU/GPU event timing instrumentation without changing method |
| Depth/pose regressions indirectly affect tracking | tracking renders current map RGB/depth and optimizes camera pose (`slam.py:265-348`) | no tracking residual/pose error timeline or controlled map intervention | Plausible, unverified | same trajectory/map counterfactual or cap ablation with per-frame tracking error |

## Interpretation

Evidence supports that the admission controls engaged and that the final maps and allocator peaks are smaller than historical Phase4 room1 values. It does **not** support “BCGM caused the quality regressions” or “resource reductions caused trajectory error.” Admission ranking optimizes the available geometric signals (depth residual and silhouette), not semantic importance or future viewpoint utility. This is a credible design limitation, not a measured failure mechanism.

Device-wide NVML sampled peak, CUDA allocated, and CUDA reserved are different measurements. The 1Hz NVML sample is not an unsampled absolute peak; no process-isolated GPU attribution is claimed. Phase4 runtime included separate evaluation timing; do not infer compute saved from raw wall delta.

## Scientific limitations

One run/seed per method and scene; 401 view samples for RGB/depth/semantic; no conventional Depth RMSE; ATE Mean vs true RMSE distinction; no matched Phase4 BCGM-off full-scene run with exact harness; Phase6 includes BAM; room0/room1 differ; no Event/Global ablation; no room1 visualization A–H (deferred). Thus current conclusions are an implementation/runtime feasibility result plus a measurable resource/quality trade-off, not a controlled causal claim.
