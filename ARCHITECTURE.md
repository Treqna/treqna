# Technical Architecture Document

Treqna is built around a decoupled, plugin-based architecture designed for universal data transformation.

## Architectural Principles

1. **Universal Data Model (UDM)**: Treqna NEVER performs direct format-to-format conversion. Every format converts strictly to and from the UDM data tree.
2. **First-Class Descriptors**: Formats and operations are declared using immutable descriptors (`FormatDescriptor`, `OperationDescriptor`).
3. **8-Stage Pipeline**: Transformations execute through an 8-stage pipeline (`Detect` -> `Inspect` -> `Parse` -> `Generate UDM` -> `Transform` -> `Validate` -> `Write` -> `Finalize`).
4. **Planning Engine**: Route discovery and cost estimation precede pipeline execution.
5. **Zero Inline Comments & Strict Type Hints**: Code is self-documenting with 100% static type safety.

## Core Component Diagram

```
+-----------------------------------------------------------------+
|                         Public API                              |
|   transform() | inspect() | detect() | validate() | CLI         |
+-------------------------------+---------------------------------+
                                |
                                v
+-------------------------------+---------------------------------+
|                    Transformation Engine                        |
|  +-------------------+  +-------------------+                   |
|  |  Pipeline Session |  |  Plugin Registry  |                   |
|  +---------+---------+  +---------+---------+                   |
|            |                      |                             |
|            v                      v                             |
|  8-Stage Execution Pipeline (Parse -> UDM -> Write)              |
+-------------------------------+---------------------------------+
                                |
                                v
+-------------------------------+---------------------------------+
|                    Universal Data Model                         |
|   UDMDocument / UDMTabular / UDMPrimitive / UDMCollection       |
+-----------------------------------------------------------------+
```
