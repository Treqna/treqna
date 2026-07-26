import io
import json
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
from treqna.plugins.json import (
    JSONDetector,
    JSONInspector,
    JSONOptions,
    JSONParserPlugin,
    JSONPluginManifest,
    JSONValidator,
    JSONWriterPlugin,
    register_json_plugin,
)
from treqna.plugins.json.parser import extract_json_options
from treqna.plugins.registry import PluginRegistry


def create_mock_context(attributes: dict[str, object] | None = None) -> PipelineContext:
    metadata = TransformationMetadata(
        request_id="test_json_req",
        custom_attributes=attributes if attributes is not None else {},
    )
    exec_ctx = ExecutionContext(
        current_format="json",
        target_format="udm",
        metadata=metadata,
    )
    return PipelineContext(session_id="test_json_sess", execution_context=exec_ctx)


def test_extract_json_options_nil_context() -> None:
    opts1 = extract_json_options(None)
    assert opts1.indent == 2

    exec_ctx = ExecutionContext(current_format="json", target_format="udm")
    p_ctx = PipelineContext(session_id="test", execution_context=exec_ctx)
    opts2 = extract_json_options(p_ctx)
    assert opts2.indent == 2


def test_json_parser_basic_object() -> None:
    parser = JSONParserPlugin()
    context = create_mock_context()
    raw_json = '{"id": 1, "name": "Alice", "active": true}'

    doc = parser.parse_to_udm(raw_json, context)
    assert isinstance(doc.root, UDMTabular)
    assert doc.root.columns == ("id", "name", "active")
    assert doc.root.rows[0] == (1, "Alice", True)


def test_json_parser_array_of_dicts() -> None:
    parser = JSONParserPlugin()
    context = create_mock_context()
    raw_json = '[{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob", "role": "dev"}]'

    doc = parser.parse_to_udm(raw_json, context)
    assert isinstance(doc.root, UDMTabular)
    assert "id" in doc.root.columns
    assert "role" in doc.root.columns
    assert len(doc.root.rows) == 2


def test_json_parser_primitive_and_empty() -> None:
    parser = JSONParserPlugin()
    context = create_mock_context()

    empty_doc = parser.parse_to_udm("", context)
    assert isinstance(empty_doc.root, UDMPrimitive)
    assert empty_doc.root.value is None

    prim_doc = parser.parse_to_udm("123.456", context)
    assert isinstance(prim_doc.root, UDMPrimitive)
    assert prim_doc.root.value == 123.456


def test_json_parser_utf16() -> None:
    parser = JSONParserPlugin()
    context = create_mock_context({"encoding": "utf-16"})
    text = '{"msg": "hello 🔥"}'
    encoded_utf16 = text.encode("utf-16")

    doc = parser.parse_to_udm(encoded_utf16, context)
    assert isinstance(doc.root, UDMTabular)
    assert doc.root.rows[0][0] == "hello 🔥"


def test_json_parser_streaming() -> None:
    parser = JSONParserPlugin()
    lines = ['{"items": [1, 2, 3]}']
    doc = parser.stream_parse_to_udm(lines)

    assert isinstance(doc.root, UDMTabular)

    empty_doc = parser.stream_parse_to_udm([])
    assert isinstance(empty_doc.root, UDMPrimitive)


def test_json_writer_basic() -> None:
    writer = JSONWriterPlugin()
    context = create_mock_context({"indent": None, "sort_keys": True})
    tabular = UDMTabular(
        columns=("b", "a"),
        rows=((2, 1),),
    )
    doc = UDMDocument(root=tabular)

    output = writer.write_from_udm(doc, context)
    assert output == '[{"a": 1, "b": 2}]'


def test_json_writer_primitive_and_collection() -> None:
    writer = JSONWriterPlugin()
    context = create_mock_context({"indent": 0})

    prim_doc = UDMDocument(root=UDMPrimitive(value="test_str"))
    output_prim = writer.write_from_udm(prim_doc, context)
    assert output_prim == '"test_str"'

    coll_doc = UDMDocument(root=UDMCollection(items=(UDMPrimitive(value=1), UDMPrimitive(value=2))))
    output_coll = writer.write_from_udm(coll_doc, context)
    assert "1" in output_coll and "2" in output_coll


def test_json_writer_streaming() -> None:
    writer = JSONWriterPlugin()
    doc = UDMDocument(root=UDMPrimitive(value={"key": "val"}))
    stream = io.StringIO()

    writer.stream_write_from_udm(doc, stream, JSONOptions(indent=None))
    result = stream.getvalue()
    assert result == '{"key": "val"}'


def test_json_detector() -> None:
    detector = JSONDetector()
    json_obj = '{"name": "test"}'
    json_arr = "[1, 2, 3]"

    assert detector.can_detect(json_obj) is True
    assert detector.can_detect(json_arr) is True
    assert detector.can_detect("not json text") is False
    assert detector.can_detect("") is False

    assert detector.detect_format(json_obj) == "json"
    assert detector.detect_format("invalid") == "unknown"


def test_json_inspector() -> None:
    inspector = JSONInspector()

    obj_info = inspector.inspect_schema('{"a": 1, "b": 2}')
    assert obj_info["structure_type"] == "object"
    assert obj_info["key_count"] == 2
    assert obj_info["depth"] == 2

    arr_info = inspector.inspect_schema('[{"x": 10}, {"x": 20}]')
    assert arr_info["structure_type"] == "array"
    assert arr_info["item_count"] == 2

    empty_info = inspector.inspect_schema("")
    assert empty_info["structure_type"] == "empty"

    malformed_info = inspector.inspect_schema("{unclosed")
    assert malformed_info["structure_type"] == "malformed"


def test_json_validator() -> None:
    validator = JSONValidator()
    valid_json = '{"a": 1}'
    invalid_json = '{"a": 1'

    assert validator.validate_output(valid_json) is True
    assert validator.validate_output("") is True

    valid, errors = validator.validate_json_structure(invalid_json)
    assert valid is False
    assert len(errors) > 0


def test_json_plugin_registration() -> None:
    plugin_reg = PluginRegistry()
    format_reg = FormatRegistry()

    register_json_plugin(plugin_reg, format_reg)

    parser = plugin_reg.get_parser("json")
    writer = plugin_reg.get_writer("json")
    descriptor = format_reg.get_descriptor("json")

    assert parser.metadata.name == "json_parser"
    assert writer.metadata.name == "json_writer"
    assert descriptor.name == "JSON"


def test_json_inspector_edge_cases() -> None:
    inspector = JSONInspector()

    empty_obj = inspector.inspect_schema("{}")
    assert empty_obj["depth"] == 1

    empty_arr = inspector.inspect_schema("[]")
    assert empty_arr["depth"] == 1

    prim_info = inspector.inspect_schema('"hello_world"')
    assert prim_info["structure_type"] == "primitive"
    assert prim_info["depth"] == 1


def test_json_detector_unknown() -> None:
    detector = JSONDetector()
    assert detector.detect_format("plain_text") == "unknown"


def test_json_manifest_metadata() -> None:
    manifest = JSONPluginManifest()
    assert manifest.parser.format_identifier == "json"
    assert manifest.writer.format_identifier == "json"

    manifest.parser.initialize(create_mock_context())
    manifest.parser.shutdown()
    manifest.writer.initialize(create_mock_context())
    manifest.writer.shutdown()
