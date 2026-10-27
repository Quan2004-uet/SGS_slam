"""CPU checks against the actual and frozen Phase 4 insertion functions."""

import ast
import copy
import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import torch

from utils.bcgm import (BCGMBudget, parse_bcgm_config,
                        select_bounded_candidates, validate_bcgm_config)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "scripts" / "slam.py"


def load_functions(source_text):
    wanted = {"get_pointcloud", "initialize_new_params", "add_new_gaussians"}
    nodes = [node for node in ast.parse(source_text).body
             if isinstance(node, ast.FunctionDef) and node.name in wanted]
    namespace = {"torch": torch, "np": np, "json": json,
                 "build_rotation": lambda rotation: torch.eye(3).unsqueeze(0),
                 "transform_to_frame": lambda params, *_args, **_kwargs: params["means3D"],
                 "transformed_params2depthplussilhouette": lambda *_args, **_kwargs: {},
                 "select_bounded_candidates": select_bounded_candidates}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), "exec"), namespace)
    return namespace


class FakeRenderer:
    def __init__(self, raster_settings):
        pass

    def __call__(self, **_kwargs):
        rendered = torch.ones((2, 2, 3), dtype=torch.float32)
        rendered[0] = 2.0
        rendered[1] = torch.tensor([[0.1, 0.1, 0.9], [0.1, 0.1, 0.9]])
        return rendered, None, None


def scene_inputs():
    params = {
        "means3D": torch.nn.Parameter(torch.tensor([[0.0, 0.0, 1.0]])),
        "rgb_colors": torch.nn.Parameter(torch.tensor([[0.0, 0.0, 0.0]])),
        "unnorm_rotations": torch.nn.Parameter(torch.tensor([[1.0, 0.0, 0.0, 0.0]])),
        "logit_opacities": torch.nn.Parameter(torch.zeros(1, 1)),
        "log_scales": torch.nn.Parameter(torch.zeros(1, 1)),
        "semantic_ids": torch.tensor([0.0]),
        "semantic_colors": torch.nn.Parameter(torch.zeros(1, 3)),
        "cam_unnorm_rots": torch.nn.Parameter(torch.tensor([[[1.0, 1.0], [0.0, 0.0],
                                                              [0.0, 0.0], [0.0, 0.0]]])),
        "cam_trans": torch.nn.Parameter(torch.zeros(1, 3, 2)),
    }
    variables = {name: torch.zeros(1) for name in
                 ("means2D_gradient_accum", "denom", "max_2D_radius", "timestep")}
    pixel_ids = torch.arange(6, dtype=torch.float32).reshape(2, 3)
    data = {"cam": None, "w2c": torch.eye(4), "intrinsics": torch.eye(3),
            "im": torch.stack((pixel_ids, pixel_ids + 10, pixel_ids + 20)),
            "depth": torch.tensor([[[1.0, 1.0, 1.0], [1.0, 0.0, 1.0]]]),
            "semantic_id": pixel_ids.unsqueeze(0),
            "semantic_color": torch.stack((pixel_ids + 30, pixel_ids + 40, pixel_ids + 50))}
    return params, variables, data


class BCGMPolicyTests(unittest.TestCase):
    def test_config_validation(self):
        self.assertIsNone(parse_bcgm_config(None))
        self.assertIsNone(parse_bcgm_config({"enabled": False}))
        self.assertEqual(parse_bcgm_config({"enabled": True,
                                            "max_new_gaussians_per_event": 0,
                                            "max_gaussians": 10}), BCGMBudget(0, 10))
        for invalid in ({"enabled": True}, {"enabled": 1},
                        {"enabled": True, "max_new_gaussians_per_event": -1, "max_gaussians": 10},
                        {"enabled": True, "max_new_gaussians_per_event": True, "max_gaussians": 10},
                        {"enabled": False, "max_gaussians": "10"},
                        {"enabled": True, "max_new_gaussians_per_event": 1,
                         "max_gaussians": 10, "unexpected": 2}):
            with self.subTest(config=invalid), self.assertRaises(ValueError):
                parse_bcgm_config(invalid)

    def test_gradient_densification_is_rejected_when_bounded(self):
        config = {"bcgm": {"enabled": True, "max_new_gaussians_per_event": 1,
                            "max_gaussians": 10},
                  "mapping": {"use_gaussian_splatting_densification": True}}
        with self.assertRaises(ValueError):
            validate_bcgm_config(config)
        config["bcgm"]["enabled"] = False
        self.assertIsNone(validate_bcgm_config(config))

    def test_event_and_global_arithmetic(self):
        mask = torch.tensor([True] * 4)
        priority = torch.zeros(4, dtype=torch.bool)
        scores = torch.ones(4)
        selected, record = select_bounded_candidates(mask, priority, scores, scores,
                                                      5, BCGMBudget(2, 100))
        self.assertEqual(selected.nonzero().flatten().tolist(), [0, 1])
        self.assertEqual((record["valid_candidates"], record["admitted"],
                          record["rejected"]), (4, 2, 2))
        self.assertTrue(record["event_saturated"])
        selected, record = select_bounded_candidates(mask, priority, scores, scores,
                                                      9, BCGMBudget(4, 10))
        self.assertEqual(selected.nonzero().flatten().tolist(), [0])
        self.assertTrue(record["global_saturated"])

    def test_deterministic_priority_and_ties(self):
        mask = torch.tensor([True] * 4)
        priority = torch.tensor([False, True, True, False])
        errors = torch.tensor([0.0, 2.0, 2.0, 0.0])
        silhouette = torch.zeros(4)
        for _ in range(3):
            selected, _ = select_bounded_candidates(mask, priority, errors, silhouette,
                                                    0, BCGMBudget(2, 10))
            self.assertEqual(selected.nonzero().flatten().tolist(), [1, 2])
        selected, _ = select_bounded_candidates(mask, priority, errors, silhouette,
                                                0, BCGMBudget(1, 10))
        self.assertEqual(selected.nonzero().flatten().tolist(), [1])

    def test_zero_budget_and_over_cap(self):
        mask = torch.tensor([True, True])
        priority = torch.zeros(2, dtype=torch.bool)
        scores = torch.ones(2)
        selected, record = select_bounded_candidates(mask, priority, scores, scores,
                                                      2, BCGMBudget(0, 5))
        self.assertFalse(selected.any())
        self.assertEqual(record["reason"], "event_cap_zero")
        selected, record = select_bounded_candidates(mask, priority, scores, scores,
                                                      5, BCGMBudget(2, 5))
        self.assertFalse(selected.any())
        self.assertEqual(record["reason"], "global_cap_reached")
        with self.assertRaises(ValueError):
            select_bounded_candidates(mask, priority, scores, scores, 6, BCGMBudget(2, 5))


class InsertionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        baseline = subprocess.check_output(
            ["git", "show", "68f9060f7ff4d8d141be1d5f71339401327edd06:scripts/slam.py"],
            cwd=ROOT, text=True)
        cls.old = load_functions(baseline)
        cls.new = load_functions(SOURCE.read_text())
        cls.old["Renderer"] = FakeRenderer
        cls.new["Renderer"] = FakeRenderer

    def test_early_projection_matches_frozen_and_fields_align(self):
        _, _, data = scene_inputs()
        mask = torch.tensor([True, False, True, True, False, False])
        args = (data["im"], data["depth"], data["intrinsics"], data["w2c"])
        kwargs = {"mask": mask, "compute_mean_sq_dist": True, "device": "cpu",
                  "load_semantics": True, "semantic_id": data["semantic_id"],
                  "semantic_color": data["semantic_color"]}
        old_cloud, old_scale = self.old["get_pointcloud"](*args, **kwargs)
        new_cloud, new_scale = self.new["get_pointcloud"](
            *args, **kwargs, select_before_allocation=True)
        self.assertTrue(torch.equal(old_cloud, new_cloud))
        self.assertTrue(torch.equal(old_scale, new_scale))
        self.assertEqual(new_cloud[:, 6].tolist(), [0.0, 2.0, 3.0])
        self.assertEqual(new_cloud[:, 3].tolist(), [0.0, 2.0, 3.0])

    def test_off_matches_frozen_params_and_schema(self):
        old_params, old_vars, old_data = scene_inputs()
        new_params, new_vars, new_data = scene_inputs()
        old_params, old_vars = self.old["add_new_gaussians"](
            old_params, {"semantic_ids"}, old_vars, old_data, 0.5, 1,
            "projective", device="cpu", load_semantics=True)
        new_params, new_vars = self.new["add_new_gaussians"](
            new_params, {"semantic_ids"}, new_vars, new_data, 0.5, 1,
            "projective", device="cpu", load_semantics=True, bcgm_budget=None)
        self.assertEqual(set(old_params), set(new_params))
        self.assertEqual(set(old_vars), set(new_vars))
        for name in old_params:
            self.assertTrue(torch.equal(old_params[name], new_params[name]), name)
        for name in old_vars:
            self.assertTrue(torch.equal(old_vars[name], new_vars[name]), name)
        self.assertEqual(new_params["means3D"].shape[0], 4)
        self.assertFalse(new_params["semantic_ids"].requires_grad)

    def test_bounded_append_schema_and_optimizer_isolation(self):
        params, variables, data = scene_inputs()
        optimizer = torch.optim.Adam([params["means3D"]], lr=0.01)
        params["means3D"].grad = torch.ones_like(params["means3D"])
        optimizer.step()
        state_before = copy.deepcopy(optimizer.state_dict())
        with patch("builtins.print") as log:
            params, variables = self.new["add_new_gaussians"](
                params, {"semantic_ids"}, variables, data, 0.5, 1,
                "projective", device="cpu", load_semantics=True,
                bcgm_budget=BCGMBudget(2, 3))
        self.assertEqual(params["means3D"].shape[0], 3)
        self.assertEqual(params["semantic_ids"].tolist()[1:], [0.0, 1.0])
        self.assertEqual(params["rgb_colors"][:, 0].tolist()[1:], [0.0, 1.0])
        self.assertEqual(params["semantic_colors"][:, 0].tolist()[1:], [30.0, 31.0])
        for name, tensor in params.items():
            if name not in ("cam_unnorm_rots", "cam_trans"):
                self.assertEqual(tensor.shape[0], 3, name)
        state_after = optimizer.state_dict()
        for key in state_before["state"]:
            for field in state_before["state"][key]:
                self.assertTrue(torch.equal(state_before["state"][key][field],
                                            state_after["state"][key][field]))
        record = json.loads(log.call_args.args[0].removeprefix("BCGM_INSERTION "))
        self.assertEqual((record["before"], record["after"], record["admitted"],
                          record["rejected"]), (1, 3, 2, 1))
        self.assertTrue(record["budget_saturated"])

    def test_no_capacity_skips_parameter_mutation(self):
        params, variables, data = scene_inputs()
        originals = {name: id(value) for name, value in params.items()}
        with patch("builtins.print") as log:
            updated, updated_vars = self.new["add_new_gaussians"](
                params, {"semantic_ids"}, variables, data, 0.5, 1,
                "projective", device="cpu", load_semantics=True,
                bcgm_budget=BCGMBudget(0, 1))
        self.assertIs(updated, params)
        self.assertIs(updated_vars, variables)
        self.assertEqual({name: id(value) for name, value in params.items()}, originals)
        record = json.loads(log.call_args.args[0].removeprefix("BCGM_INSERTION "))
        self.assertEqual(record["reason"], "global_cap_reached")
        self.assertEqual(record["after"], 1)


if __name__ == "__main__":
    unittest.main()
