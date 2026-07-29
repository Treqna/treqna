import xml.etree.ElementTree as ET
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
from treqna.plugins.parser import ParserPluginInterface
from treqna.plugins.xml.options import XMLOptions


def elem_to_dict_or_scalar(elem: ET.Element) -> Any:
    children = list(elem)
    attrs = dict(elem.attrib)
    text = (elem.text or "").strip()

    if not children and not attrs:
        if not text:
            return None
        if text.lower() == "true":
            return True
        if text.lower() == "false":
            return False
        try:
            return int(text)
        except ValueError:
            pass
        try:
            return float(text)
        except ValueError:
            pass
        return text

    res: dict[str, Any] = {}
    for k, v in attrs.items():
        res[f"@{k}"] = v

    if children:
        for child in children:
            tag = child.tag
            if "}" in tag:
                tag = tag.split("}", 1)[1]
            val = elem_to_dict_or_scalar(child)
            if tag in res:
                existing = res[tag]
                if isinstance(existing, list):
                    existing.append(val)
                else:
                    res[tag] = [existing, val]
            else:
                res[tag] = val
    elif text:
        res["#text"] = text

    return res


def xml_tree_to_udm_node(root_elem: ET.Element) -> UDMNode:
    children = list(root_elem)

    if children and all(
        len(list(child)) > 0 or len(child.attrib) > 0 for child in children
    ):
        child_dicts: list[dict[str, Any]] = []
        for child in children:
            converted = elem_to_dict_or_scalar(child)
            if isinstance(converted, dict):
                child_dicts.append(converted)

        if child_dicts:
            all_cols: list[str] = []
            for cd in child_dicts:
                for k in cd:
                    if k not in all_cols:
                        all_cols.append(k)
            rows: list[tuple[Any, ...]] = []
            for cd in child_dicts:
                row_vals = tuple(cd.get(col) for col in all_cols)
                rows.append(row_vals)
            return UDMTabular(columns=tuple(all_cols), rows=tuple(rows))

    parsed_obj = elem_to_dict_or_scalar(root_elem)
    if isinstance(parsed_obj, dict):
        cols = tuple(str(k) for k in parsed_obj)
        vals = tuple(parsed_obj.values())
        return UDMTabular(columns=cols, rows=(vals,))
    if isinstance(parsed_obj, list):
        nodes = tuple(
            xml_tree_to_udm_node(item)
            if isinstance(item, ET.Element)
            else UDMPrimitive(value=item)
            for item in parsed_obj
        )
        return UDMCollection(items=nodes)

    return UDMPrimitive(value=parsed_obj)


def extract_xml_options(context: PipelineContext | None) -> XMLOptions:
    if context is None or not context.execution_context.metadata:
        return XMLOptions()
    attrs = context.execution_context.metadata.custom_attributes
    return XMLOptions(
        indent=int(attrs.get("indent", 2)),
        encoding=str(attrs.get("encoding", "utf-8")),
        pretty_print=bool(attrs.get("pretty_print", True)),
        xml_declaration=bool(attrs.get("xml_declaration", True)),
        root_tag=str(attrs.get("root_tag", "root")),
        row_tag=str(attrs.get("row_tag", "item")),
        preserve_comments=bool(attrs.get("preserve_comments", True)),
        sort_attributes=bool(attrs.get("sort_attributes", False)),
    )


class XMLParserPlugin(ParserPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="xml_parser",
            version="1.0.0",
            format_identifier="xml",
            description="Official Treqna XML to UDM Parser Plugin",
            supported_media_types=("application/xml", "text/xml"),
        )

    @property
    def format_identifier(self) -> str:
        return "xml"

    def initialize(self, context: PipelineContext) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def parse_to_udm(
        self,
        source_data: bytes | str,
        context: PipelineContext,
    ) -> UDMDocument:
        options = extract_xml_options(context)
        text_content = decode_source_data(source_data, encoding=options.encoding)
        if not text_content.strip():
            return UDMDocument(
                root=UDMPrimitive(value=None),
                schema_identifier="xml_empty",
            )
        try:
            root_elem = ET.fromstring(text_content)
            root_node = xml_tree_to_udm_node(root_elem)
            return UDMDocument(root=root_node, schema_identifier="xml")
        except (ET.ParseError, ValueError):
            return UDMDocument(
                root=UDMPrimitive(value=text_content),
                schema_identifier="xml_raw",
            )

    def stream_parse_to_udm(
        self,
        stream: Iterable[str],
        options: XMLOptions | None = None,
    ) -> UDMDocument:
        text_content = "".join(stream)
        if not text_content.strip():
            return UDMDocument(
                root=UDMPrimitive(value=None),
                schema_identifier="xml_stream_empty",
            )
        try:
            root_elem = ET.fromstring(text_content)
            root_node = xml_tree_to_udm_node(root_elem)
            return UDMDocument(root=root_node, schema_identifier="xml_stream")
        except ET.ParseError:
            return UDMDocument(
                root=UDMPrimitive(value=text_content),
                schema_identifier="xml_stream_raw",
            )
