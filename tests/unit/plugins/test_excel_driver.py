import io
import random
import string
import xml.etree.ElementTree as ET
import zipfile
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
from treqna.plugins.excel import (
    EXCEL_FORMAT_DESCRIPTOR,
    ExcelDetector,
    ExcelInspector,
    ExcelOptions,
    ExcelParserPlugin,
    ExcelPluginManifest,
    ExcelValidator,
    ExcelWriterPlugin,
    register_excel_plugin,
)
from treqna.plugins.excel.parser import (
    NS_SPREADSHEET,
    col_letter_to_index,
    extract_excel_options,
    parse_cell_value,
    parse_shared_strings,
)


def create_mock_context(attributes: dict[str, object] | None = None) -> PipelineContext:
    metadata = TransformationMetadata(
        request_id="test_excel_req",
        custom_attributes=attributes if attributes is not None else {},
    )
    exec_ctx = ExecutionContext(
        current_format="excel",
        target_format="udm",
        metadata=metadata,
    )
    return PipelineContext(session_id="test_excel_sess", execution_context=exec_ctx)


def test_extract_excel_options_nil_context() -> None:
    opts1 = extract_excel_options(None)
    assert opts1.worksheet_name == "Sheet1"
    assert opts1.header_row == 0

    exec_ctx = ExecutionContext(current_format="excel", target_format="udm")
    p_ctx = PipelineContext(session_id="test", execution_context=exec_ctx)
    opts2 = extract_excel_options(p_ctx)
    assert opts2.worksheet_name == "Sheet1"


def test_excel_writer_and_parser_basic() -> None:
    writer = ExcelWriterPlugin()
    parser = ExcelParserPlugin()
    context = create_mock_context()

    tabular = UDMTabular(
        columns=("id", "name", "active", "score"),
        rows=((101, "Alice", True, 98.5), (102, None, False, 87.0), (103, "Alice", True, None)),
    )
    doc = UDMDocument(root=tabular)

    xlsx_bytes = writer.write_from_udm(doc, context)
    assert isinstance(xlsx_bytes, bytes)
    assert xlsx_bytes.startswith(b"PK\x03\x04")

    parsed_doc = parser.parse_to_udm(xlsx_bytes, context)
    assert isinstance(parsed_doc.root, UDMTabular)
    assert "id" in parsed_doc.root.columns
    assert "name" in parsed_doc.root.columns
    assert len(parsed_doc.root.rows) == 3


def test_excel_writer_primitive_and_collection() -> None:
    writer = ExcelWriterPlugin()
    parser = ExcelParserPlugin()
    context = create_mock_context()

    doc1 = UDMDocument(root=UDMPrimitive(value={"col1": "val1", "col2": 42}))
    xlsx1 = writer.write_from_udm(doc1, context)
    parsed1 = parser.parse_to_udm(xlsx1, context)
    assert isinstance(parsed1.root, UDMTabular)

    doc2 = UDMDocument(root=UDMCollection(items=(UDMPrimitive(value=10), UDMPrimitive(value=20))))
    xlsx2 = writer.write_from_udm(doc2, context)
    parsed2 = parser.parse_to_udm(xlsx2, context)
    assert isinstance(parsed2.root, UDMTabular)

    doc3 = UDMDocument(root=UDMPrimitive(value="simple_string"))
    xlsx3 = writer.write_from_udm(doc3, context)
    parsed3 = parser.parse_to_udm(xlsx3, context)
    assert isinstance(parsed3.root, UDMTabular)


def test_excel_detector() -> None:
    detector = ExcelDetector()
    writer = ExcelWriterPlugin()
    context = create_mock_context()

    doc = UDMDocument(root=UDMTabular(columns=("a",), rows=((1,),)))
    valid_xlsx = writer.write_from_udm(doc, context)

    assert detector.can_detect(valid_xlsx) is True
    assert detector.can_detect(valid_xlsx.decode("latin1")) is True
    assert detector.can_detect(b"invalid_bytes") is False
    assert detector.can_detect("") is False

    assert detector.detect_format(valid_xlsx) == "excel"
    assert detector.detect_format("invalid") == "unknown"


def test_excel_inspector() -> None:
    inspector = ExcelInspector()
    writer = ExcelWriterPlugin()
    context = create_mock_context({"worksheet_name": "DataSheet"})

    doc = UDMDocument(root=UDMTabular(columns=("a",), rows=((1,),)))
    xlsx_bytes = writer.write_from_udm(doc, context)

    info = inspector.inspect_schema(xlsx_bytes)
    assert info["structure_type"] == "workbook"
    assert info["sheet_count"] >= 1
    assert "DataSheet" in info["sheet_names"]

    empty_info = inspector.inspect_schema(b"")
    assert empty_info["structure_type"] == "invalid"

    malformed_info = inspector.inspect_schema(b"PK\x03\x04invalid")
    assert malformed_info["structure_type"] == "malformed"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("xl/worksheets/sheet1.xml", "<worksheet/>")
    buf.seek(0)
    sheet_info = inspector.inspect_schema(buf.getvalue())
    assert sheet_info["structure_type"] == "workbook"
    assert "xl/worksheets/sheet1.xml" in sheet_info["sheet_names"]

    sheet_info_str = inspector.inspect_schema(buf.getvalue().decode("latin1"))
    assert sheet_info_str["structure_type"] == "workbook"


def test_excel_validator() -> None:
    validator = ExcelValidator()
    writer = ExcelWriterPlugin()
    context = create_mock_context()

    doc = UDMDocument(root=UDMTabular(columns=("a",), rows=((1,),)))
    valid_xlsx = writer.write_from_udm(doc, context)

    assert validator.validate_output(valid_xlsx) is True
    assert validator.validate_output(valid_xlsx.decode("latin1")) is True
    assert validator.validate_output(b"") is True
    assert validator.validate_output("") is True

    valid, errors = validator.validate_excel_structure(b"PK\x03\x04invalid")
    assert valid is False
    assert len(errors) > 0

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("other.xml", "<test/>")
    buf.seek(0)
    valid_no_wb, err_no_wb = validator.validate_excel_structure(buf.getvalue())
    assert valid_no_wb is False
    assert "Missing required OpenXML workbook entry" in err_no_wb[0]


def test_excel_plugin_registration() -> None:
    plugin_reg = PluginRegistry()
    format_reg = FormatRegistry()

    register_excel_plugin(plugin_reg, format_reg)

    parser = plugin_reg.get_parser("excel")
    writer = plugin_reg.get_writer("excel")
    descriptor = format_reg.get_descriptor("excel")

    assert parser.metadata.name == "excel_parser"
    assert writer.metadata.name == "excel_writer"
    assert descriptor.name == "EXCEL"


def test_excel_manifest_metadata() -> None:
    manifest = ExcelPluginManifest()
    assert manifest.parser.format_identifier == "excel"
    assert manifest.writer.format_identifier == "excel"

    manifest.parser.initialize(create_mock_context())
    manifest.parser.shutdown()
    manifest.writer.initialize(create_mock_context())
    manifest.writer.shutdown()


def test_excel_streaming() -> None:
    writer = ExcelWriterPlugin()
    parser = ExcelParserPlugin()
    doc = UDMDocument(root=UDMTabular(columns=("x",), rows=((10,),)))
    stream = io.StringIO()

    writer.stream_write_from_udm(doc, stream, ExcelOptions(worksheet_name="StreamSheet"))
    raw_str = stream.getvalue()

    parsed_doc = parser.stream_parse_to_udm([raw_str], ExcelOptions(worksheet_name="StreamSheet"))
    assert isinstance(parsed_doc.root, UDMTabular)


def test_excel_col_letter_to_index() -> None:
    assert col_letter_to_index("A1") == 0
    assert col_letter_to_index("Z1") == 25
    assert col_letter_to_index("AA1") == 26
    assert col_letter_to_index("AB10") == 27


def test_excel_parse_cell_values() -> None:
    c_str = ET.Element(f"{{{NS_SPREADSHEET}}}c", t="s")
    v_str = ET.SubElement(c_str, f"{{{NS_SPREADSHEET}}}v")
    v_str.text = "0"
    assert parse_cell_value(c_str, ["hello"]) == "hello"

    c_int = ET.Element(f"{{{NS_SPREADSHEET}}}c")
    v_int = ET.SubElement(c_int, f"{{{NS_SPREADSHEET}}}v")
    v_int.text = "42"
    assert parse_cell_value(c_int, []) == 42

    c_float = ET.Element(f"{{{NS_SPREADSHEET}}}c")
    v_float = ET.SubElement(c_float, f"{{{NS_SPREADSHEET}}}v")
    v_float.text = "99.5"
    assert parse_cell_value(c_float, []) == 99.5

    c_str_fallback = ET.Element(f"{{{NS_SPREADSHEET}}}c")
    v_str_fallback = ET.SubElement(c_str_fallback, f"{{{NS_SPREADSHEET}}}v")
    v_str_fallback.text = "raw_text_val"
    assert parse_cell_value(c_str_fallback, []) == "raw_text_val"

    c_str_out_of_bounds = ET.Element(f"{{{NS_SPREADSHEET}}}c", t="s")
    v_str_oob = ET.SubElement(c_str_out_of_bounds, f"{{{NS_SPREADSHEET}}}v")
    v_str_oob.text = "99"
    assert parse_cell_value(c_str_out_of_bounds, ["hello"]) == ""

    c_str_empty = ET.Element(f"{{{NS_SPREADSHEET}}}c", t="s")
    assert parse_cell_value(c_str_empty, ["hello"]) == ""

    c_inline = ET.Element(f"{{{NS_SPREADSHEET}}}c", t="inlineStr")
    is_elem = ET.SubElement(c_inline, f"{{{NS_SPREADSHEET}}}is")
    t_elem = ET.SubElement(is_elem, f"{{{NS_SPREADSHEET}}}t")
    t_elem.text = "inline_val"
    assert parse_cell_value(c_inline, []) == "inline_val"

    c_bool = ET.Element(f"{{{NS_SPREADSHEET}}}c", t="b")
    v_bool = ET.SubElement(c_bool, f"{{{NS_SPREADSHEET}}}v")
    v_bool.text = "1"
    assert parse_cell_value(c_bool, []) is True

    c_empty = ET.Element(f"{{{NS_SPREADSHEET}}}c")
    assert parse_cell_value(c_empty, []) is None


def test_excel_parse_shared_strings_formatted() -> None:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        ss_xml = (
            '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
            f'<sst xmlns="{NS_SPREADSHEET}">\n'
            '  <si><t>simple</t></si>\n'
            '  <si><r><t>part1 </t></r><r><t>part2</t></r></si>\n'
            '</sst>'
        )
        zf.writestr("xl/sharedStrings.xml", ss_xml.encode("utf-8"))

    buf.seek(0)
    with zipfile.ZipFile(buf) as zf:
        strings = parse_shared_strings(zf)
        assert strings == ["simple", "part1 part2"]


def test_excel_parser_edge_cases() -> None:
    parser = ExcelParserPlugin()
    context = create_mock_context({"header_row": 5, "preserve_empty_rows": True})

    empty_doc = parser.parse_to_udm(b"", context)
    assert empty_doc.schema_identifier == "excel_empty"

    raw_doc = parser.parse_to_udm(b"not_a_zip", context)
    assert raw_doc.schema_identifier == "excel_raw"

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("xl/worksheets/sheet1.xml", f'<worksheet xmlns="{NS_SPREADSHEET}"/>')
    buf.seek(0)
    parsed_no_data = parser.parse_to_udm(buf.getvalue(), context)
    assert isinstance(parsed_no_data.root, UDMTabular)
    assert len(parsed_no_data.root.rows) == 0


def test_excel_random_fuzzing() -> None:
    parser = ExcelParserPlugin()
    context = create_mock_context()
    random.seed(42)

    for _ in range(50):
        chars = "".join(random.choices(string.printable, k=50))
        doc = parser.parse_to_udm(chars.encode("utf-8"), context)
        assert isinstance(doc.root, (UDMTabular, UDMCollection, UDMPrimitive))
