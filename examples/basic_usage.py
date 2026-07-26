from treqna import EngineConfig, TreqnaClient


def run_example() -> None:
    configuration = EngineConfig(name="example_instance", verbose=True)
    client = TreqnaClient(config=configuration)
    client.initialize()

    result = client.transform(
        source_format="json",
        target_format="xml",
        payload="<data>sample payload</data>",
    )

    print(f"Transformation status: {result.status.value}")
    print(f"Stage count: {len(result.stage_results)}")

    status = client.get_status()
    print(f"Client status: {status}")

    client.shutdown()


if __name__ == "__main__":
    run_example()

