from treqna.exceptions import PluginNotFoundError
from treqna.plugins.parser import ParserPluginInterface
from treqna.plugins.transformer import UDMTransformerPluginInterface
from treqna.plugins.writer import WriterPluginInterface


class PluginRegistry:
    def __init__(self) -> None:
        self._parsers: dict[str, ParserPluginInterface] = {}
        self._writers: dict[str, WriterPluginInterface] = {}
        self._transformers: dict[str, UDMTransformerPluginInterface] = {}

    def register_parser(self, parser: ParserPluginInterface) -> None:
        self._parsers[parser.format_identifier] = parser

    def get_parser(self, format_identifier: str) -> ParserPluginInterface:
        if format_identifier not in self._parsers:
            raise PluginNotFoundError(f"Parser for format '{format_identifier}'")
        return self._parsers[format_identifier]

    def has_parser(self, format_identifier: str) -> bool:
        return format_identifier in self._parsers

    def register_writer(self, writer: WriterPluginInterface) -> None:
        self._writers[writer.format_identifier] = writer

    def get_writer(self, format_identifier: str) -> WriterPluginInterface:
        if format_identifier not in self._writers:
            raise PluginNotFoundError(f"Writer for format '{format_identifier}'")
        return self._writers[format_identifier]

    def has_writer(self, format_identifier: str) -> bool:
        return format_identifier in self._writers

    def register_transformer(
        self,
        name: str,
        transformer: UDMTransformerPluginInterface,
    ) -> None:
        self._transformers[name] = transformer

    def get_transformer(self, name: str) -> UDMTransformerPluginInterface:
        if name not in self._transformers:
            raise PluginNotFoundError(f"Transformer '{name}'")
        return self._transformers[name]

    def list_parsers(self) -> tuple[str, ...]:
        return tuple(self._parsers.keys())

    def list_writers(self) -> tuple[str, ...]:
        return tuple(self._writers.keys())

    def list_transformers(self) -> tuple[str, ...]:
        return tuple(self._transformers.keys())

    def clear(self) -> None:
        self._parsers.clear()
        self._writers.clear()
        self._transformers.clear()
