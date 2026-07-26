# Official Treqna YAML Driver Plugin

The **YAML Driver Plugin** is the official Treqna plugin providing production-grade YAML format parsing (YAML -> UDM), writing (UDM -> YAML), single and multi-document YAML support, detection, inspection, and validation.

## Features

- **Format to UDM Parsing**: Parses single-document or multi-document YAML payloads into `UDMDocument` representations (`UDMTabular`, `UDMCollection`, `UDMPrimitive`).
- **UDM to Format Writing**: Serializes UDM tree nodes into YAML strings or byte streams.
- **Multi-Document Support**: Supports multi-document YAML streams separated by `---` markers.
- **Anchors & Aliases**: Supports YAML anchors and alias referencing.
- **Formatting Options**: Configurable `indent`, `explicit_start`, `explicit_end`, `default_flow_style`, `allow_unicode`, and `sort_keys`.
- **Auto-Detection**: Detects YAML documents, mappings, and sequences.
- **Schema Inspection**: Analyzes structure type (`object`, `array`, `primitive`), key count, item count, depth, and multi-document presence.
- **Syntax Validation**: Validates YAML syntax integrity.
- **Multi-Encoding Support**: Supports UTF-8 and UTF-16 byte encodings.

## Usage Example

```python
import treqna

yaml_data = """
- id: 101
  name: Alice
  role: Developer
- id: 102
  name: Bob
  role: Architect
"""

# Transform YAML to CSV
csv_result = treqna.transform(yaml_data).to("csv").execute()
print(csv_result.output)

# Transform CSV back to YAML
yaml_result = treqna.transform(csv_result.output).to("yaml").execute()
print(yaml_result.output)
```

## Options Configuration

Configure options using `YAMLOptions`:

```python
from treqna.plugins.yaml import YAMLOptions

options = YAMLOptions(
    indent=4,
    explicit_start=True,
    explicit_end=True,
    default_flow_style=False,
    allow_unicode=True,
)
```
