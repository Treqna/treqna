# Technical Roadmap

This document outlines the strategic engineering roadmap for Treqna.

## Milestone Status

### Sprint 0.1 - 0.8: Core Foundation & Engine Architecture (Completed)
- Foundation: Project skeleton, build system, CLI entry point, logging, config.
- Core Transformation Engine: Universal Data Model (UDM), 8-stage pipeline (`Detect` -> `Inspect` -> `Parse` -> `Generate UDM` -> `Transform` -> `Validate` -> `Write` -> `Finalize`).
- Format System: `FormatDescriptor`, capability enums, registry lookups.
- Operation System: 15 operation categories, Operation Graph DAG.
- Planning System: Intelligent planner, cost estimation, quality scoring.
- Public API: 13 top-level functions, multi-source inputs, immutable builder.

### Sprint 0.9: Official CSV Adapter Vertical Slice (Completed)
- Production CSV parser, writer, detector, inspector, validator.
- End-to-end integration across public API and CLI subcommands (`detect`, `inspect`, `validate`, `transform`).

### Sprint 1.0: Structured Text Formats (Planned)
- Official JSON and JSON Lines (JSONL) adapter plugins.

### Sprint 1.1: Configuration Formats (Planned)
- Official YAML and TOML adapter plugins.

### Sprint 1.2: Markup & Document Formats (Planned)
- Official XML and HTML adapter plugins.

### Sprint 1.3: Binary & Tabular Analytics (Planned)
- Official Apache Parquet and Arrow adapter plugins.

### Sprint 2.0: High-Performance Engine (Planned)
- C-extension acceleration, WebAssembly target, and distributed pipeline execution.

