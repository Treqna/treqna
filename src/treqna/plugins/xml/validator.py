import xml.etree.ElementTree as ET

from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.writer import FormatValidatorInterface


class XMLValidator(FormatValidatorInterface):
    def validate_output(self, output_data: bytes | str) -> bool:
        valid, _ = self.validate_xml_structure(output_data)
        return valid

    def validate_xml_structure(
        self,
        source_data: bytes | str,
    ) -> tuple[bool, tuple[str, ...]]:
        text = decode_source_data(source_data)
        if not text.strip():
            return True, ()
        try:
            if isinstance(source_data, bytes):
                ET.fromstring(source_data)
            else:
                ET.fromstring(source_data.encode("utf-8"))
            return True, ()
        except (ET.ParseError, ValueError, Exception) as err:
            msg = f"XML syntax error: {err}"
            return False, (msg,)

