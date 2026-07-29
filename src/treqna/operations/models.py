from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from treqna.formats.enums import FormatFamily
from treqna.operations.enums import (
    OperationCapability,
    OperationCategory,
    OperationPriority,
)


@dataclass(frozen=True, kw_only=True)
class OperationRequirement:
    required_memory_bytes: int = 0
    required_cpu_cores: int = 1
    required_packages: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, kw_only=True)
class OperationConstraint:
    max_payload_bytes: int | None = None
    min_payload_bytes: int | None = None
    custom_constraints: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class OperationMetadata:
    identifier: str
    version: str = "1.0.0"
    author: str = ""
    attributes: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class OperationStatistics:
    invocations_count: int = 0
    total_execution_time_seconds: float = 0.0
    average_duration_seconds: float = 0.0
    success_rate: float = 1.0


@dataclass(frozen=True, kw_only=True)
class OperationCost:
    time_complexity_score: float = 1.0
    memory_cost_mb: float = 1.0
    cpu_cost_score: float = 1.0

    def compute_cost_score(self) -> float:
        return (
            self.time_complexity_score * 0.4
            + self.memory_cost_mb * 0.3
            + self.cpu_cost_score * 0.3
        )


@dataclass(frozen=True, kw_only=True)
class OperationContext:
    operation_id: str
    request_id: str
    options: Mapping[str, Any] = field(default_factory=dict)
    metadata: OperationMetadata | None = None


@dataclass(frozen=True, kw_only=True)
class OperationResult:
    operation_id: str
    status: str
    output_data: Any = None
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    statistics: OperationStatistics | None = None


@dataclass(frozen=True, kw_only=True)
class OperationDescriptor:
    name: str
    description: str = ""
    category: OperationCategory = OperationCategory.TRANSFORM
    consumes: tuple[str, ...] = field(default_factory=tuple)
    produces: tuple[str, ...] = field(default_factory=tuple)
    supported_format_families: tuple[FormatFamily, ...] = field(default_factory=tuple)
    priority: OperationPriority = OperationPriority.NORMAL
    estimated_cost: OperationCost = field(default_factory=OperationCost)
    streaming_support: bool = False
    thread_safety: bool = True
    deterministic: bool = True
    reversible: bool = False
    lossless: bool = True
    capabilities: tuple[OperationCapability, ...] = field(default_factory=tuple)
    constraints: OperationConstraint = field(default_factory=OperationConstraint)
    requirements: OperationRequirement = field(default_factory=OperationRequirement)
