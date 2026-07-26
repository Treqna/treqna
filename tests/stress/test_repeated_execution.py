import pytest

import treqna
from treqna.testing.matrix import CompatibilityMatrixRunner


def test_repeated_matrix_execution_100_iterations() -> None:
    runner = CompatibilityMatrixRunner()
    for iteration in range(100):
        report = runner.run_matrix()
        assert report.failed_pairs == 0, f"Failed on iteration {iteration}"
        assert report.passed_pairs == report.total_pairs


def test_repeated_transform_100_iterations() -> None:
    sample_csv = "id,name,role\n101,Alice,Engineer\n"
    for _ in range(100):
        res1 = treqna.transform(sample_csv).to("json").execute()
        assert res1.success is True
        res2 = treqna.transform(res1.output).to("xml").execute()
        assert res2.success is True
        res3 = treqna.transform(res2.output).to("yaml").execute()
        assert res3.success is True
        res4 = treqna.transform(res3.output).to("csv").execute()
        assert res4.success is True
