# Treqna

### One API. Every Format.

[![PyPI version](https://img.shields.io/pypi/v/treqna.svg)](https://pypi.org/project/treqna/)
[![Build Status](https://github.com/treqna/treqna/workflows/CI/badge.svg)](https://github.com/treqna/treqna/actions)
[![Coverage Status](https://img.shields.io/codecov/c/github/treqna/treqna)](https://codecov.io/gh/treqna/treqna)
[![Python Version](https://img.shields.io/pypi/pyversions/treqna.svg)](https://pypi.org/project/treqna/)
[![License](https://img.shields.io/github/license/treqna/treqna.svg)](LICENSE)

---

## Short Description

Treqna is a modular Python library and CLI tool engineered for universal data format transformation. By decoupling input formats from target formats using an intermediate Universal Data Model (UDM), Treqna eliminates the $O(N^2)$ explosion of format-to-format converters, reducing system complexity to $O(N)$ modular parsers and writers.

---

## Installation

Install Treqna via pip:

```bash
pip install treqna
```

Or using uv:

```bash
uv add treqna
```

---

## Quick Start

```python
import treqna

result = (
    treqna.transform("input.csv")
    .to("csv")
    .validate()
    .optimize()
    .execute()
)

print(result.output)
```

---

## 5-Minute Example

```python
import treqna

payload = """id,name,role
101,Alice,Engineer
102,Bob,Architect
"""

detection = treqna.detect(payload)
print(f"Format: {detection.detected_format} (Confidence: {detection.confidence_score})")

inspection = treqna.inspect(payload)
print(f"Columns: {inspection.schema_info['columns']}")
print(f"Column Count: {inspection.schema_info['column_count']}")

validation = treqna.validate(payload)
print(f"Valid Payload: {validation.is_valid}")

result = (
    treqna.transform(payload)
    .to("csv")
    .with_options({"delimiter": ","})
    .execute()
)

if result.success:
    print("Transformation Output:")
    print(result.output)
```

---

## Features

- **Universal Data Model (UDM)**: Decouples input formats from target formats via an intermediate, language-agnostic data tree.
- **Unified Public API**: Provides simple, predictable top-level functions (`transform`, `detect`, `inspect`, `validate`, `repair`, `normalize`, `preview`, `compare`, `compress`, `extract`, `merge`, `split`).
- **8-Stage Execution Pipeline**: Deterministic lifecycle processing (`Detect` -> `Inspect` -> `Parse` -> `Generate UDM` -> `Transform` -> `Validate` -> `Write` -> `Finalize`).
- **First-Class Format Descriptors**: Explicit capabilities, MIME types, extension aliases, and quality metrics registered per format.
- **Zero Third-Party Runtime Dependencies**: Built directly on Python standard library primitives for security and portability.
- **Streaming & Large File Support**: Memory-efficient generator streaming for large data files.
- **Command Line Interface (CLI)**: Command-line application for automated shell execution.

---

## Architecture Diagram

```
+------------------+
|   Input Format   |  (CSV, TSV, etc.)
+--------+---------+
         |
         v
+------------------+
|   Parser Plugin  |  Format -> UDM
+--------+---------+
         |
         v
+------------------+
| Universal Data   |  UDM Data Tree
|   Model (UDM)    |
+--------+---------+
         |
         v
+------------------+
| Transformation   |  Pipeline & Operations
|     Pipeline     |
+--------+---------+
         |
         v
+------------------+
|   Writer Plugin  |  UDM -> Format
+--------+---------+
         |
         v
+------------------+
|  Output Format   |
+------------------+
```

---

## How Treqna Works

Treqna processes transformations through an 8-stage pipeline managed within an execution session:

1. **Detect Stage**: Identifies the format family, character encoding, and dialect.
2. **Inspect Stage**: Extracts structural metadata, column definitions, and schema statistics.
3. **Parse Stage**: Translates the raw payload into the Universal Data Model (UDM) via the format parser plugin.
4. **Generate UDM Stage**: Constructs an immutable hierarchical UDM tree node.
5. **Transform Stage**: Applies UDM-level transformations, field normalizations, or custom mappings.
6. **Validate Stage**: Checks target format constraints and structural validity.
7. **Write Stage**: Serializes the UDM tree into the output format text or byte representation.
8. **Finalize Stage**: Compiles execution statistics, warnings, errors, and output into an immutable result object.

---

## Plugin System

Treqna features a plugin architecture where formats and operations register explicit descriptors:

```python
from treqna.plugins import PluginRegistry, ParserPluginInterface, WriterPluginInterface
from treqna.formats import FormatDescriptor, FormatFamily

class CustomParser(ParserPluginInterface):
    @property
    def format_identifier(self) -> str:
        return "custom_fmt"
    # Implement parse_to_udm(source_data, context) -> UDMDocument

registry = PluginRegistry()
registry.register_parser(CustomParser())
```

Every plugin implements ONLY:
- `Format -> UDM` (Parser)
- `UDM -> Format` (Writer)

Plugins NEVER perform direct `Format -> Format` conversions.

---

## Why Universal Transformation Model

In traditional data transformation systems supporting $N$ file formats, implementing direct format converters requires $N \times (N - 1)$ distinct conversion modules. Adding a single new format requires writing $2(N - 1)$ new converters.

Treqna eliminates this complexity. By translating every format into a Universal Data Model (UDM):
- Adding format $N+1$ requires only **1 Parser** (`Format -> UDM`) and **1 Writer** (`UDM -> Format`).
- System complexity remains strictly $O(N)$.
- Transformation operations operate on the UDM layer, ensuring universal reusability across all present and future formats.

---

## Roadmap

- **Sprint 0.1 - 0.8**: Core Engine, Format Descriptors, Operation DAG, Planning Engine, and Public API Architecture. (Completed)
- **Sprint 0.9**: Official CSV Adapter Vertical Slice & CLI Integration. (Completed)
- **Sprint 1.0**: JSON & JSON Lines (JSONL) Adapter plugins.
- **Sprint 1.1**: YAML & TOML Adapter plugins.
- **Sprint 1.2**: XML & HTML Adapter plugins.
- **Sprint 1.3**: Parquet & Arrow Tabular Adapter plugins.
- **Sprint 2.0**: Distributed execution engine & WebAssembly target support.

---

## Examples

### Processing Custom Delimiters and Encodings

```python
import treqna

result = (
    treqna.transform("data.tsv")
    .to("csv")
    .with_options({
        "delimiter": "\t",
        "encoding": "utf-16",
        "has_header": True,
    })
    .execute()
)

print(f"Success: {result.success}")
print(f"Duration: {result.duration:.4f}s")
```

---

## CLI

Treqna provides a command-line interface:

```bash
# Detect format of input file
treqna detect data.csv

# Inspect schema details
treqna inspect data.csv

# Validate format syntax
treqna validate data.csv

# Transform format
treqna transform data.csv --to csv --out output.csv

# Display CLI version
treqna --version
```

---

## Performance

Treqna is engineered for low latency and minimal memory overhead:

- **Parsing Throughput**: 10,000 tabular rows parsed to UDM in under 0.15 seconds.
- **Serialization Speed**: 10,000 UDM rows written to CSV in under 0.15 seconds.
- **Memory Footprint**: Streaming generator support guarantees $O(1)$ memory overhead for large file streams.

---

## Contributing

Contributions are welcome. Please consult [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines on code style, testing, and pull request procedures.

```bash
git clone https://github.com/treqna/treqna.git
cd treqna
pip install -e .
python -m pytest
```

---

## License

Treqna is released under the MIT License. See [LICENSE](LICENSE) for full details.
