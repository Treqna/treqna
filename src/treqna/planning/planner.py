import hashlib
import time
import uuid

from treqna.planning.context import PlannerContext, PlanningRequest, PlanningResult
from treqna.planning.knowledge import KnowledgeGraph
from treqna.planning.models import (
    PipelineFingerprint,
    PlanCost,
    PlanEdge,
    PlanNode,
    PlanQuality,
    PlanStatistics,
    TransformationPlan,
)
from treqna.planning.strategy import PlanningPolicy


def generate_plan_id() -> str:
    return str(uuid.uuid4())


def compute_fingerprint_hash(source_format: str, target_format: str) -> str:
    raw = f"{source_format}->{target_format}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


class Planner:
    def __init__(
        self,
        knowledge_graph: KnowledgeGraph | None = None,
        policy: PlanningPolicy | None = None,
    ) -> None:
        self.knowledge_graph = (
            knowledge_graph if knowledge_graph is not None else KnowledgeGraph()
        )
        self.policy = policy if policy is not None else PlanningPolicy()

    def create_plan(
        self,
        request: PlanningRequest,
        context: PlannerContext | None = None,
    ) -> PlanningResult:
        start_time = time.perf_counter()
        fingerprint = PipelineFingerprint(
            input_format=request.source_format,
            output_format=request.target_format,
            pipeline_hash=compute_fingerprint_hash(
                request.source_format,
                request.target_format,
            ),
        )

        n1 = PlanNode(
            node_id="n1",
            operation_name="parse",
            format_name=request.source_format,
        )
        n2 = PlanNode(node_id="n2", operation_name="udm", format_name="udm")
        n3 = PlanNode(
            node_id="n3",
            operation_name="write",
            format_name=request.target_format,
        )

        e1 = PlanEdge(source_node_id="n1", target_node_id="n2", data_label="raw_to_udm")
        e2 = PlanEdge(
            source_node_id="n2", target_node_id="n3", data_label="udm_to_target"
        )

        cost = PlanCost()
        quality = PlanQuality()
        stats = PlanStatistics(node_count=3, edge_count=2)

        plan = TransformationPlan(
            plan_id=generate_plan_id(),
            request_id=request.request_id,
            nodes=(n1, n2, n3),
            edges=(e1, e2),
            fingerprint=fingerprint,
            estimated_cost=cost,
            estimated_quality=quality,
            statistics=stats,
        )

        duration = time.perf_counter() - start_time
        return PlanningResult(
            request_id=request.request_id,
            status="success",
            selected_plan=plan,
            candidate_plans=(plan,),
            duration_seconds=duration,
        )
