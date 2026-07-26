import csv
import io
from collections.abc import Iterable
from typing import Any

from treqna.core.context import PipelineContext
from treqna.core.udm import UDMDocument, UDMTabular
from treqna.plugins.csv.options import CSVOptions
from treqna.plugins.interface import PluginMetadata
from treqna.plugins.parser import ParserPluginInterface


def decode_source_data(source_data: bytes | str, encoding: str = "utf-8") -> str:
    if isinstance(source_data, str):
        return source_data
    if source_data.startswith(b"\xff\xfe") or source_data.startswith(b"\xfe\xff"):
        return source_data.decode("utf-16")
    if encoding.lower().replace("-", "") in ("utf16", "utf16le", "utf16be"):
        return source_data.decode(encoding)
    try:
        return source_data.decode(encoding)
    except UnicodeDecodeError:
        return source_data.decode("utf-16", errors="replace")


def extract_csv_options(context: PipelineContext | None) -> CSVOptions:
    if context is None or not context.execution_context.metadata:
        return CSVOptions()
    attrs = context.execution_context.metadata.custom_attributes
    return CSVOptions(
        delimiter=str(attrs.get("delimiter", ",")),
        quotechar=str(attrs.get("quotechar", '"')),
        escapechar=attrs.get("escapechar"),
        doublequote=bool(attrs.get("doublequote", True)),
        skipinitialspace=bool(attrs.get("skipinitialspace", False)),
        lineterminator=str(attrs.get("lineterminator", "\r\n")),
        quoting=int(attrs.get("quoting", csv.QUOTE_MINIMAL)),
        encoding=str(attrs.get("encoding", "utf-8")),
        has_header=bool(attrs.get("has_header", True)),
    )


class CSVParserPlugin(ParserPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="csv_parser",
            version="1.0.0",
            format_identifier="csv",
            description="Official Treqna CSV to UDM Parser Plugin",
            supported_media_types=("text/csv", "text/tab-separated-values"),
        )

    @property
    def format_identifier(self) -> str:
        return "csv"

    def initialize(self, context: PipelineContext) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def parse_to_udm(
        self,
        source_data: bytes | str,
        context: PipelineContext,
    ) -> UDMDocument:
        options = extract_csv_options(context)
        text_content = decode_source_data(source_data, encoding=options.encoding)
        stream = io.StringIO(text_content)

        kwargs: dict[str, Any] = {
            "delimiter": options.delimiter,
            "quotechar": options.quotechar,
            "doublequote": options.doublequote,
            "skipinitialspace": options.skipinitialspace,
            "quoting": options.quoting,
        }
        if options.escapechar is not None:
            kwargs["escapechar"] = options.escapechar

        reader = csv.reader(stream, **kwargs)

        columns_list: list[str] = []
        rows_list: list[tuple[Any, ...]] = []

        try:
            if options.has_header:
                try:
                    first_row = next(reader)
                    columns_list = [str(col).strip() for col in first_row]
                except StopIteration:
                    columns_list = []

            for row in reader:
                if not row or (len(row) == 1 and row[0] == ""):
                    continue
                if not columns_list and not options.has_header:
                    columns_list = [f"column_{i}" for i in range(len(row))]
                rows_list.append(tuple(row))
        except (csv.Error, UnicodeDecodeError):
            pass

        tabular_node = UDMTabular(
            columns=tuple(columns_list),
            rows=tuple(rows_list),
        )
        return UDMDocument(root=tabular_node, schema_identifier="csv_tabular")

    def stream_parse_to_udm(
        self,
        stream: Iterable[str],
        options: CSVOptions | None = None,
    ) -> UDMDocument:
        opts = options if options is not None else CSVOptions()
        kwargs: dict[str, Any] = {
            "delimiter": opts.delimiter,
            "quotechar": opts.quotechar,
            "doublequote": opts.doublequote,
            "skipinitialspace": opts.skipinitialspace,
            "quoting": opts.quoting,
        }
        if opts.escapechar is not None:
            kwargs["escapechar"] = opts.escapechar

        reader = csv.reader(stream, **kwargs)

        columns_list: list[str] = []
        rows_list: list[tuple[Any, ...]] = []

        try:
            if opts.has_header:
                try:
                    first_row = next(reader)
                    columns_list = [str(col).strip() for col in first_row]
                except StopIteration:
                    columns_list = []

            for row in reader:
                if not row or (len(row) == 1 and row[0] == ""):
                    continue
                if not columns_list:
                    columns_list = [f"column_{i}" for i in range(len(row))]
                rows_list.append(tuple(row))
        except (csv.Error, UnicodeDecodeError):
            pass

        tabular_node = UDMTabular(
            columns=tuple(columns_list),
            rows=tuple(rows_list),
        )
        return UDMDocument(root=tabular_node, schema_identifier="csv_tabular_stream")

