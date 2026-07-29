from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, kw_only=True)
class PlanRequirement:
    required_memory_bytes: int = 0
    required_cpu_cores: int = 1
    max_allowed_duration_seconds: float = 60.0


@dataclass(frozen=True, kw_only=True)
class PlanConstraint:
    require_lossless: bool = False
    require_streaming: bool = False
    max_cost_score: float | None = None
    custom_rules: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class PlanStatistics:
    node_count: int = 0
    edge_count: int = 0
    estimated_duration_seconds: float = 0.0
    estimated_memory_bytes: int = 0


@dataclass(frozen=True, kw_only=True)
class PlanCost:
    time_complexity_score: float = 1.0
    memory_cost_mb: float = 1.0
    cpu_cost_score: float = 1.0
    composite_cost: float = 1.0


@dataclass(frozen=True, kw_only=True)
class PlanQuality:
    metadata_preservation: float = 1.0
    formatting_preservation: float = 1.0
    lossless_score: float = 1.0
    reliability_score: float = 1.0
    composite_quality: float = 1.0


@dataclass(frozen=True, kw_only=True)
class PipelineFingerprint:
    input_format: str
    output_format: str
    pipeline_hash: str
    plugin_versions: Mapping[str, str] = field(default_factory=dict)
    capabilities: tuple[str, ...] = field(default_factory=tuple)
    planner_version: str = "1.0.0"


@dataclass(frozen=True, kw_only=True)
class PlanNode:
    node_id: str
    operation_name: str
    format_name: str


@dataclass(frozen=True, kw_only=True)
class PlanEdge:
    source_node_id: str
    target_node_id: str
    data_label: str = ""


@dataclass(frozen=True, kw_only=True)
class TransformationPlan:
    plan_id: str
    request_id: str
    nodes: tuple[PlanNode, ...] = field(default_factory=tuple)
    edges: tuple[PlanEdge, ...] = field(default_factory=tuple)
    fingerprint: PipelineFingerprint
    estimated_cost: PlanCost = field(default_factory=PlanCost)
    estimated_quality: PlanQuality = field(default_factory=PlanQuality)
    statistics: PlanStatistics = field(default_factory=PlanStatistics)
