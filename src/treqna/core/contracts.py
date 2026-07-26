from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from treqna.core.context import ExecutionStatistics, TransformationMetadata
from treqna.core.enums import PipelineStageEnum, ResultStatusEnum
from treqna.core.udm import UDMDocument, UDMNode


@dataclass(frozen=True, kw_only=True)
class TransformationRequest:
    source_format: str
    target_format: str
    payload: UDMDocument | UDMNode | bytes | str
    options: Mapping[str, Any] = field(default_factory=dict)
    metadata: TransformationMetadata | None = None


@dataclass(frozen=True, kw_only=True)
class StageResult:
    stage: PipelineStageEnum
    status: ResultStatusEnum
    output_data: UDMDocument | UDMNode | bytes | str | None = None
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    duration_seconds: float = 0.0


@dataclass(frozen=True, kw_only=True)
class TransformationResult:
    request_id: str
    status: ResultStatusEnum
    output_format: str
    result_data: UDMDocument | UDMNode | bytes | str | None = None
    stage_results: tuple[StageResult, ...] = field(default_factory=tuple)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    statistics: ExecutionStatistics = field(default_factory=ExecutionStatistics)

