import json
from typing import Any, TextIO

from treqna.core.context import PipelineContext
from treqna.core.udm import (
    UDMCollection,
    UDMDocument,
    UDMNode,
    UDMPrimitive,
    UDMTabular,
)
from treqna.plugins.interface import PluginMetadata
from treqna.plugins.json.options import JSONOptions
from treqna.plugins.json.parser import extract_json_options
from treqna.plugins.writer import WriterPluginInterface


def udm_node_to_json_obj(node: UDMNode) -> Any:
    if isinstance(node, UDMPrimitive):
        return node.value
    if isinstance(node, UDMTabular):
        cols = list(node.columns)
        result_list: list[dict[str, Any]] = []
        for row in node.rows:
            row_dict = {
                cols[i]: row[i] if i < len(row) else None for i in range(len(cols))
            }
            result_list.append(row_dict)
        return result_list
    if isinstance(node, UDMCollection):
        return [udm_node_to_json_obj(item) for item in node.items]
    if isinstance(node, UDMDocument):
        return udm_node_to_json_obj(node.root)
    return str(node)


class JSONWriterPlugin(WriterPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="json_writer",
            version="1.0.0",
            format_identifier="json",
            description="Official Treqna UDM to JSON Writer Plugin",
            supported_media_types=("application/json", "text/json"),
        )

    @property
    def format_identifier(self) -> str:
        return "json"

    def initialize(self, context: PipelineContext) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def write_from_udm(
        self,
        document: UDMDocument,
        context: PipelineContext,
    ) -> str:
        options = extract_json_options(context)
        json_obj = udm_node_to_json_obj(document.root)
        return json.dumps(
            json_obj,
            indent=options.indent,
            ensure_ascii=options.ensure_ascii,
            sort_keys=options.sort_keys,
            allow_nan=options.allow_nan,
        )

    def stream_write_from_udm(
        self,
        document: UDMDocument,
        target_stream: TextIO,
        options: JSONOptions | None = None,
    ) -> None:
        opts = options if options is not None else JSONOptions()
        json_obj = udm_node_to_json_obj(document.root)
        json.dump(
            json_obj,
            target_stream,
            indent=opts.indent,
            ensure_ascii=opts.ensure_ascii,
            sort_keys=opts.sort_keys,
            allow_nan=opts.allow_nan,
        )
