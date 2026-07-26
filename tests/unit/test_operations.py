import pytest

from treqna.formats.enums import FormatFamily
from treqna.operations.enums import (
    OperationCapability,
    OperationCategory,
    OperationPriority,
)
from treqna.operations.models import OperationCost, OperationDescriptor
from treqna.operations.pipeline import OperationBuilder
from treqna.operations.registry import OperationNotFoundError, OperationRegistry


def create_sample_descriptor(name: str, category: OperationCategory) -> OperationDescriptor:
    return OperationDescriptor(
        name=name,
        description=f"Sample operation {name}",
        category=category,
        consumes=("json",),
        produces=("udm",),
        supported_format_families=(FormatFamily.STRUCTURED,),
        priority=OperationPriority.HIGH,
        estimated_cost=OperationCost(time_complexity_score=1.2),
        streaming_support=True,
        thread_safety=True,
        deterministic=True,
        reversible=False,
        lossless=True,
        capabilities=(OperationCapability.STREAMING, OperationCapability.THREAD_SAFE),
    )


def test_operation_categories_enum() -> None:
    categories = [cat.value for cat in OperationCategory]
    assert len(categories) == 15
    assert "read" in categories
    assert "write" in categories
    assert "normalize" in categories
    assert "metadata" in categories


def test_operation_descriptor_immutability() -> None:
    desc = create_sample_descriptor("parse_json", OperationCategory.PARSE if hasattr(OperationCategory, "PARSE") else OperationCategory.TRANSFORM)
    assert desc.name == "parse_json"
    assert desc.streaming_support is True
    assert desc.deterministic is True

    with pytest.raises(AttributeError):
        desc.name = "new_name"  # type: ignore[misc]


def test_operation_builder_and_graph() -> None:
    builder = OperationBuilder()
    read_desc = create_sample_descriptor("read_file", OperationCategory.READ)
    transform_desc = create_sample_descriptor("transform_udm", OperationCategory.TRANSFORM)

    builder.add_operation(read_desc, node_id="node_read")
    builder.add_operation(transform_desc, node_id="node_transform")
    builder.connect("node_read", "node_transform", data_flow_label="raw_to_udm")

    pipeline = builder.build_pipeline()
    graph = pipeline.graph

    assert graph.node_count() == 2
    assert graph.edge_count() == 1
    assert graph.edges[0].source_node_id == "node_read"
    assert graph.edges[0].target_node_id == "node_transform"


def test_operation_registry_lookups() -> None:
    registry = OperationRegistry()
    read_desc = create_sample_descriptor("read_op", OperationCategory.READ)
    write_desc = create_sample_descriptor("write_op", OperationCategory.WRITE)

    registry.register(read_desc)
    registry.register(write_desc)

    retrieved = registry.get_by_name("read_op")
    assert retrieved.category == OperationCategory.READ

    read_ops = registry.list_by_category(OperationCategory.READ)
    assert len(read_ops) == 1
    assert read_ops[0].name == "read_op"

    with pytest.raises(OperationNotFoundError):
        registry.get_by_name("non_existent")
