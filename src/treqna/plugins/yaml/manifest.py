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
from treqna.plugins.registry import PluginRegistry
from treqna.plugins.yaml.detector import YAMLDetector
from treqna.plugins.yaml.inspector import YAMLInspector
from treqna.plugins.yaml.parser import YAMLParserPlugin
from treqna.plugins.yaml.validator import YAMLValidator
from treqna.plugins.yaml.writer import YAMLWriterPlugin

YAML_FORMAT_DESCRIPTOR = FormatDescriptor(
    name="YAML",
    description="YAML Ain't Markup Language data format",
    extensions=Extension(primary="yaml", aliases=("yml",)),
    mime_types=MimeType(
        primary="application/x-yaml",
        aliases=("text/yaml", "application/yaml"),
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


class YAMLPluginManifest:
    descriptor: FormatDescriptor = YAML_FORMAT_DESCRIPTOR
    parser: YAMLParserPlugin = YAMLParserPlugin()
    writer: YAMLWriterPlugin = YAMLWriterPlugin()
    detector: YAMLDetector = YAMLDetector()
    inspector: YAMLInspector = YAMLInspector()
    validator: YAMLValidator = YAMLValidator()


def register_yaml_plugin(
    plugin_registry: PluginRegistry,
    format_registry: FormatRegistry | None = None,
) -> None:
    manifest = YAMLPluginManifest()
    plugin_registry.register_parser(manifest.parser)
    plugin_registry.register_writer(manifest.writer)
    if format_registry is not None:
        format_registry.register_descriptor(manifest.descriptor)
