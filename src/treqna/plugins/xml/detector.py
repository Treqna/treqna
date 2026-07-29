import xml.etree.ElementTree as ET

from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.parser import FormatDetectorInterface


class XMLDetector(FormatDetectorInterface):
    def can_detect(self, source_data: bytes | str) -> bool:
        try:
            text = decode_source_data(source_data).strip()
            if not text:
                return False
            if text.startswith("<?xml") or text.startswith("<!DOCTYPE"):
                return True
            if text.startswith("<") and text.endswith(">"):
                ET.fromstring(text)
                return True
            return False
        except (ET.ParseError, ValueError, UnicodeDecodeError):
            return False

    def detect_format(self, source_data: bytes | str) -> str:
        if self.can_detect(source_data):
            return "xml"
        return "unknown"
