from __future__ import annotations

import unittest

from driving_system import SystemScenario, run_pipeline


class PipelineTests(unittest.TestCase):
    def test_nominal_scenario_completes(self) -> None:
        report = run_pipeline(
            SystemScenario(
                name="nominal",
                reference_timestamp_ms=1000,
                camera_timestamps_ms=(990, 1000, 1010),
                ego_state_timestamp_ms=1000,
                proposed_trajectory_timestamps_ms=(1100, 1200, 1300),
            )
        )

        self.assertTrue(report.completed)
        self.assertIsNone(report.stopped_at)
        self.assertEqual(
            [
                "sensor_capture",
                "data_contract",
                "model_inference",
                "safety_monitor",
                "control",
                "environment_feedback",
            ],
            [event.stage for event in report.trace],
        )

    def test_stale_camera_stops_before_model(self) -> None:
        report = run_pipeline(
            SystemScenario(
                name="stale_camera",
                reference_timestamp_ms=5000,
                camera_timestamps_ms=(4750, 5000, 5010),
                ego_state_timestamp_ms=5000,
                proposed_trajectory_timestamps_ms=(5100, 5200, 5300),
            )
        )

        self.assertFalse(report.completed)
        self.assertEqual("data_contract", report.stopped_at)
        self.assertNotIn(
            "model_inference",
            {event.stage for event in report.trace},
        )

    def test_past_trajectory_stops_at_safety_monitor(self) -> None:
        report = run_pipeline(
            SystemScenario(
                name="past_trajectory",
                reference_timestamp_ms=6000,
                camera_timestamps_ms=(5990, 6000, 6010),
                ego_state_timestamp_ms=6000,
                proposed_trajectory_timestamps_ms=(5900, 6100, 6200),
            )
        )

        self.assertFalse(report.completed)
        self.assertEqual("safety_monitor", report.stopped_at)
        self.assertIn(
            "model_inference",
            {event.stage for event in report.trace},
        )
        self.assertNotIn(
            "control",
            {event.stage for event in report.trace},
        )

    def test_controller_timeout_is_not_a_model_failure(self) -> None:
        report = run_pipeline(
            SystemScenario(
                name="controller_timeout",
                reference_timestamp_ms=7000,
                camera_timestamps_ms=(6990, 7000, 7010),
                ego_state_timestamp_ms=7000,
                proposed_trajectory_timestamps_ms=(7100, 7200, 7300),
                controller_available=False,
            )
        )

        self.assertFalse(report.completed)
        self.assertEqual("control", report.stopped_at)
        outcomes = {event.stage: event.outcome for event in report.trace}
        self.assertEqual("pass", outcomes["model_inference"])
        self.assertEqual("pass", outcomes["safety_monitor"])
        self.assertEqual("fail", outcomes["control"])


if __name__ == "__main__":
    unittest.main()
