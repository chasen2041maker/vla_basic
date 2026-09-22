"""不导入模拟器的参数与结束原因测试；不能代替集成测试。"""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from run_episode import end_reason, validate_options


class LogicTests(unittest.TestCase):
    def test_valid_options(self):
        validate_options(7, 1, "IDLE", None, 8.0, 0)

    def test_invalid_options(self):
        valid = [7, 1, "IDLE", None, 8.0, 12]
        for index, bad in ((0, -1), (0, True), (1, 0), (1, 1.5),
                           (2, "BRAKE"), (3, "video"), (4, float("nan")),
                           (4, 0), (4, 61), (5, -1), (5, 101)):
            with self.subTest(index=index, bad=bad):
                values = list(valid)
                values[index] = bad
                with self.assertRaises(ValueError):
                    validate_options(*values)

    def test_end_reasons(self):
        for crashed, on_road, terminated, truncated, expected in (
            (True, True, True, False, "collision"),
            (True, False, True, True, "collision"),
            (False, False, True, False, "off_road"),
            (False, True, True, False, "terminated"),
            (False, True, False, True, "environment_time_limit"),
            (False, True, False, False, "runner_step_limit"),
        ):
            with self.subTest(expected=expected):
                self.assertEqual(end_reason(crashed=crashed, on_road=on_road,
                                 terminated=terminated, truncated=truncated), expected)


if __name__ == "__main__":
    unittest.main()
