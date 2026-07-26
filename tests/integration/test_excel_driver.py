from pathlib import Path
import pytest

import treqna
from treqna.plugins.excel import ExcelWriterPlugin
from treqna.core.context import ExecutionContext, PipelineContext
from treqna.core.udm import UDMDocument, UDMTabular


@pytest.fixture
def temp_excel_file(tmp_path: Path) -> Path:
    p = tmp_path / "sample.xlsx"
    writer = ExcelWriterPlugin()
    doc = UDMDocument(root=UDMTabular(columns=("id", "name", "role"), rows=((101, "Alice", "Admin"),)))
    ctx = PipelineContext(session_id="test", execution_context=ExecutionContext(current_format="excel", target_format="udm"))
    xlsx_bytes = writer.write_from_udm(doc, ctx)
    p.write_bytes(xlsx_bytes)
    return p


def test_public_api_detect_excel(temp_excel_file: Path) -> None:
    res = treqna.detect(temp_excel_file)
    assert res.success is True
    assert res.detected_format == "excel"


def test_public_api_inspect_excel(temp_excel_file: Path) -> None:
    res = treqna.inspect(temp_excel_file)
    assert res.success is True
    assert res.schema_info["structure_type"] == "workbook"


def test_public_api_validate_excel(temp_excel_file: Path) -> None:
    res = treqna.validate(temp_excel_file)
    assert res.success is True
    assert res.is_valid is True


def test_cross_format_excel_to_csv(temp_excel_file: Path) -> None:
    res = treqna.transform(temp_excel_file).to("csv").execute()
    assert res.success is True
    assert "id,name,role" in res.output
    assert "101,Alice,Admin" in res.output


def test_cross_format_csv_to_excel(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("col1,col2\nval1,val2\n", encoding="utf-8")

    res = treqna.transform(csv_file).to("excel").execute()
    assert res.success is True
    assert isinstance(res.output, (bytes, str))


def test_cross_format_json_to_excel(tmp_path: Path) -> None:
    json_file = tmp_path / "data.json"
    json_file.write_text('[{"key": "value"}]', encoding="utf-8")

    res = treqna.transform(json_file).to("excel").execute()
    assert res.success is True


def test_cross_format_excel_to_json(temp_excel_file: Path) -> None:
    res = treqna.transform(temp_excel_file).to("json").execute()
    assert res.success is True
    assert "Alice" in str(res.output)


def test_cross_format_yaml_to_excel(tmp_path: Path) -> None:
    yaml_file = tmp_path / "data.yaml"
    yaml_file.write_text("- key: value\n", encoding="utf-8")

    res = treqna.transform(yaml_file).to("excel").execute()
    assert res.success is True


def test_cross_format_excel_to_yaml(temp_excel_file: Path) -> None:
    res = treqna.transform(temp_excel_file).to("yaml").execute()
    assert res.success is True
    assert "Alice" in str(res.output)


def test_cross_format_xml_to_excel(tmp_path: Path) -> None:
    xml_file = tmp_path / "data.xml"
    xml_file.write_text("<root><item><id>1</id></item></root>", encoding="utf-8")

    res = treqna.transform(xml_file).to("excel").execute()
    assert res.success is True


def test_cross_format_excel_to_xml(temp_excel_file: Path) -> None:
    res = treqna.transform(temp_excel_file).to("xml").execute()
    assert res.success is True
    assert "<name>Alice</name>" in str(res.output)


def test_cross_format_excel_to_excel(temp_excel_file: Path) -> None:
    res = treqna.transform(temp_excel_file).to("excel").execute()
    assert res.success is True
