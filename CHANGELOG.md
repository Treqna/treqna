# Changelog

All notable changes to Treqna will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-07-26

### Added
- **Repository Foundation & Packaging**: Modern PEP 621 `pyproject.toml` build system targeting Python 3.13+.
- **Core Transformation Engine**: Universal Data Model (UDM) tree representation (`UDMNode`, `UDMTabular`, `UDMDocument`), 8-stage pipeline (`Detect`, `Inspect`, `Parse`, `Generate UDM`, `Transform`, `Validate`, `Write`, `Finalize`), `PipelineExecutor`, `PipelineContext`, `TransformationSession`, and `TransformationEngine`.
- **Format System Architecture**: First-class `FormatDescriptor`, capability enums, `QualityMetrics`, `FormatRegistry`, `CapabilityRegistry`, and `DescriptorRegistry`.
- **Operation System Architecture**: 15 operation categories (`READ`, `WRITE`, `INSPECT`, `VALIDATE`, `REPAIR`, `NORMALIZE`, `TRANSFORM`, `COMPRESS`, `DECOMPRESS`, `EXTRACT`, `EMBED`, `ANALYZE`, `PREVIEW`, `OPTIMIZE`, `METADATA`), `OperationDescriptor`, and DAG graph primitives (`OperationNode`, `OperationEdge`, `OperationGraph`).
- **Planning System Architecture**: `Planner` facade, `TransformationPlan`, `PipelineFingerprint`, cost/quality estimators, route selectors, capability matchers, constraint solvers, and knowledge graph history tracking.
- **Public Developer API**: 13 top-level functions (`transform`, `inspect`, `detect`, `validate`, `repair`, `normalize`, `preview`, `compare`, `compress`, `extract`, `merge`, `split`), multi-source coercion (`PathSource`, `BytesSource`, `StreamSource`, `URLSource`, `FolderSource`), immutable `TransformationBuilder`, and 10 result dataclasses.
- **Official CSV Adapter Plugin**: Production-grade `CSVParserPlugin`, `CSVWriterPlugin`, `CSVDetector`, `CSVInspector`, `CSVValidator`, `CSVOptions`, `CSVPluginManifest`, and `register_csv_plugin`.
- **Sprint 0.9 Vertical Slice & CLI**: Connected end-to-end transformation execution across public API and CLI commands (`detect`, `inspect`, `validate`, `transform`).
- **Release Management & Governance**: Configured GitHub Actions CI/CD matrix, CodeQL security scanning, Dependabot, issue templates, PR template, CODEOWNERS, governance model, security policy, roadmap, architecture, style guide, and maintainers roster.
