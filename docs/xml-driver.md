# Official Treqna XML Driver Plugin

The **XML Driver Plugin** is the official Treqna plugin providing production-grade XML format parsing (XML -> UDM), writing (UDM -> XML), element/attribute/namespace handling, detection, inspection, and validation.

## Features

- **Format to UDM Parsing**: Parses XML documents, elements, attributes, text, and CDATA into `UDMDocument` representations (`UDMTabular`, `UDMCollection`, `UDMPrimitive`).
- **UDM to Format Writing**: Serializes UDM tree nodes into XML documents with customizable `root_tag` and `row_tag`.
- **Namespaces & Attributes**: Preserves element namespaces and `@attribute` key prefixes.
- **Formatting Options**: Configurable `indent`, `pretty_print`, `xml_declaration`, `encoding`, `root_tag`, and `row_tag`.
- **Auto-Detection**: Detects XML documents starting with `<?xml`, `<!DOCTYPE`, or matching root element tags.
- **Schema Inspection**: Analyzes root tag, element count, attribute count, namespaces, CDATA presence, DOCTYPE presence, and tree depth.
- **Syntax Validation**: Validates XML syntax integrity.
- **Multi-Encoding Support**: Supports UTF-8 and UTF-16 byte encodings.

## Usage Example

```python
import treqna

xml_data = """<root>
  <item>
    <id>101</id>
    <name>Alice</name>
    <role>Engineer</role>
  </item>
  <item>
    <id>102</id>
    <name>Bob</name>
    <role>Architect</role>
  </item>
</root>"""

# Transform XML to JSON
json_result = treqna.transform(xml_data).to("json").execute()
print(json_result.output)

# Transform JSON back to XML
xml_result = treqna.transform(json_result.output).to("xml").execute()
print(xml_result.output)
```

## Options Configuration

Configure options using `XMLOptions`:

```python
from treqna.plugins.xml import XMLOptions

options = XMLOptions(
    indent=4,
    pretty_print=True,
    xml_declaration=True,
    root_tag="dataset",
    row_tag="record",
)
```

