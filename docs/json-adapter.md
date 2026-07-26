# Official Treqna JSON Adapter Plugin

The **JSON Adapter Plugin** is the official Treqna plugin providing production-grade JSON format parsing (JSON -> UDM), writing (UDM -> JSON), detection, inspection, and validation.

## Features

- **Format to UDM Parsing**: Parses JSON object, array, or primitive text/byte payloads into `UDMDocument` representations (`UDMTabular`, `UDMCollection`, `UDMPrimitive`).
- **UDM to Format Writing**: Serializes UDM tree nodes into JSON strings or bytes.
- **Pretty-Printing & Minification**: Configurable `indent` option (e.g. `2` for pretty, `None` for minified).
- **Auto-Detection**: Identifies JSON objects and arrays.
- **Schema Inspection**: Extracts keys, depth, item count, and structure type (`object`, `array`, `primitive`).
- **Syntax Validation**: Validates JSON syntax.
- **Multi-Encoding Support**: UTF-8 and UTF-16 byte streams.
- **Options Configuration**: Configurable formatting, key sorting, and ASCII enforcement via `JSONOptions`.
- **Streaming & Large File Support**: Memory-efficient generator streaming parsers and writers.

## Usage

```python
from treqna.plugins.json import JSONParserPlugin, JSONWriterPlugin, register_json_plugin
from treqna.plugins.registry import PluginRegistry

registry = PluginRegistry()
register_json_plugin(registry)

parser = registry.get_parser("json")
writer = registry.get_writer("json")
```

## Options Configuration

Configure options via `JSONOptions`:

```python
from treqna.plugins.json import JSONOptions

options = JSONOptions(
    indent=2,
    ensure_ascii=False,
    sort_keys=True,
)
```

