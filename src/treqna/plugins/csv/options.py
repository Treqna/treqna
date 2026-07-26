import csv
from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class CSVOptions:
    delimiter: str = ","
    quotechar: str = '"'
    escapechar: str | None = None
    doublequote: bool = True
    skipinitialspace: bool = False
    lineterminator: str = "\r\n"
    quoting: int = csv.QUOTE_MINIMAL
    encoding: str = "utf-8"
    has_header: bool = True
