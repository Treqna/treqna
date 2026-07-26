import uuid
from dataclasses import dataclass, field

from treqna.operations.graph import OperationEdge, OperationGraph, OperationNode
from treqna.operations.models import OperationDescriptor


def generate_pipeline_id() -> str:
    return str(uuid.uuid4())


@dataclass(frozen=True, kw_only=True)
class OperationPipeline:
    pipeline_id: str = field(default_factory=generate_pipeline_id)
    graph: OperationGraph
    operations: tuple[OperationDescriptor, ...] = field(default_factory=tuple)


class OperationBuilder:
    def __init__(self) -> None:
        self._nodes: dict[str, OperationNode] = {}
        self._edges: list[OperationEdge] = []
        self._operations: list[OperationDescriptor] = []

    def add_operation(
        self,
        descriptor: OperationDescriptor,
        node_id: str | None = None,
    ) -> "OperationBuilder":
        id_key = node_id if node_id is not None else f"node_{len(self._nodes)}"
        node = OperationNode(node_id=id_key, descriptor=descriptor)
        self._nodes[id_key] = node
        self._operations.append(descriptor)
        return self

    def connect(
        self,
        source_node_id: str,
        target_node_id: str,
        data_flow_label: str = "",
    ) -> "OperationBuilder":
        edge = OperationEdge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            data_flow_label=data_flow_label,
        )
        self._edges.append(edge)
        return self

    def build_graph(self) -> OperationGraph:
        return OperationGraph(
            nodes=dict(self._nodes),
            edges=tuple(self._edges),
        )

    def build_pipeline(self) -> OperationPipeline:
        graph = self.build_graph()
        return OperationPipeline(
            graph=graph,
            operations=tuple(self._operations),
        )

