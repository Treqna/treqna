from abc import ABC, abstractmethod

from treqna.core.context import PipelineContext
from treqna.core.udm import UDMDocument
from treqna.plugins.interface import PluginInterface


class UDMTransformerPluginInterface(PluginInterface, ABC):
    @abstractmethod
    def transform_udm(
        self,
        document: UDMDocument,
        context: PipelineContext,
    ) -> UDMDocument: ...
