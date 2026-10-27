"""CPU-only Gate 3 BCGM-cap and Gate 2 NVML parser regressions."""

import copy
import tempfile
import unittest
from pathlib import Path

import torch

from tools.phase7.nvml_telemetry import parse_nvml_csv
from utils.bcgm import BCGMBudget, select_bounded_candidates


ROOT = Path(__file__).resolve().parents[1]
EVENT_CAP = 9000
GLOBAL_CAP = 4500000


class NvmlParserTests(unittest.TestCase):
    def parse_text(self, text):
        with tempfile.NamedTemporaryFile(mode="w", newline="", encoding="utf-8") as f:
            f.write(text)
            f.flush()
            return parse_nvml_csv(f.name, expected_gpu_index=0)

    def test_representative_valid_error_and_malformed_rows(self):
        summary = self.parse_text(
            "utc,gpu_index,memory_used_mib,utilization_gpu_percent\n"
            "2026-10-27T03:39:03.067451+00:00,0,818,0\n"
            "2026-10-27T04:16:03.322036+00:00,0,4877,98\n"
            "2026-10-27T04:16:04+00:00,NVML_ERROR\n"
            "bad-row\n"
            "2026-10-27T04:16:05+00:00,1,4000,25\n")
        self.assertEqual(summary["valid_samples"], 2)
        self.assertEqual(summary["invalid_samples"], 2)
        self.assertEqual(summary["error_rows"], 1)
        self.assertEqual(summary["peak_device_used_mib"], 4877)
        self.assertEqual(summary["peak_timestamp_utc"], "2026-10-27T04:16:03.322036+00:00")
        self.assertEqual(summary["maximum_sampled_gpu_utilization_percent"], 98)

    def test_actual_gate2_csv_recovered_values(self):
        path = ROOT / "results/runtime_artifacts/phase7_gate2/" \
               "p7_bcgm_g2_room0_on_0_499_r01/nvml_samples.csv"
        summary = parse_nvml_csv(path, expected_gpu_index=0)
        self.assertEqual(summary["valid_samples"], 2334)
        self.assertEqual(summary["invalid_samples"], 0)
        self.assertEqual(summary["error_rows"], 0)
        self.assertEqual(summary["peak_device_used_mib"], 4877)
        self.assertEqual(summary["peak_timestamp_utc"], "2026-10-27T04:16:03.322036+00:00")
        self.assertEqual(summary["maximum_sampled_gpu_utilization_percent"], 98)


class GlobalCapAdmissionTests(unittest.TestCase):
    def select(self, candidate_count, current, event_cap=EVENT_CAP, global_cap=GLOBAL_CAP):
        mask = torch.ones(candidate_count, dtype=torch.bool)
        priority = torch.zeros(candidate_count, dtype=torch.bool)
        depth_error = torch.arange(candidate_count, dtype=torch.float32)
        silhouette = torch.zeros(candidate_count, dtype=torch.float32)
        return select_bounded_candidates(
            mask, priority, depth_error, silhouette, current,
            BCGMBudget(event_cap, global_cap))

    def test_below_global_limit_admits_all_when_within_event_cap(self):
        mask, record = self.select(3, GLOBAL_CAP - 10)
        self.assertEqual(int(mask.sum()), 3)
        self.assertEqual(record["admitted"], min(3, EVENT_CAP, 10))
        self.assertFalse(record["global_saturated"])
        self.assertFalse(record["event_saturated"])

    def test_at_global_limit_admits_zero_without_negative_count(self):
        mask, record = self.select(5, GLOBAL_CAP)
        self.assertEqual(int(mask.sum()), 0)
        self.assertEqual(record["admitted"], 0)
        self.assertGreaterEqual(record["admitted"], 0)
        self.assertEqual(record["reason"], "global_cap_reached")
        self.assertTrue(record["global_saturated"])
        self.assertFalse(record["event_saturated"])

    def test_current_count_above_limit_fails_closed(self):
        with self.assertRaisesRegex(ValueError, "already exceeds"):
            self.select(1, GLOBAL_CAP + 1)

    def test_candidates_exceeding_remaining_global_capacity(self):
        mask, record = self.select(20, GLOBAL_CAP - 7)
        self.assertEqual(record["admitted"], 7)
        self.assertEqual(record["rejected"], 13)
        self.assertEqual(int(mask.sum()), 7)
        self.assertTrue(record["global_saturated"])
        self.assertFalse(record["event_saturated"])

    def test_event_and_global_caps_tie_and_both_saturate(self):
        mask, record = self.select(12000, GLOBAL_CAP - EVENT_CAP)
        self.assertEqual(int(mask.sum()), EVENT_CAP)
        self.assertEqual(record["admitted"], min(12000, EVENT_CAP, EVENT_CAP))
        self.assertTrue(record["event_saturated"])
        self.assertTrue(record["global_saturated"])

    def test_event_cap_alone_binds(self):
        mask, record = self.select(EVENT_CAP + 5, 0)
        self.assertEqual(int(mask.sum()), EVENT_CAP)
        self.assertTrue(record["event_saturated"])
        self.assertFalse(record["global_saturated"])

    def test_zero_candidates_and_zero_remaining_capacity(self):
        mask, record = self.select(0, GLOBAL_CAP - 1)
        self.assertEqual(int(mask.sum()), 0)
        self.assertEqual(record["reason"], "no_valid_candidates")
        self.assertFalse(record["global_saturated"])
        mask, record = self.select(3, GLOBAL_CAP)
        self.assertEqual(int(mask.sum()), 0)
        self.assertEqual(record["admitted"], 0)
        self.assertGreaterEqual(record["admitted"], 0)

    def test_deterministic_ranking_and_aligned_payload_selection(self):
        mask = torch.tensor([True, True, True, True, False])
        priority = torch.tensor([False, True, True, False, False])
        depth_error = torch.tensor([99.0, 4.0, 4.0, 3.0, 100.0])
        silhouette = torch.tensor([0.0, 0.0, 0.0, 0.2, 0.0])
        payloads = {
            "rgb": torch.arange(15).reshape(5, 3),
            "depth": torch.arange(5).reshape(5, 1) + 20,
            "semantic_id": torch.arange(5).reshape(5, 1) + 30,
            "semantic_color": torch.arange(15).reshape(5, 3) + 40,
        }
        budget = BCGMBudget(2, GLOBAL_CAP)
        outputs = []
        for _ in range(3):
            selected, _ = select_bounded_candidates(
                mask, priority, depth_error, silhouette, 0, budget)
            ids = selected.nonzero().flatten()
            outputs.append(ids.tolist())
            selected_payloads = {name: tensor[ids] for name, tensor in payloads.items()}
            self.assertEqual(selected_payloads["rgb"][:, 0].tolist(), [3, 6])
            self.assertEqual(selected_payloads["depth"][:, 0].tolist(), [21, 22])
            self.assertEqual(selected_payloads["semantic_id"][:, 0].tolist(), [31, 32])
            self.assertEqual(selected_payloads["semantic_color"][:, 0].tolist(), [43, 46])
        self.assertEqual(outputs, [[1, 2], [1, 2], [1, 2]])


class Gate3ConfigContractTests(unittest.TestCase):
    def test_only_frame_count_and_run_identity_change_from_gate2(self):
        import runpy
        gate2 = runpy.run_path(str(ROOT / "configs/replica/phase7_gate2_room0_on_0_499_r01.py"))["config"]
        gate3 = runpy.run_path(str(ROOT / "configs/replica/phase7_gate3_room0_on_0_1999_r01.py"))["config"]
        expected = copy.deepcopy(gate2)
        expected["run_name"] = "p7_bcgm_g3_room0_on_0_1999_r01"
        expected["data"]["end"] = 2000
        expected["data"]["num_frames"] = 2000
        self.assertEqual(gate3, expected)
        self.assertEqual(gate3["data"]["start"], 0)
        self.assertEqual(gate3["data"]["stride"], 1)
        self.assertEqual(gate3["bcgm"], {
            "enabled": True, "max_new_gaussians_per_event": EVENT_CAP,
            "max_gaussians": GLOBAL_CAP})
        self.assertFalse(gate3["mapping"]["use_gaussian_splatting_densification"])


if __name__ == "__main__":
    unittest.main()
