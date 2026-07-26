from collections.abc import Iterable
from typing import Any

import yaml  # type: ignore[import-untyped]

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
from treqna.plugins.parser import ParserPluginInterface
from treqna.plugins.yaml.options import YAMLOptions


def yaml_obj_to_udm_node(obj: Any) -> UDMNode:
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
        nodes = tuple(yaml_obj_to_udm_node(item) for item in obj)
        return UDMCollection(items=nodes)
    return UDMPrimitive(value=obj)


def extract_yaml_options(context: PipelineContext | None) -> YAMLOptions:
    if context is None or not context.execution_context.metadata:
        return YAMLOptions()
    attrs = context.execution_context.metadata.custom_attributes
    return YAMLOptions(
        indent=int(attrs.get("indent", 2)),
        explicit_start=bool(attrs.get("explicit_start", False)),
        explicit_end=bool(attrs.get("explicit_end", False)),
        default_flow_style=attrs.get("default_flow_style", False),
        allow_unicode=bool(attrs.get("allow_unicode", True)),
        sort_keys=bool(attrs.get("sort_keys", False)),
        encoding=str(attrs.get("encoding", "utf-8")),
        is_multi_document=bool(attrs.get("is_multi_document", False)),
    )


class YAMLParserPlugin(ParserPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="yaml_parser",
            version="1.0.0",
            format_identifier="yaml",
            description="Official Treqna YAML to UDM Parser Plugin",
            supported_media_types=("application/x-yaml", "text/yaml"),
        )

    @property
    def format_identifier(self) -> str:
        return "yaml"

    def initialize(self, context: PipelineContext) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def parse_to_udm(
        self,
        source_data: bytes | str,
        context: PipelineContext,
    ) -> UDMDocument:
        options = extract_yaml_options(context)
        text_content = decode_source_data(source_data, encoding=options.encoding)
        if not text_content.strip():
            return UDMDocument(
                root=UDMPrimitive(value=None),
                schema_identifier="yaml_empty",
            )
        try:
            if options.is_multi_document or "---" in text_content:
                docs_list = list(yaml.safe_load_all(text_content))
                if len(docs_list) > 1:
                    nodes = tuple(yaml_obj_to_udm_node(doc) for doc in docs_list)
                    return UDMDocument(
                        root=UDMCollection(items=nodes),
                        schema_identifier="yaml_multi",
                    )
                parsed = docs_list[0] if docs_list else None
            else:
                parsed = yaml.safe_load(text_content)
            root_node = yaml_obj_to_udm_node(parsed)
            return UDMDocument(root=root_node, schema_identifier="yaml")
        except Exception:
            return UDMDocument(
                root=UDMPrimitive(value=text_content),
                schema_identifier="yaml_raw",
            )

    def stream_parse_to_udm(
        self,
        stream: Iterable[str],
        options: YAMLOptions | None = None,
    ) -> UDMDocument:
        text_content = "".join(stream)
        if not text_content.strip():
            return UDMDocument(
                root=UDMPrimitive(value=None),
                schema_identifier="yaml_stream_empty",
            )
        try:
            parsed = yaml.safe_load(text_content)
            root_node = yaml_obj_to_udm_node(parsed)
            return UDMDocument(root=root_node, schema_identifier="yaml_stream")
        except Exception:
            return UDMDocument(
                root=UDMPrimitive(value=text_content),
                schema_identifier="yaml_stream_raw",
            )
