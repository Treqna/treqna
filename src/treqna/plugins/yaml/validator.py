import yaml  # type: ignore[import-untyped]

from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.writer import FormatValidatorInterface


class YAMLValidator(FormatValidatorInterface):
    def validate_output(self, output_data: bytes | str) -> bool:
        valid, _ = self.validate_yaml_structure(output_data)
        return valid

    def validate_yaml_structure(
        self,
        source_data: bytes | str,
    ) -> tuple[bool, tuple[str, ...]]:
        text = decode_source_data(source_data)
        if not text.strip():
            return True, ()
        try:
            list(yaml.safe_load_all(text))
            return True, ()
        except yaml.YAMLError as err:
            msg = f"YAML syntax error: {err}"
            return False, (msg,)

