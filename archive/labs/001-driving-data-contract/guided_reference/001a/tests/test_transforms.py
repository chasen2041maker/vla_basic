from __future__ import annotations

import math
import unittest

from driving_contract.transforms import (
    Pose2D,
    ego_point_to_world,
    world_point_to_ego,
)


class TransformTests(unittest.TestCase):
    def test_round_trip_world_and_ego(self) -> None:
        pose = Pose2D(x_m=10.0, y_m=-3.0, yaw_rad=math.radians(30.0))
        world_x, world_y = ego_point_to_world(4.0, 1.5, pose)
        ego_x, ego_y = world_point_to_ego(world_x, world_y, pose)

        self.assertAlmostEqual(4.0, ego_x, places=9)
        self.assertAlmostEqual(1.5, ego_y, places=9)

    def test_ninety_degree_rotation(self) -> None:
        pose = Pose2D(x_m=0.0, y_m=0.0, yaw_rad=math.pi / 2)
        world_x, world_y = ego_point_to_world(2.0, 0.0, pose)

        self.assertAlmostEqual(0.0, world_x, places=9)
        self.assertAlmostEqual(2.0, world_y, places=9)


if __name__ == "__main__":
    unittest.main()
