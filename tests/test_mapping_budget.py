"""CPU-only contract tests for P6-BAM-001."""

import ast
import copy
import os
import random
import unittest
from importlib.machinery import SourceFileLoader
from pathlib import Path
from unittest import mock

from utils.mapping_budget import record_mapping_budget, select_mapping_budget


ROOT = Path(__file__).resolve().parents[1]
PRUNING = {"start_after": 0, "stop_after": 20, "prune_every": 20,
           "reset_opacities": False}
ADAPTIVE = {"enabled": True, "mode": "adaptive",
            "budgets": {"low": 30, "mid": 45, "full": 60},
            "fraction_thresholds": {"low_max": 0.01, "mid_max": 0.05}}


class Recorder:
    def __init__(self):
        self.records = {}

    def record(self, component, name, value, unit, frame_id):
        self.records[name] = (value, unit, frame_id)


class MappingBudgetTests(unittest.TestCase):
    def choose(self, control=ADAPTIVE, pre=1000, post=1000, frame=1,
               pruning=PRUNING, iters=60):
        mapping = {"budget_control": control} if control is not None else {}
        return select_mapping_budget({"mapping": mapping}, iters, pre, post, frame, pruning)

    def test_off_and_missing_preserve_v0_without_rng_use(self):
        for control in (None, {"enabled": False}):
            random.seed(18)
            before = random.getstate()
            decision = self.choose(control, pre=None, post=None)
            self.assertEqual(decision.effective_iters, 60)
            self.assertFalse(decision.enabled)
            self.assertEqual(random.getstate(), before)
        self.assertEqual(self.choose(None, iters=0).effective_iters, 0)
        self.assertEqual(self.choose(True).fallback_reason, "invalid_control")
        self.assertEqual(self.choose({"enabled": 1}).fallback_reason, "invalid_control")

    def test_initial_frame_and_missing_signal_use_full_budget(self):
        self.assertEqual(self.choose(frame=0, pre=None, post=None).fallback_reason, "initial_frame")
        self.assertEqual(self.choose(pre=100, post=None).effective_iters, 60)
        self.assertFalse(self.choose(pre=100, post=None).signal_valid)

    def test_zero_low_mid_high_novelty(self):
        cases = [(1000, "LOW", 30), (1010, "LOW", 30),
                 (1030, "MID", 45), (1050, "MID", 45),
                 (1051, "FULL", 60)]
        for post, tier, expected in cases:
            with self.subTest(post=post):
                decision = self.choose(post=post)
                self.assertEqual((decision.tier, decision.effective_iters), (tier, expected))
                self.assertEqual(decision.added_count, post - 1000)
        self.assertEqual(self.choose().added_fraction, 0.0)

    def test_bad_counts_do_not_produce_negative_novelty(self):
        for pre, post in ((-1, 10), (10, -1), (11, 10), (0, 0), (1.5, 2), (True, 2)):
            with self.subTest(pre=pre, post=post):
                decision = self.choose(pre=pre, post=post)
                self.assertEqual(decision.effective_iters, 60)
                self.assertIsNone(decision.added_count)
                self.assertFalse(decision.signal_valid)

    def test_invalid_thresholds_and_budgets_fall_back(self):
        for name, value in (("low_max", -0.1), ("mid_max", 0.01),
                            ("mid_max", float("nan")), ("low_max", "0.01")):
            control = copy.deepcopy(ADAPTIVE)
            control["fraction_thresholds"][name] = value
            self.assertEqual(self.choose(control).fallback_reason, "invalid_tier_config")
        for name, value in (("low", 0), ("low", 61), ("mid", 20),
                            ("full", 59), ("mid", True)):
            control = copy.deepcopy(ADAPTIVE)
            control["budgets"][name] = value
            self.assertEqual(self.choose(control).effective_iters, 60)

    def test_fixed_budgets_and_pruning_floor(self):
        for count in (30, 45):
            decision = self.choose({"enabled": True, "mode": "fixed", "fixed_iters": count})
            self.assertEqual(decision.effective_iters, count)
            self.assertEqual(self.choose({"enabled": True, "mode": "fixed", "fixed_iters": count},
                                         frame=0).effective_iters, 60)
        self.assertEqual(self.choose({"enabled": True, "mode": "fixed", "fixed_iters": 20})
                         .fallback_reason, "pruning_iteration_floor")
        self.assertEqual(self.choose({"enabled": True, "mode": "fixed", "fixed_iters": 21})
                         .effective_iters, 21)
        self.assertEqual(self.choose({"enabled": True, "mode": "fixed", "fixed_iters": 20},
                                     pruning=None).effective_iters, 20)
        self.assertEqual(self.choose({"enabled": True, "mode": "fixed", "fixed_iters": 61})
                         .fallback_reason, "invalid_budget")
        control = copy.deepcopy(ADAPTIVE)
        control["budgets"]["low"] = 20
        self.assertEqual(self.choose(control, post=1100).fallback_reason,
                         "pruning_iteration_floor")

    def test_invalid_pruning_and_densification_fall_back(self):
        pruning = dict(PRUNING, prune_every=0)
        self.assertEqual(self.choose(pruning=pruning).fallback_reason,
                         "invalid_or_reset_pruning_schedule")
        config = {"mapping": {"budget_control": ADAPTIVE,
                              "use_gaussian_splatting_densification": True}}
        decision = select_mapping_budget(config, 60, 1000, 1000, 1, PRUNING)
        self.assertEqual(decision.fallback_reason, "densification_enabled")

    def test_deterministic_immutable_and_no_rng_use(self):
        random.seed(10)
        before = random.getstate()
        a = self.choose(post=1040)
        self.assertEqual(a, self.choose(post=1040))
        self.assertEqual(before, random.getstate())
        with self.assertRaises(Exception):
            a.effective_iters = 60

    def test_module_has_no_tensor_or_cuda_dependency(self):
        source = (ROOT / "utils/mapping_budget.py").read_text()
        tree = ast.parse(source)
        imported = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertFalse(any("torch" in ast.unparse(node) or "numpy" in ast.unparse(node)
                             for node in imported))
        for forbidden in (".item(", ".cpu(", ".cuda(", ".numpy(", "synchronize("):
            self.assertNotIn(forbidden, source)

    def test_telemetry_has_selected_executed_and_prune_counts(self):
        recorder = Recorder()
        decision = self.choose(post=1030)
        values = record_mapping_budget(recorder, decision, 8, 1000, 1030, 45, PRUNING)
        self.assertEqual(values["event_id"], 8)
        self.assertEqual(values["effective_iters"], 45)
        self.assertEqual(values["executed_iters"], 45)
        self.assertEqual(values["prune_required_iters"], 21)
        self.assertEqual(recorder.records["added_fraction"], (0.03, "fraction", 8))

    def test_config_wrappers_isolate_tracking_and_outputs(self):
        for variant in ("v0", "va", "vfixed30", "vfixed45"):
            with self.subTest(variant=variant), mock.patch.dict(os.environ,
                    {"P6_BAM_RUN_ID": f"p6_bam_cpu_static_{variant}"}):
                path = ROOT / "configs/replica" / f"phase6_bam_{variant}.py"
                module = SourceFileLoader(f"test_p6_{variant}", str(path)).load_module()
                config = module.config
                self.assertEqual(config["tracking"]["num_iters"], 40)
                self.assertEqual(config["mapping"]["num_iters"], 60)
                self.assertEqual(config["profiling"]["mode"], "off")
                self.assertEqual(config["phase6_variant"].lower().replace("-", ""),
                                 variant.replace("vfixed", "vfixed") if variant != "va" else "va")
                self.assertIn("/results/runtime_artifacts/phase6_bam", config["workdir"])
                self.assertFalse(Path(config["workdir"], config["run_name"]).exists())

    def test_missing_run_id_rejected_before_execution(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            with self.assertRaises(ValueError):
                SourceFileLoader("test_p6_missing", str(ROOT / "configs/replica/phase6_bam_v0.py")).load_module()

    def test_existing_phase6_destination_is_rejected(self):
        path = ROOT / "configs/replica/phase6_bam_base.py"
        module = SourceFileLoader("test_p6_existing", str(path)).load_module()
        with mock.patch.dict(os.environ, {"P6_BAM_RUN_ID": "p6_bam_existing_cpu_test"}), \
                mock.patch.object(module.os.path, "exists", return_value=True):
            with self.assertRaises(FileExistsError):
                module.make_config("V0", {"enabled": False})

    def test_static_integration_scope(self):
        source = (ROOT / "scripts/slam.py").read_text()
        self.assertIn("post_num_pts = None  # An absent append", source)
        self.assertIn("select_mapping_budget(config, configured_mapping_iters, pre_num_pts,", source)
        self.assertIn("for iter in range(effective_mapping_iters):", source)
        self.assertIn("executed_mapping_iters += 1", source)
        self.assertIn("record_mapping_budget(profiler, budget_decision", source)

    def test_mapping_event_sequence_uses_source_assignments_and_loop_range(self):
        """Run the actual CPU budget statements extracted from the mapping branch."""
        tree = ast.parse((ROOT / "scripts/slam.py").read_text())
        slam = next(node for node in tree.body if isinstance(node, ast.FunctionDef)
                    and node.name == "rgbd_slam")
        frame_loop = next(node for node in ast.walk(slam) if isinstance(node, ast.For)
                          and isinstance(node.target, ast.Name) and node.target.id == "time_idx")
        mapping_if = next(node for node in frame_loop.body if isinstance(node, ast.If)
                          and "config['map_every']" in ast.unparse(node.test))
        names = ("configured_mapping_iters", "budget_decision", "effective_mapping_iters")
        assignments = [next(node for node in mapping_if.body if isinstance(node, ast.Assign)
                            and any(isinstance(target, ast.Name) and target.id == name
                                    for target in node.targets)) for name in names]
        loop = next(node for node in mapping_if.body if isinstance(node, ast.For)
                    and isinstance(node.target, ast.Name) and node.target.id == "iter")
        self.assertEqual(ast.unparse(loop.iter), "range(effective_mapping_iters)")
        self.assertIn("tqdm(range(effective_mapping_iters),", ast.unparse(mapping_if))
        module = ast.fix_missing_locations(ast.Module(body=[*copy.deepcopy(assignments),
            ast.For(target=copy.deepcopy(loop.target), iter=copy.deepcopy(loop.iter),
                    body=ast.parse("observed.append(iter)").body, orelse=[])], type_ignores=[]))
        code = compile(module, str(ROOT / "scripts/slam.py"), "exec")

        def sequence(control, expected, posts=(None, 1000, 1100, 1030, None, 1000)):
            received_maxima = []

            def checked_select(config, configured_iters, pre, post, frame, pruning):
                received_maxima.append(configured_iters)
                return select_mapping_budget(config, configured_iters, pre, post, frame, pruning)

            scope = {"config": {"mapping": {"num_iters": 60, "budget_control": control}},
                     "select_mapping_budget": checked_select, "pruning_config": PRUNING}
            actual = []
            for frame, post in enumerate(posts):
                scope.update(time_idx=frame, pre_num_pts=1000, post_num_pts=post, observed=[])
                exec(code, scope)
                actual.append(scope["effective_mapping_iters"])
                self.assertEqual(scope["configured_mapping_iters"], 60)
                self.assertEqual(scope["budget_decision"].configured_iters, 60)
                self.assertEqual(len(scope["observed"]), scope["effective_mapping_iters"])
                self.assertIn(20, scope["observed"])  # Replica's last required prune.
            self.assertEqual(actual, expected)
            self.assertEqual(received_maxima, [60] * len(posts))

        sequence(ADAPTIVE, [60, 30, 60, 45, 60, 30])
        valid_posts = (None, 1000, 1100, 1030, 1000, 1000)
        sequence({"enabled": True, "mode": "fixed", "fixed_iters": 30},
                 [60, 30, 30, 30, 30, 30], valid_posts)
        sequence({"enabled": True, "mode": "fixed", "fixed_iters": 45},
                 [60, 45, 45, 45, 45, 45], valid_posts)
        sequence({"enabled": False}, [60] * 6)


if __name__ == "__main__":
    unittest.main()
