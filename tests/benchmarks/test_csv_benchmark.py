import io
import time
import pytest

from treqna.core.context import ExecutionContext, PipelineContext, TransformationMetadata
from treqna.core.udm import UDMDocument, UDMTabular
from treqna.plugins.csv import CSVParserPlugin, CSVWriterPlugin


def generate_large_csv_data(num_rows: int = 10000) -> str:
    lines = ["id,name,email,score,status\n"]
    for i in range(num_rows):
        lines.append(f"{i},User{i},user{i}@example.com,{i * 1.5},active\n")
    return "".join(lines)


def create_benchmark_context() -> PipelineContext:
    metadata = TransformationMetadata(request_id="bench_req")
    exec_ctx = ExecutionContext(
        current_format="csv",
        target_format="udm",
        metadata=metadata,
    )
    return PipelineContext(session_id="bench_sess", execution_context=exec_ctx)


def test_csv_parser_performance_benchmark() -> None:
    csv_data = generate_large_csv_data(num_rows=10000)
    parser = CSVParserPlugin()
    context = create_benchmark_context()

    start_time = time.perf_counter()
    doc = parser.parse_to_udm(csv_data, context)
    duration = time.perf_counter() - start_time

    assert isinstance(doc.root, UDMTabular)
    assert len(doc.root.rows) == 10000
    assert duration < 2.0


def test_csv_writer_performance_benchmark() -> None:
    columns = ("id", "name", "email", "score", "status")
    rows = tuple(
        (str(i), f"User{i}", f"user{i}@example.com", str(i * 1.5), "active")
        for i in range(10000)
    )
    doc = UDMDocument(root=UDMTabular(columns=columns, rows=rows))

    writer = CSVWriterPlugin()
    context = create_benchmark_context()

    start_time = time.perf_counter()
    output = writer.write_from_udm(doc, context)
    duration = time.perf_counter() - start_time

    assert len(output) > 100000
    assert duration < 2.0

