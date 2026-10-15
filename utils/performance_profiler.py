"""Low-overhead, opt-in performance telemetry for online SGS-SLAM.

The profiler is disabled when the ``profiling`` config section is absent or
its mode is ``off``.  The disabled path does not create output files, CUDA
events, timers, buffers, or retain tensor references.
"""

from __future__ import annotations

import contextlib
import atexit
import hashlib
import json
import math
import os
import platform
import subprocess
import sys
import time
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Iterable, Mapping, Optional, Tuple

import torch


SCHEMA_VERSION = "p5g2.telemetry.v1"
VALID_MODES = {"off", "light", "detailed"}
REQUIRED_RECORD_FIELDS = {
    "schema_version",
    "run_id",
    "frame_id",
    "iteration_id",
    "component",
    "metric_name",
    "value",
    "unit",
    "measurement_mode",
    "timestamp_relative_s",
}
REQUIRED_SUMMARY_FIELDS = {
    "schema_version", "run_id", "profiling_mode", "status", "wall_time_seconds",
    "aggregate_metrics", "archive", "staging", "cuda_event_validation",
}
REQUIRED_METADATA_FIELDS = {
    "schema_version", "run_id", "profiling_mode", "sampling",
    "cuda_event_validation", "python", "platform",
}


@dataclass(frozen=True)
class ProfilingSettings:
    mode: str = "off"
    run_id: str = ""
    output_dir: str = ""
    cpu_timing_interval: int = 1
    memory_interval: int = 5
    cuda_event_interval: int = 10
    cuda_resolve_interval: int = 10
    flush_every: int = 128
    max_buffered_records: int = 512
    max_pending_cuda_events: int = 512
    max_summary_samples: int = 2048

    @classmethod
    def from_config(cls, config: Optional[Mapping[str, Any]]) -> "ProfilingSettings":
        raw = dict(config or {})
        mode = str(raw.get("mode", "off")).lower()
        if mode not in VALID_MODES:
            raise ValueError(f"Invalid profiling mode '{mode}'; expected one of {sorted(VALID_MODES)}")
        integer_fields = (
            "cpu_timing_interval",
            "memory_interval",
            "cuda_event_interval",
            "cuda_resolve_interval",
            "flush_every",
            "max_buffered_records",
            "max_pending_cuda_events",
            "max_summary_samples",
        )
        values = {field: int(raw.get(field, getattr(cls, field))) for field in integer_fields}
        if any(value <= 0 for value in values.values()):
            raise ValueError("Profiling sampling, flushing, and buffer limits must be positive integers")
        return cls(
            mode=mode,
            run_id=str(raw.get("run_id", "")),
            output_dir=str(raw.get("output_dir", "")),
            **values,
        )


def validate_record(record: Mapping[str, Any]) -> None:
    missing = REQUIRED_RECORD_FIELDS.difference(record)
    if missing:
        raise ValueError(f"Telemetry record is missing required fields: {sorted(missing)}")
    if record["schema_version"] != SCHEMA_VERSION:
        raise ValueError(f"Unsupported telemetry schema: {record['schema_version']}")
    if record["measurement_mode"] not in VALID_MODES.difference({"off"}):
        raise ValueError("Telemetry records are only valid in light or detailed mode")
    if not isinstance(record["value"], (int, float)) or not math.isfinite(float(record["value"])):
        raise ValueError("Telemetry value must be a finite number")


def validate_summary(summary: Mapping[str, Any]) -> None:
    missing = REQUIRED_SUMMARY_FIELDS.difference(summary)
    if missing:
        raise ValueError(f"Telemetry summary is missing required fields: {sorted(missing)}")
    if summary["schema_version"] != SCHEMA_VERSION or summary["profiling_mode"] not in {"light", "detailed"}:
        raise ValueError("Invalid telemetry summary schema or mode")


def validate_run_metadata(metadata: Mapping[str, Any]) -> None:
    missing = REQUIRED_METADATA_FIELDS.difference(metadata)
    if missing:
        raise ValueError(f"Run metadata is missing required fields: {sorted(missing)}")
    if metadata["schema_version"] != SCHEMA_VERSION or metadata["profiling_mode"] not in {"light", "detailed"}:
        raise ValueError("Invalid run metadata schema or mode")


def build_run_metadata(config: Mapping[str, Any], repository_root: os.PathLike[str] | str) -> Dict[str, Any]:
    """Collect reproducibility metadata only for an explicitly enabled profiler."""
    canonical_config = json.dumps(config, sort_keys=True, default=str, separators=(",", ":"))
    root = str(repository_root)

    def git(*args: str) -> str:
        result = subprocess.run(
            ["git", *args], cwd=root, check=True, capture_output=True, text=True,
        )
        return result.stdout.strip()

    metadata = {
        "config_sha256": hashlib.sha256(canonical_config.encode("utf-8")).hexdigest(),
        "git_commit": git("rev-parse", "HEAD"),
        "git_branch": git("branch", "--show-current"),
        "git_status_short": git("status", "--short", "--untracked-files=all").splitlines(),
        "torch_version": torch.__version__,
        "torch_cuda_version": torch.version.cuda,
    }
    return metadata


def read_jsonl(path: os.PathLike[str] | str) -> list[Dict[str, Any]]:
    records = []
    with open(path, "r", encoding="utf-8") as stream:
        for line in stream:
            if line.strip():
                record = json.loads(line)
                validate_record(record)
                records.append(record)
    return records


def tensor_storage_bytes(value: Any, seen: Optional[set[Tuple[str, int, int]]] = None) -> int:
    """Return unique tensor storage bytes without moving or cloning tensors."""
    if seen is None:
        seen = set()
    if isinstance(value, torch.Tensor):
        storage = value.untyped_storage()
        key = (value.device.type, value.device.index or -1, storage.data_ptr())
        if key in seen:
            return 0
        seen.add(key)
        return int(storage.nbytes())
    if isinstance(value, Mapping):
        return sum(tensor_storage_bytes(item, seen) for item in value.values())
    if isinstance(value, (list, tuple, set)):
        return sum(tensor_storage_bytes(item, seen) for item in value)
    return 0


def tensor_storage_breakdown(values: Mapping[str, Any]) -> Dict[str, int]:
    seen: set[Tuple[str, int, int]] = set()
    return {name: tensor_storage_bytes(value, seen) for name, value in values.items()}


def process_memory_bytes() -> Dict[str, Optional[int]]:
    result: Dict[str, Optional[int]] = {"rss_bytes": None, "hwm_bytes": None}
    try:
        with open("/proc/self/status", "r", encoding="utf-8") as stream:
            for line in stream:
                if line.startswith("VmRSS:"):
                    result["rss_bytes"] = int(line.split()[1]) * 1024
                elif line.startswith("VmHWM:"):
                    result["hwm_bytes"] = int(line.split()[1]) * 1024
    except (FileNotFoundError, OSError, ValueError, IndexError):
        pass
    return result


def keyframe_metadata_bytes(keyframes: Iterable[Mapping[str, Any]]) -> int:
    """Approximate Python-container bytes; tensor storage is intentionally excluded."""
    total = sys.getsizeof(keyframes)
    for keyframe in keyframes:
        total += sys.getsizeof(keyframe)
        total += sum(sys.getsizeof(key) for key in keyframe.keys())
    return total


class _NullProfiler:
    mode = "off"
    enabled = False
    detailed = False
    cuda_timing_available = False

    def should_sample(self, *args: Any, **kwargs: Any) -> bool:
        return False

    def cpu_start(self, *args: Any, **kwargs: Any) -> None:
        return None

    def cpu_stop(self, *args: Any, **kwargs: Any) -> None:
        return None

    def cuda_start(self, *args: Any, **kwargs: Any) -> None:
        return None

    def cuda_stop(self, *args: Any, **kwargs: Any) -> None:
        return None

    def record(self, *args: Any, **kwargs: Any) -> None:
        return None

    def record_archive(self, *args: Any, **kwargs: Any) -> None:
        return None

    def record_staging(self, *args: Any, **kwargs: Any) -> None:
        return None

    def record_tensor_bytes(self, *args: Any, **kwargs: Any) -> None:
        return None

    def sample_state(self, *args: Any, **kwargs: Any) -> None:
        return None

    def resolve_cuda_events(self, *args: Any, **kwargs: Any) -> None:
        return None

    def close(self, *args: Any, **kwargs: Any) -> None:
        return None

    @contextlib.contextmanager
    def cpu_span(self, *args: Any, **kwargs: Any):
        yield


NULL_PROFILER = _NullProfiler()


class PerformanceProfiler:
    def __init__(self, settings: ProfilingSettings, metadata: Optional[Mapping[str, Any]] = None):
        if settings.mode == "off":
            raise ValueError("Use create_profiler() for off mode")
        if not settings.run_id or not settings.output_dir:
            raise ValueError("Enabled profiling requires non-empty run_id and output_dir")
        self.settings = settings
        self.mode = settings.mode
        self.enabled = True
        self.detailed = settings.mode == "detailed"
        self.started = time.perf_counter()
        self.output_dir = Path(settings.output_dir) / settings.run_id
        if self.output_dir.exists():
            raise FileExistsError(f"Profiling output already exists: {self.output_dir}")
        self.output_dir.mkdir(parents=True, exist_ok=False)
        self.jsonl_path = self.output_dir / "telemetry.jsonl"
        self.summary_path = self.output_dir / "telemetry_summary.json"
        self.metadata_path = self.output_dir / "run_metadata.json"
        self._stream = open(self.jsonl_path, "x", encoding="utf-8")
        self._buffer: list[Dict[str, Any]] = []
        self._samples: Dict[str, list[float]] = defaultdict(list)
        self._counts: Dict[str, int] = defaultdict(int)
        self._totals: Dict[str, float] = defaultdict(float)
        self._peaks: Dict[str, float] = defaultdict(float)
        self._pending_cuda: list[Tuple[Any, Any, Dict[str, Any]]] = []
        self._cuda_batch_wall_start_ns: Optional[int] = None
        self._dropped_cuda_event_spans = 0
        self._archive_bytes = 0
        self._archive_count = 0
        self._staged_bytes = 0
        self._staging_events = 0
        self._closed = False
        self.cuda_timing_available = self.detailed and torch.cuda.is_available()
        run_metadata = {
            "schema_version": SCHEMA_VERSION,
            "run_id": settings.run_id,
            "profiling_mode": settings.mode,
            "sampling": {
                "cpu_timing_interval": settings.cpu_timing_interval,
                "memory_interval": settings.memory_interval,
                "cuda_event_interval": settings.cuda_event_interval,
                "cuda_resolve_interval": settings.cuda_resolve_interval,
                "flush_every": settings.flush_every,
                "max_buffered_records": settings.max_buffered_records,
                "max_pending_cuda_events": settings.max_pending_cuda_events,
                "max_summary_samples": settings.max_summary_samples,
            },
            "cuda_event_validation": "PENDING_P5_G3_CUDA_VALIDATION",
            "python": sys.version,
            "platform": platform.platform(),
            **dict(metadata or {}),
        }
        validate_run_metadata(run_metadata)
        self.metadata_path.write_text(json.dumps(run_metadata, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        atexit.register(self.close, "exception_or_process_exit")

    def __enter__(self):
        return self

    def __exit__(self, exception_type, exception, traceback) -> bool:
        self.close(status="failed" if exception_type is not None else "completed")
        return False

    def should_sample(self, frame_id: int, iteration_id: Optional[int] = None, category: str = "cpu") -> bool:
        intervals = {
            "cpu": self.settings.cpu_timing_interval,
            "memory": self.settings.memory_interval,
            "cuda": self.settings.cuda_event_interval,
        }
        interval = intervals[category]
        index = frame_id if iteration_id is None else iteration_id
        return index >= 0 and index % interval == 0

    def cpu_start(self, frame_id: int, iteration_id: Optional[int] = None) -> Optional[int]:
        if not self.should_sample(frame_id, iteration_id, "cpu"):
            return None
        return time.perf_counter_ns()

    def cpu_stop(
        self,
        token: Optional[int],
        component: str,
        frame_id: int,
        iteration_id: Optional[int] = None,
        metric_name: str = "wall_time",
    ) -> None:
        if token is None:
            return
        elapsed_ms = (time.perf_counter_ns() - token) / 1_000_000.0
        self.record(component, metric_name, elapsed_ms, "ms", frame_id, iteration_id)

    @contextlib.contextmanager
    def cpu_span(self, component: str, frame_id: int, iteration_id: Optional[int] = None):
        token = self.cpu_start(frame_id, iteration_id)
        try:
            yield
        finally:
            self.cpu_stop(token, component, frame_id, iteration_id)

    def cuda_start(self, component: str, frame_id: int, iteration_id: Optional[int] = None) -> Any:
        if not self.cuda_timing_available or not self.should_sample(frame_id, iteration_id, "cuda"):
            return None
        if len(self._pending_cuda) >= self.settings.max_pending_cuda_events:
            self._dropped_cuda_event_spans += 1
            return None
        if not self._pending_cuda and self._cuda_batch_wall_start_ns is None:
            self._cuda_batch_wall_start_ns = time.perf_counter_ns()
        start = torch.cuda.Event(enable_timing=True)
        end = torch.cuda.Event(enable_timing=True)
        start.record()
        return start, end, {
            "component": component,
            "frame_id": frame_id,
            "iteration_id": iteration_id,
        }

    def cuda_stop(self, token: Any) -> None:
        if token is None:
            return
        start, end, context = token
        end.record()
        self._pending_cuda.append((start, end, context))

    def resolve_cuda_events(self, frame_id: int, force: bool = False) -> None:
        if not self._pending_cuda:
            return
        if not force and frame_id % self.settings.cuda_resolve_interval != 0:
            return
        sync_start = time.perf_counter_ns()
        torch.cuda.synchronize()
        sync_ms = (time.perf_counter_ns() - sync_start) / 1_000_000.0
        self.record("profiler", "cuda_batch_synchronize", sync_ms, "ms", frame_id)
        if self._cuda_batch_wall_start_ns is not None:
            batch_wall_ms = (time.perf_counter_ns() - self._cuda_batch_wall_start_ns) / 1_000_000.0
            self.record("profiler", "cuda_batch_end_to_end_wall", batch_wall_ms, "ms", frame_id)
            self._cuda_batch_wall_start_ns = None
        pending, self._pending_cuda = self._pending_cuda, []
        for start, end, context in pending:
            self.record(
                context["component"],
                "gpu_elapsed",
                float(start.elapsed_time(end)),
                "ms",
                context["frame_id"],
                context["iteration_id"],
            )

    def record(
        self,
        component: str,
        metric_name: str,
        value: int | float,
        unit: str,
        frame_id: Optional[int] = None,
        iteration_id: Optional[int] = None,
    ) -> None:
        record = {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.settings.run_id,
            "frame_id": frame_id,
            "iteration_id": iteration_id,
            "component": component,
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "measurement_mode": self.mode,
            "timestamp_relative_s": time.perf_counter() - self.started,
        }
        validate_record(record)
        key = f"{component}.{metric_name}.{unit}"
        self._counts[key] += 1
        self._totals[key] += float(value)
        samples = self._samples[key]
        if len(samples) < self.settings.max_summary_samples:
            samples.append(float(value))
        else:
            replacement_index = (self._counts[key] - 1) % self.settings.max_summary_samples
            samples[replacement_index] = float(value)
        self._peaks[key] = max(self._peaks[key], float(value))
        self._buffer.append(record)
        if len(self._buffer) >= min(self.settings.flush_every, self.settings.max_buffered_records):
            self.flush()

    def flush(self) -> None:
        for record in self._buffer:
            self._stream.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")
        self._stream.flush()
        self._buffer.clear()

    def record_archive(self, keyframe: Mapping[str, Any], frame_id: int) -> None:
        payload = {name: keyframe[name] for name in ("color", "depth", "semantic_id", "semantic_color") if name in keyframe}
        field_bytes = tensor_storage_breakdown(payload)
        event_bytes = sum(field_bytes.values())
        self._archive_bytes += event_bytes
        self._archive_count += 1
        self.record("keyframe_archive", "payload_bytes", event_bytes, "bytes", frame_id)
        self.record("keyframe_archive", "logical_bytes", self._archive_bytes, "bytes", frame_id)
        self.record("keyframe_archive", "keyframe_count", self._archive_count, "count", frame_id)
        if self.detailed:
            for field, value in field_bytes.items():
                self.record("keyframe_archive", f"{field}_bytes", value, "bytes", frame_id)

    def record_staging(self, payload: Mapping[str, Any], frame_id: int, iteration_id: int) -> None:
        event_bytes = tensor_storage_bytes(payload)
        self._staged_bytes += event_bytes
        self._staging_events += 1
        if self.detailed and self.should_sample(frame_id, iteration_id, "cuda"):
            self.record("h2d_staging", "event_bytes", event_bytes, "bytes", frame_id, iteration_id)

    def record_tensor_bytes(
        self,
        component: str,
        metric_name: str,
        values: Any,
        frame_id: int,
        iteration_id: int,
    ) -> None:
        if self.detailed and self.should_sample(frame_id, iteration_id, "cuda"):
            self.record(component, metric_name, tensor_storage_bytes(values), "bytes", frame_id, iteration_id)

    def sample_state(
        self,
        frame_id: int,
        params: Mapping[str, Any],
        variables: Mapping[str, Any],
        keyframes: Iterable[Mapping[str, Any]],
        optimizer: Any = None,
    ) -> None:
        if not self.should_sample(frame_id, category="memory"):
            return
        self.record("state", "gaussian_count", int(params["means3D"].shape[0]), "count", frame_id)
        self.record("state", "keyframe_count", len(keyframes), "count", frame_id)
        self.record("keyframe_archive", "logical_bytes", self._archive_bytes, "bytes", frame_id)
        self.record("h2d_staging", "cumulative_bytes", self._staged_bytes, "bytes", frame_id)
        self.record("h2d_staging", "event_count", self._staging_events, "count", frame_id)
        self.record("keyframe_archive", "metadata_estimate", keyframe_metadata_bytes(keyframes), "bytes", frame_id)
        cpu_memory = process_memory_bytes()
        for name, value in cpu_memory.items():
            if value is not None:
                self.record("process", name, value, "bytes", frame_id)
        if torch.cuda.is_available():
            self.record("cuda_allocator", "allocated", torch.cuda.memory_allocated(), "bytes", frame_id)
            self.record("cuda_allocator", "reserved", torch.cuda.memory_reserved(), "bytes", frame_id)
            self.record("cuda_allocator", "peak_allocated", torch.cuda.max_memory_allocated(), "bytes", frame_id)
            self.record("cuda_allocator", "peak_reserved", torch.cuda.max_memory_reserved(), "bytes", frame_id)
        if not self.detailed:
            return
        parameter_fields = {name: value for name, value in params.items() if name not in {"cam_unnorm_rots", "cam_trans"}}
        semantic_fields = {name: parameter_fields.pop(name) for name in ("semantic_ids", "semantic_colors") if name in parameter_fields}
        gradients = {name: value.grad for name, value in params.items() if isinstance(value, torch.Tensor) and value.grad is not None}
        optimizer_state = optimizer.state if optimizer is not None else {}
        keyframe_gpu_payload = {
            f"{index}.{field}": keyframe[field]
            for index, keyframe in enumerate(keyframes)
            for field in ("color", "depth", "semantic_id", "semantic_color")
            if field in keyframe and isinstance(keyframe[field], torch.Tensor)
            and keyframe[field].device.type == "cuda"
        }
        categories = {
            "gaussian_parameters": parameter_fields,
            "semantic_attributes": semantic_fields,
            "gradients": gradients,
            "optimizer_state": optimizer_state,
            "auxiliary_tensors": variables,
            "keyframe_pose": [keyframe.get("est_w2c") for keyframe in keyframes],
            "keyframe_payload_gpu": keyframe_gpu_payload,
        }
        seen: set[Tuple[str, int, int]] = set()
        known_storage_bytes = 0
        for name, values in categories.items():
            category_bytes = tensor_storage_bytes(values, seen)
            known_storage_bytes += category_bytes
            self.record("state", f"{name}_bytes", category_bytes, "bytes", frame_id)
        if torch.cuda.is_available():
            unattributed = max(0, int(torch.cuda.memory_allocated()) - known_storage_bytes)
            self.record("state", "unattributed_allocator_bound_bytes", unattributed, "bytes", frame_id)

    def _summary(self, status: str) -> Dict[str, Any]:
        aggregates = {}
        for key, values in self._samples.items():
            ordered = sorted(values)
            count = len(ordered)
            observed_count = self._counts[key]
            def percentile(q: float) -> float:
                return ordered[min(count - 1, int(math.ceil(q * count) - 1))]
            aggregates[key] = {
                "observed_sample_count": observed_count,
                "percentile_sample_count": count,
                "total": self._totals[key],
                "mean": self._totals[key] / observed_count,
                "p50": percentile(0.50),
                "p90": percentile(0.90),
                "p95": percentile(0.95),
                "p99": percentile(0.99),
                "peak": max(ordered),
            }
        return {
            "schema_version": SCHEMA_VERSION,
            "run_id": self.settings.run_id,
            "profiling_mode": self.mode,
            "status": status,
            "wall_time_seconds": time.perf_counter() - self.started,
            "aggregate_metrics": aggregates,
            "archive": {"keyframe_count": self._archive_count, "logical_bytes": self._archive_bytes},
            "staging": {"event_count": self._staging_events, "cumulative_bytes": self._staged_bytes},
            "pending_cuda_events_at_close": len(self._pending_cuda),
            "dropped_cuda_event_spans": self._dropped_cuda_event_spans,
            "cuda_event_validation": "PENDING_P5_G3_CUDA_VALIDATION",
        }

    def close(self, status: str = "completed") -> None:
        if self._closed:
            return
        try:
            self.resolve_cuda_events(frame_id=0, force=True)
            self.flush()
            summary = self._summary(status)
            validate_summary(summary)
            self.summary_path.write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        finally:
            self._stream.close()
            self._closed = True
            try:
                atexit.unregister(self.close)
            except Exception:
                pass


def create_profiler(config: Optional[Mapping[str, Any]], metadata: Optional[Mapping[str, Any]] = None):
    settings = ProfilingSettings.from_config(config)
    if settings.mode == "off":
        return NULL_PROFILER
    return PerformanceProfiler(settings, metadata=metadata)
