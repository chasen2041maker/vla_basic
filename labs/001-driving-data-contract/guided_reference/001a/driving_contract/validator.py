"""An intentionally incomplete validator used as a teaching baseline."""

from __future__ import annotations

from dataclasses import dataclass

from .contracts import DrivingSample


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str


@dataclass(frozen=True)
class TraceEvent:
    check: str
    outcome: str
    detail: str


@dataclass(frozen=True)
class ValidationReport:
    valid: bool
    issues: tuple[ValidationIssue, ...]
    trace: tuple[TraceEvent, ...]


def validate_sample_baseline(sample: DrivingSample) -> ValidationReport:
    """Run structural checks, but intentionally miss two semantic checks.

    Deliberate gaps:
      1. camera capture timestamps may be too far from the reference time;
      2. trajectory points may start before the reference time.

    These gaps make the baseline score 4/6 and are the subject of Lab 001A.
    """

    issues: list[ValidationIssue] = []
    trace: list[TraceEvent] = []

    camera_names = [camera.name for camera in sample.cameras]
    duplicate_camera_names = sorted(
        name for name in set(camera_names) if camera_names.count(name) > 1
    )
    if duplicate_camera_names:
        issues.append(
            ValidationIssue(
                code="duplicate_camera_name",
                message=f"duplicate cameras: {duplicate_camera_names}",
            )
        )
        trace.append(
            TraceEvent(
                check="unique_camera_names",
                outcome="fail",
                detail=str(duplicate_camera_names),
            )
        )
    else:
        trace.append(
            TraceEvent(
                check="unique_camera_names",
                outcome="pass",
                detail=f"{len(camera_names)} unique camera names",
            )
        )

    trajectory_timestamps = [
        point.timestamp_ms for point in sample.future_trajectory
    ]
    strictly_increasing = all(
        current < following
        for current, following in zip(
            trajectory_timestamps, trajectory_timestamps[1:]
        )
    )
    if not trajectory_timestamps:
        issues.append(
            ValidationIssue(
                code="empty_future_trajectory",
                message="future trajectory must contain at least one point",
            )
        )
        trace.append(
            TraceEvent(
                check="trajectory_non_empty",
                outcome="fail",
                detail="no points",
            )
        )
    else:
        trace.append(
            TraceEvent(
                check="trajectory_non_empty",
                outcome="pass",
                detail=f"{len(trajectory_timestamps)} points",
            )
        )

    if trajectory_timestamps and not strictly_increasing:
        issues.append(
            ValidationIssue(
                code="trajectory_time_not_increasing",
                message="future trajectory timestamps must be strictly increasing",
            )
        )
        trace.append(
            TraceEvent(
                check="trajectory_time_order",
                outcome="fail",
                detail=str(trajectory_timestamps),
            )
        )
    elif trajectory_timestamps:
        trace.append(
            TraceEvent(
                check="trajectory_time_order",
                outcome="pass",
                detail=str(trajectory_timestamps),
            )
        )

    # The baseline intentionally stops here.
    # It never checks camera clock skew or whether the future starts in the future.
    return ValidationReport(
        valid=not issues,
        issues=tuple(issues),
        trace=tuple(trace),
    )
