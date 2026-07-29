import csv
import io

from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.writer import FormatValidatorInterface


class CSVValidator(FormatValidatorInterface):
    def validate_output(self, output_data: bytes | str) -> bool:
        valid, _ = self.validate_csv_structure(output_data)
        return valid

    def validate_csv_structure(
        self,
        source_data: bytes | str,
    ) -> tuple[bool, tuple[str, ...]]:
        text_content = decode_source_data(source_data)
        if not text_content:
            return True, ()

        errors: list[str] = []
        stream = io.StringIO(text_content)
        reader = csv.reader(stream)

        expected_column_count: int | None = None
        line_num = 0

        try:
            for row in reader:
                line_num += 1
                if not row:
                    continue
                if expected_column_count is None:
                    expected_column_count = len(row)
                elif len(row) != expected_column_count:
                    errors.append(
                        f"Line {line_num}: expected {expected_column_count} "
                        f"columns, got {len(row)}"
                    )
        except csv.Error as err:
            errors.append(f"CSV format error at line {line_num}: {err}")

        return len(errors) == 0, tuple(errors)
