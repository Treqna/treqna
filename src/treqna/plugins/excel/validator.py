import io
import zipfile

from treqna.plugins.writer import FormatValidatorInterface


class ExcelValidator(FormatValidatorInterface):
    def validate_output(self, output_data: bytes | str) -> bool:
        valid, _ = self.validate_excel_structure(output_data)
        return valid

    def validate_excel_structure(
        self,
        source_data: bytes | str,
    ) -> tuple[bool, tuple[str, ...]]:
        if isinstance(source_data, str):
            source_bytes = source_data.encode("latin1", errors="replace")
        else:
            source_bytes = source_data

        if not source_bytes:
            return True, ()

        if not source_bytes.startswith(b"PK\x03\x04"):
            return False, ("Invalid Excel binary header signature",)

        try:
            with zipfile.ZipFile(io.BytesIO(source_bytes)) as zf:
                names = zf.namelist()
                has_wb = "xl/workbook.xml" in names
                has_ct = "[Content_Types].xml" in names
                if not has_wb and not has_ct:
                    return False, ("Missing required OpenXML workbook entry",)
                return True, ()
        except zipfile.BadZipFile as err:
            return False, (f"Corrupted Excel ZIP package: {err}",)
