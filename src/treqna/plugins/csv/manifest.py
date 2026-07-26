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
from treqna.formats.models import (
    Extension,
    FormatDescriptor,
    MimeType,
    QualityMetrics,
)
from treqna.formats.registry import FormatRegistry
from treqna.plugins.csv.detector import CSVDetector
from treqna.plugins.csv.inspector import CSVInspector
from treqna.plugins.csv.parser import CSVParserPlugin
from treqna.plugins.csv.validator import CSVValidator
from treqna.plugins.csv.writer import CSVWriterPlugin
from treqna.plugins.registry import PluginRegistry

CSV_FORMAT_DESCRIPTOR = FormatDescriptor(
    name="CSV",
    description="Comma-Separated Values tabular format",
    extensions=Extension(primary="csv", aliases=("tsv", "txt")),
    mime_types=MimeType(
        primary="text/csv",
        aliases=("text/comma-separated-values", "text/tab-separated-values"),
    ),
    family=FormatFamily.TABULAR,
    encoding=EncodingEnum.UTF8,
    binary=False,
    supports_reading=True,
    supports_writing=True,
    supports_streaming=StreamingEnum.BIDIRECTIONAL,
    supports_metadata=MetadataSupportEnum.BASIC,
    supports_validation=ValidationSupportEnum.SYNTAX_ONLY,
    supports_repair=RepairSupportEnum.NONE,
    supports_preview=PreviewSupportEnum.TEXTUAL,
    compression=CompressionEnum.NONE,
    priority=PluginPriority.HIGH,
    quality_metrics=QualityMetrics(
        metadata_preservation=0.8,
        formatting_preservation=0.7,
        lossless_conversion=0.9,
        performance_score=0.95,
        memory_efficiency=0.95,
        reliability=1.0,
        compatibility=1.0,
    ),
)


class CSVPluginManifest:
    descriptor: FormatDescriptor = CSV_FORMAT_DESCRIPTOR
    parser: CSVParserPlugin = CSVParserPlugin()
    writer: CSVWriterPlugin = CSVWriterPlugin()
    detector: CSVDetector = CSVDetector()
    inspector: CSVInspector = CSVInspector()
    validator: CSVValidator = CSVValidator()


def register_csv_plugin(
    plugin_registry: PluginRegistry,
    format_registry: FormatRegistry | None = None,
) -> None:
    manifest = CSVPluginManifest()
    plugin_registry.register_parser(manifest.parser)
    plugin_registry.register_writer(manifest.writer)
    if format_registry is not None:
        format_registry.register_descriptor(manifest.descriptor)

