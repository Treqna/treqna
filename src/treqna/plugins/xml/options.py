from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class XMLOptions:
    indent: int = 2
    encoding: str = "utf-8"
    pretty_print: bool = True
    xml_declaration: bool = True
    root_tag: str = "root"
    row_tag: str = "item"
    preserve_comments: bool = True
    standalone: bool | None = None
    sort_attributes: bool = False

