import io
import random
import string
import pytest

from treqna.core.context import (
    ExecutionContext,
    PipelineContext,
    TransformationMetadata,
)
from treqna.core.udm import (
    UDMCollection,
    UDMDocument,
    UDMPrimitive,
    UDMTabular,
)
from treqna.formats.registry import FormatRegistry
from treqna.plugins.registry import PluginRegistry
from treqna.plugins.xml import (
    XMLDetector,
    XMLInspector,
    XMLOptions,
    XMLParserPlugin,
    XMLPluginManifest,
    XMLValidator,
    XMLWriterPlugin,
    register_xml_plugin,
)
from treqna.plugins.xml.parser import extract_xml_options


def create_mock_context(attributes: dict[str, object] | None = None) -> PipelineContext:
    metadata = TransformationMetadata(
        request_id="test_xml_req",
        custom_attributes=attributes if attributes is not None else {},
    )
    exec_ctx = ExecutionContext(
        current_format="xml",
        target_format="udm",
        metadata=metadata,
    )
    return PipelineContext(session_id="test_xml_sess", execution_context=exec_ctx)


def test_extract_xml_options_nil_context() -> None:
    opts1 = extract_xml_options(None)
    assert opts1.indent == 2
    assert opts1.root_tag == "root"

    exec_ctx = ExecutionContext(current_format="xml", target_format="udm")
    p_ctx = PipelineContext(session_id="test", execution_context=exec_ctx)
    opts2 = extract_xml_options(p_ctx)
    assert opts2.indent == 2


def test_xml_parser_basic() -> None:
    parser = XMLParserPlugin()
    context = create_mock_context()
    raw_xml = "<root><item><id>1</id><name>Alice</name></item></root>"

    doc = parser.parse_to_udm(raw_xml, context)
    assert isinstance(doc.root, UDMTabular)
    assert "id" in doc.root.columns
    assert "name" in doc.root.columns


def test_xml_parser_attributes_and_namespaces() -> None:
    parser = XMLParserPlugin()
    context = create_mock_context()
    raw_xml = '<ns:root xmlns:ns="http://example.com" id="100"><item id="1">Text</item></ns:root>'

    doc = parser.parse_to_udm(raw_xml, context)
    assert isinstance(doc.root, (UDMTabular, UDMPrimitive))


def test_xml_parser_primitive_and_empty() -> None:
    parser = XMLParserPlugin()
    context = create_mock_context()

    empty_doc = parser.parse_to_udm("", context)
    assert isinstance(empty_doc.root, UDMPrimitive)
    assert empty_doc.root.value is None

    prim_doc = parser.parse_to_udm("<root>hello</root>", context)
    assert isinstance(prim_doc.root, UDMPrimitive)
    assert prim_doc.root.value == "hello"


def test_xml_parser_utf16() -> None:
    parser = XMLParserPlugin()
    context = create_mock_context({"encoding": "utf-16"})
    text = "<?xml version='1.0' encoding='utf-16'?><root><msg>hello 🌟</msg></root>"
    encoded_utf16 = text.encode("utf-16")

    doc = parser.parse_to_udm(encoded_utf16, context)
    assert isinstance(doc.root, (UDMTabular, UDMPrimitive))


def test_xml_parser_streaming() -> None:
    parser = XMLParserPlugin()
    lines = ["<root>", "<item><id>1</id></item>", "</root>"]
    doc = parser.stream_parse_to_udm(lines)

    assert isinstance(doc.root, (UDMTabular, UDMPrimitive))

    empty_doc = parser.stream_parse_to_udm([])
    assert isinstance(empty_doc.root, UDMPrimitive)


def test_xml_writer_basic() -> None:
    writer = XMLWriterPlugin()
    context = create_mock_context({"indent": 2, "root_tag": "data", "row_tag": "row"})
    tabular = UDMTabular(
        columns=("id", "name"),
        rows=((1, "Alice"),),
    )
    doc = UDMDocument(root=tabular)

    output = writer.write_from_udm(doc, context)
    assert "<data>" in output
    assert "<row>" in output
    assert "<name>Alice</name>" in output


def test_xml_writer_streaming() -> None:
    writer = XMLWriterPlugin()
    doc = UDMDocument(root=UDMPrimitive(value={"key": "val"}))
    stream = io.StringIO()

    writer.stream_write_from_udm(doc, stream, XMLOptions(root_tag="dataset"))
    result = stream.getvalue()
    assert "<dataset>" in result
    assert "<key>val</key>" in result


def test_xml_detector() -> None:
    detector = XMLDetector()
    xml_header = "<?xml version='1.0'?><root></root>"
    xml_element = "<root><child>value</child></root>"

    assert detector.can_detect(xml_header) is True
    assert detector.can_detect(xml_element) is True
    assert detector.can_detect('{"json": "only"}') is False
    assert detector.can_detect("") is False

    assert detector.detect_format(xml_header) == "xml"
    assert detector.detect_format("plain_text") == "unknown"


def test_xml_inspector() -> None:
    inspector = XMLInspector()

    raw_xml = '<!DOCTYPE root><root id="1"><item><![CDATA[cdata]]></item></root>'
    info = inspector.inspect_schema(raw_xml)

    assert info["structure_type"] == "document"
    assert info["root_tag"] == "root"
    assert info["element_count"] == 2
    assert info["has_cdata"] is True
    assert info["has_doctype"] is True

    empty_info = inspector.inspect_schema("")
    assert empty_info["structure_type"] == "empty"

    malformed_info = inspector.inspect_schema("<root><unclosed>")
    assert malformed_info["structure_type"] == "malformed"


def test_xml_validator() -> None:
    validator = XMLValidator()
    valid_xml = "<root><item>1</item></root>"
    invalid_xml = "<root><item>1</root>"

    assert validator.validate_output(valid_xml) is True
    assert validator.validate_output("") is True

    valid, errors = validator.validate_xml_structure(invalid_xml)
    assert valid is False
    assert len(errors) > 0


def test_xml_plugin_registration() -> None:
    plugin_reg = PluginRegistry()
    format_reg = FormatRegistry()

    register_xml_plugin(plugin_reg, format_reg)

    parser = plugin_reg.get_parser("xml")
    writer = plugin_reg.get_writer("xml")
    descriptor = format_reg.get_descriptor("xml")

    assert parser.metadata.name == "xml_parser"
    assert writer.metadata.name == "xml_writer"
    assert descriptor.name == "XML"


def test_xml_manifest_metadata() -> None:
    manifest = XMLPluginManifest()
    assert manifest.parser.format_identifier == "xml"
    assert manifest.writer.format_identifier == "xml"

    manifest.parser.initialize(create_mock_context())
    manifest.parser.shutdown()
    manifest.writer.initialize(create_mock_context())
    manifest.writer.shutdown()


def test_xml_parser_booleans_floats_and_repeated_tags() -> None:
    parser = XMLParserPlugin()
    context = create_mock_context()
    raw_xml = "<root><b1>true</b1><b2>false</b2><f>12.34</f><tag>val1</tag><tag>val2</tag></root>"

    doc = parser.parse_to_udm(raw_xml, context)
    assert isinstance(doc.root, UDMTabular)


def test_xml_writer_primitive_and_collection() -> None:
    writer = XMLWriterPlugin()
    context = create_mock_context({"root_tag": "records", "row_tag": "entry"})

    doc = UDMDocument(root=UDMCollection(items=(UDMPrimitive(value=10), UDMPrimitive(value=20))))
    output = writer.write_from_udm(doc, context)
    assert "<records>" in output


def test_xml_writer_nested_dict_and_list() -> None:
    writer = XMLWriterPlugin()
    context = create_mock_context()
    nested_data = {
        "user": {
            "@id": 42,
            "#text": "Alice",
            "tags": ["admin", "dev"],
            "meta": [{"key": "k1"}, {"key": "k2"}],
        }
    }
    doc = UDMDocument(root=UDMPrimitive(value=nested_data))
    output = writer.write_from_udm(doc, context)

    assert 'id="42"' in output
    assert "<tags>admin</tags>" in output
    assert "<key>k1</key>" in output


def test_xml_detector_unknown() -> None:
    detector = XMLDetector()
    assert detector.detect_format("invalid_text") == "unknown"


def test_xml_writer_formatting_options() -> None:
    writer = XMLWriterPlugin()
    context = create_mock_context({"pretty_print": False, "xml_declaration": False})
    doc = UDMDocument(root=UDMPrimitive(value={"key": "val"}))

    output = writer.write_from_udm(doc, context)
    assert "<root>" in output
    assert not output.startswith("<?xml")


def test_xml_parser_malformed_raw_fallback() -> None:
    parser = XMLParserPlugin()
    context = create_mock_context()

    doc = parser.parse_to_udm("<unclosed>", context)
    assert doc.schema_identifier == "xml_raw"

    stream_doc = parser.stream_parse_to_udm(["<unclosed>"])
    assert stream_doc.schema_identifier == "xml_stream_raw"


def test_xml_random_fuzzing() -> None:
    parser = XMLParserPlugin()
    context = create_mock_context()
    random.seed(42)

    for _ in range(50):
        chars = "".join(random.choices(string.printable, k=50))
        doc = parser.parse_to_udm(chars, context)
        assert isinstance(doc.root, (UDMTabular, UDMCollection, UDMPrimitive))

