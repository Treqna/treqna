import yaml  # type: ignore[import-untyped]

from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.parser import FormatDetectorInterface


class YAMLDetector(FormatDetectorInterface):
    def can_detect(self, source_data: bytes | str) -> bool:
        try:
            text = decode_source_data(source_data).strip()
            if not text:
                return False
            if text.startswith(("<", "<?xml", "<!DOCTYPE")):
                return False
            if text.startswith("---") or text.startswith("%YAML"):
                return True
            if (text.startswith("{") or text.startswith("[")) and text.endswith(
                ("}", "]"),
            ):
                return False
            if ":" not in text and "-" not in text:
                return False
            parsed = yaml.safe_load(text)
            return isinstance(parsed, (dict, list))
        except (yaml.YAMLError, ValueError, UnicodeDecodeError):
            return False

    def detect_format(self, source_data: bytes | str) -> str:
        if self.can_detect(source_data):
            return "yaml"
        return "unknown"
