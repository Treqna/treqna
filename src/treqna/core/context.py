from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from treqna.core.enums import PipelineStageEnum, ResultStatusEnum


def current_utc_datetime() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, kw_only=True)
class ExecutionStatistics:
    start_time: datetime = field(default_factory=current_utc_datetime)
    end_time: datetime | None = None
    duration_seconds: float = 0.0
    stage_durations: Mapping[str, float] = field(default_factory=dict)
    bytes_processed: int = 0
    records_processed: int = 0


@dataclass(frozen=True, kw_only=True)
class TransformationMetadata:
    request_id: str
    created_at: datetime = field(default_factory=current_utc_datetime)
    source_identifier: str = ""
    target_identifier: str = ""
    custom_attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class PipelineStageEvent:
    stage: PipelineStageEnum
    timestamp: datetime = field(default_factory=current_utc_datetime)
    event_type: str
    message: str = ""
    payload: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class PipelineEvents:
    events: tuple[PipelineStageEvent, ...] = field(default_factory=tuple)

    def append(self, event: PipelineStageEvent) -> "PipelineEvents":
        return PipelineEvents(events=(*self.events, event))


@dataclass(frozen=True, kw_only=True)
class PipelineState:
    current_stage: PipelineStageEnum = PipelineStageEnum.DETECT
    status: ResultStatusEnum = ResultStatusEnum.PENDING
    progress_percentage: float = 0.0
    active_since: datetime = field(default_factory=current_utc_datetime)


@dataclass(frozen=True, kw_only=True)
class ExecutionContext:
    current_format: str
    target_format: str
    plugin_used: str = ""
    execution_time_seconds: float = 0.0
    metadata: TransformationMetadata | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    statistics: ExecutionStatistics = field(default_factory=ExecutionStatistics)


@dataclass(frozen=True, kw_only=True)
class PipelineContext:
    session_id: str
    execution_context: ExecutionContext
    state: PipelineState = field(default_factory=PipelineState)
    events: PipelineEvents = field(default_factory=PipelineEvents)
