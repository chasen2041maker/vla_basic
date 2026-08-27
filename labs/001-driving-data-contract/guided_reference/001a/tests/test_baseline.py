from __future__ import annotations

import contextlib
import io
import unittest
from pathlib import Path

from driving_contract import DrivingSample, validate_sample_baseline
from run_eval import evaluate_cases, load_cases


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "data" / "cases.json"


class BaselineEvaluationTests(unittest.TestCase):
    def test_teaching_baseline_is_exactly_four_of_six(self) -> None:
        with contextlib.redirect_stdout(io.StringIO()):
            results = evaluate_cases(load_cases(CASES_PATH))
        self.assertEqual(6, len(results))
        self.assertEqual(4, sum(result.passed for result in results))

    def test_duplicate_camera_is_detected(self) -> None:
        cases = load_cases(CASES_PATH)
        case = next(item for item in cases if item["name"] == "duplicate_camera_name")
        report = validate_sample_baseline(DrivingSample.from_dict(case["sample"]))
        self.assertFalse(report.valid)
        self.assertIn(
            "duplicate_camera_name",
            {issue.code for issue in report.issues},
        )

    def test_non_increasing_trajectory_time_is_detected(self) -> None:
        cases = load_cases(CASES_PATH)
        case = next(
            item
            for item in cases
            if item["name"] == "trajectory_time_not_increasing"
        )
        report = validate_sample_baseline(DrivingSample.from_dict(case["sample"]))
        self.assertFalse(report.valid)
        self.assertIn(
            "trajectory_time_not_increasing",
            {issue.code for issue in report.issues},
        )

    def test_baseline_intentionally_misses_camera_clock_skew(self) -> None:
        cases = load_cases(CASES_PATH)
        case = next(item for item in cases if item["name"] == "camera_clock_skew")
        report = validate_sample_baseline(DrivingSample.from_dict(case["sample"]))
        self.assertTrue(report.valid)

    def test_baseline_intentionally_misses_past_future_label(self) -> None:
        cases = load_cases(CASES_PATH)
        case = next(
            item
            for item in cases
            if item["name"] == "future_trajectory_starts_in_past"
        )
        report = validate_sample_baseline(DrivingSample.from_dict(case["sample"]))
        self.assertTrue(report.valid)


if __name__ == "__main__":
    unittest.main()
