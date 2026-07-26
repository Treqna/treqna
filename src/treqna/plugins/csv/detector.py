import csv

from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.parser import FormatDetectorInterface


class CSVDetector(FormatDetectorInterface):
    def can_detect(self, source_data: bytes | str) -> bool:
        try:
            text_sample = decode_source_data(source_data)[:2048]
            if not text_sample or not text_sample.strip():
                return False
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(text_sample, delimiters=",;\t|")
            return dialect.delimiter in (",", ";", "\t", "|")
        except (csv.Error, UnicodeDecodeError, ValueError):
            return False

    def detect_format(self, source_data: bytes | str) -> str:
        try:
            text_sample = decode_source_data(source_data)[:2048]
            sniffer = csv.Sniffer()
            dialect = sniffer.sniff(text_sample, delimiters=",;\t|")
            if dialect.delimiter == "\t":
                return "tsv"
            return "csv"
        except (csv.Error, UnicodeDecodeError, ValueError):
            return "unknown"
