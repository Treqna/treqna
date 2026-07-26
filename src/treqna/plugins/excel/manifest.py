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
from treqna.plugins.excel.detector import ExcelDetector
from treqna.plugins.excel.inspector import ExcelInspector
from treqna.plugins.excel.parser import ExcelParserPlugin
from treqna.plugins.excel.validator import ExcelValidator
from treqna.plugins.excel.writer import ExcelWriterPlugin
from treqna.plugins.registry import PluginRegistry

EXCEL_FORMAT_DESCRIPTOR = FormatDescriptor(
    name="EXCEL",
    description="Microsoft Excel OpenXML spreadsheet format (.xlsx)",
    extensions=Extension(primary="xlsx", aliases=("xls", "xlsm")),
    mime_types=MimeType(
        primary="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        aliases=("application/vnd.ms-excel",),
    ),
    family=FormatFamily.DOCUMENT,
    encoding=EncodingEnum.UTF8,
    binary=True,
    supports_reading=True,
    supports_writing=True,
    supports_streaming=StreamingEnum.BIDIRECTIONAL,
    supports_metadata=MetadataSupportEnum.FULL,
    supports_validation=ValidationSupportEnum.SCHEMA_STRICT,
    supports_repair=RepairSupportEnum.PARTIAL,
    supports_preview=PreviewSupportEnum.TEXTUAL,
    compression=CompressionEnum.ZIP,
    priority=PluginPriority.HIGH,
    quality_metrics=QualityMetrics(
        metadata_preservation=1.0,
        formatting_preservation=0.95,
        lossless_conversion=1.0,
        performance_score=0.95,
        memory_efficiency=0.95,
        reliability=1.0,
        compatibility=1.0,
    ),
)


class ExcelPluginManifest:
    descriptor: FormatDescriptor = EXCEL_FORMAT_DESCRIPTOR
    parser: ExcelParserPlugin = ExcelParserPlugin()
    writer: ExcelWriterPlugin = ExcelWriterPlugin()
    detector: ExcelDetector = ExcelDetector()
    inspector: ExcelInspector = ExcelInspector()
    validator: ExcelValidator = ExcelValidator()


def register_excel_plugin(
    plugin_registry: PluginRegistry,
    format_registry: FormatRegistry | None = None,
) -> None:
    manifest = ExcelPluginManifest()
    plugin_registry.register_parser(manifest.parser)
    plugin_registry.register_writer(manifest.writer)
    if format_registry is not None:
        format_registry.register_descriptor(manifest.descriptor)

