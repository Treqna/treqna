from abc import ABC, abstractmethod

from treqna.core.context import PipelineContext
from treqna.core.udm import UDMDocument
from treqna.plugins.interface import PluginInterface


class WriterPluginInterface(PluginInterface, ABC):
    @property
    @abstractmethod
    def format_identifier(self) -> str:
        ...

    @abstractmethod
    def write_from_udm(
        self,
        document: UDMDocument,
        context: PipelineContext,
    ) -> bytes | str:
        ...


class FormatValidatorInterface(ABC):
    @abstractmethod
    def validate_output(self, output_data: bytes | str) -> bool:
        ...

