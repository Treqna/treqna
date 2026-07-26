import pytest

from treqna.formats.enums import (
    FormatCapability,
    FormatFamily,
    PluginPriority,
)
from treqna.formats.models import (
    Extension,
    FormatDescriptor,
    MimeType,
    QualityMetrics,
)
from treqna.formats.registry import FormatNotFoundError, FormatRegistry


def create_json_descriptor() -> FormatDescriptor:
    return FormatDescriptor(
        name="JSON",
        description="JavaScript Object Notation",
        extensions=Extension(primary="json", aliases=("jsonc",)),
        mime_types=MimeType(primary="application/json"),
        family=FormatFamily.STRUCTURED,
        binary=False,
        supports_reading=True,
        supports_writing=True,
        priority=PluginPriority.HIGH,
        quality_metrics=QualityMetrics(
            metadata_preservation=0.9,
            formatting_preservation=0.8,
            lossless_conversion=1.0,
        ),
    )


def create_xml_descriptor() -> FormatDescriptor:
    return FormatDescriptor(
        name="XML",
        description="Extensible Markup Language",
        extensions=Extension(primary="xml"),
        mime_types=MimeType(primary="application/xml"),
        family=FormatFamily.HIERARCHICAL,
        binary=False,
        supports_reading=True,
        supports_writing=True,
        priority=PluginPriority.NORMAL,
        quality_metrics=QualityMetrics(
            metadata_preservation=0.95,
            formatting_preservation=0.85,
            lossless_conversion=0.95,
        ),
    )


def test_format_descriptor_immutability() -> None:
    descriptor = create_json_descriptor()

    assert descriptor.name == "JSON"
    assert descriptor.family == FormatFamily.STRUCTURED
    assert descriptor.extensions.primary == "json"

    with pytest.raises(AttributeError):
        descriptor.name = "XML"  # type: ignore[misc]


def test_format_registry_lookup() -> None:
    registry = FormatRegistry()
    json_desc = create_json_descriptor()
    registry.register_descriptor(json_desc)

    by_name = registry.get_descriptor("json")
    by_ext = registry.get_descriptor("jsonc")
    by_mime = registry.get_descriptor("application/json")

    assert by_name.name == "JSON"
    assert by_ext.name == "JSON"
    assert by_mime.name == "JSON"


def test_format_registry_not_found() -> None:
    registry = FormatRegistry()
    with pytest.raises(FormatNotFoundError):
        registry.get_descriptor("unknown_format")


def test_planner_find_best_descriptor() -> None:
    registry = FormatRegistry()
    json_desc = create_json_descriptor()
    xml_desc = create_xml_descriptor()

    registry.register_descriptor(json_desc)
    registry.register_descriptor(xml_desc)

    best = registry.find_best_descriptor(FormatCapability.READ)
    assert best is not None
    assert best.name == "JSON"

