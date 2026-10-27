#!/usr/bin/env python3
"""Guarded single-arm Gate 2 runner reusing the validated Gate 1B worker.

Default invocation performs read-only preflight. --execute is required to
create the unique evidence/model directories and launch a CUDA workload.
"""

import argparse
import csv
import hashlib
import json
import os
import re
import runpy
import subprocess
import sys
import threading
import time
import zipfile
from datetime import datetime, timezone
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
PYTHON = Path("/home/robot/miniconda3/envs/sgs_slam_5080/bin/python")
DATA_ROOT = Path("/home/robot/research/SGS_slam/data/Replica/room0")
CAMERA_CONFIG = Path("/home/robot/research/SGS_slam_phase4_multiscene/configs/data/replica.yaml")
RUN_ID = "p7_bcgm_g2_room0_on_0_499_r01"
CONFIG = ROOT / "configs/replica/phase7_gate2_room0_on_0_499_r01.py"
MODEL_DIR = ROOT / "experiments/Replica" / RUN_ID
EVIDENCE_DIR = ROOT / "results/runtime_artifacts/phase7_gate2" / RUN_ID
BASE_HEAD = "68f9060f7ff4d8d141be1d5f71339401327edd06"
BASE_CONFIG_SHA = "08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3"
CAMERA_SHA = "4c1e33544bef24c146c4ec9a622bb3ad7a314168db8d192c191db08bad3edf58"
TRAJECTORY_SHA = "5692a60076e426b403dc64025ff38c443606a506704545ee192d4dbadedaaca2"
PHASE7_SOURCE_SHA = "ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999"
BCGM_MODULE_SHA = "8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400"
GATE1B_WORKER_SHA = "9a449ef10506ebbe6ccd0616d29aa02e9183554b333d605c9440ec07e09ad40b"
CONFIG_SHA = "ff025785249c1811c9ee3b3359cd4656b1992e78d9465b610bfe840ea2026b49"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


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
        raise RuntimeError(f"Unreviewed GPU compute process(es): {conflicts}")
    return gpu, processes


def load_config():
    sys.path.insert(0, str(ROOT))
    try:
        return runpy.run_path(str(CONFIG))["config"]
    finally:
        sys.path.pop(0)


def preflight():
    if git("rev-parse", "HEAD") != BASE_HEAD:
        raise RuntimeError("Unexpected Phase 7 base HEAD")
    if git("branch", "--show-current") != "phase7-bcgm":
        raise RuntimeError("Unexpected Phase 7 branch")
    if sha256(ROOT / "scripts/slam.py") != PHASE7_SOURCE_SHA:
        raise RuntimeError("Phase 7 online source hash changed")
    if sha256(ROOT / "utils/bcgm.py") != BCGM_MODULE_SHA:
        raise RuntimeError("BCGM source hash changed")
    if sha256(ROOT / "configs/replica/slam.py") != BASE_CONFIG_SHA:
        raise RuntimeError("Base Replica config hash changed")
    if sha256(CAMERA_CONFIG) != CAMERA_SHA:
        raise RuntimeError("Replica camera config hash changed")
    if sha256(DATA_ROOT / "traj.txt") != TRAJECTORY_SHA:
        raise RuntimeError("Replica room0 trajectory hash changed")
    if sha256(CONFIG) != CONFIG_SHA:
        raise RuntimeError("Gate 2 config hash changed")
    if sha256(ROOT / "tools/phase7/gate1b_worker.py") != GATE1B_WORKER_SHA:
        raise RuntimeError("Validated Gate 1B worker hash changed")
    if MODEL_DIR.exists() or EVIDENCE_DIR.exists():
        raise RuntimeError("Gate 2 output collision; preserve existing paths")
    if shutil_disk_free(ROOT) < 10 * 1024 ** 3:
        raise RuntimeError("Less than 10 GiB free on the output filesystem")
    if not PYTHON.is_file():
        raise RuntimeError("Pinned Python interpreter missing")
    environment = subprocess.check_output(
        [str(PYTHON), "-B", "-c",
         "import torch, diff_gaussian_rasterization; "
         "assert torch.__version__ == '2.7.1+cu128'; "
         "assert torch.version.cuda == '12.8'; "
         "assert torch.cuda.is_available(); "
         "print(torch.__version__, torch.version.cuda, "
         "torch.cuda.get_device_name(0))"], text=True).strip()
    for directory, prefix, suffix in (
            ("frames", "frame", ".jpg"), ("depths", "depth", ".png"),
            ("semantic_ids", "semantic_id", ".png"),
            ("semantic_colors", "semantic_color", ".png")):
        paths = list((DATA_ROOT / directory).glob(f"{prefix}*{suffix}"))
        if len(paths) != 2000:
            raise RuntimeError(f"Unexpected {directory} file count: {len(paths)}")
        for index in range(500):
            path = DATA_ROOT / directory / f"{prefix}{index:06d}{suffix}"
            if not path.is_file() or path.stat().st_size == 0:
                raise RuntimeError(f"Missing/empty frame input: {path}")
    config = load_config()
    d = config["data"]
    observed = (d["sequence"], d["start"], d["end"], d["stride"], d["num_frames"])
    if observed != ("room0", 0, 500, 1, 500):
        raise RuntimeError(f"Unexpected frame specification: {observed}")
    if Path(config["workdir"]) / config["run_name"] != MODEL_DIR:
        raise RuntimeError("Model output path mismatch")
    if config["run_name"] != RUN_ID or Path(d["basedir"]) / "room0" != DATA_ROOT:
        raise RuntimeError("Run or dataset identity mismatch")
    scientific = (config["seed"], config["primary_device"], config["map_every"],
                  config["keyframe_every"], config["mapping_window_size"],
                  config["tracking"]["num_iters"], config["mapping"]["num_iters"],
                  d["desired_image_width"], d["desired_image_height"],
                  d["load_semantics"], config["eval_every"], config["use_wandb"])
    if scientific != (0, "cuda:0", 1, 5, 24, 40, 60, 1200, 680, True, 5, False):
        raise RuntimeError(f"Scientific settings differ from Gate 1B: {scientific}")
    if config["mapping"]["use_gaussian_splatting_densification"]:
        raise RuntimeError("Gradient clone/split densification must remain disabled")
    if not config["mapping"]["add_new_gaussians"]:
        raise RuntimeError("Pixel-driven insertion must remain enabled")
    if config["bcgm"] != {"enabled": True, "max_new_gaussians_per_event": 9000,
                           "max_gaussians": 4500000}:
        raise RuntimeError("BCGM settings mismatch")
    sys.path.insert(0, str(ROOT))
    try:
        from utils.bcgm import validate_bcgm_config
        validate_bcgm_config(config)
    finally:
        sys.path.pop(0)
    gpu, processes = gpu_state()
    return config, gpu, processes, environment


def shutil_disk_free(path):
    import shutil
    return shutil.disk_usage(path).free


def run(config, gpu, processes, environment):
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=False)
    with (EVIDENCE_DIR / "effective_config_input.json").open("w") as stream:
        json.dump(config, stream, indent=2, sort_keys=True)
        stream.write("\n")
    nvml_path = EVIDENCE_DIR / "nvml_samples.csv"
    stop = threading.Event()

    def sample_gpu():
        with nvml_path.open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["utc", "gpu_index", "memory_used_mib", "utilization_gpu_percent"])
            while not stop.is_set():
                try:
                    output = subprocess.check_output(
                        ["nvidia-smi", "--query-gpu=index,memory.used,utilization.gpu",
                         "--format=csv,noheader,nounits"], text=True).strip()
                    for line in output.splitlines():
                        writer.writerow([datetime.now(timezone.utc).isoformat(),
                                         *[item.strip() for item in line.split(",")]])
                except Exception:
                    writer.writerow([datetime.now(timezone.utc).isoformat(), "NVML_ERROR"])
                stream.flush()
                stop.wait(1.0)

    sampler = threading.Thread(target=sample_gpu, daemon=True)
    sampler.start()
    started_utc = datetime.now(timezone.utc).isoformat()
    start = time.monotonic()
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["CUDA_VISIBLE_DEVICES"] = "0"
    worker = ROOT / "tools/phase7/gate1b_worker.py"
    command = [str(PYTHON), "-B", str(worker), "--source-root", str(ROOT),
               "--config", str(CONFIG), "--evidence-dir", str(EVIDENCE_DIR)]
    with (EVIDENCE_DIR / "stdout_stderr.log").open("w") as output:
        completed = subprocess.run(command, cwd=ROOT, env=env, stdout=output,
                                    stderr=subprocess.STDOUT, check=False)
    elapsed = time.monotonic() - start
    finished_utc = datetime.now(timezone.utc).isoformat()
    stop.set()
    sampler.join()

    worker_metrics = None
    tracking_s = mapping_s = None
    bcgm_events = []
    for line in (EVIDENCE_DIR / "stdout_stderr.log").open(errors="replace"):
        if line.startswith("GATE1B_WORKER_METRICS "):
            worker_metrics = json.loads(line.removeprefix("GATE1B_WORKER_METRICS "))
        if line.startswith("BCGM_INSERTION "):
            bcgm_events.append(json.loads(line.removeprefix("BCGM_INSERTION ")))
        match = re.search(r"Average Tracking/Frame Time: ([0-9.eE+-]+) s", line)
        if match:
            tracking_s = float(match.group(1))
        match = re.search(r"Average Mapping/Frame Time: ([0-9.eE+-]+) s", line)
        if match:
            mapping_s = float(match.group(1))
    nvml_values = []
    with nvml_path.open(newline="") as stream:
        for row in list(csv.reader(stream))[1:]:
            if len(row) == 3 and row[1] != "NVML_ERROR":
                try:
                    nvml_values.append(float(row[1]))
                except ValueError:
                    pass
    event_cap_activations = [event for event in bcgm_events
                             if event.get("event_saturated")]
    admission_totals = {
        key: sum(int(event.get(key, 0)) for event in bcgm_events)
        for key in ("valid_candidates", "admitted", "rejected")
    }
    insertion_records = EVIDENCE_DIR / "insertion_counts.jsonl"
    insertion_count = sum(1 for line in insertion_records.open() if line.strip()) \
        if insertion_records.is_file() else 0
    checkpoint = MODEL_DIR / "params.npz"
    checkpoint_validation = {"exists": checkpoint.is_file(), "zip_crc": False,
                             "numpy_load": False, "all_numeric_finite": False,
                             "gaussian_fields_aligned": False, "saved_pose_count": None,
                             "estimated_pose_count": None, "gaussian_count": None}
    if checkpoint.is_file():
        import numpy as np
        with zipfile.ZipFile(checkpoint) as archive:
            checkpoint_validation["zip_crc"] = archive.testzip() is None
        with np.load(checkpoint, allow_pickle=False) as data:
            checkpoint_validation["numpy_load"] = True
            numeric = [data[key] for key in data.files if np.issubdtype(data[key].dtype, np.number)]
            checkpoint_validation["all_numeric_finite"] = all(np.isfinite(value).all() for value in numeric)
            count = int(data["means3D"].shape[0])
            fields = ("rgb_colors", "unnorm_rotations", "logit_opacities", "log_scales",
                      "semantic_ids", "semantic_colors")
            checkpoint_validation["gaussian_fields_aligned"] = all(
                data[field].shape[0] == count for field in fields)
            checkpoint_validation["gaussian_count"] = count
            checkpoint_validation["saved_pose_count"] = int(data["gt_w2c_all_frames"].shape[0])
            checkpoint_validation["estimated_pose_count"] = min(
                int(data["cam_unnorm_rots"].shape[-1]),
                int(data["cam_trans"].shape[-1]))
    run_complete = bool(
        completed.returncode == 0 and worker_metrics and
        worker_metrics.get("rgbd_slam_returned_normally") and
        checkpoint_validation["zip_crc"] and checkpoint_validation["numpy_load"] and
        checkpoint_validation["all_numeric_finite"] and
        checkpoint_validation["gaussian_fields_aligned"] and
        checkpoint_validation["saved_pose_count"] == 500 and
        checkpoint_validation["estimated_pose_count"] == 500 and
        insertion_count == 499 and len(bcgm_events) == 499)
    eval_validation = {}
    eval_dir = MODEL_DIR / "eval"
    if eval_dir.is_dir():
        import numpy as np
        for metric in ("psnr", "ssim", "lpips", "l1", "rmse", "miou"):
            path = eval_dir / f"{metric}.txt"
            try:
                values = np.asarray(np.loadtxt(path)).reshape(-1) if path.is_file() else np.asarray([])
                eval_validation[metric] = {"exists": path.is_file(), "count": int(values.size),
                                           "finite": bool(values.size and np.isfinite(values).all())}
            except Exception as exc:
                eval_validation[metric] = {"exists": path.is_file(), "count": None,
                                           "finite": False,
                                           "error": f"{type(exc).__name__}: {exc}"}
    summary = {
        "run_id": RUN_ID,
        "status": "COMPLETE" if run_complete else "INCOMPLETE_OR_FAILED",
        "execution_and_checkpoint_validation_pass": run_complete,
        "process_exit_code": completed.returncode, "started_utc": started_utc,
        "finished_utc": finished_utc, "process_wall_seconds": elapsed,
        "end_to_end_fps": 500 / elapsed if run_complete else None,
        "source_sha256": sha256(ROOT / "scripts/slam.py"),
        "bcgm_sha256": sha256(ROOT / "utils/bcgm.py"),
        "config_sha256": sha256(CONFIG), "worker_sha256": sha256(worker),
        "model_dir": str(MODEL_DIR), "evidence_dir": str(EVIDENCE_DIR),
        "frame_range": [0, 499], "gpu_preflight": gpu,
        "gpu_processes_preflight": processes, "runtime_preflight": environment,
        "nvml_samples_seconds": 1.0,
        "nvml_peak_device_used_mib": max(nvml_values) if nvml_values else None,
        "nvml_valid_samples": len(nvml_values),
        "tracking_average_frame_seconds": tracking_s,
        "tracking_reciprocal_fps": 1 / tracking_s if tracking_s else None,
        "mapping_average_frame_seconds": mapping_s,
        "mapping_reciprocal_fps": 1 / mapping_s if mapping_s else None,
        "worker_metrics": worker_metrics,
        "checkpoint_validation": checkpoint_validation,
        "evaluation_validation": eval_validation,
        "insertion_record_count": insertion_count,
        "bcgm_event_count": len(bcgm_events),
        "bcgm_event_cap_activation_count": len(event_cap_activations),
        "bcgm_event_cap_activation_frames": [event.get("frame") for event in event_cap_activations],
        "bcgm_admission_totals": admission_totals,
        "global_cap_activation_count": sum(bool(event.get("global_saturated"))
                                            for event in bcgm_events),
        "global_cap_runtime_verified": any(event.get("global_saturated")
                                            for event in bcgm_events),
    }
    with (EVIDENCE_DIR / "run_summary.json").open("w") as stream:
        json.dump(summary, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(summary, sort_keys=True))
    if completed.returncode:
        raise SystemExit(completed.returncode)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--execute", action="store_true",
                        help="Launch the single Gate 2 CUDA run after guarded preflight")
    args = parser.parse_args()
    config, gpu, processes, environment = preflight()
    print(json.dumps({"preflight": "PASS", "execute": args.execute,
                      "run_id": RUN_ID, "frame_range": [0, 499],
                      "config": str(CONFIG), "model_dir": str(MODEL_DIR),
                      "evidence_dir": str(EVIDENCE_DIR), "gpu": gpu,
                      "gpu_processes": processes,
                      "runtime_preflight": environment,
                      "free_bytes": shutil_disk_free(ROOT)}, sort_keys=True))
    if args.execute:
        run(config, gpu, processes, environment)


if __name__ == "__main__":
    main()
