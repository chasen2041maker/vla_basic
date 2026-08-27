"""Minimal two-dimensional coordinate transforms for later lab steps."""

from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Pose2D:
    x_m: float
    y_m: float
    yaw_rad: float


def ego_point_to_world(
    point_x_m: float,
    point_y_m: float,
    ego_pose_in_world: Pose2D,
) -> tuple[float, float]:
    """Transform a point from ego coordinates into world coordinates."""

    cos_yaw = math.cos(ego_pose_in_world.yaw_rad)
    sin_yaw = math.sin(ego_pose_in_world.yaw_rad)
    world_x = ego_pose_in_world.x_m + cos_yaw * point_x_m - sin_yaw * point_y_m
    world_y = ego_pose_in_world.y_m + sin_yaw * point_x_m + cos_yaw * point_y_m
    return world_x, world_y


def world_point_to_ego(
    world_x_m: float,
    world_y_m: float,
    ego_pose_in_world: Pose2D,
) -> tuple[float, float]:
    """Transform a point from world coordinates into ego coordinates."""

    delta_x = world_x_m - ego_pose_in_world.x_m
    delta_y = world_y_m - ego_pose_in_world.y_m
    cos_yaw = math.cos(ego_pose_in_world.yaw_rad)
    sin_yaw = math.sin(ego_pose_in_world.yaw_rad)
    ego_x = cos_yaw * delta_x + sin_yaw * delta_y
    ego_y = -sin_yaw * delta_x + cos_yaw * delta_y
    return ego_x, ego_y
