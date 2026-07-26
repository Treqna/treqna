from pathlib import Path
import pytest

import treqna


@pytest.fixture
def temp_json_file(tmp_path: Path) -> Path:
    p = tmp_path / "sample.json"
    p.write_text('{"id": 1, "name": "Alice", "role": "admin"}', encoding="utf-8")
    return p


def test_public_api_detect_json(temp_json_file: Path) -> None:
    res = treqna.detect(temp_json_file)
    assert res.success is True
    assert res.detected_format == "json"
    assert res.confidence_score == 1.0


def test_public_api_inspect_json(temp_json_file: Path) -> None:
    res = treqna.inspect(temp_json_file)
    assert res.success is True
    assert res.schema_info["structure_type"] == "object"
    assert res.schema_info["key_count"] == 3


def test_public_api_validate_json(temp_json_file: Path) -> None:
    res = treqna.validate(temp_json_file)
    assert res.success is True
    assert res.is_valid is True


def test_public_api_transform_json_to_csv(temp_json_file: Path) -> None:
    builder = treqna.transform(temp_json_file).to("csv").validate().optimize()
    res = builder.execute()

    assert res.success is True
    assert isinstance(res.output, str)
    assert "id,name,role" in res.output
    assert "1,Alice,admin" in res.output


def test_public_api_transform_csv_to_json(tmp_path: Path) -> None:
    csv_file = tmp_path / "data.csv"
    csv_file.write_text("item,qty\nApple,10\nBanana,20\n", encoding="utf-8")

    builder = treqna.transform(csv_file).to("json").with_options({"indent": None})
    res = builder.execute()

    assert res.success is True
    assert isinstance(res.output, str)
    assert '"item": "Apple"' in res.output or '"item":"Apple"' in res.output
