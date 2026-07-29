import json

from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.writer import FormatValidatorInterface


class JSONValidator(FormatValidatorInterface):
    def validate_output(self, output_data: bytes | str) -> bool:
        valid, _ = self.validate_json_structure(output_data)
        return valid

    def validate_json_structure(
        self,
        source_data: bytes | str,
    ) -> tuple[bool, tuple[str, ...]]:
        text = decode_source_data(source_data)
        if not text.strip():
            return True, ()
        try:
            json.loads(text)
            return True, ()
        except json.JSONDecodeError as err:
            msg = f"JSON syntax error at line {err.lineno}, col {err.colno}: {err.msg}"
            return False, (msg,)
