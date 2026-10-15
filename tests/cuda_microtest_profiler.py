"""Bounded CUDA-only profiler lifecycle checks; no dataset or SLAM imports."""

import json
import math
import sys
import time
from pathlib import Path

import torch

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from utils.performance_profiler import PerformanceProfiler, ProfilingSettings, tensor_storage_bytes


def main() -> None:
    if not torch.cuda.is_available() or torch.cuda.device_count() < 1:
        raise RuntimeError("CUDA is required for this microtest")

    root = Path("results/runtime_artifacts/phase5_profiling/p5_g3a_fix1_profiler_validation/cuda_microtest")
    if root.exists():
        raise FileExistsError(f"Refusing to overwrite {root}")
    root.mkdir(parents=True)
    settings = ProfilingSettings.from_config({
        "mode": "detailed",
        "run_id": "p5g3a_fix1_cuda_microtest",
        "output_dir": str(root),
        "cuda_event_interval": 1,
        "cuda_resolve_interval": 1000,
        "max_pending_cuda_events": 16,
        "flush_every": 128,
        "max_buffered_records": 256,
    })

    started = time.perf_counter()
    profiler = PerformanceProfiler(settings, metadata={"test": "synthetic_cuda_profiler"})
    x = torch.ones((64, 64), device="cuda")
    cpu_payload = torch.ones((16, 16), dtype=torch.float32)
    accepted_work = 0
    try:
        # Exceeds the historical queue capacity and forces many bounded drains.
        for index in range(640):
            token = profiler.cuda_start("synthetic.add", index // 64, index)
            x.add_(1.0)
            profiler.cuda_stop(token)
            accepted_work += 1
            if index in (127, 255, 383, 511):
                profiler.resolve_cuda_events(index // 64)

        # A small real H2D operation is measured independently of the profiler's
        # logical staging counter; no pinned memory or nonblocking transfer is used.
        for index in range(8):
            token = profiler.cuda_start("synthetic.h2d", 20, index)
            staged = cpu_payload.to("cuda")
            profiler.cuda_stop(token)
            profiler.record_staging({"payload": cpu_payload}, 20, index)
            del staged

        alias = x.view(-1)
        if tensor_storage_bytes([x, alias]) != x.untyped_storage().nbytes():
            raise AssertionError("shared CUDA storage was double-counted")
        profiler.resolve_cuda_events(frame_id=20, force=True)
    finally:
        profiler.close(status="completed")
        del x
        torch.cuda.synchronize()
        torch.cuda.empty_cache()

    summary = json.loads(profiler.summary_path.read_text())
    accounting = summary["cuda_event_accounting"]
    if accounting["dropped"] != 0 or accounting["pending"] != 0:
        raise AssertionError(accounting)
    if accounting["accepted"] != accounting["resolved"]:
        raise AssertionError(accounting)
    if accounting["accepted"] <= 512:
        raise AssertionError("microtest did not exceed the historical queue load")
    records = [json.loads(line) for line in profiler.jsonl_path.read_text().splitlines() if line.strip()]
    gpu_values = [r["value"] for r in records if r["metric_name"] == "gpu_elapsed"]
    if not gpu_values or any((not math.isfinite(v) or v < 0) for v in gpu_values):
        raise AssertionError("invalid CUDA elapsed values")
    summary["microtest_wall_time_seconds"] = time.perf_counter() - started
    summary["accepted_work_spans"] = accepted_work
    summary["gpu_elapsed_sample_count"] = len(gpu_values)
    (root / "microtest_result.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n")
    print(json.dumps({
        "status": "PASS",
        "wall_time_seconds": summary["microtest_wall_time_seconds"],
        "accounting": accounting,
        "gpu_elapsed_sample_count": len(gpu_values),
        "gpu_name": torch.cuda.get_device_name(0),
    }, sort_keys=True))


if __name__ == "__main__":
    main()
