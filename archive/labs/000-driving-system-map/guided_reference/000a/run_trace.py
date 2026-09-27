"""Run the deterministic Lab 000A system-map evaluation."""

from __future__ import annotations

from dataclasses import dataclass

from driving_system import SystemScenario, run_pipeline


@dataclass(frozen=True)
class ExpectedResult:
    scenario: SystemScenario
    expected_completed: bool
    expected_stopped_at: str | None


def build_cases() -> tuple[ExpectedResult, ...]:
    return (
        ExpectedResult(
            scenario=SystemScenario(
                name="nominal",
                reference_timestamp_ms=1000,
                camera_timestamps_ms=(990, 1000, 1010),
                ego_state_timestamp_ms=1000,
                proposed_trajectory_timestamps_ms=(1100, 1200, 1300),
            ),
            expected_completed=True,
            expected_stopped_at=None,
        ),
        ExpectedResult(
            scenario=SystemScenario(
                name="stale_camera",
                reference_timestamp_ms=5000,
                camera_timestamps_ms=(4750, 5000, 5010),
                ego_state_timestamp_ms=5000,
                proposed_trajectory_timestamps_ms=(5100, 5200, 5300),
            ),
            expected_completed=False,
            expected_stopped_at="data_contract",
        ),
        ExpectedResult(
            scenario=SystemScenario(
                name="past_trajectory",
                reference_timestamp_ms=6000,
                camera_timestamps_ms=(5990, 6000, 6010),
                ego_state_timestamp_ms=6000,
                proposed_trajectory_timestamps_ms=(5900, 6100, 6200),
            ),
            expected_completed=False,
            expected_stopped_at="safety_monitor",
        ),
        ExpectedResult(
            scenario=SystemScenario(
                name="controller_timeout",
                reference_timestamp_ms=7000,
                camera_timestamps_ms=(6990, 7000, 7010),
                ego_state_timestamp_ms=7000,
                proposed_trajectory_timestamps_ms=(7100, 7200, 7300),
                controller_available=False,
            ),
            expected_completed=False,
            expected_stopped_at="control",
        ),
    )


def evaluate_cases(cases: tuple[ExpectedResult, ...]) -> int:
    passed_count = 0

    for case in cases:
        report = run_pipeline(case.scenario)
        passed = (
            report.completed == case.expected_completed
            and report.stopped_at == case.expected_stopped_at
        )
        passed_count += int(passed)

        print(f"\nSCENARIO {case.scenario.name}")
        for event in report.trace:
            print(
                f"  stage={event.stage:<22} "
                f"outcome={event.outcome:<4} detail={event.detail}"
            )
        print(f"  completed={report.completed}")
        print(f"  stopped_at={report.stopped_at or 'none'}")
        print(f"  evaluator={'PASS' if passed else 'FAIL'}")

    print("\n" + "=" * 72)
    print(f"SYSTEM MAP RESULT: {passed_count} / {len(cases)} PASS")
    print("=" * 72)
    return 0 if passed_count == len(cases) else 1


def main() -> int:
    return evaluate_cases(build_cases())


if __name__ == "__main__":
    raise SystemExit(main())
