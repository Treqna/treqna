import io
import zipfile

from treqna.plugins.parser import FormatDetectorInterface


class ExcelDetector(FormatDetectorInterface):
    def can_detect(self, source_data: bytes | str) -> bool:
        if isinstance(source_data, str):
            source_bytes = source_data.encode("latin1", errors="replace")
        else:
            source_bytes = source_data

        if not source_bytes.startswith(b"PK\x03\x04"):
            return False

        try:
            with zipfile.ZipFile(io.BytesIO(source_bytes)) as zf:
                names = zf.namelist()
                return "xl/workbook.xml" in names or "[Content_Types].xml" in names
        except (zipfile.BadZipFile, Exception):
            return False

    def detect_format(self, source_data: bytes | str) -> str:
        if self.can_detect(source_data):
            return "excel"
        return "unknown"

