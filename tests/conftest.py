import pytest

from treqna.config import EngineConfig


@pytest.fixture
def default_engine_config() -> EngineConfig:
    return EngineConfig(name="test_engine", verbose=False)

