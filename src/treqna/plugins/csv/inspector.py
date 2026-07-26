import csv
import io
from collections.abc import Mapping
from typing import Any

from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.parser import FormatInspectorInterface


class CSVInspector(FormatInspectorInterface):
    def inspect_schema(self, source_data: bytes | str) -> Mapping[str, Any]:
        text_sample = decode_source_data(source_data)
        if not text_sample.strip():
            return {
                "columns": (),
                "column_count": 0,
                "has_header": False,
                "delimiter": ",",
                "sample_row_count": 0,
            }

        sample = text_sample[:4096]
        has_header = False
        delimiter = ","

        try:
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(sample, delimiters=",;\t|")
            delimiter = dialect.delimiter
            has_header = sniffer.has_header(sample)
        except csv.Error:
            pass

        stream = io.StringIO(text_sample)
        reader = csv.reader(stream, delimiter=delimiter)

        columns: tuple[str, ...] = ()
        row_count = 0

        try:
            first_row = next(reader)
            if first_row:
                row_count += 1
                if has_header:
                    columns = tuple(str(col).strip() for col in first_row)
                else:
                    columns = tuple(f"column_{i}" for i in range(len(first_row)))
            for _ in reader:
                row_count += 1
        except (csv.Error, StopIteration):
            pass

        return {
            "columns": columns,
            "column_count": len(columns),
            "has_header": has_header,
            "delimiter": delimiter,
            "sample_row_count": row_count,
        }
