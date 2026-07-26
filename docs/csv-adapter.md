# Official CSV Adapter Plugin

The **CSV Adapter Plugin** is the official Treqna plugin providing production-grade CSV format parsing (CSV -> UDM), writing (UDM -> CSV), detection, inspection, and validation.

## Features

- **Format to UDM Parsing**: Parses CSV string or byte payloads into `UDMTabular` representations.
- **UDM to Format Writing**: Serializes `UDMTabular` data tree nodes into valid CSV format strings.
- **Auto-Detection**: Uses Python's `csv.Sniffer` to identify CSV and TSV dialects.
- **Schema Inspection**: Extracts column names, row counts, header presence, and delimiter metadata.
- **Syntax Validation**: Validates row column consistency and quotes balancing.
- **Multi-Encoding Support**: UTF-8 and UTF-16 byte streams.
- **Customization Options**: Configurable delimiters (comma, tab, semicolon, pipe), quote characters, escape characters, quoting rules, and headers via `CSVOptions`.
- **Streaming & Large File Support**: Memory-efficient generator streaming parsers and writers.

## Usage

```python
from treqna.plugins.csv import CSVParserPlugin, CSVWriterPlugin, register_csv_plugin
from treqna.plugins.registry import PluginRegistry

registry = PluginRegistry()
register_csv_plugin(registry)

parser = registry.get_parser("csv")
writer = registry.get_writer("csv")
```

## Options Configuration

Configure options via `CSVOptions`:

```python
from treqna.plugins.csv import CSVOptions

options = CSVOptions(
    delimiter="\t",
    quotechar='"',
    encoding="utf-8",
    has_header=True,
)
```

