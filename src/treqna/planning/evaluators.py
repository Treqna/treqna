from abc import ABC, abstractmethod
from collections.abc import Sequence

from treqna.planning.models import (
    PlanConstraint,
    PlanCost,
    PlanEdge,
    PlanNode,
    PlanQuality,
    TransformationPlan,
)
from treqna.planning.strategy import PlanningPolicy


class CostEstimator(ABC):
    @abstractmethod
    def estimate_cost(self, plan: TransformationPlan) -> PlanCost:
        ...


class QualityEstimator(ABC):
    @abstractmethod
    def estimate_quality(self, plan: TransformationPlan) -> PlanQuality:
        ...


class PathEvaluator(ABC):
    @abstractmethod
    def evaluate_path(
        self,
        nodes: Sequence[PlanNode],
        edges: Sequence[PlanEdge],
    ) -> tuple[PlanCost, PlanQuality]:
        ...


class PathScorer(ABC):
    @abstractmethod
    def score_path(
        self,
        cost: PlanCost,
        quality: PlanQuality,
        policy: PlanningPolicy,
    ) -> float:
        ...


class RouteSelector(ABC):
    @abstractmethod
    def select_best_route(
        self,
        candidate_plans: Sequence[TransformationPlan],
        policy: PlanningPolicy,
    ) -> TransformationPlan | None:
        ...


class CapabilityMatcher(ABC):
    @abstractmethod
    def matches_capabilities(self, source_format: str, target_format: str) -> bool:
        ...


class ConstraintSolver(ABC):
    @abstractmethod
    def satisfies_constraints(
        self,
        plan: TransformationPlan,
        constraint: PlanConstraint,
    ) -> bool:
        ...
