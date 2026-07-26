# Official Treqna Driver SDK

The **Treqna Driver SDK** enables developers to create production-ready format driver plugins for Treqna with a single command.

## Overview

Format drivers in Treqna bridge external data formats (e.g. `Protobuf`, `Parquet`, `TOML`, `MsgPack`) to and from the **Universal Data Model (UDM)**. The SDK generates a standalone, fully typed, linted, tested, and documented driver package ready for publication.

## Generating a New Driver

Use the `treqna create-driver` command:

```bash
treqna create-driver protobuf
```

This creates a new project directory: `treqna-protobuf/`.

### Custom Output Directory

```bash
treqna create-driver myformat --output-dir ./custom-driver
```

## Generated Project Structure

```
treqna-myformat/
├── .github/
│   └── workflows/
│       └── ci.yml
├── benchmarks/
│   └── test_myformat_benchmark.py
├── docs/
│   ├── index.md
│   └── mkdocs.yml
├── src/
│   └── treqna_myformat/
│       ├── __init__.py
│       ├── detector.py
│       ├── inspector.py
│       ├── manifest.py
│       ├── options.py
│       ├── parser.py
│       ├── validator.py
│       └── writer.py
├── tests/
│   ├── test_myformat_driver.py
│   └── test_myformat_integration.py
├── LICENSE
├── pyproject.toml
└── README.md
```

## Programmatic Usage

You can also generate driver projects programmatically using Python:

```python
from pathlib import Path
from treqna.sdk import DriverGenerator

generator = DriverGenerator()
project_dir = generator.generate_driver_project("toml", output_dir=Path("./treqna-toml"))
print(f"Generated at: {project_dir}")
```

