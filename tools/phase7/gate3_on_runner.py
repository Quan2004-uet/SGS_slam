#!/usr/bin/env python3
"""Guarded Phase 7 Gate 3 full-scene BCGM-on runner.

Default invocation is a read-only preflight. Only --execute creates the unique
run directories and launches the reused Gate 1B worker. It never retries.
"""

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
import zipfile
from pathlib import Path

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
PYTHON = Path("/home/robot/miniconda3/envs/sgs_slam_5080/bin/python")
DATA_ROOT = Path("/home/robot/research/SGS_slam/data/Replica/room0")
CAMERA_CONFIG = Path("/home/robot/research/SGS_slam_phase4_multiscene/configs/data/replica.yaml")
FROZEN_PHASE4_ROOT = Path("/home/robot/research/SGS_slam_phase4_multiscene")
FROZEN_PHASE4_SOURCE = FROZEN_PHASE4_ROOT / "scripts/slam.py"
RUN_ID = "p7_bcgm_g3_room0_on_0_1999_r01"
CONFIG = ROOT / "configs/replica/phase7_gate3_room0_on_0_1999_r01.py"
GATE2_CONFIG = ROOT / "configs/replica/phase7_gate2_room0_on_0_499_r01.py"
MODEL_DIR = ROOT / "experiments/Replica" / RUN_ID
EVIDENCE_DIR = ROOT / "results/runtime_artifacts/phase7_gate3" / RUN_ID
BASE_HEAD = "68f9060f7ff4d8d141be1d5f71339401327edd06"
BASE_CONFIG_SHA = "08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3"
CAMERA_SHA = "4c1e33544bef24c146c4ec9a622bb3ad7a314168db8d192c191db08bad3edf58"
TRAJECTORY_SHA = "5692a60076e426b403dc64025ff38c443606a506704545ee192d4dbadedaaca2"
PHASE7_SOURCE_SHA = "ce57372060d631e667b262e9cbb168d4ef73b094d7805ed9046635a762a0b999"
BCGM_MODULE_SHA = "8f30b9c997b10acd988c5a5ac053f2d15c28adde3783ba193ed9da832e908400"
FROZEN_PHASE4_SOURCE_SHA = "a26aafe4686acf65ca5523eb2758b7026ee35cc4e6a63690fc1f433c950732b3"
GATE1B_WORKER_SHA = "9a449ef10506ebbe6ccd0616d29aa02e9183554b333d605c9440ec07e09ad40b"
GATE2_CONFIG_SHA = "ff025785249c1811c9ee3b3359cd4656b1992e78d9465b610bfe840ea2026b49"
GATE3_CONFIG_SHA = "1bb57b3dd38e98c39a24310ceaee656a8415ce901e61808bb19cea8422c4ff22"
EVENT_CAP = 9000
GLOBAL_CAP = 4500000
MIN_FREE_DISK_BYTES = 20 * 1024 ** 3
MIN_AVAILABLE_RAM_BYTES = 32 * 1024 ** 3
MIN_FREE_GPU_MIB = 12 * 1024
EXPECTED_GPU_NAME = "NVIDIA GeForce RTX 5080"


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def git(*args):
    return subprocess.check_output(["git", *args], cwd=ROOT, text=True).strip()


def load_config(path):
    sys.path.insert(0, str(ROOT))
    try:
        return runpy.run_path(str(path))["config"]
    finally:
        sys.path.pop(0)


def config_differences(left, right, prefix=""):
    differences = []
    if isinstance(left, dict) and isinstance(right, dict):
        if set(left) != set(right):
            return [(prefix or "<root>", left, right)]
        for key in sorted(left):
            child = f"{prefix}.{key}" if prefix else key
            differences.extend(config_differences(left[key], right[key], child))
    elif isinstance(left, (list, tuple)) and isinstance(right, (list, tuple)):
        if len(left) != len(right):
            return [(prefix, left, right)]
        for index, (a, b) in enumerate(zip(left, right)):
            differences.extend(config_differences(a, b, f"{prefix}[{index}]"))
    elif left != right:
        differences.append((prefix, left, right))
    return differences


def dataset_inventory():
    expected = (
        ("frames", "frame", ".jpg"),
        ("depths", "depth", ".png"),
        ("semantic_ids", "semantic_id", ".png"),
        ("semantic_colors", "semantic_color", ".png"),
    )
    inventory = {}
    for directory, prefix, suffix in expected:
        folder = DATA_ROOT / directory
        files = list(folder.glob(f"{prefix}*{suffix}")) if folder.is_dir() else []
        if len(files) != 2000:
            raise RuntimeError(f"Expected 2000 {directory} files; found {len(files)}")
        for frame in range(2000):
            path = folder / f"{prefix}{frame:06d}{suffix}"
            if not path.is_file() or path.stat().st_size == 0:
                raise RuntimeError(f"Missing/empty dataset input: {path}")
        inventory[directory] = {"count": len(files), "frame_ids": [0, 1999]}
    return inventory


def available_ram_bytes():
    values = {}
    with Path("/proc/meminfo").open() as stream:
        for line in stream:
            key, value = line.split(":", 1)
            if key in ("MemTotal", "MemAvailable"):
                values[key] = int(value.split()[0]) * 1024
    return values


def gpu_and_runtime_preflight():
    try:
        gpu_lines = subprocess.check_output(
            ["nvidia-smi", "--query-gpu=index,name,memory.total,memory.used,utilization.gpu",
             "--format=csv,noheader,nounits"], text=True, stderr=subprocess.STDOUT
        ).strip().splitlines()
        process_lines = subprocess.check_output(
            ["nvidia-smi", "--query-compute-apps=pid,process_name,used_gpu_memory",
             "--format=csv,noheader,nounits"], text=True, stderr=subprocess.STDOUT
        ).splitlines()
    except (OSError, subprocess.CalledProcessError) as exc:
        raise RuntimeError(f"CODEX_GPU_NOT_VERIFIED: {exc}") from exc
    records = list(csv.reader(gpu_lines, skipinitialspace=True))
    if len(records) < 1 or len(records[0]) != 5:
        raise RuntimeError(f"Unexpected nvidia-smi GPU output: {gpu_lines!r}")
    index, name, total_mib, used_mib, utilization = [value.strip() for value in records[0]]
    gpu = {"index": int(index), "name": name, "total_mib": int(total_mib),
           "used_mib": int(used_mib), "utilization_percent": int(utilization)}
    if gpu["index"] != 0 or gpu["name"] != EXPECTED_GPU_NAME:
        raise RuntimeError(f"Unexpected selected GPU: {gpu}")
    if gpu["total_mib"] < 16000 or gpu["total_mib"] - gpu["used_mib"] < MIN_FREE_GPU_MIB:
        raise RuntimeError(f"Insufficient free GPU VRAM: {gpu}")
    conflicts = [line for line in process_lines if line.strip() and
                 "No running processes found" not in line and
                 "gnome-remote-desktop-daemon" not in line]
    if conflicts:
        raise RuntimeError(f"Unreviewed GPU compute process(es): {conflicts}")
    runtime = subprocess.check_output(
        [str(PYTHON), "-B", "-c",
         "import torch, diff_gaussian_rasterization; "
         "assert torch.__version__ == '2.7.1+cu128'; "
         "assert torch.version.cuda == '12.8'; "
         "assert torch.cuda.is_available(); "
         "print(torch.__version__, torch.version.cuda, torch.cuda.get_device_name(0))"],
        text=True, stderr=subprocess.STDOUT).strip()
    if EXPECTED_GPU_NAME not in runtime:
        raise RuntimeError(f"Pinned runtime reports unexpected device: {runtime}")
    return gpu, process_lines, runtime


def preflight():
    checks = {"branch": git("branch", "--show-current"),
              "head": git("rev-parse", "HEAD")}
    if checks["head"] != BASE_HEAD or checks["branch"] != "phase7-bcgm":
        raise RuntimeError(f"Unexpected source identity: {checks}")
    identities = {
        "phase7_scripts_slam_sha256": (ROOT / "scripts/slam.py", PHASE7_SOURCE_SHA),
        "bcgm_sha256": (ROOT / "utils/bcgm.py", BCGM_MODULE_SHA),
        "frozen_phase4_scripts_slam_sha256": (FROZEN_PHASE4_SOURCE, FROZEN_PHASE4_SOURCE_SHA),
        "gate1b_worker_sha256": (ROOT / "tools/phase7/gate1b_worker.py", GATE1B_WORKER_SHA),
        "gate2_config_sha256": (GATE2_CONFIG, GATE2_CONFIG_SHA),
        "gate3_config_sha256": (CONFIG, GATE3_CONFIG_SHA),
        "base_replica_config_sha256": (ROOT / "configs/replica/slam.py", BASE_CONFIG_SHA),
        "replica_data_config_sha256": (CAMERA_CONFIG, CAMERA_SHA),
        "room0_trajectory_sha256": (DATA_ROOT / "traj.txt", TRAJECTORY_SHA),
    }
    observed = {}
    for name, (path, expected) in identities.items():
        actual = sha256(path)
        observed[name] = actual
        if actual != expected:
            raise RuntimeError(f"Identity mismatch for {path}: {actual}")
    if MODEL_DIR.exists() or EVIDENCE_DIR.exists():
        raise RuntimeError("Gate 3 output collision; preserve existing paths")
    free_disk = shutil.disk_usage(ROOT).free
    if free_disk < MIN_FREE_DISK_BYTES:
        raise RuntimeError(f"Insufficient free disk bytes: {free_disk}")
    ram = available_ram_bytes()
    if ram.get("MemAvailable", 0) < MIN_AVAILABLE_RAM_BYTES:
        raise RuntimeError(f"Insufficient available host RAM: {ram}")
    if not PYTHON.is_file():
        raise RuntimeError(f"Pinned Python interpreter missing: {PYTHON}")
    data_files = dataset_inventory()
    trajectory_path = DATA_ROOT / "traj.txt"
    if not trajectory_path.is_file() or trajectory_path.stat().st_size == 0:
        raise RuntimeError("Replica room0 traj.txt missing/empty")
    gate2 = load_config(GATE2_CONFIG)
    gate3 = load_config(CONFIG)
    differences = config_differences(gate2, gate3)
    allowed = {"run_name", "data.end", "data.num_frames"}
    observed_differences = {path for path, _old, _new in differences}
    if observed_differences != allowed:
        raise RuntimeError(f"Unexpected Gate 2/Gate 3 config differences: {differences}")
    d = gate3["data"]
    if (gate3["run_name"], d["sequence"], d["start"], d["end"], d["stride"],
            d["num_frames"]) != (RUN_ID, "room0", 0, 2000, 1, 2000):
        raise RuntimeError("Gate 3 run/frame identity mismatch")
    if (gate3["bcgm"] != {"enabled": True,
            "max_new_gaussians_per_event": EVENT_CAP, "max_gaussians": GLOBAL_CAP}):
        raise RuntimeError("Gate 3 BCGM caps mismatch")
    if gate3["mapping"]["use_gaussian_splatting_densification"]:
        raise RuntimeError("Gradient clone/split densification must remain disabled")
    if not gate3["mapping"]["add_new_gaussians"]:
        raise RuntimeError("Pixel-driven insertion must remain enabled")
    expected_science = (0, "cuda:0", 1, 5, 24, 40, 60, 1200, 680, True, 5, False)
    actual_science = (gate3["seed"], gate3["primary_device"], gate3["map_every"],
                      gate3["keyframe_every"], gate3["mapping_window_size"],
                      gate3["tracking"]["num_iters"], gate3["mapping"]["num_iters"],
                      d["desired_image_width"], d["desired_image_height"],
                      d["load_semantics"], gate3["eval_every"], gate3["use_wandb"])
    if actual_science != expected_science:
        raise RuntimeError(f"Scientific config drift: {actual_science}")
    if Path(gate3["workdir"]) / gate3["run_name"] != MODEL_DIR:
        raise RuntimeError("Gate 3 model output path mismatch")
    from utils.bcgm import validate_bcgm_config
    validate_bcgm_config(gate3)
    checks.update({"identities": observed, "config_differences": differences,
                   "dataset_inventory": data_files, "free_disk_bytes": free_disk,
                   "minimum_free_disk_bytes": MIN_FREE_DISK_BYTES,
                   "available_ram_bytes": ram["MemAvailable"],
                   "minimum_available_ram_bytes": MIN_AVAILABLE_RAM_BYTES,
                   "model_dir": str(MODEL_DIR), "evidence_dir": str(EVIDENCE_DIR),
                   "estimated_new_output_budget_bytes": 6 * 1024 ** 3,
                   "disk_safety_margin_bytes": free_disk - 6 * 1024 ** 3})
    try:
        gpu, processes, runtime = gpu_and_runtime_preflight()
    except Exception as exc:
        checks.update({"preflight_status": "BLOCKED",
                       "gpu_status": "CODEX_GPU_NOT_VERIFIED"
                       if "CODEX_GPU_NOT_VERIFIED" in str(exc) else "GPU_OR_RUNTIME_CHECK_FAILED",
                       "gpu_error": f"{type(exc).__name__}: {exc}"})
        return gate3, checks
    checks.update({"preflight_status": "PASS", "gpu_status": "HOST_GPU_VERIFIED_AT_PREFLIGHT",
                   "gpu": gpu, "gpu_processes": processes, "runtime": runtime})
    return gate3, checks


def validate_admission(events, insertion_trace):
    if len(events) != 1999 or len(insertion_trace) != 1999:
        return False, "expected exactly 1999 insertion events and transitions"
    trace_by_frame = {int(item["frame"]): item for item in insertion_trace}
    if len(trace_by_frame) != len(insertion_trace):
        return False, "duplicate worker insertion frame"
    for expected_frame, event in enumerate(events, start=1):
        trace = trace_by_frame.get(expected_frame)
        if trace is None:
            return False, f"missing insertion trace for frame {expected_frame}"
        if (event.get("frame") != expected_frame or event.get("event_cap") != EVENT_CAP or
                event.get("global_cap") != GLOBAL_CAP or
                event.get("before", -1) < 0 or event.get("valid_candidates", -1) < 0 or
                event.get("rejected", -1) < 0 or
                event.get("valid_candidates") != event.get("admitted", -1) + event.get("rejected", -1) or
                event.get("after", -1) - event.get("before", -1) != event.get("admitted") or
                event.get("admitted", -1) < 0 or event.get("admitted", -1) > EVENT_CAP or
                event.get("after", GLOBAL_CAP + 1) > GLOBAL_CAP or
                event.get("global_saturated") != (event["before"] + event["admitted"] >= GLOBAL_CAP) or
                event.get("event_saturated") != (
                    event["valid_candidates"] > event["admitted"] and event["admitted"] == EVENT_CAP) or
                event.get("budget_saturated") != (event["event_saturated"] or event["global_saturated"]) or
                trace.get("before") != event.get("before") or
                trace.get("after") != event.get("after")):
            return False, f"admission invariant failed at frame {expected_frame}"
    return True, None


def run(config, preflight_checks):
    EVIDENCE_DIR.mkdir(parents=True, exist_ok=False)
    with (EVIDENCE_DIR / "effective_config_input.json").open("w", encoding="utf-8") as stream:
        json.dump(config, stream, indent=2, sort_keys=True)
        stream.write("\n")
    nvml_path = EVIDENCE_DIR / "nvml_samples.csv"
    sampler_stop = threading.Event()

    def sample_gpu():
        with nvml_path.open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(["utc", "gpu_index", "memory_used_mib", "utilization_gpu_percent"])
            while not sampler_stop.is_set():
                try:
                    output = subprocess.check_output(
                        ["nvidia-smi", "--query-gpu=index,memory.used,utilization.gpu",
                         "--format=csv,noheader,nounits"], text=True, stderr=subprocess.STDOUT)
                    for line in output.splitlines():
                        values = [part.strip() for part in line.split(",")]
                        writer.writerow([time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()), *values])
                except Exception:
                    writer.writerow([time.strftime("%Y-%m-%dT%H:%M:%S+00:00", time.gmtime()), "NVML_ERROR"])
                stream.flush()
                sampler_stop.wait(1.0)

    sampler = threading.Thread(target=sample_gpu, daemon=True)
    sampler.start()
    started = time.monotonic()
    started_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    worker = ROOT / "tools/phase7/gate1b_worker.py"
    command = [str(PYTHON), "-B", str(worker), "--source-root", str(ROOT),
               "--config", str(CONFIG), "--evidence-dir", str(EVIDENCE_DIR)]
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["CUDA_VISIBLE_DEVICES"] = "0"
    try:
        with (EVIDENCE_DIR / "stdout_stderr.log").open("w", encoding="utf-8") as output:
            completed = subprocess.run(command, cwd=ROOT, env=env, stdout=output,
                                        stderr=subprocess.STDOUT, check=False)
    finally:
        elapsed = time.monotonic() - started
        sampler_stop.set()
        sampler.join()
    finished_utc = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    worker_metrics = None
    tracking_seconds = mapping_seconds = None
    events = []
    for line in (EVIDENCE_DIR / "stdout_stderr.log").open(encoding="utf-8", errors="replace"):
        if line.startswith("GATE1B_WORKER_METRICS "):
            worker_metrics = json.loads(line.removeprefix("GATE1B_WORKER_METRICS "))
        elif line.startswith("BCGM_INSERTION "):
            events.append(json.loads(line.removeprefix("BCGM_INSERTION ")))
        match = re.search(r"Average Tracking/Frame Time: ([0-9.eE+-]+) s", line)
        if match:
            tracking_seconds = float(match.group(1))
        match = re.search(r"Average Mapping/Frame Time: ([0-9.eE+-]+) s", line)
        if match:
            mapping_seconds = float(match.group(1))
    trace_path = EVIDENCE_DIR / "insertion_counts.jsonl"
    trace = [json.loads(line) for line in trace_path.read_text().splitlines() if line.strip()] \
        if trace_path.is_file() else []
    admission_ok, admission_error = validate_admission(events, trace)
    from tools.phase7.nvml_telemetry import parse_nvml_csv
    nvml = parse_nvml_csv(nvml_path, expected_gpu_index=0)

    checkpoint = MODEL_DIR / "params.npz"
    checkpoint_validation = {"exists": checkpoint.is_file(), "zip_crc": False,
                             "numpy_load": False, "all_numeric_finite": False,
                             "gaussian_fields_aligned": False, "gaussian_count": None,
                             "saved_pose_count": None, "estimated_pose_count": None}
    eval_validation = {}
    try:
        import numpy as np
        if checkpoint.is_file():
            with zipfile.ZipFile(checkpoint) as archive:
                checkpoint_validation["zip_crc"] = archive.testzip() is None
            with np.load(checkpoint, allow_pickle=False) as saved:
                checkpoint_validation["numpy_load"] = True
                numeric = [saved[key] for key in saved.files
                           if np.issubdtype(saved[key].dtype, np.number)]
                checkpoint_validation["all_numeric_finite"] = all(
                    np.isfinite(array).all() for array in numeric)
                count = int(saved["means3D"].shape[0])
                fields = ("rgb_colors", "unnorm_rotations", "logit_opacities",
                          "log_scales", "semantic_ids", "semantic_colors", "timestep")
                checkpoint_validation["gaussian_fields_aligned"] = all(
                    saved[field].shape[0] == count for field in fields)
                checkpoint_validation["gaussian_count"] = count
                checkpoint_validation["saved_pose_count"] = int(saved["gt_w2c_all_frames"].shape[0])
                checkpoint_validation["estimated_pose_count"] = min(
                    int(saved["cam_unnorm_rots"].shape[-1]), int(saved["cam_trans"].shape[-1]))
        eval_dir = MODEL_DIR / "eval"
        for metric in ("psnr", "ssim", "lpips", "l1", "rmse", "miou"):
            path = eval_dir / f"{metric}.txt"
            values = np.asarray(np.loadtxt(path)).reshape(-1) if path.is_file() else np.asarray([])
            eval_validation[metric] = {"exists": path.is_file(), "count": int(values.size),
                                       "finite": bool(values.size and np.isfinite(values).all())}
    except Exception as exc:
        eval_validation["validation_error"] = f"{type(exc).__name__}: {exc}"

    required_eval_metrics = {"psnr", "ssim", "lpips", "l1", "rmse", "miou"}
    eval_ok = (set(eval_validation) == required_eval_metrics and
               all(item.get("count") == 401 and item.get("finite")
                   for item in eval_validation.values()))
    run_complete = bool(
        completed.returncode == 0 and worker_metrics and
        worker_metrics.get("rgbd_slam_returned_normally") and admission_ok and
        checkpoint_validation["zip_crc"] and checkpoint_validation["numpy_load"] and
        checkpoint_validation["all_numeric_finite"] and checkpoint_validation["gaussian_fields_aligned"] and
        checkpoint_validation["saved_pose_count"] == 2000 and
        checkpoint_validation["estimated_pose_count"] == 2000 and eval_ok)
    totals = {key: sum(int(event.get(key, 0)) for event in events)
              for key in ("valid_candidates", "admitted", "rejected")}
    summary = {
        "run_id": RUN_ID, "status": "COMPLETE" if run_complete else "INCOMPLETE_OR_FAILED",
        "execution_validation_pass": run_complete, "process_exit_code": completed.returncode,
        "started_utc": started_utc, "finished_utc": finished_utc,
        "process_wall_seconds": elapsed, "end_to_end_fps": 2000 / elapsed if run_complete else None,
        "git_branch": preflight_checks["branch"], "git_head": preflight_checks["head"],
        "frame_range": [0, 1999], "frame_count": 2000,
        "source_sha256": sha256(ROOT / "scripts/slam.py"),
        "bcgm_sha256": sha256(ROOT / "utils/bcgm.py"), "config_sha256": sha256(CONFIG),
        "worker_sha256": sha256(worker), "runner_sha256": sha256(Path(__file__)),
        "model_dir": str(MODEL_DIR), "evidence_dir": str(EVIDENCE_DIR),
        "preflight": preflight_checks,
        "cuda_peak_allocated_bytes": worker_metrics.get("cuda_peak_allocated_bytes") if worker_metrics else None,
        "cuda_peak_reserved_bytes": worker_metrics.get("cuda_peak_reserved_bytes") if worker_metrics else None,
        "cuda_allocator_scope": worker_metrics.get("allocator_scope") if worker_metrics else None,
        "nvml_sampling_interval_seconds": 1.0,
        "nvml_valid_samples": nvml["valid_samples"], "nvml_invalid_samples": nvml["invalid_samples"],
        "nvml_error_rows": nvml["error_rows"],
        "nvml_peak_device_used_mib": nvml["peak_device_used_mib"],
        "nvml_peak_timestamp_utc": nvml["peak_timestamp_utc"],
        "nvml_peak_gpu_index": nvml["peak_gpu_index"],
        "nvml_max_sampled_utilization_percent": nvml["maximum_sampled_gpu_utilization_percent"],
        "nvml_scope": "device-wide sampled memory; separate from process CUDA allocator peaks",
        "tracking_average_frame_seconds": tracking_seconds,
        "tracking_reciprocal_fps": 1 / tracking_seconds if tracking_seconds else None,
        "mapping_average_frame_seconds": mapping_seconds,
        "mapping_reciprocal_fps": 1 / mapping_seconds if mapping_seconds else None,
        "worker_metrics": worker_metrics, "checkpoint_validation": checkpoint_validation,
        "evaluation_validation": eval_validation, "insertion_record_count": len(trace),
        "bcgm_event_count": len(events), "bcgm_admission_valid": admission_ok,
        "bcgm_admission_error": admission_error, "bcgm_admission_totals": totals,
        "event_cap_activation_count": sum(bool(event.get("event_saturated")) for event in events),
        "global_cap_activation_count": sum(bool(event.get("global_saturated")) for event in events),
        "global_cap_runtime_verified": any(bool(event.get("global_saturated")) for event in events),
        "global_cap_note": "Global Cap is runtime-verified only if global_saturated is observed; pruning may later reduce map count.",
    }
    with (EVIDENCE_DIR / "run_summary.json").open("w", encoding="utf-8") as stream:
        json.dump(summary, stream, indent=2, sort_keys=True)
        stream.write("\n")
    print(json.dumps(summary, sort_keys=True))
    if completed.returncode:
        raise SystemExit(completed.returncode)
    if not run_complete:
        raise SystemExit("Run returned but Gate 3 validation is incomplete; preserve evidence and do not retry automatically")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--execute", action="store_true",
                        help="Launch the sole Gate 3 CUDA experiment after all guarded preflight checks")
    args = parser.parse_args()
    try:
        config, checks = preflight()
    except Exception as exc:
        result = {"preflight": "BLOCKED", "run_id": RUN_ID,
                  "gpu_status": "CODEX_GPU_NOT_VERIFIED" if "CODEX_GPU_NOT_VERIFIED" in str(exc) else "NOT_ESTABLISHED",
                  "reason": f"{type(exc).__name__}: {exc}"}
        print(json.dumps(result, sort_keys=True), file=sys.stderr)
        return 2
    if checks["preflight_status"] != "PASS":
        print(json.dumps({"preflight": "BLOCKED", "execute": args.execute,
                          "run_id": RUN_ID, "frame_range": [0, 1999], **checks},
                         sort_keys=True))
        return 2
    result = {"preflight": "PASS", "execute": args.execute, "run_id": RUN_ID,
              "frame_range": [0, 1999], "config": str(CONFIG), **checks}
    print(json.dumps(result, sort_keys=True))
    if args.execute:
        run(config, checks)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
