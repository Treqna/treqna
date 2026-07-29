from collections.abc import Mapping
from typing import Any

from treqna.config import EngineConfig
from treqna.core.contracts import TransformationRequest, TransformationResult
from treqna.core.engine import TransformationEngine
from treqna.core.udm import UDMDocument, UDMNode
from treqna.plugins.parser import ParserPluginInterface
from treqna.plugins.registry import PluginRegistry
from treqna.plugins.transformer import UDMTransformerPluginInterface
from treqna.plugins.writer import WriterPluginInterface


class TreqnaClient:
    def __init__(
        self,
        config: EngineConfig | None = None,
        plugin_registry: PluginRegistry | None = None,
    ) -> None:
        self._plugin_registry = (
            plugin_registry if plugin_registry is not None else PluginRegistry()
        )
        self._engine = TransformationEngine(config=config)

    @property
    def engine(self) -> TransformationEngine:
        return self._engine

    @property
    def plugin_registry(self) -> PluginRegistry:
        return self._plugin_registry

    def initialize(self) -> None:
        self._engine.initialize()

    def shutdown(self) -> None:
        self._engine.shutdown()

    def register_parser(self, parser: ParserPluginInterface) -> None:
        self._plugin_registry.register_parser(parser)

    def register_writer(self, writer: WriterPluginInterface) -> None:
        self._plugin_registry.register_writer(writer)

    def register_transformer(
        self,
        name: str,
        transformer: UDMTransformerPluginInterface,
    ) -> None:
        self._plugin_registry.register_transformer(name, transformer)

    def transform(
        self,
        source_format: str,
        target_format: str,
        payload: UDMDocument | UDMNode | bytes | str,
        options: Mapping[str, Any] | None = None,
    ) -> TransformationResult:
        request = TransformationRequest(
            source_format=source_format,
            target_format=target_format,
            payload=payload,
            options=options if options is not None else {},
        )
        return self._engine.transform(request)

    def get_status(self) -> dict[str, Any]:
        status = self._engine.get_status()
        status["registered_parsers"] = list(self._plugin_registry.list_parsers())
        status["registered_writers"] = list(self._plugin_registry.list_writers())
        status["registered_transformers"] = list(
            self._plugin_registry.list_transformers()
        )
        return status
