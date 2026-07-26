# Treqna

### One API. Every Format.

Treqna is a modular Python library and CLI tool engineered for universal data format transformation. By decoupling input formats from target formats using an intermediate Universal Data Model (UDM), Treqna eliminates the $O(N^2)$ explosion of format-to-format converters, reducing system complexity to $O(N)$ modular parsers and writers.

---

## Key Features

- **Universal Data Model (UDM)**: Decouples input formats from target formats via an intermediate, language-agnostic data tree.
- **Unified Public API**: Predictable top-level functions (`transform`, `detect`, `inspect`, `validate`, `repair`, `normalize`, `preview`, `compare`, `compress`, `extract`, `merge`, `split`).
- **8-Stage Execution Pipeline**: Deterministic lifecycle processing (`Detect` -> `Inspect` -> `Parse` -> `Generate UDM` -> `Transform` -> `Validate` -> `Write` -> `Finalize`).
- **First-Class Format Descriptors**: Explicit capabilities, MIME types, extension aliases, and quality metrics registered per format.
- **Zero Third-Party Runtime Dependencies**: Built directly on Python standard library primitives for security and portability.
- **Streaming & Large File Support**: Memory-efficient generator streaming for large data files.
- **Command Line Interface (CLI)**: Command-line application for automated shell execution.

---

## Quick Example

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

