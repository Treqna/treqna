from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any

from treqna.core.context import PipelineContext
from treqna.core.udm import UDMDocument
from treqna.plugins.interface import PluginInterface


class ParserPluginInterface(PluginInterface, ABC):
    @property
    @abstractmethod
    def format_identifier(self) -> str:
        ...

    @abstractmethod
    def parse_to_udm(
        self,
        source_data: bytes | str,
        context: PipelineContext,
    ) -> UDMDocument:
        ...


class FormatDetectorInterface(ABC):
    @abstractmethod
    def can_detect(self, source_data: bytes | str) -> bool:
        ...

    @abstractmethod
    def detect_format(self, source_data: bytes | str) -> str:
        ...


class FormatInspectorInterface(ABC):
    @abstractmethod
    def inspect_schema(self, source_data: bytes | str) -> Mapping[str, Any]:
        ...
