# Changelog

All notable changes to Treqna will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-26

### Added
- **Core Transformation Engine**: Universal Data Model (UDM) tree representation, 8-stage pipeline (`Detect`, `Inspect`, `Parse`, `Generate UDM`, `Transform`, `Validate`, `Write`, `Finalize`), `PipelineExecutor`, `TransformationSession`, and `TransformationEngine`.
- **Format System Architecture**: First-class `FormatDescriptor`, capability enums, `FormatRegistry`, `CapabilityRegistry`, and `DescriptorRegistry`.
- **Operation System Architecture**: 15 operation categories, `OperationDescriptor`, and DAG graph primitives (`OperationNode`, `OperationEdge`, `OperationGraph`).
- **Planning System Architecture**: `Planner` facade, `TransformationPlan`, `PipelineFingerprint`, cost/quality estimators, and route selectors.
- **Public Developer API**: 13 top-level functions (`transform`, `inspect`, `detect`, `validate`, `repair`, `normalize`, `preview`, `compare`, `compress`, `extract`, `merge`, `split`), multi-source coercion, immutable `TransformationBuilder`, and 10 result dataclasses.
- **Official CSV Adapter Plugin**: Production-grade `CSVParserPlugin`, `CSVWriterPlugin`, `CSVDetector`, `CSVInspector`, `CSVValidator`, `CSVOptions`, `CSVPluginManifest`, and `register_csv_plugin`.
- **Vertical Slice & CLI**: Connected end-to-end transformation execution across public API and CLI commands (`detect`, `inspect`, `validate`, `transform`).
- **MkDocs Material Documentation**: Comprehensive documentation suite with search, light/dark mode, code copy buttons, and Mermaid architecture diagrams.

