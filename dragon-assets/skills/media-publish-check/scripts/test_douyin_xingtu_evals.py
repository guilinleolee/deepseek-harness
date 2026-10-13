import importlib.util
import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
DATASET = ROOT / "evals" / "douyin-xingtu-diversion-v1.json"
SPEC = importlib.util.spec_from_file_location("validate_evals", ROOT / "scripts" / "validate_evals.py")
VALIDATOR = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(VALIDATOR)


class DouyinXingtuEvalTests(unittest.TestCase):
    def setUp(self):
        self.payload = json.loads(DATASET.read_text(encoding="utf-8"))

    def test_dataset_schema_is_valid(self):
        self.assertEqual([], VALIDATOR.validate(self.payload))

    def test_all_seed_cases_are_original_synthetic(self):
        for case in self.payload["cases"]:
            with self.subTest(case=case["case_id"]):
                self.assertEqual("original-synthetic", case["origin"])
                self.assertEqual("project-owned-fiction", case["rights_status"])

    def test_suite_has_positive_negative_and_evidence_gap_cases(self):
        cases = self.payload["cases"]
        codes = {code for case in cases for code in case["expected_codes_or_checks"]}
        self.assertTrue(any(case["expected_minimum_risk"] == "R3" for case in cases))
        self.assertIn("no-DYX-01-to-DYX-06-trigger", codes)
        self.assertIn("evidence-scope-incomplete", codes)


if __name__ == "__main__":
    unittest.main()
