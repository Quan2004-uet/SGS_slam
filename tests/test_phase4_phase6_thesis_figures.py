import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/visualization/package_phase4_phase6_thesis_figures.py"
SPEC = importlib.util.spec_from_file_location("phase4_phase6_thesis_figures", SCRIPT)
packager = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(packager)


class ThesisFigurePackagingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.repo = SCRIPT.parents[2]
        cls.gate2 = cls.repo / "results/runtime_artifacts/phase6_bam/p6_bam_007_qualitative_comparison/gate2_side_by_side/run_02"
        cls.manifest, cls.validation, cls.pairs, cls.source_hashes = packager.load_gate2(cls.repo, cls.gate2)
        cls.selections = packager.choose(cls.pairs)

    def test_accepted_gate2_provenance_and_counts(self):
        self.assertEqual(len(self.pairs), 43)
        self.assertEqual(len(self.source_hashes), 86)
        self.assertEqual(len(self.manifest["previews"]), 7)
        self.assertEqual(self.validation["final_gate_classification"], "PASS_P6_BAM_007_GATE2_SIDE_BY_SIDE")

    def test_semantic_3d_has_both_representations_and_views(self):
        rows = self.selections["semantic_3d"]
        self.assertEqual(len(rows), 4)
        self.assertEqual([(r["modality"], r["frame_view_id"]) for r, _ in rows], [
            ("Raw learned semantic color", "room_overview"),
            ("Raw learned semantic color", "top_oblique"),
            ("Fixed semantic IDs", "room_overview"),
            ("Fixed semantic IDs", "top_oblique"),
        ])

    def test_full_scene_rgb_is_phase4_v3a_camera_family(self):
        rows = self.selections["full_rgb"]
        self.assertEqual([r["frame_view_id"] for r, _ in rows], ["room_overview", "top_oblique"])
        self.assertTrue(all(r["family_directory"] == "v3a_cross_modal" for r, _ in rows))

    def test_v1_and_v3a_top_oblique_are_distinct_camera_definitions(self):
        v1 = packager.find_pair(self.pairs, family="v1", frame_view="top_oblique", modality="RGB Gaussian reconstruction")
        v3a = packager.find_pair(self.pairs, family="v3a_cross_modal", frame_view="top_oblique", modality="RGB")
        self.assertNotEqual(v1["camera_sha256"], v3a["camera_sha256"])

    def test_utility_has_no_gpu_or_model_imports(self):
        source = SCRIPT.read_text(encoding="utf-8")
        for prohibited in ("import torch", "import cupy", "cuda.init", "GaussianModel(", "subprocess.", "requests."):
            self.assertNotIn(prohibited, source)


if __name__ == "__main__":
    unittest.main()
