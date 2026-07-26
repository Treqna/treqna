from collections.abc import Mapping
from dataclasses import dataclass, field

from treqna.operations.models import OperationDescriptor


@dataclass(frozen=True, kw_only=True)
class OperationNode:
    node_id: str
    descriptor: OperationDescriptor


@dataclass(frozen=True, kw_only=True)
class OperationEdge:
    source_node_id: str
    target_node_id: str
    data_flow_label: str = ""


@dataclass(frozen=True, kw_only=True)
class OperationGraph:
    nodes: Mapping[str, OperationNode] = field(default_factory=dict)
    edges: tuple[OperationEdge, ...] = field(default_factory=tuple)

    def node_count(self) -> int:
        return len(self.nodes)

    def edge_count(self) -> int:
        return len(self.edges)
