import xml.etree.ElementTree as ET
from collections.abc import Mapping
from typing import Any

from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.parser import FormatInspectorInterface


def calculate_xml_depth(element: ET.Element) -> int:
    children = list(element)
    if not children:
        return 1
    return 1 + max(calculate_xml_depth(c) for c in children)


class XMLInspector(FormatInspectorInterface):
    def inspect_schema(self, source_data: bytes | str) -> Mapping[str, Any]:
        text = decode_source_data(source_data).strip()
        if not text:
            return {
                "structure_type": "empty",
                "root_tag": "",
                "element_count": 0,
                "attribute_count": 0,
                "has_namespaces": False,
                "has_cdata": False,
                "has_doctype": False,
                "depth": 0,
            }
        try:
            root = ET.fromstring(text)
            all_elements = list(root.iter())
            total_attrs = sum(len(e.attrib) for e in all_elements)
            has_ns = any("}" in e.tag for e in all_elements)
            has_cdata = "<![CDATA[" in text
            has_doctype = "<!DOCTYPE" in text
            depth = calculate_xml_depth(root)

            return {
                "structure_type": "document",
                "root_tag": root.tag,
                "element_count": len(all_elements),
                "attribute_count": total_attrs,
                "has_namespaces": has_ns,
                "has_cdata": has_cdata,
                "has_doctype": has_doctype,
                "depth": depth,
            }
        except ET.ParseError:
            return {
                "structure_type": "malformed",
                "root_tag": "",
                "element_count": 0,
                "attribute_count": 0,
                "has_namespaces": False,
                "has_cdata": False,
                "has_doctype": False,
                "depth": 0,
            }

