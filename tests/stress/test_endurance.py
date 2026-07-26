import tracemalloc
import pytest

import treqna


def test_long_running_stress_100000_transformations() -> None:
    tracemalloc.start()
    start_mem, _ = tracemalloc.get_traced_memory()

    sample_csv = "id,name,role\n101,Alice,Engineer\n102,Bob,Architect\n"
    num_transformations = 100000

    for i in range(num_transformations):
        target = ("json", "xml", "yaml", "csv")[i % 4]
        res = treqna.transform(sample_csv).to(target).execute()
        assert res.success is True

    current_mem, peak_mem = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    memory_growth = current_mem - start_mem
    assert memory_growth < 5 * 1024 * 1024
