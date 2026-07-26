import io
import xml.etree.ElementTree as ET
import zipfile
from typing import Any, TextIO

from treqna.core.context import ExecutionContext, PipelineContext
from treqna.core.udm import UDMDocument, UDMTabular
from treqna.plugins.excel.options import ExcelOptions
from treqna.plugins.excel.parser import extract_excel_options
from treqna.plugins.interface import PluginMetadata
from treqna.plugins.json.writer import udm_node_to_json_obj
from treqna.plugins.writer import WriterPluginInterface

NS_SPREADSHEET = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


def index_to_col_letter(col_idx: int) -> str:
    result: list[str] = []
    col = col_idx + 1
    while col > 0:
        col, remainder = divmod(col - 1, 26)
        result.append(chr(65 + remainder))
    return "".join(reversed(result))


def build_xlsx_bytes(
    columns: tuple[str, ...],
    rows: tuple[tuple[Any, ...], ...],
    options: ExcelOptions,
) -> bytes:
    shared_strings: list[str] = []
    string_map: dict[str, int] = {}

    def get_string_index(s: str) -> int:
        if s in string_map:
            return string_map[s]
        idx = len(shared_strings)
        shared_strings.append(s)
        string_map[s] = idx
        return idx

    sheet_root = ET.Element("worksheet", xmlns=NS_SPREADSHEET)
    sheet_data = ET.SubElement(sheet_root, "sheetData")

    current_row = 1
    if columns:
        r_elem = ET.SubElement(sheet_data, "row", r=str(current_row))
        for col_idx, col_name in enumerate(columns):
            cell_ref = f"{index_to_col_letter(col_idx)}{current_row}"
            s_idx = get_string_index(str(col_name))
            c_elem = ET.SubElement(r_elem, "c", r=cell_ref, t="s")
            v_elem = ET.SubElement(c_elem, "v")
            v_elem.text = str(s_idx)
        current_row += 1

    for row_tuple in rows:
        r_elem = ET.SubElement(sheet_data, "row", r=str(current_row))
        for col_idx, val in enumerate(row_tuple):
            if val is None:
                continue
            cell_ref = f"{index_to_col_letter(col_idx)}{current_row}"
            if isinstance(val, bool):
                c_elem = ET.SubElement(r_elem, "c", r=cell_ref, t="b")
                v_elem = ET.SubElement(c_elem, "v")
                v_elem.text = "1" if val else "0"
            elif isinstance(val, (int, float)):
                c_elem = ET.SubElement(r_elem, "c", r=cell_ref)
                v_elem = ET.SubElement(c_elem, "v")
                v_elem.text = str(val)
            else:
                s_idx = get_string_index(str(val))
                c_elem = ET.SubElement(r_elem, "c", r=cell_ref, t="s")
                v_elem = ET.SubElement(c_elem, "v")
                v_elem.text = str(s_idx)
        current_row += 1

    sheet_xml_bytes = ET.tostring(sheet_root, encoding="utf-8", xml_declaration=True)

    ss_root = ET.Element(
        "sst",
        xmlns=NS_SPREADSHEET,
        count=str(len(shared_strings)),
        uniqueCount=str(len(shared_strings)),
    )
    for s in shared_strings:
        si_elem = ET.SubElement(ss_root, "si")
        t_elem = ET.SubElement(si_elem, "t")
        t_elem.text = s
    ss_xml_bytes = ET.tostring(ss_root, encoding="utf-8", xml_declaration=True)

    ct_pkg = "application/vnd.openxmlformats-package.relationships+xml"
    ct_sheet = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"
    )
    ct_ws = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"
    )
    ct_ss = (
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"
    )

    content_types_str = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        f'  <Default Extension="rels" ContentType="{ct_pkg}"/>\n'
        '  <Default Extension="xml" ContentType="application/xml"/>\n'
        f'  <Override PartName="/xl/workbook.xml" ContentType="{ct_sheet}"/>\n'
        f'  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="{ct_ws}"/>\n'
        f'  <Override PartName="/xl/sharedStrings.xml" ContentType="{ct_ss}"/>\n'
        '</Types>'
    )

    rel_ns = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
    doc_rel = f"{rel_ns}/officeDocument"
    rels_str = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        f'  <Relationship Id="rId1" Type="{doc_rel}" Target="xl/workbook.xml"/>\n'
        '</Relationships>'
    )

    ws_rel = f"{rel_ns}/worksheet"
    ss_rel = f"{rel_ns}/sharedStrings"
    workbook_rels_str = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        f'  <Relationship Id="rId1" Type="{ws_rel}" Target="worksheets/sheet1.xml"/>\n'
        f'  <Relationship Id="rId2" Type="{ss_rel}" Target="sharedStrings.xml"/>\n'
        '</Relationships>'
    )

    sheet_name = options.worksheet_name or "Sheet1"
    workbook_str = (
        '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
        f'<workbook xmlns="{NS_SPREADSHEET}" xmlns:r="{rel_ns}">\n'
        '  <sheets>\n'
        f'    <sheet name="{sheet_name}" sheetId="1" r:id="rId1"/>\n'
        '  </sheets>\n'
        '</workbook>'
    )

    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_str.encode("utf-8"))
        zf.writestr("_rels/.rels", rels_str.encode("utf-8"))
        zf.writestr("xl/_rels/workbook.xml.rels", workbook_rels_str.encode("utf-8"))
        zf.writestr("xl/workbook.xml", workbook_str.encode("utf-8"))
        zf.writestr("xl/worksheets/sheet1.xml", sheet_xml_bytes)
        zf.writestr("xl/sharedStrings.xml", ss_xml_bytes)

    return buf.getvalue()


class ExcelWriterPlugin(WriterPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="excel_writer",
            version="1.0.0",
            format_identifier="excel",
            description="Official Treqna UDM to Excel (.xlsx) Writer Plugin",
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

    def write_from_udm(
        self,
        document: UDMDocument,
        context: PipelineContext,
    ) -> bytes:
        options = extract_excel_options(context)
        node = document.root

        if isinstance(node, UDMTabular):
            return build_xlsx_bytes(node.columns, node.rows, options)

        json_obj = udm_node_to_json_obj(node)
        if isinstance(json_obj, list) and json_obj and isinstance(json_obj[0], dict):
            cols_list: list[str] = []
            for item in json_obj:
                for k in item:
                    if k not in cols_list:
                        cols_list.append(k)
            rows_list: list[tuple[Any, ...]] = []
            for item in json_obj:
                rows_list.append(tuple(item.get(c) for c in cols_list))
            return build_xlsx_bytes(tuple(cols_list), tuple(rows_list), options)

        if isinstance(json_obj, dict):
            cols_tuple: tuple[str, ...] = tuple(str(k) for k in json_obj)
            rows_tuple: tuple[tuple[Any, ...], ...] = (tuple(json_obj.values()),)
            return build_xlsx_bytes(cols_tuple, rows_tuple, options)

        cols_tuple = ("value",)
        rows_tuple = ((str(json_obj),),)
        return build_xlsx_bytes(cols_tuple, rows_tuple, options)

    def stream_write_from_udm(
        self,
        document: UDMDocument,
        target_stream: TextIO,
        options: ExcelOptions | None = None,
    ) -> None:
        exec_ctx = ExecutionContext(current_format="excel", target_format="udm")
        ctx = PipelineContext(session_id="stream", execution_context=exec_ctx)
        xlsx_bytes = self.write_from_udm(document, ctx)
        target_stream.write(xlsx_bytes.decode("latin1"))
