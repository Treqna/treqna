from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from treqna.planning.context import PlannerContext, PlanningRequest, PlanningResult
from treqna.planning.models import TransformationPlan


class PlanningRule(ABC):
    @property
    @abstractmethod
    def rule_name(self) -> str:
        ...

    @abstractmethod
    def evaluate(self, plan: TransformationPlan, context: PlannerContext) -> bool:
        ...


@dataclass(frozen=True, kw_only=True)
class PlanningPolicy:
    name: str = "default_policy"
    rules: tuple[PlanningRule, ...] = field(default_factory=tuple)
    allow_lossy: bool = False
    prefer_speed: bool = True


class PlanningStrategy(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @abstractmethod
    def create_plan(
        self,
        request: PlanningRequest,
        context: PlannerContext,
    ) -> PlanningResult:
        ...
