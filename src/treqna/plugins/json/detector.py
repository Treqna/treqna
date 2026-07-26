import json

from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.parser import FormatDetectorInterface


class JSONDetector(FormatDetectorInterface):
    def can_detect(self, source_data: bytes | str) -> bool:
        try:
            text = decode_source_data(source_data).strip()
            if not text:
                return False
            if not (text.startswith("{") or text.startswith("[")):
                return False
            json.loads(text)
            return True
        except (json.JSONDecodeError, ValueError, UnicodeDecodeError):
            return False

    def detect_format(self, source_data: bytes | str) -> str:
        if self.can_detect(source_data):
            return "json"
        return "unknown"

