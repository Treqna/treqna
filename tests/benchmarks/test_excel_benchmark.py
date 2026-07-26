import time
import pytest

from treqna.core.context import ExecutionContext, PipelineContext, TransformationMetadata
from treqna.core.udm import UDMDocument, UDMTabular
from treqna.plugins.excel import ExcelOptions, ExcelParserPlugin, ExcelWriterPlugin


def create_benchmark_context() -> PipelineContext:
    metadata = TransformationMetadata(request_id="bench_excel_req")
    exec_ctx = ExecutionContext(
        current_format="excel",
        target_format="udm",
        metadata=metadata,
    )
    return PipelineContext(session_id="bench_excel_sess", execution_context=exec_ctx)


def test_excel_writer_performance_benchmark() -> None:
    columns = ("id", "name", "email", "active")
    rows = tuple(
        (i, f"User{i}", f"user{i}@example.com", True)
        for i in range(1000)
    )
    doc = UDMDocument(root=UDMTabular(columns=columns, rows=rows))

    writer = ExcelWriterPlugin()
    context = create_benchmark_context()

    start_time = time.perf_counter()
    output = writer.write_from_udm(doc, context)
    duration = time.perf_counter() - start_time

    assert isinstance(output, bytes)
    assert len(output) > 1000
    assert duration < 5.0


def test_excel_parser_performance_benchmark() -> None:
    columns = ("id", "name", "email", "active")
    rows = tuple(
        (i, f"User{i}", f"user{i}@example.com", True)
        for i in range(1000)
    )
    doc = UDMDocument(root=UDMTabular(columns=columns, rows=rows))

    writer = ExcelWriterPlugin()
    parser = ExcelParserPlugin()
    context = create_benchmark_context()

    xlsx_bytes = writer.write_from_udm(doc, context)

    start_time = time.perf_counter()
    parsed_doc = parser.parse_to_udm(xlsx_bytes, context)
    duration = time.perf_counter() - start_time

    assert isinstance(parsed_doc.root, UDMTabular)
    assert len(parsed_doc.root.rows) == 1000
    assert duration < 5.0
