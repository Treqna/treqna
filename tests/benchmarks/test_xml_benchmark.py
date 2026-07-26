import time
import xml.etree.ElementTree as ET
import pytest

from treqna.core.context import ExecutionContext, PipelineContext, TransformationMetadata
from treqna.core.udm import UDMDocument, UDMTabular
from treqna.plugins.xml import XMLParserPlugin, XMLWriterPlugin


def generate_large_xml_data(num_items: int = 10000) -> str:
    root = ET.Element("root")
    for i in range(num_items):
        item = ET.SubElement(root, "item")
        ET.SubElement(item, "id").text = str(i)
        ET.SubElement(item, "name").text = f"User{i}"
        ET.SubElement(item, "email").text = f"user{i}@example.com"
        ET.SubElement(item, "active").text = "true"
    return ET.tostring(root, encoding="utf-8").decode("utf-8")


def create_benchmark_context() -> PipelineContext:
    metadata = TransformationMetadata(request_id="bench_xml_req")
    exec_ctx = ExecutionContext(
        current_format="xml",
        target_format="udm",
        metadata=metadata,
    )
    return PipelineContext(session_id="bench_xml_sess", execution_context=exec_ctx)


def test_xml_parser_performance_benchmark() -> None:
    xml_data = generate_large_xml_data(num_items=10000)
    parser = XMLParserPlugin()
    context = create_benchmark_context()

    start_time = time.perf_counter()
    doc = parser.parse_to_udm(xml_data, context)
    duration = time.perf_counter() - start_time

    assert isinstance(doc.root, UDMTabular)
    assert len(doc.root.rows) == 10000
    assert duration < 5.0


def test_xml_writer_performance_benchmark() -> None:
    columns = ("id", "name", "email", "active")
    rows = tuple(
        (i, f"User{i}", f"user{i}@example.com", True)
        for i in range(10000)
    )
    doc = UDMDocument(root=UDMTabular(columns=columns, rows=rows))

    writer = XMLWriterPlugin()
    context = create_benchmark_context()

    start_time = time.perf_counter()
    output = writer.write_from_udm(doc, context)
    duration = time.perf_counter() - start_time

    assert len(output) > 100000
    assert duration < 5.0
