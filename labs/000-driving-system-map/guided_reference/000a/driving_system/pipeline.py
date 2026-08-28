"""A deterministic, intentionally small autonomous-driving pipeline trace.

The goal is not to model a production stack. It makes stage responsibilities and
fail-fast behavior visible before the learner enters data, model, or control labs.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SystemScenario:
    """Synthetic inputs and expected model output for one pipeline run."""

    name: str
    reference_timestamp_ms: int
    camera_timestamps_ms: tuple[int, ...]
    ego_state_timestamp_ms: int
    proposed_trajectory_timestamps_ms: tuple[int, ...]
    controller_available: bool = True


@dataclass(frozen=True)
class PipelineTraceEvent:
    stage: str
    outcome: str
    detail: str


@dataclass(frozen=True)
class PipelineReport:
    scenario_name: str
    completed: bool
    stopped_at: str | None
    trace: tuple[PipelineTraceEvent, ...]


def _stop(
    scenario: SystemScenario,
    stage: str,
    trace: list[PipelineTraceEvent],
) -> PipelineReport:
    return PipelineReport(
        scenario_name=scenario.name,
        completed=False,
        stopped_at=stage,
        trace=tuple(trace),
    )


def run_pipeline(
    scenario: SystemScenario,
    *,
    max_camera_skew_ms: int = 100,
    max_ego_skew_ms: int = 50,
) -> PipelineReport:
    """Run the synthetic pipeline and stop at the first violated boundary."""

    trace: list[PipelineTraceEvent] = []

    if not scenario.camera_timestamps_ms:
        trace.append(
            PipelineTraceEvent(
                stage="sensor_capture",
                outcome="fail",
                detail="no camera frames",
            )
        )
        return _stop(scenario, "sensor_capture", trace)

    trace.append(
        PipelineTraceEvent(
            stage="sensor_capture",
            outcome="pass",
            detail=f"captured {len(scenario.camera_timestamps_ms)} camera frames",
        )
    )

    camera_skews_ms = tuple(
        abs(timestamp_ms - scenario.reference_timestamp_ms)
        for timestamp_ms in scenario.camera_timestamps_ms
    )
    maximum_camera_skew_ms = max(camera_skews_ms)
    ego_skew_ms = abs(
        scenario.ego_state_timestamp_ms - scenario.reference_timestamp_ms
    )

    if maximum_camera_skew_ms > max_camera_skew_ms:
        trace.append(
            PipelineTraceEvent(
                stage="data_contract",
                outcome="fail",
                detail=(
                    f"maximum camera skew {maximum_camera_skew_ms} ms exceeds "
                    f"{max_camera_skew_ms} ms"
                ),
            )
        )
        return _stop(scenario, "data_contract", trace)

    if ego_skew_ms > max_ego_skew_ms:
        trace.append(
            PipelineTraceEvent(
                stage="data_contract",
                outcome="fail",
                detail=(
                    f"ego-state skew {ego_skew_ms} ms exceeds "
                    f"{max_ego_skew_ms} ms"
                ),
            )
        )
        return _stop(scenario, "data_contract", trace)

    trace.append(
        PipelineTraceEvent(
            stage="data_contract",
            outcome="pass",
            detail=(
                f"camera_skew<={max_camera_skew_ms} ms, "
                f"ego_skew<={max_ego_skew_ms} ms"
            ),
        )
    )

    if not scenario.proposed_trajectory_timestamps_ms:
        trace.append(
            PipelineTraceEvent(
                stage="model_inference",
                outcome="fail",
                detail="model returned no trajectory points",
            )
        )
        return _stop(scenario, "model_inference", trace)

    trace.append(
        PipelineTraceEvent(
            stage="model_inference",
            outcome="pass",
            detail=(
                "synthetic model returned timestamps "
                f"{scenario.proposed_trajectory_timestamps_ms}"
            ),
        )
    )

    trajectory_timestamps_ms = scenario.proposed_trajectory_timestamps_ms
    strictly_increasing = all(
        current < following
        for current, following in zip(
            trajectory_timestamps_ms,
            trajectory_timestamps_ms[1:],
        )
    )
    starts_after_reference = (
        trajectory_timestamps_ms[0] > scenario.reference_timestamp_ms
    )

    if not starts_after_reference:
        trace.append(
            PipelineTraceEvent(
                stage="safety_monitor",
                outcome="fail",
                detail=(
                    f"first trajectory timestamp {trajectory_timestamps_ms[0]} "
                    f"is not after reference {scenario.reference_timestamp_ms}"
                ),
            )
        )
        return _stop(scenario, "safety_monitor", trace)

    if not strictly_increasing:
        trace.append(
            PipelineTraceEvent(
                stage="safety_monitor",
                outcome="fail",
                detail="trajectory timestamps are not strictly increasing",
            )
        )
        return _stop(scenario, "safety_monitor", trace)

    trace.append(
        PipelineTraceEvent(
            stage="safety_monitor",
            outcome="pass",
            detail="trajectory is strictly increasing and entirely in the future",
        )
    )

    if not scenario.controller_available:
        trace.append(
            PipelineTraceEvent(
                stage="control",
                outcome="fail",
                detail="controller missed its execution deadline",
            )
        )
        return _stop(scenario, "control", trace)

    trace.append(
        PipelineTraceEvent(
            stage="control",
            outcome="pass",
            detail="trajectory converted into a synthetic control command",
        )
    )
    trace.append(
        PipelineTraceEvent(
            stage="environment_feedback",
            outcome="pass",
            detail="synthetic command applied; the next observation would change",
        )
    )

    return PipelineReport(
        scenario_name=scenario.name,
        completed=True,
        stopped_at=None,
        trace=tuple(trace),
    )
