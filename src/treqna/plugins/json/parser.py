import json
from collections.abc import Iterable
from typing import Any

from treqna.core.context import PipelineContext
from treqna.core.udm import (
    UDMCollection,
    UDMDocument,
    UDMNode,
    UDMPrimitive,
    UDMTabular,
)
from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.interface import PluginMetadata
from treqna.plugins.json.options import JSONOptions
from treqna.plugins.parser import ParserPluginInterface


def json_obj_to_udm_node(obj: Any) -> UDMNode:
    if isinstance(obj, dict):
        cols = tuple(str(k) for k in obj)
        vals = tuple(obj.values())
        return UDMTabular(columns=cols, rows=(vals,))
    if isinstance(obj, list):
        if obj and all(isinstance(item, dict) for item in obj):
            all_cols: list[str] = []
            for item in obj:
                for k in item:
                    if str(k) not in all_cols:
                        all_cols.append(str(k))
            rows_list: list[tuple[Any, ...]] = []
            for item in obj:
                row_vals = tuple(item.get(c) for c in all_cols)
                rows_list.append(row_vals)
            return UDMTabular(columns=tuple(all_cols), rows=tuple(rows_list))
        nodes = tuple(json_obj_to_udm_node(item) for item in obj)
        return UDMCollection(items=nodes)
    return UDMPrimitive(value=obj)


def extract_json_options(context: PipelineContext | None) -> JSONOptions:
    if context is None or not context.execution_context.metadata:
        return JSONOptions()
    attrs = context.execution_context.metadata.custom_attributes
    indent_val = attrs.get("indent", 2)
    indent = int(indent_val) if indent_val is not None else None
    return JSONOptions(
        indent=indent,
        ensure_ascii=bool(attrs.get("ensure_ascii", False)),
        sort_keys=bool(attrs.get("sort_keys", False)),
        encoding=str(attrs.get("encoding", "utf-8")),
        allow_nan=bool(attrs.get("allow_nan", True)),
    )


class JSONParserPlugin(ParserPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="json_parser",
            version="1.0.0",
            format_identifier="json",
            description="Official Treqna JSON to UDM Parser Plugin",
            supported_media_types=("application/json", "text/json"),
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
        options = extract_json_options(context)
        text_content = decode_source_data(source_data, encoding=options.encoding)
        if not text_content.strip():
            return UDMDocument(
                root=UDMPrimitive(value=None),
                schema_identifier="json_empty",
            )
        try:
            parsed = json.loads(text_content)
            root_node = json_obj_to_udm_node(parsed)
            return UDMDocument(root=root_node, schema_identifier="json")
        except json.JSONDecodeError:
            return UDMDocument(
                root=UDMPrimitive(value=text_content),
                schema_identifier="json_raw",
            )

    def stream_parse_to_udm(
        self,
        stream: Iterable[str],
        options: JSONOptions | None = None,
    ) -> UDMDocument:
        text_content = "".join(stream)
        if not text_content.strip():
            return UDMDocument(
                root=UDMPrimitive(value=None),
                schema_identifier="json_stream_empty",
            )
        parsed = json.loads(text_content)
        root_node = json_obj_to_udm_node(parsed)
        return UDMDocument(root=root_node, schema_identifier="json_stream")
