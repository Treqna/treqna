from dataclasses import dataclass, field

from treqna.formats.enums import (
    CompressionEnum,
    EncodingEnum,
    FormatFamily,
    MetadataSupportEnum,
    PluginPriority,
    PreviewSupportEnum,
    RepairSupportEnum,
    StreamingEnum,
    ValidationSupportEnum,
)


@dataclass(frozen=True, kw_only=True)
class MimeType:
    primary: str
    aliases: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, kw_only=True)
class Extension:
    primary: str
    aliases: tuple[str, ...] = field(default_factory=tuple)


@dataclass(frozen=True, kw_only=True)
class QualityMetrics:
    metadata_preservation: float = 1.0
    formatting_preservation: float = 1.0
    lossless_conversion: float = 1.0
    performance_score: float = 1.0
    memory_efficiency: float = 1.0
    reliability: float = 1.0
    compatibility: float = 1.0

    def compute_composite_score(self) -> float:
        scores = (
            self.metadata_preservation,
            self.formatting_preservation,
            self.lossless_conversion,
            self.performance_score,
            self.memory_efficiency,
            self.reliability,
            self.compatibility,
        )
        return sum(scores) / len(scores)


@dataclass(frozen=True, kw_only=True)
class PluginQuality:
    quality_metrics: QualityMetrics = field(default_factory=QualityMetrics)
    overall_score: float = field(default_factory=lambda: 1.0)


@dataclass(frozen=True, kw_only=True)
class FormatDescriptor:
    name: str
    description: str = ""
    extensions: Extension
    mime_types: MimeType
    family: FormatFamily
    encoding: EncodingEnum = EncodingEnum.UTF8
    binary: bool = False
    supports_reading: bool = True
    supports_writing: bool = True
    supports_streaming: StreamingEnum = StreamingEnum.UNSUPPORTED
    supports_metadata: MetadataSupportEnum = MetadataSupportEnum.NONE
    supports_validation: ValidationSupportEnum = ValidationSupportEnum.NONE
    supports_repair: RepairSupportEnum = RepairSupportEnum.NONE
    supports_preview: PreviewSupportEnum = PreviewSupportEnum.NONE
    compression: CompressionEnum = CompressionEnum.NONE
    priority: PluginPriority = PluginPriority.NORMAL
    quality_metrics: QualityMetrics = field(default_factory=QualityMetrics)

