import io
import pytest

from treqna.core.context import (
    ExecutionContext,
    PipelineContext,
    TransformationMetadata,
)
from treqna.core.udm import UDMDocument, UDMTabular
from treqna.formats.registry import FormatRegistry
from treqna.plugins.csv import (
    CSVDetector,
    CSVInspector,
    CSVOptions,
    CSVParserPlugin,
    CSVPluginManifest,
    CSVValidator,
    CSVWriterPlugin,
    register_csv_plugin,
)
from treqna.plugins.csv.parser import decode_source_data, extract_csv_options
from treqna.plugins.registry import PluginRegistry


def create_mock_context(attributes: dict[str, object] | None = None) -> PipelineContext:
    metadata = TransformationMetadata(
        request_id="test_req",
        custom_attributes=attributes if attributes is not None else {},
    )
    exec_ctx = ExecutionContext(
        current_format="csv",
        target_format="udm",
        metadata=metadata,
    )
    return PipelineContext(session_id="test_sess", execution_context=exec_ctx)


def test_extract_csv_options_nil_context() -> None:
    opts1 = extract_csv_options(None)
    assert opts1.delimiter == ","

    exec_ctx = ExecutionContext(current_format="csv", target_format="udm")
    p_ctx = PipelineContext(session_id="test", execution_context=exec_ctx)
    opts2 = extract_csv_options(p_ctx)
    assert opts2.delimiter == ","


def test_decode_source_data_utf16_fallback() -> None:
    raw_invalid_utf8 = b"\xff\xfeh\x00e\x00l\x00l\x00o\x00"
    decoded = decode_source_data(raw_invalid_utf8, encoding="utf-8")
    assert "hello" in decoded


def test_csv_parser_basic() -> None:
    parser = CSVParserPlugin()
    context = create_mock_context()
    raw_csv = "name,age,city\nAlice,30,New York\nBob,25,London\n"

    doc = parser.parse_to_udm(raw_csv, context)
    assert isinstance(doc.root, UDMTabular)
    assert doc.root.columns == ("name", "age", "city")
    assert len(doc.root.rows) == 2
    assert doc.root.rows[0] == ("Alice", "30", "New York")
    assert doc.root.rows[1] == ("Bob", "25", "London")


def test_csv_parser_escapechar_and_empty() -> None:
    parser = CSVParserPlugin()
    context = create_mock_context({"escapechar": "\\", "delimiter": ","})
    raw_csv = 'col1,col2\nval1,val\\,2\n\n'

    doc = parser.parse_to_udm(raw_csv, context)
    assert isinstance(doc.root, UDMTabular)
    assert len(doc.root.rows) == 1

    empty_doc = parser.parse_to_udm("", context)
    assert isinstance(empty_doc.root, UDMTabular)
    assert len(empty_doc.root.columns) == 0


def test_csv_parser_custom_delimiter_and_bytes() -> None:
    parser = CSVParserPlugin()
    context = create_mock_context({"delimiter": ";", "has_header": True})
    raw_bytes = "id;value\n1;foo\n2;bar\n".encode("utf-8")

    doc = parser.parse_to_udm(raw_bytes, context)
    assert isinstance(doc.root, UDMTabular)
    assert doc.root.columns == ("id", "value")
    assert doc.root.rows[0] == ("1", "foo")


def test_csv_parser_utf16() -> None:
    parser = CSVParserPlugin()
    context = create_mock_context({"encoding": "utf-16"})
    text = "col1,col2\nval1,val2\n"
    encoded_utf16 = text.encode("utf-16")

    doc = parser.parse_to_udm(encoded_utf16, context)
    assert isinstance(doc.root, UDMTabular)
    assert doc.root.columns == ("col1", "col2")
    assert doc.root.rows[0] == ("val1", "val2")


def test_csv_parser_no_header() -> None:
    parser = CSVParserPlugin()
    context = create_mock_context({"has_header": False})
    raw_csv = "v1,v2\nv3,v4\n"

    doc = parser.parse_to_udm(raw_csv, context)
    assert isinstance(doc.root, UDMTabular)
    assert doc.root.columns == ("column_0", "column_1")
    assert len(doc.root.rows) == 2


def test_csv_parser_streaming_edge_cases() -> None:
    parser = CSVParserPlugin()
    lines = ["name,score\n", "Charlie,95\n", "\n", "Delta,88\n"]
    doc = parser.stream_parse_to_udm(lines, options=CSVOptions(escapechar="\\"))

    assert isinstance(doc.root, UDMTabular)
    assert doc.root.columns == ("name", "score")
    assert len(doc.root.rows) == 2

    empty_stream_doc = parser.stream_parse_to_udm([], options=CSVOptions(has_header=True))
    assert len(empty_stream_doc.root.columns) == 0

    no_header_stream = parser.stream_parse_to_udm(["a,b\n", "c,d\n"], options=CSVOptions(has_header=False))
    assert no_header_stream.root.columns == ("column_0", "column_1")


def test_csv_writer_basic() -> None:
    writer = CSVWriterPlugin()
    context = create_mock_context({"escapechar": "\\"})
    tabular = UDMTabular(
        columns=("header1", "header2"),
        rows=(("row1_col1", "row1_col2"), ("row2_col1", "row2_col2")),
    )
    doc = UDMDocument(root=tabular)

    output = writer.write_from_udm(doc, context)
    assert "header1,header2" in output
    assert "row1_col1,row1_col2" in output


def test_csv_writer_streaming() -> None:
    writer = CSVWriterPlugin()
    tabular = UDMTabular(
        columns=("a", "b"),
        rows=(("1", "2"),),
    )
    doc = UDMDocument(root=tabular)
    stream = io.StringIO()

    writer.stream_write_from_udm(doc, stream, CSVOptions(delimiter="|", escapechar="\\"))
    result = stream.getvalue()
    assert "a|b" in result
    assert "1|2" in result


def test_csv_detector() -> None:
    detector = CSVDetector()
    csv_sample = "a,b,c\n1,2,3\n4,5,6\n"
    tsv_sample = "a\tb\tc\n1\t2\t3\n"

    assert detector.can_detect(csv_sample) is True
    assert detector.can_detect(tsv_sample) is True
    assert detector.can_detect("invalid non-csv sample text without commas") is False
    assert detector.can_detect("") is False

    assert detector.detect_format(csv_sample) == "csv"
    assert detector.detect_format(tsv_sample) == "tsv"
    assert detector.detect_format("invalid data") == "unknown"


def test_csv_inspector() -> None:
    inspector = CSVInspector()
    sample = "name,age,role\nAlice,30,dev\nBob,25,design\n"

    info = inspector.inspect_schema(sample)
    assert info["columns"] == ("name", "age", "role")
    assert info["column_count"] == 3
    assert info["has_header"] is True
    assert info["sample_row_count"] == 3

    empty_info = inspector.inspect_schema("")
    assert empty_info["column_count"] == 0

    no_header_sample = "1,2,3\n4,5,6\n"
    no_header_info = inspector.inspect_schema(no_header_sample)
    assert no_header_info["column_count"] == 3


def test_csv_validator() -> None:
    validator = CSVValidator()
    valid_csv = "col1,col2\nval1,val2\nval3,val4\n"
    mismatched_csv = "col1,col2\nval1\n"

    assert validator.validate_output(valid_csv) is True
    assert validator.validate_output("") is True

    valid, errors = validator.validate_csv_structure(mismatched_csv)
    assert valid is False
    assert len(errors) > 0

    malformed_csv = 'col1,col2\n"unclosed quote,val2\n'
    v2, e2 = validator.validate_csv_structure(malformed_csv)
    assert v2 is False or len(e2) > 0


def test_csv_plugin_registration() -> None:
    plugin_reg = PluginRegistry()
    format_reg = FormatRegistry()

    register_csv_plugin(plugin_reg, format_reg)

    parser = plugin_reg.get_parser("csv")
    writer = plugin_reg.get_writer("csv")
    descriptor = format_reg.get_descriptor("csv")

    assert parser.metadata.name == "csv_parser"
    assert writer.metadata.name == "csv_writer"
    assert descriptor.name == "CSV"


def test_decode_source_data_unicode_decode_error() -> None:
    bad_bytes = b"\x80\x81\x82\x83"
    decoded = decode_source_data(bad_bytes, encoding="utf-8")
    assert isinstance(decoded, str)


def test_csv_manifest_metadata() -> None:
    manifest = CSVPluginManifest()
    assert manifest.parser.format_identifier == "csv"
    assert manifest.writer.format_identifier == "csv"

    manifest.parser.initialize(create_mock_context())
    manifest.parser.shutdown()
    manifest.writer.initialize(create_mock_context())
    manifest.writer.shutdown()
