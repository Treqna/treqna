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
from treqna.plugins.xml.detector import XMLDetector
from treqna.plugins.xml.inspector import XMLInspector
from treqna.plugins.xml.parser import XMLParserPlugin
from treqna.plugins.xml.validator import XMLValidator
from treqna.plugins.xml.writer import XMLWriterPlugin

XML_FORMAT_DESCRIPTOR = FormatDescriptor(
    name="XML",
    description="Extensible Markup Language data format",
    extensions=Extension(primary="xml", aliases=("xsd", "svg")),
    mime_types=MimeType(
        primary="application/xml",
        aliases=("text/xml", "application/x-xml"),
    ),
    family=FormatFamily.DOCUMENT,
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


class XMLPluginManifest:
    descriptor: FormatDescriptor = XML_FORMAT_DESCRIPTOR
    parser: XMLParserPlugin = XMLParserPlugin()
    writer: XMLWriterPlugin = XMLWriterPlugin()
    detector: XMLDetector = XMLDetector()
    inspector: XMLInspector = XMLInspector()
    validator: XMLValidator = XMLValidator()


def register_xml_plugin(
    plugin_registry: PluginRegistry,
    format_registry: FormatRegistry | None = None,
) -> None:
    manifest = XMLPluginManifest()
    plugin_registry.register_parser(manifest.parser)
    plugin_registry.register_writer(manifest.writer)
    if format_registry is not None:
        format_registry.register_descriptor(manifest.descriptor)
