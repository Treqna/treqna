from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from treqna.core.context import PipelineContext


@dataclass(frozen=True, kw_only=True)
class PluginMetadata:
    name: str
    version: str
    format_identifier: str = ""
    description: str = ""
    author: str = ""
    supported_media_types: tuple[str, ...] = field(default_factory=tuple)
    dependencies: tuple[str, ...] = field(default_factory=tuple)


class PluginInterface(ABC):
    @property
    @abstractmethod
    def metadata(self) -> PluginMetadata:
        ...

    @abstractmethod
    def initialize(self, context: PipelineContext) -> None:
        ...

    @abstractmethod
    def shutdown(self) -> None:
        ...
