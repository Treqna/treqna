from typing import Any

from treqna.config import EngineConfig
from treqna.core.contracts import TransformationRequest, TransformationResult
from treqna.core.pipeline import PipelineExecutor, PipelineRegistry
from treqna.core.session import LifecycleManager, TransformationSession
from treqna.formats.registry import FormatRegistry
from treqna.logging import get_logger
from treqna.plugins.discovery import discover_and_register_plugins
from treqna.plugins.registry import PluginRegistry


class TransformationEngine:
    def __init__(
        self,
        config: EngineConfig | None = None,
        plugin_registry: PluginRegistry | None = None,
        format_registry: FormatRegistry | None = None,
    ) -> None:
        self.config = config if config is not None else EngineConfig()
        self.plugin_registry = (
            plugin_registry if plugin_registry is not None else PluginRegistry()
        )
        self.format_registry = (
            format_registry if format_registry is not None else FormatRegistry()
        )
        discover_and_register_plugins(self.plugin_registry, self.format_registry)

        self.pipeline_registry = PipelineRegistry()
        self.pipeline_executor = PipelineExecutor()
        self.lifecycle_manager = LifecycleManager()
        self.logger = get_logger("treqna.core.engine")
        self._is_running: bool = False

    @property
    def is_running(self) -> bool:
        return self._is_running

    def initialize(self) -> None:
        if self._is_running:
            return
        self.logger.info(f"Initializing Transformation Engine '{self.config.name}'")
        self._is_running = True

    def shutdown(self) -> None:
        if not self._is_running:
            return
        self.logger.info(f"Shutting down Transformation Engine '{self.config.name}'")
        self.lifecycle_manager.clear_all()
        self._is_running = False

    def create_session(
        self,
        request: TransformationRequest,
    ) -> TransformationSession:
        return self.lifecycle_manager.create_session(
            request,
            plugin_registry=self.plugin_registry,
        )

    def transform(self, request: TransformationRequest) -> TransformationResult:
        if not self._is_running:
            self.initialize()
        session = self.create_session(request)
        return session.execute(request, self.pipeline_executor)

    def get_status(self) -> dict[str, Any]:
        return {
            "name": self.config.name,
            "running": self._is_running,
            "registered_parsers": list(self.plugin_registry.list_parsers()),
            "registered_writers": list(self.plugin_registry.list_writers()),
            "registered_stages": [
                s.value for s in self.pipeline_registry.list_stages()
            ],
            "active_sessions": list(self.lifecycle_manager.list_active_sessions()),
        }


Engine = TransformationEngine
