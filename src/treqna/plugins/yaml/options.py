from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class YAMLOptions:
    indent: int = 2
    explicit_start: bool = False
    explicit_end: bool = False
    default_flow_style: bool | None = False
    allow_unicode: bool = True
    sort_keys: bool = False
    encoding: str = "utf-8"
    is_multi_document: bool = False
