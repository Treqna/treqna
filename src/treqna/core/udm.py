from abc import ABC, abstractmethod
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from treqna.core.enums import UDMValueKindEnum


@dataclass(frozen=True, kw_only=True)
class UDMNode(ABC):
    metadata: Mapping[str, Any] = field(default_factory=dict)

    @property
    @abstractmethod
    def kind(self) -> UDMValueKindEnum:
        ...


@dataclass(frozen=True, kw_only=True)
class UDMPrimitive(UDMNode):
    value: str | int | float | bool | None
    data_type: str = "primitive"
    unit: str | None = None

    @property
    def kind(self) -> UDMValueKindEnum:
        return UDMValueKindEnum.PRIMITIVE


@dataclass(frozen=True, kw_only=True)
class UDMText(UDMNode):
    content: str
    encoding: str = "utf-8"
    media_type: str = "text/plain"

    @property
    def kind(self) -> UDMValueKindEnum:
        return UDMValueKindEnum.TEXT


@dataclass(frozen=True, kw_only=True)
class UDMBinary(UDMNode):
    data: bytes
    media_type: str = "application/octet-stream"

    @property
    def kind(self) -> UDMValueKindEnum:
        return UDMValueKindEnum.BINARY


@dataclass(frozen=True, kw_only=True)
class UDMTabular(UDMNode):
    columns: tuple[str, ...]
    rows: tuple[tuple[Any, ...], ...]

    @property
    def kind(self) -> UDMValueKindEnum:
        return UDMValueKindEnum.TABULAR


@dataclass(frozen=True, kw_only=True)
class UDMHierarchical(UDMNode):
    name: str
    value: UDMNode | None = None
    children: tuple["UDMHierarchical", ...] = field(default_factory=tuple)

    @property
    def kind(self) -> UDMValueKindEnum:
        return UDMValueKindEnum.HIERARCHICAL


@dataclass(frozen=True, kw_only=True)
class UDMCollection(UDMNode):
    items: tuple[UDMNode, ...] = field(default_factory=tuple)

    @property
    def kind(self) -> UDMValueKindEnum:
        return UDMValueKindEnum.COLLECTION


@dataclass(frozen=True, kw_only=True)
class UDMObject(UDMNode):
    properties: Mapping[str, UDMNode] = field(default_factory=dict)

    @property
    def kind(self) -> UDMValueKindEnum:
        return UDMValueKindEnum.OBJECT


@dataclass(frozen=True, kw_only=True)
class UDMDocument:
    root: UDMNode
    metadata: Mapping[str, Any] = field(default_factory=dict)
    schema_identifier: str | None = None

