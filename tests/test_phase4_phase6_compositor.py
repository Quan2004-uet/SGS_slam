import importlib.util
import tempfile
import unittest
from pathlib import Path

from PIL import Image


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/visualization/compose_phase4_phase6_comparisons.py"
SPEC = importlib.util.spec_from_file_location("phase4_phase6_compositor", SCRIPT)
compositor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(compositor)


class CompositorTests(unittest.TestCase):
    def test_plan_has_exact_43_audited_rows_and_distribution(self):
        repo = SCRIPT.parents[2]
        plan = repo / "docs/research/phase6_bam/P6_BAM_007_QUALITATIVE_COMPARISON_PLAN.md"
        rows = compositor.parse_appendix(plan)
        self.assertEqual(len(rows), 43)
        from collections import Counter
        self.assertEqual(Counter(compositor.family_dir(r) for r in rows), compositor.EXPECTED_FAMILY_COUNTS)

    def test_composition_preserves_both_decoded_panels_exactly(self):
        with tempfile.TemporaryDirectory() as temp:
            target = Path(temp) / "pair.png"
            p4 = Image.new("RGB", (23, 17), (12, 80, 201))
            p6 = Image.new("RGB", (23, 17), (198, 33, 71))
            row = {
                "Family": "V1", "Frame/view": "unit", "Modality": "RGB Gaussian reconstruction",
                "Classification": "READY_WITH_EXPLICIT_CAVEAT",
                "Interpretation": "Unit test caveat.",
            }
            regular, bold = compositor.font_paths()
            result = compositor.compose_pair(row, p4, p6, target, regular, bold)
            with Image.open(target) as output:
                output.load()
                for name, source in [("phase4", p4), ("phase6", p6)]:
                    x, y = result["panel_origins"][name]
                    self.assertEqual(output.crop((x, y, x + source.width, y + source.height)).tobytes(), source.tobytes())

    def test_readiness_classes_are_explicit(self):
        self.assertEqual(compositor.EXPECTED_READY_COUNTS["READY_FOR_SIDE_BY_SIDE"], 12)
        self.assertEqual(compositor.EXPECTED_READY_COUNTS["READY_WITH_EXPLICIT_CAVEAT"], 31)


if __name__ == "__main__":
    unittest.main()
