import io
import xml.etree.ElementTree as ET
import zipfile
from collections.abc import Iterable
from typing import Any

from treqna.core.context import ExecutionContext, PipelineContext
from treqna.core.udm import UDMDocument, UDMPrimitive, UDMTabular
from treqna.plugins.excel.options import ExcelOptions
from treqna.plugins.interface import PluginMetadata
from treqna.plugins.parser import ParserPluginInterface

NS_SPREADSHEET = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def extract_excel_options(context: PipelineContext | None) -> ExcelOptions:
    if context is None or not context.execution_context.metadata:
        return ExcelOptions()
    attrs = context.execution_context.metadata.custom_attributes
    return ExcelOptions(
        worksheet_name=str(attrs.get("worksheet_name", "Sheet1")),
        header_row=int(attrs.get("header_row", 0)),
        create_missing_sheet=bool(attrs.get("create_missing_sheet", True)),
        overwrite_file=bool(attrs.get("overwrite_file", True)),
        date_format=str(attrs.get("date_format", "YYYY-MM-DD")),
        datetime_format=str(attrs.get("datetime_format", "YYYY-MM-DD HH:MM:SS")),
        auto_column_width=bool(attrs.get("auto_column_width", True)),
        freeze_header=bool(attrs.get("freeze_header", True)),
        preserve_empty_rows=bool(attrs.get("preserve_empty_rows", False)),
        encoding=str(attrs.get("encoding", "utf-8")),
    )


def parse_shared_strings(zf: zipfile.ZipFile) -> list[str]:
    if "xl/sharedStrings.xml" not in zf.namelist():
        return []
    xml_data = zf.read("xl/sharedStrings.xml")
    root = ET.fromstring(xml_data)
    strings: list[str] = []
    for si in root.findall(f"{{{NS_SPREADSHEET}}}si"):
        t_elem = si.find(f"{{{NS_SPREADSHEET}}}t")
        if t_elem is not None and t_elem.text is not None:
            strings.append(t_elem.text)
        else:
            text_parts = [
                t.text
                for t in si.findall(f".//{{{NS_SPREADSHEET}}}t")
                if t.text is not None
            ]
            strings.append("".join(text_parts))
    return strings


def col_letter_to_index(cell_ref: str) -> int:
    col_str = "".join(c for c in cell_ref if c.isalpha())
    index = 0
    for c in col_str.upper():
        index = index * 26 + (ord(c) - ord("A") + 1)
    return index - 1


def parse_cell_value(c_elem: ET.Element, shared_strings: list[str]) -> Any:
    cell_type = c_elem.get("t")
    val_elem = c_elem.find(f"{{{NS_SPREADSHEET}}}v")
    if cell_type == "s":
        if val_elem is not None and val_elem.text is not None:
            idx = int(val_elem.text)
            return shared_strings[idx] if idx < len(shared_strings) else ""
        return ""
    if cell_type == "inlineStr":
        is_elem = c_elem.find(f"{{{NS_SPREADSHEET}}}is")
        if is_elem is not None:
            t_elem = is_elem.find(f"{{{NS_SPREADSHEET}}}t")
            if t_elem is not None and t_elem.text is not None:
                return t_elem.text
        return ""
    if cell_type == "b":
        if val_elem is not None and val_elem.text is not None:
            return val_elem.text == "1"
        return False
    if val_elem is not None and val_elem.text is not None:
        raw_val = val_elem.text
        try:
            return int(raw_val)
        except ValueError:
            pass
        try:
            return float(raw_val)
        except ValueError:
            pass
        return raw_val
    return None


def parse_worksheet_xml(
    sheet_data_bytes: bytes,
    shared_strings: list[str],
    options: ExcelOptions,
) -> tuple[tuple[str, ...], tuple[tuple[Any, ...], ...]]:
    root = ET.fromstring(sheet_data_bytes)
    sheet_data = root.find(f"{{{NS_SPREADSHEET}}}sheetData")
    if sheet_data is None:
        return (), ()

    parsed_rows: list[dict[int, Any]] = []
    max_col = 0

    for row_elem in sheet_data.findall(f"{{{NS_SPREADSHEET}}}row"):
        row_cells: dict[int, Any] = {}
        for c_elem in row_elem.findall(f"{{{NS_SPREADSHEET}}}c"):
            ref = c_elem.get("r", "A1")
            col_idx = col_letter_to_index(ref)
            val = parse_cell_value(c_elem, shared_strings)
            row_cells[col_idx] = val
            if col_idx > max_col:
                max_col = col_idx
        if row_cells or options.preserve_empty_rows:
            parsed_rows.append(row_cells)

    if not parsed_rows:
        return (), ()

    total_cols = max_col + 1
    raw_tuples: list[tuple[Any, ...]] = []
    for rdict in parsed_rows:
        row_tuple = tuple(rdict.get(i) for i in range(total_cols))
        raw_tuples.append(row_tuple)

    if options.header_row < len(raw_tuples):
        header_vals = raw_tuples[options.header_row]
        columns = tuple(
            str(v).strip() if v is not None else f"column_{i}"
            for i, v in enumerate(header_vals)
        )
        data_rows = raw_tuples[options.header_row + 1 :]
    else:
        columns = tuple(f"column_{i}" for i in range(total_cols))
        data_rows = raw_tuples

    return columns, tuple(data_rows)


class ExcelParserPlugin(ParserPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="excel_parser",
            version="1.0.0",
            format_identifier="excel",
            description="Official Treqna Excel (.xlsx) to UDM Parser Plugin",
            supported_media_types=(
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            ),
        )

    @property
    def format_identifier(self) -> str:
        return "excel"

    def initialize(self, context: PipelineContext) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def parse_to_udm(
        self,
        source_data: bytes | str,
        context: PipelineContext,
    ) -> UDMDocument:
        options = extract_excel_options(context)
        if isinstance(source_data, str):
            source_bytes = source_data.encode("latin1", errors="replace")
        else:
            source_bytes = source_data

        if not source_bytes:
            return UDMDocument(
                root=UDMPrimitive(value=None),
                schema_identifier="excel_empty",
            )

        try:
            with zipfile.ZipFile(io.BytesIO(source_bytes)) as zf:
                shared_strings = parse_shared_strings(zf)
                ws_prefix = "xl/worksheets/sheet"
                sheet_names = [
                    name for name in zf.namelist() if name.startswith(ws_prefix)
                ]
                if not sheet_names:
                    return UDMDocument(
                        root=UDMPrimitive(value=None),
                        schema_identifier="excel_empty",
                    )
                target_sheet = sheet_names[0]
                sheet_bytes = zf.read(target_sheet)
                cols, rows = parse_worksheet_xml(sheet_bytes, shared_strings, options)

                tabular = UDMTabular(columns=cols, rows=rows)
                return UDMDocument(root=tabular, schema_identifier="excel")
        except (zipfile.BadZipFile, ET.ParseError, ValueError, KeyError):
            return UDMDocument(
                root=UDMPrimitive(value=source_bytes.decode("utf-8", errors="replace")),
                schema_identifier="excel_raw",
            )

    def stream_parse_to_udm(
        self,
        stream: Iterable[str],
        options: ExcelOptions | None = None,
    ) -> UDMDocument:
        text = "".join(stream)
        exec_ctx = ExecutionContext(current_format="excel", target_format="udm")
        ctx = PipelineContext(session_id="excel_stream", execution_context=exec_ctx)
        return self.parse_to_udm(text, ctx)
