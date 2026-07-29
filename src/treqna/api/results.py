from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from treqna.planning.models import PipelineFingerprint, TransformationPlan


@dataclass(frozen=True, kw_only=True)
class BaseApiResult:
    success: bool = True
    status: str = "success"
    output: Any = None
    metadata: Mapping[str, Any] = field(default_factory=dict)
    warnings: tuple[str, ...] = field(default_factory=tuple)
    errors: tuple[str, ...] = field(default_factory=tuple)
    statistics: Mapping[str, Any] = field(default_factory=dict)
    plan: TransformationPlan | None = None
    fingerprint: PipelineFingerprint | str | None = None
    duration: float = 0.0


@dataclass(frozen=True, kw_only=True)
class TransformationResult(BaseApiResult):
    pass


@dataclass(frozen=True, kw_only=True)
class InspectionResult(BaseApiResult):
    schema_info: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class ValidationResult(BaseApiResult):
    is_valid: bool = True
    validation_issues: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, kw_only=True)
class DetectionResult(BaseApiResult):
    detected_format: str = "unknown"
    confidence_score: float = 1.0


@dataclass(frozen=True, kw_only=True)
class PreviewResult(BaseApiResult):
    preview_content: str = ""


@dataclass(frozen=True, kw_only=True)
class ComparisonResult(BaseApiResult):
    identical: bool = True
    diff_summary: Mapping[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class CompressionResult(BaseApiResult):
    compressed_bytes_count: int = 0
    compression_ratio: float = 1.0


@dataclass(frozen=True, kw_only=True)
class ExtractionResult(BaseApiResult):
    extracted_items_count: int = 0


@dataclass(frozen=True, kw_only=True)
class MergeResult(BaseApiResult):
    merged_sources_count: int = 0


@dataclass(frozen=True, kw_only=True)
class SplitResult(BaseApiResult):
    split_parts_count: int = 0
