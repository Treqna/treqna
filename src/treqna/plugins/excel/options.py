from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class ExcelOptions:
    worksheet_name: str = "Sheet1"
    header_row: int = 0
    create_missing_sheet: bool = True
    overwrite_file: bool = True
    date_format: str = "YYYY-MM-DD"
    datetime_format: str = "YYYY-MM-DD HH:MM:SS"
    auto_column_width: bool = True
    freeze_header: bool = True
    preserve_empty_rows: bool = False
    encoding: str = "utf-8"
