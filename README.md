# Treqna

> **One API. Every Format.**

Universal data transformation framework for Python.

Transform structured data between **CSV**, **JSON**, **YAML**, **XML**, and **Excel** using one consistent API.

---

## Why Treqna?

Most data conversion libraries require writing converters for every pair of formats.

Treqna uses a **Universal Data Model (UDM)** so every format only needs:

- Parser → Format → UDM
- Writer → UDM → Format

This keeps the architecture modular, scalable, and easy to extend.

---

## Features

- Unified API for data transformation
- Built-in support for CSV, JSON, YAML, XML, and Excel (.xlsx)
- Plugin architecture for custom formats
- Streaming support for large datasets
- Format detection and validation
- Command-line interface
- Strong type hints
- Cross-platform support
- Zero runtime dependencies
- Open source

---

## Installation

```bash
pip install treqna
```

---

## Quick Start

Convert CSV to JSON.

```python
import treqna

result = (
    treqna
        .transform("users.csv")
        .to("json")
        .execute()
)

print(result.output)
```

Convert JSON to YAML.

```python
result = (
    treqna
        .transform("config.json")
        .to("yaml")
        .execute()
)
```

Convert Excel to CSV.

```python
result = (
    treqna
        .transform("employees.xlsx")
        .to("csv")
        .execute()
)
```

---

## Command Line

```bash
treqna detect users.csv

treqna inspect users.csv

treqna validate users.csv

treqna transform users.csv --to json --out users.json
```

---

## Supported Formats

| Format | Read | Write |
|---------|:----:|:-----:|
| CSV | ✅ | ✅ |
| JSON | ✅ | ✅ |
| YAML | ✅ | ✅ |
| XML | ✅ | ✅ |
| Excel (.xlsx) | ✅ | ✅ |

More formats are planned through the plugin system.

---

## Architecture

```
            Input Format
                 │
                 ▼
          Parser Plugin
                 │
                 ▼
      Universal Data Model
                 │
                 ▼
        Transformation Engine
                 │
                 ▼
          Writer Plugin
                 │
                 ▼
          Output Format
```

Every transformation passes through the Universal Data Model rather than using direct format-to-format converters.

---

## Documentation

Full documentation is available in the **docs/** directory.

Topics include:

- Installation
- Public API
- CLI
- Plugin Development
- Architecture
- Performance
- Examples

---

## Examples

```python
treqna.detect(data)

treqna.inspect(data)

treqna.validate(data)

treqna.transform(data).to("xml").execute()
```

More examples are available in the **examples/** directory.

---

## Plugin System

Treqna is designed around plugins.

Official plugins currently include:

- CSV
- JSON
- YAML
- XML
- Excel

The Driver SDK makes it easy to build new plugins for additional formats.

---

## Performance

Designed for:

- Streaming large files
- Low memory usage
- Predictable execution
- Modular architecture

---

## Contributing

Contributions are welcome.

Please read:

- CONTRIBUTING.md
- CODE_OF_CONDUCT.md
- SECURITY.md

before submitting issues or pull requests.

---

## Roadmap

Upcoming goals include:

- Community plugins
- Driver certification
- Additional data formats
- Performance improvements

See **ROADMAP.md** for details.

---

## License

Treqna is released under the MIT License. See [LICENSE](LICENSE) for full details.
