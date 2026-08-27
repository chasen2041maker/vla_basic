"""Run the deterministic Lab 001A contract evaluation."""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from driving_contract import DrivingSample, validate_sample_baseline


@dataclass(frozen=True)
class CaseResult:
    name: str
    expected_valid: bool
    actual_valid: bool
    passed: bool
    issue_codes: tuple[str, ...]


def load_cases(path: Path) -> list[dict[str, Any]]:
    with path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    cases = payload.get("cases")
    if not isinstance(cases, list):
        raise ValueError("cases.json must contain a list named 'cases'")
    return cases


def evaluate_cases(cases: list[dict[str, Any]]) -> list[CaseResult]:
    results: list[CaseResult] = []

    for case in cases:
        sample = DrivingSample.from_dict(case["sample"])
        report = validate_sample_baseline(sample)
        expected_valid = bool(case["expected_valid"])
        passed = report.valid == expected_valid

        print(f"\nCASE {case['name']}")
        print(f"  expected_valid={expected_valid}")
        print(f"  actual_valid={report.valid}")
        for event in report.trace:
            print(
                f"  trace check={event.check:<24} "
                f"outcome={event.outcome:<4} detail={event.detail}"
            )
        if report.issues:
            print(
                "  issues="
                + ", ".join(issue.code for issue in report.issues)
            )
        else:
            print("  issues=none")
        print(f"  evaluator={'PASS' if passed else 'FAIL'}")

        results.append(
            CaseResult(
                name=str(case["name"]),
                expected_valid=expected_valid,
                actual_valid=report.valid,
                passed=passed,
                issue_codes=tuple(issue.code for issue in report.issues),
            )
        )

    return results


def main() -> int:
    cases_path = Path(__file__).parent / "data" / "cases.json"
    results = evaluate_cases(load_cases(cases_path))
    passed_count = sum(result.passed for result in results)

    print("\n" + "=" * 72)
    print(f"BASELINE RESULT: {passed_count} / {len(results)} PASS")
    failing_names = [result.name for result in results if not result.passed]
    print(f"FAILING CASES: {', '.join(failing_names) if failing_names else 'none'}")
    print("=" * 72)

    # The two evaluator failures are expected teaching evidence, not a process error.
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
