"""Executed only by gate1b_runner.py --execute; never imported by preflight."""

import argparse
import json
import os
import runpy
import shutil
import sys
import time
from pathlib import Path

sys.dont_write_bytecode = True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source-root", required=True)
    parser.add_argument("--config", required=True)
    parser.add_argument("--evidence-dir", required=True)
    args = parser.parse_args()

    source_root = Path(args.source_root).resolve()
    config_path = Path(args.config).resolve()
    evidence_dir = Path(args.evidence_dir).resolve()
    sys.path.insert(0, str(source_root))
    config = runpy.run_path(str(config_path))["config"]

    import numpy as np
    import torch
    from utils.common_utils import seed_everything
    from scripts import slam

    seed_everything(seed=config["seed"])
    model_dir = Path(config["workdir"]) / config["run_name"]
    model_dir.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(config_path, model_dir / "config.py")

    insertion_trace = []
    original_add = slam.add_new_gaussians

    def record_add(*call_args, **call_kwargs):
        before = call_args[0]["means3D"].shape[0]
        event_start = time.perf_counter()
        updated_params, updated_variables = original_add(*call_args, **call_kwargs)
        insertion_trace.append({"frame": call_args[5], "before": before,
                                "after": updated_params["means3D"].shape[0],
                                "host_call_seconds": time.perf_counter() - event_start})
        return updated_params, updated_variables

    slam.add_new_gaussians = record_add
    torch.cuda.synchronize()
    torch.cuda.reset_peak_memory_stats()
    start = time.perf_counter()
    returned_normally = False
    try:
        slam.rgbd_slam(config)
        returned_normally = True
    finally:
        sync_error = None
        try:
            torch.cuda.synchronize()
        except Exception as exc:
            sync_error = f"{type(exc).__name__}: {exc}"
        rgbd_elapsed = time.perf_counter() - start
        with (evidence_dir / "effective_config_runtime.json").open("w", encoding="utf-8") as output:
            json.dump(config, output, indent=2, sort_keys=True)
            output.write("\n")
        with (evidence_dir / "insertion_counts.jsonl").open("w", encoding="utf-8") as output:
            for item in insertion_trace:
                output.write(json.dumps(item, sort_keys=True) + "\n")
        checkpoint = model_dir / "params.npz"
        final_count = None
        completed_poses = None
        if checkpoint.is_file():
            try:
                with np.load(checkpoint, allow_pickle=False) as saved:
                    final_count = int(saved["means3D"].shape[0])
                    completed_poses = int(saved["gt_w2c_all_frames"].shape[0])
            except Exception:
                pass
        metrics = {
            "rgbd_slam_call_wall_seconds": rgbd_elapsed,
            "cuda_peak_allocated_bytes": int(torch.cuda.max_memory_allocated()),
            "cuda_peak_reserved_bytes": int(torch.cuda.max_memory_reserved()),
            "allocator_scope": "after source import and before rgbd_slam through return/exception; final synchronization attempted",
            "final_gaussian_count": final_count,
            "saved_pose_count": completed_poses,
            "insertion_events_recorded": len(insertion_trace),
            "insertion_host_call_seconds_sum": sum(
                item["host_call_seconds"] for item in insertion_trace),
            "rgbd_slam_returned_normally": returned_normally,
            "synchronize_error": sync_error,
        }
        print("GATE1B_WORKER_METRICS " + json.dumps(metrics, sort_keys=True), flush=True)


if __name__ == "__main__":
    main()
