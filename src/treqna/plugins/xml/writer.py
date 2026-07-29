import xml.dom.minidom
import xml.etree.ElementTree as ET
from typing import Any, TextIO

from treqna.core.context import PipelineContext
from treqna.core.udm import UDMDocument, UDMTabular
from treqna.plugins.interface import PluginMetadata
from treqna.plugins.json.writer import udm_node_to_json_obj
from treqna.plugins.writer import WriterPluginInterface
from treqna.plugins.xml.options import XMLOptions
from treqna.plugins.xml.parser import extract_xml_options


def sanitize_xml_tag(tag: str) -> str:
    cleaned = str(tag).lstrip("@#").strip()
    cleaned = "".join(c if c.isalnum() or c in ("_", "-") else "_" for c in cleaned)
    if not cleaned or cleaned[0].isdigit():
        cleaned = f"elem_{cleaned}"
    return cleaned


def build_xml_element(tag: str, obj: Any) -> ET.Element:
    safe_tag = sanitize_xml_tag(tag)
    elem = ET.Element(safe_tag)
    if isinstance(obj, dict):
        for k, v in obj.items():
            if str(k).startswith("@"):
                attr_name = sanitize_xml_tag(str(k)[1:])
                elem.set(attr_name, str(v))
            elif str(k) == "#text":
                elem.text = str(v)
            elif isinstance(v, list):
                for item in v:
                    elem.append(build_xml_element(str(k), item))
            else:
                elem.append(build_xml_element(str(k), v))
    elif isinstance(obj, list):
        for item in obj:
            elem.append(build_xml_element("item", item))
    elif obj is not None:
        elem.text = str(obj)
    return elem


def format_xml_string(
    root_elem: ET.Element,
    options: XMLOptions,
) -> str:
    raw_bytes = ET.tostring(root_elem, encoding=options.encoding)
    if not options.pretty_print:
        out_str = raw_bytes.decode(options.encoding, errors="replace")
        if not options.xml_declaration and out_str.startswith("<?xml"):
            out_str = out_str.split("?>", 1)[-1].lstrip()
        return str(out_str)

    parsed = xml.dom.minidom.parseString(raw_bytes)
    pretty = parsed.toprettyxml(indent=" " * options.indent, encoding=options.encoding)
    pretty_str = pretty.decode(options.encoding, errors="replace")

    if not options.xml_declaration and pretty_str.startswith("<?xml"):
        pretty_str = pretty_str.split("?>", 1)[-1].lstrip()
    return str(pretty_str)


class XMLWriterPlugin(WriterPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="xml_writer",
            version="1.0.0",
            format_identifier="xml",
            description="Official Treqna UDM to XML Writer Plugin",
            supported_media_types=("application/xml", "text/xml"),
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
    ) -> str:
        options = extract_xml_options(context)
        node = document.root

        if isinstance(node, UDMTabular):
            root_elem = ET.Element(sanitize_xml_tag(options.root_tag))
            cols = list(node.columns)
            row_tag = sanitize_xml_tag(options.row_tag)
            for row in node.rows:
                row_elem = ET.SubElement(root_elem, row_tag)
                for i, c in enumerate(cols):
                    val = row[i] if i < len(row) else None
                    val_tag = sanitize_xml_tag(str(c))
                    val_elem = ET.SubElement(row_elem, val_tag)
                    if val is not None:
                        val_elem.text = str(val)
            return format_xml_string(root_elem, options)

        json_obj = udm_node_to_json_obj(node)
        root_elem = build_xml_element(options.root_tag, json_obj)
        return format_xml_string(root_elem, options)

    def stream_write_from_udm(
        self,
        document: UDMDocument,
        target_stream: TextIO,
        options: XMLOptions | None = None,
    ) -> None:
        opts = options if options is not None else XMLOptions()
        json_obj = udm_node_to_json_obj(document.root)
        root_elem = build_xml_element(opts.root_tag, json_obj)
        output_str = format_xml_string(root_elem, opts)
        target_stream.write(output_str)
