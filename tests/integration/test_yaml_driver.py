from pathlib import Path
import pytest

import treqna


@pytest.fixture
def temp_yaml_file(tmp_path: Path) -> Path:
    p = tmp_path / "sample.yaml"
    p.write_text("id: 101\nname: Alice\nrole: Admin\n", encoding="utf-8")
    return p


def test_public_api_detect_yaml(temp_yaml_file: Path) -> None:
    res = treqna.detect(temp_yaml_file)
    assert res.success is True
    assert res.detected_format == "yaml"


def test_public_api_inspect_yaml(temp_yaml_file: Path) -> None:
    res = treqna.inspect(temp_yaml_file)
    assert res.success is True
    assert res.schema_info["structure_type"] == "object"
    assert res.schema_info["key_count"] == 3


def test_public_api_validate_yaml(temp_yaml_file: Path) -> None:
    res = treqna.validate(temp_yaml_file)
    assert res.success is True
    assert res.is_valid is True


def test_cross_format_yaml_to_csv(temp_yaml_file: Path) -> None:
    res = treqna.transform(temp_yaml_file).to("csv").execute()
    assert res.success is True
    assert "id,name,role" in res.output
    assert "101,Alice,Admin" in res.output


def test_cross_format_csv_to_yaml(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("col1,col2\nval1,val2\n", encoding="utf-8")

    res = treqna.transform(csv_file).to("yaml").execute()
    assert res.success is True
    assert "col1: val1" in res.output


def test_cross_format_json_to_yaml(tmp_path: Path) -> None:
    json_file = tmp_path / "data.json"
    json_file.write_text('{"key": "value"}', encoding="utf-8")

    res = treqna.transform(json_file).to("yaml").execute()
    assert res.success is True
    assert "key: value" in res.output


def test_cross_format_yaml_to_json(temp_yaml_file: Path) -> None:
    res = treqna.transform(temp_yaml_file).to("json").execute()
    assert res.success is True
    assert '"name": "Alice"' in res.output or '"name":"Alice"' in res.output


def test_cross_format_yaml_to_yaml(temp_yaml_file: Path) -> None:
    res = treqna.transform(temp_yaml_file).to("yaml").execute()
    assert res.success is True
    assert "name: Alice" in res.output

