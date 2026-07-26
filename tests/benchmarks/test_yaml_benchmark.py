import time
import pytest
import yaml

from treqna.core.context import ExecutionContext, PipelineContext, TransformationMetadata
from treqna.core.udm import UDMDocument, UDMTabular
from treqna.plugins.yaml import YAMLParserPlugin, YAMLWriterPlugin


def generate_large_yaml_data(num_items: int = 1000) -> str:
    data = [
        {"id": i, "name": f"User{i}", "email": f"user{i}@example.com", "active": True}
        for i in range(num_items)
    ]
    return yaml.safe_dump(data)


def create_benchmark_context() -> PipelineContext:
    metadata = TransformationMetadata(request_id="bench_yaml_req")
    exec_ctx = ExecutionContext(
        current_format="yaml",
        target_format="udm",
        metadata=metadata,
    )
    return PipelineContext(session_id="bench_yaml_sess", execution_context=exec_ctx)


def test_yaml_parser_performance_benchmark() -> None:
    yaml_data = generate_large_yaml_data(num_items=1000)
    parser = YAMLParserPlugin()
    context = create_benchmark_context()

    start_time = time.perf_counter()
    doc = parser.parse_to_udm(yaml_data, context)
    duration = time.perf_counter() - start_time

    assert isinstance(doc.root, UDMTabular)
    assert len(doc.root.rows) == 1000
    assert duration < 5.0


def test_yaml_writer_performance_benchmark() -> None:
    columns = ("id", "name", "email", "active")
    rows = tuple(
        (i, f"User{i}", f"user{i}@example.com", True)
        for i in range(1000)
    )
    doc = UDMDocument(root=UDMTabular(columns=columns, rows=rows))

    writer = YAMLWriterPlugin()
    context = create_benchmark_context()

    start_time = time.perf_counter()
    output = writer.write_from_udm(doc, context)
    duration = time.perf_counter() - start_time

    assert len(output) > 10000
    assert duration < 5.0
