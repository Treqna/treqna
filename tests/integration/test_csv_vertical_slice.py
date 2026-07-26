from pathlib import Path
import pytest

import treqna
from treqna.cli.main import main


@pytest.fixture
def temp_csv_file(tmp_path: Path) -> Path:
    p = tmp_path / "slice_sample.csv"
    p.write_text("id,name,role\n101,Alice,Engineer\n102,Bob,Designer\n", encoding="utf-8")
    return p


def test_public_api_detect_csv(temp_csv_file: Path) -> None:
    res = treqna.detect(temp_csv_file)
    assert res.success is True
    assert res.detected_format == "csv"
    assert res.confidence_score == 1.0


def test_public_api_inspect_csv(temp_csv_file: Path) -> None:
    res = treqna.inspect(temp_csv_file)
    assert res.success is True
    assert res.schema_info["columns"] == ("id", "name", "role")
    assert res.schema_info["column_count"] == 3


def test_public_api_validate_csv(temp_csv_file: Path) -> None:
    res = treqna.validate(temp_csv_file)
    assert res.success is True
    assert res.is_valid is True


def test_public_api_transform_csv(temp_csv_file: Path) -> None:
    builder = treqna.transform(temp_csv_file).to("csv").validate().optimize()
    res = builder.execute()

    assert res.success is True
    assert isinstance(res.output, str)
    assert "id,name,role" in res.output
    assert "101,Alice,Engineer" in res.output


def test_cli_detect_command(temp_csv_file: Path) -> None:
    code = main(["detect", str(temp_csv_file)])
    assert code == 0


def test_cli_inspect_command(temp_csv_file: Path) -> None:
    code = main(["inspect", str(temp_csv_file)])
    assert code == 0


def test_cli_validate_command(temp_csv_file: Path) -> None:
    code = main(["validate", str(temp_csv_file)])
    assert code == 0


def test_cli_transform_command(temp_csv_file: Path, tmp_path: Path) -> None:
    out_file = tmp_path / "out.csv"
    code = main(["transform", str(temp_csv_file), "--to", "csv", "--out", str(out_file)])

    assert code == 0
    assert out_file.exists()
    content = out_file.read_text(encoding="utf-8")
    assert "Alice" in content
