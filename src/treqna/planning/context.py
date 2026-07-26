from dataclasses import dataclass, field
from datetime import UTC, datetime

from treqna.planning.models import (
    PlanConstraint,
    PlanRequirement,
    TransformationPlan,
)


def current_timestamp() -> float:
    return datetime.now(UTC).timestamp()


@dataclass(frozen=True, kw_only=True)
class PlannerContext:
    session_id: str
    strategy_name: str = "default_strategy"
    constraint: PlanConstraint | None = None
    requirement: PlanRequirement | None = None


@dataclass(frozen=True, kw_only=True)
class PlannerSession:
    session_id: str
    context: PlannerContext
    created_at: float = field(default_factory=current_timestamp)


@dataclass(frozen=True, kw_only=True)
class PlanningRequest:
    request_id: str
    source_format: str
    target_format: str
    constraint: PlanConstraint | None = None
    requirement: PlanRequirement | None = None


@dataclass(frozen=True, kw_only=True)
class PlanningResult:
    request_id: str
    status: str = "success"
    selected_plan: TransformationPlan | None = None
    candidate_plans: tuple[TransformationPlan, ...] = field(default_factory=tuple)
    duration_seconds: float = 0.0

