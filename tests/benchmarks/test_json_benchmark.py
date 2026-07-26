import json
import time
import pytest

from treqna.core.context import ExecutionContext, PipelineContext, TransformationMetadata
from treqna.core.udm import UDMDocument, UDMTabular
from treqna.plugins.json import JSONParserPlugin, JSONWriterPlugin


def generate_large_json_data(num_items: int = 10000) -> str:
    data = [
        {"id": i, "name": f"User{i}", "email": f"user{i}@example.com", "active": True}
        for i in range(num_items)
    ]
    return json.dumps(data)


def create_benchmark_context() -> PipelineContext:
    metadata = TransformationMetadata(request_id="bench_json_req")
    exec_ctx = ExecutionContext(
        current_format="json",
        target_format="udm",
        metadata=metadata,
    )
    return PipelineContext(session_id="bench_json_sess", execution_context=exec_ctx)


def test_json_parser_performance_benchmark() -> None:
    json_data = generate_large_json_data(num_items=10000)
    parser = JSONParserPlugin()
    context = create_benchmark_context()

    start_time = time.perf_counter()
    doc = parser.parse_to_udm(json_data, context)
    duration = time.perf_counter() - start_time

    assert isinstance(doc.root, UDMTabular)
    assert len(doc.root.rows) == 10000
    assert duration < 2.0


def test_json_writer_performance_benchmark() -> None:
    columns = ("id", "name", "email", "active")
    rows = tuple(
        (i, f"User{i}", f"user{i}@example.com", True)
        for i in range(10000)
    )
    doc = UDMDocument(root=UDMTabular(columns=columns, rows=rows))

    writer = JSONWriterPlugin()
    context = create_benchmark_context()

    start_time = time.perf_counter()
    output = writer.write_from_udm(doc, context)
    duration = time.perf_counter() - start_time

    assert len(output) > 100000
    assert duration < 2.0
