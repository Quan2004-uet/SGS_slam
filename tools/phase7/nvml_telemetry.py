"""Strict, CPU-only parser for the Gate 2/3 nvidia-smi CSV samples."""

import csv
from datetime import datetime
from pathlib import Path


EXPECTED_HEADER = [
    "utc", "gpu_index", "memory_used_mib", "utilization_gpu_percent"
]


def parse_nvml_csv(path, expected_gpu_index=0):
    """Parse device samples, tracking malformed and collector-error rows apart.

    `invalid_samples` counts malformed records and valid-shaped records for a
    different GPU. `error_rows` counts the sampler's explicit NVML_ERROR rows.
    Peak selection is over the requested GPU only.
    """
    valid = []
    invalid = []
    error_rows = 0
    with Path(path).open(newline="", encoding="utf-8") as stream:
        rows = csv.reader(stream)
        header = next(rows, None)
        if header != EXPECTED_HEADER:
            raise ValueError(f"Unexpected NVML CSV header: {header!r}")
        for line_number, row in enumerate(rows, start=2):
            if len(row) == 2 and row[1].strip() == "NVML_ERROR":
                error_rows += 1
                continue
            try:
                if len(row) != 4:
                    raise ValueError("expected four columns")
                timestamp = datetime.fromisoformat(row[0].strip().replace("Z", "+00:00"))
                if timestamp.tzinfo is None:
                    raise ValueError("timestamp must include a timezone")
                gpu_index = int(row[1])
                memory_mib = int(row[2])
                utilization = int(row[3])
                if gpu_index < 0 or memory_mib < 0 or not 0 <= utilization <= 100:
                    raise ValueError("GPU index, memory, or utilization out of range")
                if gpu_index != expected_gpu_index:
                    raise ValueError(f"unexpected GPU index {gpu_index}")
                valid.append({
                    "timestamp_utc": timestamp.isoformat(),
                    "gpu_index": gpu_index,
                    "memory_used_mib": memory_mib,
                    "utilization_gpu_percent": utilization,
                })
            except (TypeError, ValueError, OverflowError) as exc:
                invalid.append({"line": line_number, "reason": str(exc), "row": row})

    peak = max(valid, key=lambda sample: sample["memory_used_mib"]) if valid else None
    return {
        "valid_samples": len(valid),
        "invalid_samples": len(invalid),
        "error_rows": error_rows,
        "expected_gpu_index": expected_gpu_index,
        "peak_device_used_mib": peak["memory_used_mib"] if peak else None,
        "peak_timestamp_utc": peak["timestamp_utc"] if peak else None,
        "peak_gpu_index": peak["gpu_index"] if peak else None,
        "maximum_sampled_gpu_utilization_percent": max(
            (sample["utilization_gpu_percent"] for sample in valid), default=None),
        "invalid_row_details": invalid,
    }
