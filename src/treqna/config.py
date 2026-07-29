from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True, kw_only=True)
class EngineConfig:
    name: str = "treqna_engine"
    verbose: bool = False
    max_workers: int = 4
    timeout_seconds: float = 30.0
    extra_options: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class PluginConfig:
    enabled: bool = True
    auto_discover: bool = True
    plugin_directories: list[str] = field(default_factory=list)


@dataclass(frozen=True, kw_only=True)
class AppConfig:
    engine: EngineConfig = field(default_factory=EngineConfig)
    plugins: PluginConfig = field(default_factory=PluginConfig)
    environment: str = "production"
