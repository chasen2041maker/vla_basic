"""Explicit contracts for one autonomous-driving learning sample.

The classes are intentionally small. Their purpose is to make the time,
unit, and coordinate semantics visible before a model is introduced.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


def _require_number(value: Any, field_name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{field_name} must be a number")
    return float(value)


def _require_int(value: Any, field_name: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{field_name} must be an integer")
    return value


@dataclass(frozen=True)
class CameraFrame:
    """One camera observation.

    `timestamp_ms` is the capture time, not the time the file was read.
    `image_ref` is only a synthetic pointer in this lab.
    """

    name: str
    timestamp_ms: int
    image_ref: str

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CameraFrame":
        return cls(
            name=str(data["name"]),
            timestamp_ms=_require_int(data["timestamp_ms"], "camera.timestamp_ms"),
            image_ref=str(data["image_ref"]),
        )


@dataclass(frozen=True)
class EgoState:
    """Ego vehicle state at one time.

    Position and yaw use the sample's declared coordinate frame.
    Speed is metres per second.
    """

    timestamp_ms: int
    x_m: float
    y_m: float
    yaw_rad: float
    speed_mps: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "EgoState":
        return cls(
            timestamp_ms=_require_int(data["timestamp_ms"], "ego_state.timestamp_ms"),
            x_m=_require_number(data["x_m"], "ego_state.x_m"),
            y_m=_require_number(data["y_m"], "ego_state.y_m"),
            yaw_rad=_require_number(data["yaw_rad"], "ego_state.yaw_rad"),
            speed_mps=_require_number(data["speed_mps"], "ego_state.speed_mps"),
        )


@dataclass(frozen=True)
class TrajectoryPoint:
    """One future ego trajectory point."""

    timestamp_ms: int
    x_m: float
    y_m: float
    yaw_rad: float

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "TrajectoryPoint":
        return cls(
            timestamp_ms=_require_int(data["timestamp_ms"], "trajectory.timestamp_ms"),
            x_m=_require_number(data["x_m"], "trajectory.x_m"),
            y_m=_require_number(data["y_m"], "trajectory.y_m"),
            yaw_rad=_require_number(data["yaw_rad"], "trajectory.yaw_rad"),
        )


@dataclass(frozen=True)
class DrivingSample:
    """A model sample centred on one reference time.

    Contract:
      - camera frames and ego state describe the decision context;
      - future trajectory is the target after the reference time;
      - all positions use `coordinate_frame`;
      - all distances are metres and yaw is radians.
    """

    sample_id: str
    reference_timestamp_ms: int
    coordinate_frame: str
    cameras: tuple[CameraFrame, ...]
    ego_state: EgoState
    future_trajectory: tuple[TrajectoryPoint, ...]

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "DrivingSample":
        cameras_raw = data.get("cameras")
        trajectory_raw = data.get("future_trajectory")
        if not isinstance(cameras_raw, list):
            raise TypeError("cameras must be a list")
        if not isinstance(trajectory_raw, list):
            raise TypeError("future_trajectory must be a list")

        return cls(
            sample_id=str(data["sample_id"]),
            reference_timestamp_ms=_require_int(
                data["reference_timestamp_ms"], "reference_timestamp_ms"
            ),
            coordinate_frame=str(data["coordinate_frame"]),
            cameras=tuple(CameraFrame.from_dict(item) for item in cameras_raw),
            ego_state=EgoState.from_dict(data["ego_state"]),
            future_trajectory=tuple(
                TrajectoryPoint.from_dict(item) for item in trajectory_raw
            ),
        )
