from pathlib import Path
import pytest

from treqna.testing.matrix import (
    CompatibilityMatrixRunner,
    CompatibilityPairResult,
)


def test_compatibility_matrix_execution(tmp_path: Path) -> None:
    runner = CompatibilityMatrixRunner()
    formats = runner.list_supported_formats()

    assert "csv" in formats
    assert "json" in formats

    report = runner.run_matrix()

    assert report.total_pairs >= 16
    assert report.failed_pairs == 0
    assert report.passed_pairs == report.total_pairs

    json_path = tmp_path / "matrix_results.json"
    md_path = tmp_path / "matrix_report.md"

    runner.generate_json_report(report, json_path)
    runner.generate_markdown_report(report, md_path)

    assert json_path.exists()
    assert md_path.exists()

    json_content = json_path.read_text(encoding="utf-8")
    md_content = md_path.read_text(encoding="utf-8")

    assert '"failed_pairs": 0' in json_content
    assert "# Treqna Transformation Compatibility Matrix Report" in md_content
    assert "| `csv` | `json` |" in md_content
    assert "| `json` | `csv` |" in md_content


def test_compatibility_matrix_custom_payloads() -> None:
    runner = CompatibilityMatrixRunner()
    custom_payloads = {
        "csv": "a,b\n1,2\n",
        "json": '[{"a": 1, "b": 2}]',
    }
    report = runner.run_matrix(sample_payloads=custom_payloads)
    assert report.total_pairs >= 4
    assert report.failed_pairs == 0


def test_compatibility_pair_failed_result() -> None:
    runner = CompatibilityMatrixRunner()
    res = runner.run_pair_transformation("csv", "unsupported_xyz", "data")
    assert res.success is False
    assert len(res.errors) > 0


def test_compatibility_pair_transformation_failure_branch(monkeypatch: pytest.MonkeyPatch) -> None:
    from treqna.api.builder import TransformationBuilder
    from treqna.api.results import TransformationResult

    def mock_execute(self: TransformationBuilder) -> TransformationResult:
        return TransformationResult(
            success=False,
            status="failure",
            output=None,
            errors=("Simulated transformation failure",),
        )

    monkeypatch.setattr(TransformationBuilder, "execute", mock_execute)

    runner = CompatibilityMatrixRunner()
    res = runner.run_pair_transformation("csv", "json", "data")
    assert res.success is False
    assert res.errors == ("Simulated transformation failure",)
