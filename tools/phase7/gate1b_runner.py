#!/usr/bin/env python3
"""Guarded three-arm Gate 1B runner. Without --execute it is read-only."""

import argparse
import csv
import hashlib
import json
import os
import re
import runpy
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True


ROOT = Path(__file__).resolve().parents[2]
PHASE4_ROOT = Path("/home/robot/research/SGS_slam_phase4_multiscene")
DATA_ROOT = Path("/home/robot/research/SGS_slam/data/Replica/room0")
PYTHON = Path("/home/robot/miniconda3/envs/sgs_slam_5080/bin/python")
EVIDENCE_ROOT = ROOT / "results/runtime_artifacts/phase7_gate1b"
BASE_HEAD = "68f9060f7ff4d8d141be1d5f71339401327edd06"
CAMERA_SHA = "4c1e33544bef24c146c4ec9a622bb3ad7a314168db8d192c191db08bad3edf58"
BASE_CONFIG_SHA = "08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3"
PHASE4_SOURCE_SHA = "a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3"
PHASE7_SOURCE_SHA = "ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999"
BCGM_MODULE_SHA = "8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400"
TRAJECTORY_SHA = "5692a60076e426b403dc64025ff38c443606a506704545ee192d4dbadedaaca2"

ARMS = {
    "p4": (PHASE4_ROOT, "p7_bcgm_g1b_room0_p4_0_99_r01",
           "phase7_gate1b_room0_p4_0_99_r01.py",
           "f559e349a65fd3d92c0de0ea553abd93f75b0767e05b6d2729549de1b5c6bc27"),
    "off": (ROOT, "p7_bcgm_g1b_room0_off_0_99_r01",
            "phase7_gate1b_room0_off_0_99_r01.py",
            "887ab9d9e7b92c11bd002d5bed4c4c3944d993624ef86b39198d8fdd5392e3db"),
    "on": (ROOT, "p7_bcgm_g1b_room0_on_0_99_r01",
           "phase7_gate1b_room0_on_0_99_r01.py",
           "498d494db39beb55f28e6c6cee3d1edcc7ed763540b5cfd947c44988ef79e853"),
}


def sha256(path):
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(root, *args):
    return subprocess.check_output(["git", *args], cwd=root, text=True).strip()


def gpu_state():
    gpu = subprocess.check_output(
        ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
         "--format=csv,noheader,nounits"], text=True).strip()
    processes = subprocess.check_output(
        ["nvidia-smi", "--query-compute-apps=pid,process_name,used_gpu_memory",
         "--format=csv,noheader,nounits"], text=True).splitlines()
    conflicts = [line for line in processes if line.strip() and
                 "gnome-remote-desktop-daemon" not in line]
    if conflicts:
        raise RuntimeError("GPU has an unreviewed compute process; stop before execution")
    return gpu, processes


def read_effective_config(source_root, config_path):
    sys.path.insert(0, str(source_root))
    try:
        return runpy.run_path(str(config_path))["config"]
    finally:
        sys.path.pop(0)


def preflight(arm):
    source_root, run_id, config_name, config_sha = ARMS[arm]
    config_path = ROOT / "configs/replica" / config_name
    source = source_root / "scripts/slam.py"
    model_dir = ROOT / "experiments/Replica" / run_id
    evidence_dir = EVIDENCE_ROOT / run_id
    if git(source_root, "rev-parse", "HEAD") != BASE_HEAD:
        raise RuntimeError("Unexpected source HEAD")
    if arm == "p4" and git(source_root, "status", "--porcelain", "--untracked-files=no"):
        raise RuntimeError("Frozen Phase 4 source has tracked changes")
    if arm != "p4" and git(source_root, "branch", "--show-current") != "phase7-bcgm":
        raise RuntimeError("Unexpected Phase 7 branch")
    if sha256(source) != (PHASE4_SOURCE_SHA if arm == "p4" else PHASE7_SOURCE_SHA):
        raise RuntimeError("Online source hash changed")
    if arm != "p4" and sha256(ROOT / "utils/bcgm.py") != BCGM_MODULE_SHA:
        raise RuntimeError("BCGM module hash changed")
    if sha256(source_root / "configs/replica/slam.py") != BASE_CONFIG_SHA:
        raise RuntimeError("Base Replica config hash changed")
    if sha256(PHASE4_ROOT / "configs/data/replica.yaml") != CAMERA_SHA:
        raise RuntimeError("Replica camera config hash changed")
    if sha256(config_path) != config_sha:
        raise RuntimeError("Arm config hash changed")
    if sha256(DATA_ROOT / "traj.txt") != TRAJECTORY_SHA:
        raise RuntimeError("Room0 trajectory hash changed")
    for directory, pattern, prefix, suffix in (
            ("frames", "frame*.jpg", "frame", ".jpg"),
            ("depths", "depth*.png", "depth", ".png"),
            ("semantic_ids", "semantic_id*.png", "semantic_id", ".png"),
            ("semantic_colors", "semantic_color*.png", "semantic_color", ".png")):
        paths = list((DATA_ROOT / directory).glob(pattern))
        if len(paths) != 2000:
            raise RuntimeError(f"Unexpected {directory} file count")
        for index in range(100):
            path = DATA_ROOT / directory / f"{prefix}{index:06d}{suffix}"
            if not path.is_file() or path.stat().st_size == 0:
                raise RuntimeError(f"Missing or empty room0 input: {path}")
    if model_dir.exists() or evidence_dir.exists():
        raise RuntimeError("Output collision; existing model/evidence path must be preserved")
    if shutil.disk_usage(ROOT).free < 10 * 1024 ** 3:
        raise RuntimeError("Less than 10 GiB free on the output filesystem")
    if not PYTHON.is_file():
        raise RuntimeError("Pinned Python interpreter missing")
    config = read_effective_config(source_root, config_path)
    if config["run_name"] != run_id or Path(config["workdir"]) != model_dir.parent:
        raise RuntimeError("Effective output identity mismatch")
    data = config["data"]
    if (data["sequence"], data["start"], data["end"], data["stride"], data["num_frames"]) != (
            "room0", 0, 100, 1, 100):
        raise RuntimeError("Effective frame interval mismatch")
    if Path(data["basedir"]) / data["sequence"] != DATA_ROOT:
        raise RuntimeError("Effective dataset root mismatch")
    if (config["seed"], config["primary_device"], config["map_every"],
            config["keyframe_every"], config["mapping_window_size"],
            config["tracking"]["num_iters"], config["mapping"]["num_iters"],
            data["desired_image_width"], data["desired_image_height"],
            data["load_semantics"], config["eval_every"], config["use_wandb"]) != (
            0, "cuda:0", 1, 5, 24, 40, 60, 1200, 680, True, 5, False):
        raise RuntimeError("Effective scientific config mismatch")
    if config["mapping"]["use_gaussian_splatting_densification"]:
        raise RuntimeError("Gradient densification must remain disabled")
    if arm == "p4" and "bcgm" in config:
        raise RuntimeError("Phase 4 arm contains BCGM config")
    if arm == "off" and config.get("bcgm") != {"enabled": False}:
        raise RuntimeError("BCGM-off arm mismatch")
    if arm == "on" and config.get("bcgm") != {
            "enabled": True, "max_new_gaussians_per_event": 9000,
            "max_gaussians": 4500000}:
        raise RuntimeError("BCGM-on arm mismatch")
    if arm != "p4":
        sys.path.insert(0, str(ROOT))
        try:
            from utils.bcgm import validate_bcgm_config
            validate_bcgm_config(config)
        finally:
            sys.path.pop(0)
    gpu, processes = gpu_state()
    return source_root, config_path, run_id, model_dir, evidence_dir, config, gpu, processes


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--arm", choices=ARMS, required=True)
    parser.add_argument("--execute", action="store_true",
                        help="Explicitly authorize this one bounded arm after live preflight")
    args = parser.parse_args()
    source_root, config_path, run_id, model_dir, evidence_dir, config, gpu, processes = preflight(args.arm)
    print(json.dumps({"arm": args.arm, "run_id": run_id, "source_root": str(source_root),
                      "config": str(config_path), "model_dir": str(model_dir),
                      "evidence_dir": str(evidence_dir), "gpu": gpu,
                      "gpu_processes": processes, "frame_range": [0, 99],
                      "effective_config_sha256": hashlib.sha256(json.dumps(
                          config, sort_keys=True, separators=(",", ":")).encode()).hexdigest(),
                      "execute": args.execute}, sort_keys=True))
    if not args.execute:
        return

    evidence_dir.mkdir(parents=True, exist_ok=False)
    effective_bytes = json.dumps(config, sort_keys=True, separators=(",", ":")).encode()
    with (evidence_dir / "effective_config_input.json").open("w", encoding="utf-8") as output:
        json.dump(config, output, indent=2, sort_keys=True)
        output.write("\n")
    telemetry_path = evidence_dir / "nvml_samples.csv"
    stop = threading.Event()

    def sample_gpu():
        with telemetry_path.open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["utc", "gpu_index", "memory_used_mib", "utilization_gpu_percent"])
            while not stop.is_set():
                try:
                    sample = subprocess.check_output(
                        ["nvidia-smi", "--query-gpu=index,memory.used,utilization.gpu",
                         "--format=csv,noheader,nounits"], text=True).strip()
                    for line in sample.splitlines():
                        writer.writerow([datetime.now(timezone.utc).isoformat(),
                                         *[part.strip() for part in line.split(",")]])
                except Exception:
                    writer.writerow([datetime.now(timezone.utc).isoformat(), "NVML_ERROR"])
                stream.flush()
                stop.wait(1.0)

    sampler = threading.Thread(target=sample_gpu, daemon=True)
    sampler.start()
    started = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["CUDA_VISIBLE_DEVICES"] = "0"
    command = [str(PYTHON), str(ROOT / "tools/phase7/gate1b_worker.py"),
               "--source-root", str(source_root), "--config", str(config_path),
               "--evidence-dir", str(evidence_dir)]
    exit_code = None
    launch_error = None
    with (evidence_dir / "stdout_stderr.log").open("w") as output:
        try:
            process = subprocess.run(command, cwd=source_root, env=environment,
                                     stdout=output, stderr=subprocess.STDOUT, check=False)
            exit_code = process.returncode
        except OSError as exc:
            launch_error = f"{type(exc).__name__}: {exc}"
        finally:
            stop.set()
            sampler.join()
    elapsed = time.monotonic() - start
    nvml_values = []
    gpu_util_values = []
    with telemetry_path.open(newline="") as stream:
        for row in list(csv.reader(stream))[1:]:
            if len(row) == 4 and row[1] == "0":
                try:
                    nvml_values.append(float(row[2]))
                    gpu_util_values.append(float(row[3]))
                except ValueError:
                    pass
    worker_metrics = None
    tracking_frame_seconds = None
    mapping_frame_seconds = None
    with (evidence_dir / "stdout_stderr.log").open(errors="replace") as stream:
        for line in stream:
            if line.startswith("GATE1B_WORKER_METRICS "):
                worker_metrics = json.loads(line.removeprefix("GATE1B_WORKER_METRICS "))
            tracking = re.search(r"Average Tracking/Frame Time: ([0-9.eE+-]+) s", line)
            mapping = re.search(r"Average Mapping/Frame Time: ([0-9.eE+-]+) s", line)
            if tracking:
                tracking_frame_seconds = float(tracking.group(1))
            if mapping:
                mapping_frame_seconds = float(mapping.group(1))
    summary = {
        "arm": args.arm, "run_id": run_id, "source_root": str(source_root),
        "source_sha256": sha256(source_root / "scripts/slam.py"),
        "config_path": str(config_path), "config_sha256": sha256(config_path),
        "effective_config_input_sha256": hashlib.sha256(effective_bytes).hexdigest(),
        "runner_sha256": sha256(ROOT / "tools/phase7/gate1b_runner.py"),
        "worker_sha256": sha256(ROOT / "tools/phase7/gate1b_worker.py"),
        "model_dir": str(model_dir), "evidence_dir": str(evidence_dir),
        "started_utc": started, "finished_utc": datetime.now(timezone.utc).isoformat(),
        "process_wall_seconds": elapsed, "process_exit_code": exit_code,
        "launch_error": launch_error,
        "end_to_end_fps_if_complete": 100 / elapsed if exit_code == 0 and
        worker_metrics and worker_metrics.get("rgbd_slam_returned_normally") and
        worker_metrics.get("saved_pose_count") == 100 else None,
        "nvml_sample_interval_seconds": 1.0,
        "nvml_peak_device_used_mib": max(nvml_values) if nvml_values else None,
        "nvml_valid_samples": len(nvml_values), "gpu_preflight": gpu,
        "nvml_mean_gpu_util_percent": sum(gpu_util_values) / len(gpu_util_values)
        if gpu_util_values else None,
        "nvml_peak_gpu_util_percent": max(gpu_util_values) if gpu_util_values else None,
        "tracking_average_frame_seconds": tracking_frame_seconds,
        "tracking_reciprocal_fps": 1 / tracking_frame_seconds if tracking_frame_seconds else None,
        "mapping_average_frame_seconds": mapping_frame_seconds,
        "mapping_reciprocal_fps": 1 / mapping_frame_seconds if mapping_frame_seconds else None,
        "worker_metrics": worker_metrics,
    }
    with (evidence_dir / "run_summary.json").open("w") as stream:
        json.dump(summary, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(summary, sort_keys=True))
    if exit_code is None:
        raise SystemExit("Worker launch failed; inspect preserved evidence")
    if exit_code:
        raise SystemExit(exit_code)


if __name__ == "__main__":
    main()
