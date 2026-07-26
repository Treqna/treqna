from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class JSONOptions:
    indent: int | None = 2
    ensure_ascii: bool = False
    sort_keys: bool = False
    encoding: str = "utf-8"
    allow_nan: bool = True
