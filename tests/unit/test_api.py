from treqna.api.client import TreqnaClient
from treqna.config import EngineConfig
from treqna.core.enums import ResultStatusEnum


def test_api_client_initialization() -> None:
    config = EngineConfig(name="api_test_instance", verbose=True)
    client = TreqnaClient(config=config)

    client.initialize()
    assert client.engine.is_running

    status = client.get_status()
    assert status["name"] == "api_test_instance"
    assert status["running"] is True
    assert isinstance(status["registered_parsers"], list)
    assert isinstance(status["registered_writers"], list)

    client.shutdown()
    assert not client.engine.is_running


def test_api_client_transform_invocation() -> None:
    client = TreqnaClient()
    result = client.transform(
        source_format="json",
        target_format="xml",
        payload="<data>hello</data>",
    )

    assert result.status == ResultStatusEnum.SUCCESS
    assert result.output_format == "xml"
    assert len(result.stage_results) == 8

