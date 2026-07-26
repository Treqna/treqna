import pytest

from treqna.planning.context import PlanningRequest
from treqna.planning.knowledge import (
    KnowledgeGraph,
    PluginHistory,
    TransformationHistory,
    TransformationKnowledge,
)
from treqna.planning.models import (
    PipelineFingerprint,
    PlanConstraint,
    PlanCost,
    PlanQuality,
    PlanRequirement,
)
from treqna.planning.planner import Planner


def test_fingerprint_creation() -> None:
    fp = PipelineFingerprint(
        input_format="json",
        output_format="xml",
        pipeline_hash="abc123hash",
        plugin_versions={"json_parser": "1.0.0", "xml_writer": "1.2.0"},
    )

    assert fp.input_format == "json"
    assert fp.output_format == "xml"
    assert fp.pipeline_hash == "abc123hash"
    assert fp.plugin_versions["json_parser"] == "1.0.0"


def test_knowledge_graph_structure() -> None:
    hist = TransformationHistory(
        transformation_id="tx_1",
        timestamp=1000.0,
        source_format="csv",
        target_format="json",
        success=True,
        duration_seconds=0.15,
        metadata_preservation=1.0,
    )
    p_hist = PluginHistory(
        plugin_name="csv_parser",
        version="2.0.0",
        total_invocations=10,
        successful_invocations=10,
    )
    tk = TransformationKnowledge(
        history=(hist,),
        plugin_histories={"csv_parser": p_hist},
    )
    kg = KnowledgeGraph(knowledge=tk)

    assert len(kg.knowledge.history) == 1
    assert kg.knowledge.plugin_histories["csv_parser"].success_rate == 1.0


def test_planner_create_plan() -> None:
    planner = Planner()
    req = PlanningRequest(
        request_id="req_100",
        source_format="json",
        target_format="xml",
        constraint=PlanConstraint(require_lossless=True),
        requirement=PlanRequirement(required_memory_bytes=1024),
    )

    result = planner.create_plan(req)

    assert result.status == "success"
    assert result.selected_plan is not None
    assert result.selected_plan.fingerprint.input_format == "json"
    assert result.selected_plan.fingerprint.output_format == "xml"
    assert len(result.selected_plan.nodes) == 3
    assert len(result.selected_plan.edges) == 2


def test_plan_cost_and_quality_defaults() -> None:
    cost = PlanCost()
    quality = PlanQuality()

    assert cost.time_complexity_score == 1.0
    assert quality.metadata_preservation == 1.0
