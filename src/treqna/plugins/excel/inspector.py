import io
import xml.etree.ElementTree as ET
import zipfile
from collections.abc import Mapping
from typing import Any

from treqna.plugins.parser import FormatInspectorInterface

NS_SPREADSHEET = "http://schemas.openxmlformats.org/spreadsheetml/2006/main"


class ExcelInspector(FormatInspectorInterface):
    def inspect_schema(self, source_data: bytes | str) -> Mapping[str, Any]:
        if isinstance(source_data, str):
            source_bytes = source_data.encode("latin1", errors="replace")
        else:
            source_bytes = source_data

        if not source_bytes.startswith(b"PK\x03\x04"):
            return {
                "structure_type": "invalid",
                "sheet_names": (),
                "sheet_count": 0,
            }

        try:
            with zipfile.ZipFile(io.BytesIO(source_bytes)) as zf:
                sheet_names: list[str] = []
                if "xl/workbook.xml" in zf.namelist():
                    wb_root = ET.fromstring(zf.read("xl/workbook.xml"))
                    sheets_elem = wb_root.find(f"{{{NS_SPREADSHEET}}}sheets")
                    if sheets_elem is not None:
                        for s in sheets_elem.findall(f"{{{NS_SPREADSHEET}}}sheet"):
                            name = s.get("name")
                            if name:
                                sheet_names.append(name)

                if not sheet_names:
                    sheet_names = [
                        n for n in zf.namelist() if n.startswith("xl/worksheets/sheet")
                    ]

                return {
                    "structure_type": "workbook",
                    "sheet_names": tuple(sheet_names),
                    "sheet_count": len(sheet_names),
                    "active_sheet": sheet_names[0] if sheet_names else "",
                }
        except (zipfile.BadZipFile, ET.ParseError, Exception):
            return {
                "structure_type": "malformed",
                "sheet_names": (),
                "sheet_count": 0,
            }
