import ast
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest

import numpy as np

from scripts.evaluate_saved_phase6 import (
    expected_eval_frame_ids,
    validate_evaluation_outputs,
    validate_evaluation_paths,
)
from utils.common_utils import validate_final_checkpoint


ROOT = Path(__file__).resolve().parents[1]


class P6Bam006PreparationTests(unittest.TestCase):
    def test_full_scene_wrapper_is_explicit_and_isolated(self):
        run_id = "p6_bam_006_room0_0_1999_va2_r01"
        old = os.environ.get("P6_BAM_RUN_ID")
        os.environ["P6_BAM_RUN_ID"] = run_id
        try:
            spec = importlib.util.spec_from_file_location(
                "p6_bam_006_full_wrapper",
                ROOT / "configs/replica/phase6_bam_va2_full_0_1999.py",
            )
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            config = module.config
        finally:
            if old is None:
                os.environ.pop("P6_BAM_RUN_ID", None)
            else:
                os.environ["P6_BAM_RUN_ID"] = old
        self.assertEqual((config["data"]["start"], config["data"]["end"], config["data"]["stride"], config["data"]["num_frames"]), (0, 2000, 1, 2000))
        self.assertEqual(config["seed"], 0)
        self.assertEqual(config["tracking"]["num_iters"], 40)
        self.assertEqual(config["mapping"]["num_iters"], 60)
        self.assertEqual(config["mapping"]["budget_control"]["budgets"], {"low": 45, "mid": 60, "full": 60})
        self.assertEqual(config["mapping"]["budget_control"]["fraction_thresholds"], {"low_max": 0.01, "mid_max": 0.05})
        self.assertEqual(config["profiling"]["mode"], "light")
        self.assertEqual(config["eval_every"], 5)
        self.assertTrue(config["save_checkpoints"])
        self.assertEqual(config["checkpoint_interval"], 1999)
        self.assertEqual(config["run_name"], run_id)
        self.assertEqual(config["data"]["load_semantics"], True)
        json.dumps(config)
        baseline = json.loads((ROOT / "results/runtime_artifacts/phase6_bam/p6_bam_005_comparison/va2_effective_config.json").read_text())
        expected_changes = {
            ("checkpoint_first_finalization",): (None, True),
            ("checkpoint_interval",): (499, 1999),
            ("data", "end"): (500, 2000),
            ("data", "num_frames"): (500, 2000),
            ("eval_every",): (50, 5),
            ("phase6_variant",): ("V-A2", "V-A2-FULL-0-1999"),
            ("profiling", "run_id"): (baseline["profiling"]["run_id"], run_id),
            ("run_name",): (baseline["run_name"], run_id),
        }
        baseline["use_wandb"] = config["use_wandb"]
        baseline["data"]["start"] = config["data"]["start"]
        baseline["data"]["stride"] = config["data"]["stride"]
        baseline["profiling"]["output_dir"] = config["profiling"]["output_dir"]

        def differences(left, right, path=()):
            if isinstance(left, dict) and isinstance(right, dict):
                result = {}
                for key in set(left) | set(right):
                    if key not in left or key not in right:
                        result[path + (key,)] = (left.get(key), right.get(key))
                    else:
                        result.update(differences(left[key], right[key], path + (key,)))
                return result
            return {} if left == right else {path: (left, right)}

        self.assertEqual(differences(baseline, config), expected_changes)

    def test_e4_sample_ids_are_exactly_401(self):
        ids = expected_eval_frame_ids()
        self.assertEqual(len(ids), 401)
        self.assertEqual(ids[:3], (0, 4, 9))
        self.assertEqual(ids[-3:], (1989, 1994, 1999))

    def test_saved_state_paths_are_phase6_only_and_non_overwriting(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp) / "phase6_bam"
            root.mkdir()
            run = root / "p6_bam_006_example"
            run.mkdir()
            checkpoint = run / "params.npz"
            checkpoint.write_bytes(b"checkpoint")
            evaluation = root / "p6_bam_006_comparison" / "evaluation" / "attempt01"
            checked, output = validate_evaluation_paths(checkpoint, evaluation, root)
            self.assertEqual(checked, checkpoint.resolve())
            self.assertEqual(output, evaluation.resolve())
            with self.assertRaises(ValueError):
                validate_evaluation_paths(checkpoint, Path(temp) / "phase4" / "eval", root)
            evaluation.mkdir(parents=True)
            with self.assertRaises(FileExistsError):
                validate_evaluation_paths(checkpoint, evaluation, root)

    def test_evaluation_output_schema_is_401_finite_and_frame_matched(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp)
            for filename in ("psnr.txt", "ssim.txt", "lpips.txt", "l1.txt", "rmse.txt", "miou.txt"):
                np.savetxt(output / filename, np.ones(401))
            for subdir in ("rendered_rgb", "rendered_depth", "rendered_seg"):
                (output / subdir).mkdir()
                for frame_id in expected_eval_frame_ids():
                    (output / subdir / f"gs_{frame_id:04d}.png").touch()
            self.assertTrue(validate_evaluation_outputs(output))

    def test_final_checkpoint_schema_and_corruption_validation(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "params.npz"
            n, frames = 3, 2
            np.savez(
                path,
                means3D=np.zeros((n, 3), dtype=np.float32),
                rgb_colors=np.zeros((n, 3), dtype=np.float32),
                unnorm_rotations=np.zeros((n, 4), dtype=np.float32),
                logit_opacities=np.zeros((n, 1), dtype=np.float32),
                log_scales=np.zeros((n, 1), dtype=np.float32),
                cam_unnorm_rots=np.zeros((1, 4, frames), dtype=np.float32),
                cam_trans=np.zeros((1, 3, frames), dtype=np.float32),
                intrinsics=np.eye(3, dtype=np.float32), w2c=np.eye(4, dtype=np.float32),
                gt_w2c_all_frames=np.zeros((frames, 4, 4), dtype=np.float32),
                keyframe_time_indices=np.array([1]), timestep=np.zeros(n, dtype=np.float32),
                org_width=np.array(1200), org_height=np.array(680),
                semantic_ids=np.zeros(n, dtype=np.uint8), semantic_colors=np.zeros((n, 3), dtype=np.float32),
            )
            (Path(temp) / "params.ply").write_bytes(b"ply")
            (Path(temp) / "seg_params.ply").write_bytes(b"ply")
            self.assertTrue(validate_final_checkpoint(path, frames, require_semantics=True))
            with self.assertRaises(ValueError):
                validate_final_checkpoint(path, frames + 1, require_semantics=True)

    def test_final_save_and_validation_precede_in_process_evaluation(self):
        tree = ast.parse((ROOT / "scripts/slam.py").read_text(encoding="utf-8"))
        function = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "rgbd_slam")
        def calls_named(node, name):
            return [call for call in ast.walk(node) if isinstance(call, ast.Call)
                    and isinstance(call.func, ast.Name) and call.func.id == name]

        evaluator = calls_named(function, "eval")[0]
        saver = next(node for node in function.body if isinstance(node, ast.FunctionDef)
                     and node.name == "save_final_state")
        self.assertTrue(calls_named(saver, "save_params"))
        self.assertTrue(calls_named(saver, "validate_final_checkpoint"))
        self.assertLess(min(call.lineno for call in calls_named(saver, "save_params")),
                        min(call.lineno for call in calls_named(saver, "validate_final_checkpoint")))
        pre_eval_branch = next(node for node in function.body if isinstance(node, ast.If)
                               and isinstance(node.test, ast.Name)
                               and node.test.id == "checkpoint_first_finalization")
        legacy_branch = next(node for node in function.body if isinstance(node, ast.If)
                             and isinstance(node.test, ast.UnaryOp)
                             and isinstance(node.test.op, ast.Not))
        self.assertTrue(calls_named(pre_eval_branch, "save_final_state"))
        self.assertTrue(calls_named(legacy_branch, "save_final_state"))
        self.assertLess(pre_eval_branch.lineno, evaluator.lineno)
        self.assertGreater(legacy_branch.lineno, evaluator.lineno)
        source = (ROOT / "scripts/slam.py").read_text(encoding="utf-8")
        self.assertIn('open(os.path.join(output_dir, "effective_config.json"), "x"', source)

    def test_saved_evaluator_has_no_top_level_torch_or_renderer_import(self):
        tree = ast.parse((ROOT / "scripts/evaluate_saved_phase6.py").read_text(encoding="utf-8"))
        top_level_imports = []
        for node in tree.body:
            if isinstance(node, ast.Import):
                top_level_imports.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom):
                top_level_imports.append(node.module or "")
        self.assertFalse(any(name.startswith(("torch", "diff_gaussian", "scripts.slam", "utils.eval_helpers"))
                             for name in top_level_imports))


if __name__ == "__main__":
    unittest.main()
