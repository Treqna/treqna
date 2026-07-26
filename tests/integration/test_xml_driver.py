from pathlib import Path
import pytest

import treqna


@pytest.fixture
def temp_xml_file(tmp_path: Path) -> Path:
    p = tmp_path / "sample.xml"
    p.write_text("<root><item><id>101</id><name>Alice</name><role>Admin</role></item></root>", encoding="utf-8")
    return p


def test_public_api_detect_xml(temp_xml_file: Path) -> None:
    res = treqna.detect(temp_xml_file)
    assert res.success is True
    assert res.detected_format == "xml"


def test_public_api_inspect_xml(temp_xml_file: Path) -> None:
    res = treqna.inspect(temp_xml_file)
    assert res.success is True
    assert res.schema_info["structure_type"] == "document"
    assert res.schema_info["root_tag"] == "root"


def test_public_api_validate_xml(temp_xml_file: Path) -> None:
    res = treqna.validate(temp_xml_file)
    assert res.success is True
    assert res.is_valid is True


def test_cross_format_xml_to_csv(temp_xml_file: Path) -> None:
    res = treqna.transform(temp_xml_file).to("csv").execute()
    assert res.success is True
    assert "id,name,role" in res.output
    assert "101,Alice,Admin" in res.output


def test_cross_format_csv_to_xml(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("col1,col2\nval1,val2\n", encoding="utf-8")

    res = treqna.transform(csv_file).to("xml").execute()
    assert res.success is True
    assert "<col1>val1</col1>" in res.output


def test_cross_format_json_to_xml(tmp_path: Path) -> None:
    json_file = tmp_path / "data.json"
    json_file.write_text('{"key": "value"}', encoding="utf-8")

    res = treqna.transform(json_file).to("xml").execute()
    assert res.success is True
    assert "<key>value</key>" in res.output


def test_cross_format_xml_to_json(temp_xml_file: Path) -> None:
    res = treqna.transform(temp_xml_file).to("json").execute()
    assert res.success is True
    assert '"name": "Alice"' in res.output or '"name":"Alice"' in res.output


def test_cross_format_yaml_to_xml(tmp_path: Path) -> None:
    yaml_file = tmp_path / "data.yaml"
    yaml_file.write_text("key: value\n", encoding="utf-8")

    res = treqna.transform(yaml_file).to("xml").execute()
    assert res.success is True
    assert "<key>value</key>" in res.output


def test_cross_format_xml_to_yaml(temp_xml_file: Path) -> None:
    res = treqna.transform(temp_xml_file).to("yaml").execute()
    assert res.success is True
    assert "name: Alice" in res.output


def test_cross_format_xml_to_xml(temp_xml_file: Path) -> None:
    res = treqna.transform(temp_xml_file).to("xml").execute()
    assert res.success is True
    assert "<name>Alice</name>" in res.output

