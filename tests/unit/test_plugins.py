import pytest

from treqna.core.context import PipelineContext
from treqna.core.udm import UDMDocument, UDMPrimitive
from treqna.exceptions import PluginNotFoundError
from treqna.plugins.interface import PluginInterface, PluginMetadata
from treqna.plugins.parser import ParserPluginInterface
from treqna.plugins.registry import PluginRegistry
from treqna.plugins.writer import WriterPluginInterface


class MockParser(ParserPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="mock_parser",
            version="1.0.0",
            format_identifier="json",
        )

    @property
    def format_identifier(self) -> str:
        return "json"

    def initialize(self, context: PipelineContext) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def parse_to_udm(
        self,
        source_data: bytes | str,
        context: PipelineContext,
    ) -> UDMDocument:
        root_node = UDMPrimitive(value=str(source_data))
        return UDMDocument(root=root_node)


class MockWriter(WriterPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="mock_writer",
            version="1.0.0",
            format_identifier="xml",
        )

    @property
    def format_identifier(self) -> str:
        return "xml"

    def initialize(self, context: PipelineContext) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def write_from_udm(
        self,
        document: UDMDocument,
        context: PipelineContext,
    ) -> bytes | str:
        return "<xml></xml>"


def test_plugin_registry_operations() -> None:
    registry = PluginRegistry()
    parser = MockParser()
    writer = MockWriter()

    registry.register_parser(parser)
    registry.register_writer(writer)

    assert registry.has_parser("json")
    assert registry.has_writer("xml")

    retrieved_parser = registry.get_parser("json")
    retrieved_writer = registry.get_writer("xml")

    assert retrieved_parser.metadata.name == "mock_parser"
    assert retrieved_writer.metadata.name == "mock_writer"

    assert registry.list_parsers() == ("json",)
    assert registry.list_writers() == ("xml",)


def test_plugin_not_found_raises() -> None:
    registry = PluginRegistry()

    with pytest.raises(PluginNotFoundError):
        registry.get_parser("yaml")

    with pytest.raises(PluginNotFoundError):
        registry.get_writer("csv")
