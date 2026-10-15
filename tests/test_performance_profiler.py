import copy
import hashlib
import json
import random
import tempfile
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

import numpy as np
import torch

from utils.performance_profiler import (
    NULL_PROFILER,
    PerformanceProfiler,
    ProfilingSettings,
    SCHEMA_VERSION,
    build_run_metadata,
    create_profiler,
    keyframe_metadata_bytes,
    process_memory_bytes,
    read_jsonl,
    tensor_storage_breakdown,
    tensor_storage_bytes,
    validate_record,
    validate_run_metadata,
    validate_summary,
)


class PerformanceProfilerTests(unittest.TestCase):
    def settings(self, root, mode="light", **overrides):
        values = {
            "mode": mode,
            "run_id": "unit-run",
            "output_dir": root,
            "flush_every": 2,
            "max_buffered_records": 3,
            "max_pending_cuda_events": 2,
            "max_summary_samples": 3,
        }
        values.update(overrides)
        return ProfilingSettings.from_config(values)

    def test_01_missing_section_is_disabled_noop_without_cuda_probe(self):
        with mock.patch("torch.cuda.is_available", side_effect=AssertionError("CUDA probe")):
            profiler = create_profiler(None)
        self.assertIs(profiler, NULL_PROFILER)
        self.assertIsNone(profiler.cpu_start(0))
        self.assertFalse(profiler.should_sample(0))

    def test_02_off_mode_creates_no_output(self):
        with tempfile.TemporaryDirectory() as root:
            profiler = create_profiler({"mode": "off", "output_dir": root, "run_id": "off"})
            profiler.record("x", "y", 1, "count", 0)
            profiler.close()
            self.assertEqual(list(Path(root).iterdir()), [])

    def test_03_valid_and_invalid_mode_parsing(self):
        self.assertEqual(ProfilingSettings.from_config({"mode": "LIGHT"}).mode, "light")
        self.assertEqual(ProfilingSettings.from_config({"mode": "detailed"}).mode, "detailed")
        with self.assertRaises(ValueError):
            ProfilingSettings.from_config({"mode": "turbo"})
        with self.assertRaises(ValueError):
            ProfilingSettings.from_config({"mode": "light", "memory_interval": 0})

    def test_04_schema_validation(self):
        record = {
            "schema_version": SCHEMA_VERSION,
            "run_id": "r",
            "frame_id": 1,
            "iteration_id": None,
            "component": "tracking",
            "metric_name": "wall_time",
            "value": 1.0,
            "unit": "ms",
            "measurement_mode": "light",
            "timestamp_relative_s": 0.1,
        }
        validate_record(record)
        broken = dict(record)
        broken.pop("unit")
        with self.assertRaises(ValueError):
            validate_record(broken)

    def test_05_jsonl_write_read_and_summary(self):
        with tempfile.TemporaryDirectory() as root, mock.patch("torch.cuda.is_available", return_value=False):
            profiler = PerformanceProfiler(self.settings(root), metadata={"commit": "abc"})
            profiler.record("tracking", "wall_time", 2.0, "ms", 0)
            profiler.record("tracking", "wall_time", 4.0, "ms", 1)
            profiler.close()
            records = read_jsonl(profiler.jsonl_path)
            self.assertEqual(len(records), 2)
            summary = json.loads(profiler.summary_path.read_text())
            aggregate = summary["aggregate_metrics"]["tracking.wall_time.ms"]
            self.assertEqual(aggregate["observed_sample_count"], 2)
            self.assertEqual(aggregate["mean"], 3.0)

    def test_06_deterministic_sampling_schedule(self):
        with tempfile.TemporaryDirectory() as root, mock.patch("torch.cuda.is_available", return_value=False):
            profiler = PerformanceProfiler(self.settings(root, cpu_timing_interval=3))
            self.assertEqual([profiler.should_sample(i) for i in range(7)], [True, False, False, True, False, False, True])
            profiler.close()

    def test_07_tensor_storage_deduplication(self):
        tensor = torch.arange(16, dtype=torch.float32)
        view = tensor.view(4, 4)
        expected = tensor.untyped_storage().nbytes()
        self.assertEqual(tensor_storage_bytes([tensor, view]), expected)
        breakdown = tensor_storage_breakdown({"tensor": tensor, "view": view})
        self.assertEqual(sum(breakdown.values()), expected)

    def test_08_profiler_does_not_change_rng_states(self):
        random.seed(3)
        np.random.seed(3)
        torch.manual_seed(3)
        py_state = random.getstate()
        np_state = np.random.get_state()
        torch_state = torch.random.get_rng_state().clone()
        with tempfile.TemporaryDirectory() as root, mock.patch("torch.cuda.is_available", return_value=False):
            profiler = PerformanceProfiler(self.settings(root))
            profiler.should_sample(12, 6)
            profiler.record("state", "count", 1, "count", 0)
            profiler.close()
        self.assertEqual(py_state, random.getstate())
        self.assertTrue(np.array_equal(np_state[1], np.random.get_state()[1]))
        self.assertTrue(torch.equal(torch_state, torch.random.get_rng_state()))

    def test_09_input_config_is_not_mutated(self):
        config = {"mode": "light", "run_id": "r", "output_dir": "/tmp/x", "memory_interval": 7}
        before = copy.deepcopy(config)
        ProfilingSettings.from_config(config)
        self.assertEqual(config, before)

    def test_10_run_metadata_integrity_and_pending_gpu_label(self):
        with tempfile.TemporaryDirectory() as root, mock.patch("torch.cuda.is_available", return_value=False):
            profiler = PerformanceProfiler(self.settings(root, mode="detailed"), metadata={"seed": 0})
            metadata = json.loads(profiler.metadata_path.read_text())
            self.assertEqual(metadata["seed"], 0)
            self.assertEqual(metadata["cuda_event_validation"], "PENDING_P5_G3_CUDA_VALIDATION")
            self.assertFalse(profiler.cuda_timing_available)
            profiler.close()

    def test_11_buffer_and_summary_samples_are_bounded(self):
        with tempfile.TemporaryDirectory() as root, mock.patch("torch.cuda.is_available", return_value=False):
            profiler = PerformanceProfiler(self.settings(root))
            for index in range(20):
                profiler.record("x", "value", index, "count", index)
                self.assertLessEqual(len(profiler._buffer), profiler.settings.max_buffered_records)
            self.assertEqual(len(profiler._samples["x.value.count"]), 3)
            profiler.close()

    def test_12_context_cleanup_after_exception(self):
        with tempfile.TemporaryDirectory() as root, mock.patch("torch.cuda.is_available", return_value=False):
            profiler = PerformanceProfiler(self.settings(root))
            with self.assertRaisesRegex(RuntimeError, "synthetic"):
                with profiler:
                    with profiler.cpu_span("work", 0):
                        raise RuntimeError("synthetic")
            self.assertTrue(profiler._closed)
            summary = json.loads(profiler.summary_path.read_text())
            self.assertEqual(summary["status"], "failed")

    def test_13_existing_output_is_never_overwritten(self):
        with tempfile.TemporaryDirectory() as root, mock.patch("torch.cuda.is_available", return_value=False):
            Path(root, "unit-run").mkdir()
            with self.assertRaises(FileExistsError):
                PerformanceProfiler(self.settings(root))

    def test_14_archive_staging_and_cpu_memory_counters(self):
        with tempfile.TemporaryDirectory() as root, mock.patch("torch.cuda.is_available", return_value=False):
            profiler = PerformanceProfiler(self.settings(root, mode="detailed", memory_interval=1))
            keyframe = {"id": 0, "color": torch.zeros(3, 2, 2), "depth": torch.zeros(1, 2, 2), "est_w2c": torch.eye(4)}
            profiler.record_archive(keyframe, 0)
            profiler.record_staging({"color": keyframe["color"], "depth": keyframe["depth"]}, 0, 0)
            profiler.sample_state(0, {"means3D": torch.zeros(2, 3)}, {}, [keyframe])
            profiler.close()
            summary = json.loads(profiler.summary_path.read_text())
            self.assertEqual(summary["archive"]["keyframe_count"], 1)
            self.assertEqual(summary["staging"]["event_count"], 1)
            self.assertGreater(keyframe_metadata_bytes([keyframe]), 0)
            self.assertIsNotNone(process_memory_bytes()["rss_bytes"])

    def test_15_phase4_algorithm_configs_are_unchanged(self):
        root = Path(__file__).resolve().parents[1]
        expected = {
            "configs/replica/slam.py": "08cc1aef22d70fa3ab390339afdf2cb7a77e34be04a2b08ac3b1353dcbea19b3",
            "utils/keyframe_selection.py": "1dc1711b017884a3f04b8932e2bfd78fbb72704d48bea7f5d6e86bf81679ef87",
        }
        for relative, digest in expected.items():
            actual = hashlib.sha256((root / relative).read_bytes()).hexdigest()
            self.assertEqual(actual, digest)

    def test_16_cuda_is_not_initialized_by_cpu_test_path(self):
        self.assertFalse(torch.cuda.is_initialized())

    def test_17_summary_schema_validation(self):
        summary = {
            "schema_version": SCHEMA_VERSION,
            "run_id": "r",
            "profiling_mode": "light",
            "status": "completed",
            "wall_time_seconds": 1.0,
            "aggregate_metrics": {},
            "archive": {},
            "staging": {},
            "cuda_event_validation": "PENDING_P5_G3_CUDA_VALIDATION",
        }
        validate_summary(summary)
        summary.pop("archive")
        with self.assertRaises(ValueError):
            validate_summary(summary)

    def test_18_run_metadata_schema_validation(self):
        metadata = {
            "schema_version": SCHEMA_VERSION,
            "run_id": "r",
            "profiling_mode": "detailed",
            "sampling": {},
            "cuda_event_validation": "PENDING_P5_G3_CUDA_VALIDATION",
            "python": "test",
            "platform": "test",
        }
        validate_run_metadata(metadata)
        metadata["profiling_mode"] = "off"
        with self.assertRaises(ValueError):
            validate_run_metadata(metadata)

    def test_19_profile_wrapper_preserves_base_hyperparameters(self):
        root = Path(__file__).resolve().parents[1]
        base = SourceFileLoader("test_phase5_base", str(root / "configs/replica/slam.py")).load_module()
        profile = SourceFileLoader("test_phase5_profile", str(root / "configs/replica/phase5_profile.py")).load_module()
        profile_config = copy.deepcopy(profile.config)
        profiling = profile_config.pop("profiling")
        self.assertEqual(profile_config, base.config)
        self.assertEqual(profiling["mode"], "off")

    def test_20_reproducibility_metadata_has_git_and_config_identity(self):
        root = Path(__file__).resolve().parents[1]
        config = {"seed": 0, "profiling": {"mode": "light"}}
        metadata = build_run_metadata(config, root)
        self.assertEqual(len(metadata["config_sha256"]), 64)
        self.assertTrue(metadata["git_commit"])
        self.assertEqual(config, {"seed": 0, "profiling": {"mode": "light"}})


if __name__ == "__main__":
    unittest.main()
