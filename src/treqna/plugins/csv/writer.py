import csv
import io
from typing import Any, TextIO

from treqna.core.context import PipelineContext
from treqna.core.udm import UDMDocument, UDMTabular
from treqna.plugins.csv.options import CSVOptions
from treqna.plugins.csv.parser import extract_csv_options
from treqna.plugins.interface import PluginMetadata
from treqna.plugins.writer import WriterPluginInterface


class CSVWriterPlugin(WriterPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="csv_writer",
            version="1.0.0",
            format_identifier="csv",
            description="Official Treqna UDM to CSV Writer Plugin",
            supported_media_types=("text/csv", "text/tab-separated-values"),
        )

    @property
    def format_identifier(self) -> str:
        return "csv"

    def initialize(self, context: PipelineContext) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def write_from_udm(
        self,
        document: UDMDocument,
        context: PipelineContext,
    ) -> str:
        options = extract_csv_options(context)
        stream = io.StringIO()
        self.stream_write_from_udm(document, stream, options)
        return stream.getvalue()

    def stream_write_from_udm(
        self,
        document: UDMDocument,
        target_stream: TextIO,
        options: CSVOptions | None = None,
    ) -> None:
        opts = options if options is not None else CSVOptions()
        kwargs: dict[str, Any] = {
            "delimiter": opts.delimiter,
            "quotechar": opts.quotechar,
            "doublequote": opts.doublequote,
            "skipinitialspace": opts.skipinitialspace,
            "lineterminator": opts.lineterminator,
            "quoting": opts.quoting,
        }
        if opts.escapechar is not None:
            kwargs["escapechar"] = opts.escapechar

        writer = csv.writer(target_stream, **kwargs)

        if isinstance(document.root, UDMTabular):
            tabular = document.root
            if opts.has_header and tabular.columns:
                writer.writerow(list(tabular.columns))
            for row in tabular.rows:
                writer.writerow(list(row))

