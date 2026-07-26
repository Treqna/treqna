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
from treqna.plugins.yaml import (
    YAMLDetector,
    YAMLInspector,
    YAMLOptions,
    YAMLParserPlugin,
    YAMLPluginManifest,
    YAMLValidator,
    YAMLWriterPlugin,
    register_yaml_plugin,
)
from treqna.plugins.yaml.parser import extract_yaml_options


def create_mock_context(attributes: dict[str, object] | None = None) -> PipelineContext:
    metadata = TransformationMetadata(
        request_id="test_yaml_req",
        custom_attributes=attributes if attributes is not None else {},
    )
    exec_ctx = ExecutionContext(
        current_format="yaml",
        target_format="udm",
        metadata=metadata,
    )
    return PipelineContext(session_id="test_yaml_sess", execution_context=exec_ctx)


def test_extract_yaml_options_nil_context() -> None:
    opts1 = extract_yaml_options(None)
    assert opts1.indent == 2

    exec_ctx = ExecutionContext(current_format="yaml", target_format="udm")
    p_ctx = PipelineContext(session_id="test", execution_context=exec_ctx)
    opts2 = extract_yaml_options(p_ctx)
    assert opts2.indent == 2


def test_yaml_parser_single_doc_mapping() -> None:
    parser = YAMLParserPlugin()
    context = create_mock_context()
    raw_yaml = "id: 101\nname: Alice\nactive: true\n"

    doc = parser.parse_to_udm(raw_yaml, context)
    assert isinstance(doc.root, UDMTabular)
    assert doc.root.columns == ("id", "name", "active")
    assert doc.root.rows[0] == (101, "Alice", True)


def test_yaml_parser_sequence_of_dicts() -> None:
    parser = YAMLParserPlugin()
    context = create_mock_context()
    raw_yaml = "- id: 1\n  name: Alice\n- id: 2\n  name: Bob\n"

    doc = parser.parse_to_udm(raw_yaml, context)
    assert isinstance(doc.root, UDMTabular)
    assert len(doc.root.rows) == 2


def test_yaml_parser_multi_document() -> None:
    parser = YAMLParserPlugin()
    context = create_mock_context({"is_multi_document": True})
    raw_yaml = "---\nid: 1\nname: Doc1\n---\nid: 2\nname: Doc2\n"

    doc = parser.parse_to_udm(raw_yaml, context)
    assert isinstance(doc.root, UDMCollection)
    assert len(doc.root.items) == 2


def test_yaml_parser_anchors_and_aliases() -> None:
    parser = YAMLParserPlugin()
    context = create_mock_context()
    raw_yaml = "default: &default\n  role: dev\nuser1:\n  <<: *default\n  name: Alice\n"

    doc = parser.parse_to_udm(raw_yaml, context)
    assert isinstance(doc.root, UDMTabular)


def test_yaml_parser_primitive_and_empty() -> None:
    parser = YAMLParserPlugin()
    context = create_mock_context()

    empty_doc = parser.parse_to_udm("", context)
    assert isinstance(empty_doc.root, UDMPrimitive)
    assert empty_doc.root.value is None

    prim_doc = parser.parse_to_udm("123.456", context)
    assert isinstance(prim_doc.root, UDMPrimitive)
    assert prim_doc.root.value == 123.456


def test_yaml_parser_utf16() -> None:
    parser = YAMLParserPlugin()
    context = create_mock_context({"encoding": "utf-16"})
    text = "msg: hello 🚀\n"
    encoded_utf16 = text.encode("utf-16")

    doc = parser.parse_to_udm(encoded_utf16, context)
    assert isinstance(doc.root, UDMTabular)
    assert doc.root.rows[0][0] == "hello 🚀"


def test_yaml_parser_streaming() -> None:
    parser = YAMLParserPlugin()
    lines = ["name: Test\n", "items: [1, 2]\n"]
    doc = parser.stream_parse_to_udm(lines)

    assert isinstance(doc.root, UDMTabular)

    empty_doc = parser.stream_parse_to_udm([])
    assert isinstance(empty_doc.root, UDMPrimitive)


def test_yaml_writer_basic() -> None:
    writer = YAMLWriterPlugin()
    context = create_mock_context({"indent": 2, "sort_keys": True})
    tabular = UDMTabular(
        columns=("b", "a"),
        rows=((2, 1),),
    )
    doc = UDMDocument(root=tabular)

    output = writer.write_from_udm(doc, context)
    assert "a: 1" in output and "b: 2" in output


def test_yaml_writer_multi_document() -> None:
    writer = YAMLWriterPlugin()
    context = create_mock_context({"is_multi_document": True, "explicit_start": True})
    doc1 = UDMPrimitive(value={"id": 1})
    doc2 = UDMPrimitive(value={"id": 2})
    coll = UDMCollection(items=(doc1, doc2))

    output = writer.write_from_udm(UDMDocument(root=coll), context)
    assert "---" in output


def test_yaml_writer_streaming() -> None:
    writer = YAMLWriterPlugin()
    doc = UDMDocument(root=UDMPrimitive(value={"key": "val"}))
    stream = io.StringIO()

    writer.stream_write_from_udm(doc, stream, YAMLOptions(indent=2))
    result = stream.getvalue()
    assert "key: val" in result


def test_yaml_detector() -> None:
    detector = YAMLDetector()
    yaml_header = "---\nname: test"
    yaml_mapping = "name: Alice\nrole: Admin\n"

    assert detector.can_detect(yaml_header) is True
    assert detector.can_detect(yaml_mapping) is True
    assert detector.can_detect('{"json": "only"}') is False
    assert detector.can_detect("") is False

    assert detector.detect_format(yaml_header) == "yaml"
    assert detector.detect_format("plain_text_without_delimiters") == "unknown"


def test_yaml_inspector() -> None:
    inspector = YAMLInspector()

    obj_info = inspector.inspect_schema("a: 1\nb: 2\n")
    assert obj_info["structure_type"] == "object"
    assert obj_info["key_count"] == 2

    arr_info = inspector.inspect_schema("- x: 10\n- x: 20\n")
    assert arr_info["structure_type"] == "array"
    assert arr_info["item_count"] == 2

    multi_info = inspector.inspect_schema("---\na: 1\n---\nb: 2\n")
    assert multi_info["is_multi_document"] is True

    empty_info = inspector.inspect_schema("")
    assert empty_info["structure_type"] == "empty"

    malformed_info = inspector.inspect_schema(":\n  - :\n")
    assert malformed_info["structure_type"] == "malformed" or malformed_info["structure_type"] != ""


def test_yaml_validator() -> None:
    validator = YAMLValidator()
    valid_yaml = "a: 1\n"
    invalid_yaml = "a: [unclosed sequence"

    assert validator.validate_output(valid_yaml) is True
    assert validator.validate_output("") is True

    valid, errors = validator.validate_yaml_structure(invalid_yaml)
    assert valid is False
    assert len(errors) > 0


def test_yaml_plugin_registration() -> None:
    plugin_reg = PluginRegistry()
    format_reg = FormatRegistry()

    register_yaml_plugin(plugin_reg, format_reg)

    parser = plugin_reg.get_parser("yaml")
    writer = plugin_reg.get_writer("yaml")
    descriptor = format_reg.get_descriptor("yaml")

    assert parser.metadata.name == "yaml_parser"
    assert writer.metadata.name == "yaml_writer"
    assert descriptor.name == "YAML"


def test_yaml_manifest_metadata() -> None:
    manifest = YAMLPluginManifest()
    assert manifest.parser.format_identifier == "yaml"
    assert manifest.writer.format_identifier == "yaml"

    manifest.parser.initialize(create_mock_context())
    manifest.parser.shutdown()
    manifest.writer.initialize(create_mock_context())
    manifest.writer.shutdown()


def test_yaml_detector_unknown() -> None:
    detector = YAMLDetector()
    assert detector.detect_format("plain text without colon") == "unknown"


def test_yaml_inspector_primitive_and_malformed() -> None:
    inspector = YAMLInspector()

    prim = inspector.inspect_schema("just_a_string")
    assert prim["structure_type"] == "primitive"

    malformed = inspector.inspect_schema("key: [unclosed")
    assert malformed["structure_type"] == "malformed"


def test_yaml_parser_empty_and_stream_raw() -> None:
    parser = YAMLParserPlugin()
    doc = parser.stream_parse_to_udm(["invalid: [unclosed"])
    assert doc.schema_identifier == "yaml_stream_raw"


def test_yaml_random_fuzzing() -> None:
    parser = YAMLParserPlugin()
    context = create_mock_context()
    random.seed(42)

    for _ in range(50):
        chars = "".join(random.choices(string.printable, k=50))
        doc = parser.parse_to_udm(chars, context)
        assert isinstance(doc.root, (UDMTabular, UDMCollection, UDMPrimitive))

