from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, kw_only=True)
class TransformationHistory:
    transformation_id: str
    timestamp: float
    source_format: str
    target_format: str
    success: bool
    duration_seconds: float
    metadata_preservation: float = 1.0
    failure_reason: str | None = None


@dataclass(frozen=True, kw_only=True)
class PluginHistory:
    plugin_name: str
    version: str
    total_invocations: int = 0
    successful_invocations: int = 0
    average_duration_seconds: float = 0.0
    historical_quality_score: float = 1.0
    historical_failures: tuple[str, ...] = field(default_factory=tuple)

    @property
    def success_rate(self) -> float:
        if self.total_invocations == 0:
            return 1.0
        return self.successful_invocations / self.total_invocations


@dataclass(frozen=True, kw_only=True)
class TransformationKnowledge:
    history: tuple[TransformationHistory, ...] = field(default_factory=tuple)
    plugin_histories: Mapping[str, PluginHistory] = field(default_factory=dict)
    attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class KnowledgeGraph:
    knowledge: TransformationKnowledge = field(
        default_factory=TransformationKnowledge
    )
    node_weights: Mapping[str, float] = field(default_factory=dict)
    edge_weights: Mapping[str, float] = field(default_factory=dict)

