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
from treqna.plugins.json.detector import JSONDetector
from treqna.plugins.json.inspector import JSONInspector
from treqna.plugins.json.parser import JSONParserPlugin
from treqna.plugins.json.validator import JSONValidator
from treqna.plugins.json.writer import JSONWriterPlugin
from treqna.plugins.registry import PluginRegistry

JSON_FORMAT_DESCRIPTOR = FormatDescriptor(
    name="JSON",
    description="JavaScript Object Notation data format",
    extensions=Extension(primary="json", aliases=("jsonl", "ndjson")),
    mime_types=MimeType(
        primary="application/json",
        aliases=("text/json", "application/x-ndjson"),
    ),
    family=FormatFamily.HIERARCHICAL,
    encoding=EncodingEnum.UTF8,
    binary=False,
    supports_reading=True,
    supports_writing=True,
    supports_streaming=StreamingEnum.BIDIRECTIONAL,
    supports_metadata=MetadataSupportEnum.FULL,
    supports_validation=ValidationSupportEnum.SCHEMA_STRICT,
    supports_repair=RepairSupportEnum.PARTIAL,
    supports_preview=PreviewSupportEnum.TEXTUAL,
    compression=CompressionEnum.NONE,
    priority=PluginPriority.HIGH,
    quality_metrics=QualityMetrics(
        metadata_preservation=1.0,
        formatting_preservation=0.9,
        lossless_conversion=1.0,
        performance_score=0.95,
        memory_efficiency=0.9,
        reliability=1.0,
        compatibility=1.0,
    ),
)


class JSONPluginManifest:
    descriptor: FormatDescriptor = JSON_FORMAT_DESCRIPTOR
    parser: JSONParserPlugin = JSONParserPlugin()
    writer: JSONWriterPlugin = JSONWriterPlugin()
    detector: JSONDetector = JSONDetector()
    inspector: JSONInspector = JSONInspector()
    validator: JSONValidator = JSONValidator()


def register_json_plugin(
    plugin_registry: PluginRegistry,
    format_registry: FormatRegistry | None = None,
) -> None:
    manifest = JSONPluginManifest()
    plugin_registry.register_parser(manifest.parser)
    plugin_registry.register_writer(manifest.writer)
    if format_registry is not None:
        format_registry.register_descriptor(manifest.descriptor)

