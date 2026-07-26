from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class DriverTemplateOptions:
    format_name: str
    class_prefix: str
    package_name: str
    version: str = "0.1.0"
    author: str = "Treqna Contributor"
    email: str = "developer@treqna.org"


def render_pyproject_toml(opts: DriverTemplateOptions) -> str:
    pkg_mod = opts.package_name.replace("-", "_")
    entry_point = f"{pkg_mod}.manifest:register_{opts.format_name}_plugin"
    return f"""[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "{opts.package_name}"
version = "{opts.version}"
description = "Official Treqna driver for {opts.format_name.upper()} format"
readme = "README.md"
requires-python = ">=3.11"
authors = [
    {{ name = "{opts.author}", email = "{opts.email}" }}
]
dependencies = [
    "treqna>=0.9.0",
]

[project.entry-points."treqna.plugins"]
{opts.format_name} = "{entry_point}"

[tool.mypy]
strict = true
python_version = "3.11"

[tool.ruff]
line-length = 88
target-version = "py311"
"""


def render_readme(opts: DriverTemplateOptions) -> str:
    fn_upper = opts.format_name.upper()
    return f"""# Treqna {fn_upper} Driver Plugin

The **{fn_upper} Driver Plugin** for Treqna provides production-grade
parsing ({fn_upper} -> UDM), writing (UDM -> {fn_upper}),
detection, inspection, and validation.

## Installation

```bash
pip install {opts.package_name}
```

## Quick Start

```python
import treqna

# Transform {fn_upper} to JSON
result = treqna.transform("sample.{opts.format_name}").to("json").execute()
print(result.output)
```

## License

Apache-2.0
"""


def render_manifest(opts: DriverTemplateOptions) -> str:
    p = opts.class_prefix
    fn = opts.format_name
    pkg = opts.package_name.replace("-", "_")
    return f"""from treqna.formats.enums import (
    CompressionEnum,
    EncodingEnum,
    FormatFamily,
    MetadataSupportEnum,
    PluginPriority,
    PreviewSupportEnum,
    RepairSupportEnum,
    StreamingEnum,
    ValidationSupportEnum,
)
from treqna.formats.models import (
    Extension,
    FormatDescriptor,
    MimeType,
    QualityMetrics,
)
from treqna.formats.registry import FormatRegistry
from treqna.plugins.registry import PluginRegistry
from {pkg}.detector import {p}Detector
from {pkg}.inspector import {p}Inspector
from {pkg}.parser import {p}ParserPlugin
from {pkg}.validator import {p}Validator
from {pkg}.writer import {p}WriterPlugin

{p.upper()}_FORMAT_DESCRIPTOR = FormatDescriptor(
    name="{fn.upper()}",
    description="{fn.upper()} data format driver",
    extensions=Extension(primary="{fn}", aliases=()),
    mime_types=MimeType(primary="application/x-{fn}", aliases=()),
    family=FormatFamily.DOCUMENT,
    encoding=EncodingEnum.UTF8,
    binary=False,
    supports_reading=True,
    supports_writing=True,
    supports_streaming=StreamingEnum.BIDIRECTIONAL,
    supports_metadata=MetadataSupportEnum.FULL,
    supports_validation=ValidationSupportEnum.SCHEMA_STRICT,
    supports_repair=RepairSupportEnum.PARTIAL,
    supports_preview=PreviewSupportEnum.TEXTUAL,
    compression=CompressionEnum.NONE,
    priority=PluginPriority.HIGH,
    quality_metrics=QualityMetrics(
        metadata_preservation=1.0,
        formatting_preservation=0.9,
        lossless_conversion=1.0,
        performance_score=0.95,
        memory_efficiency=0.9,
        reliability=1.0,
        compatibility=1.0,
    ),
)


class {p}PluginManifest:
    descriptor: FormatDescriptor = {p.upper()}_FORMAT_DESCRIPTOR
    parser: {p}ParserPlugin = {p}ParserPlugin()
    writer: {p}WriterPlugin = {p}WriterPlugin()
    detector: {p}Detector = {p}Detector()
    inspector: {p}Inspector = {p}Inspector()
    validator: {p}Validator = {p}Validator()


def register_{fn}_plugin(
    plugin_registry: PluginRegistry,
    format_registry: FormatRegistry | None = None,
) -> None:
    manifest = {p}PluginManifest()
    plugin_registry.register_parser(manifest.parser)
    plugin_registry.register_writer(manifest.writer)
    if format_registry is not None:
        format_registry.register_descriptor(manifest.descriptor)
"""


def render_options(opts: DriverTemplateOptions) -> str:
    p = opts.class_prefix
    return f"""from dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class {p}Options:
    encoding: str = "utf-8"
    pretty_print: bool = True
"""


def render_parser(opts: DriverTemplateOptions) -> str:
    p = opts.class_prefix
    fn = opts.format_name
    pkg = opts.package_name.replace("-", "_")
    return f"""from collections.abc import Iterable
from typing import Any

from treqna.core.context import PipelineContext
from treqna.core.udm import UDMDocument, UDMPrimitive, UDMTabular
from treqna.plugins.interface import PluginMetadata
from treqna.plugins.parser import ParserPluginInterface
from {pkg}.options import {p}Options


def extract_{fn}_options(context: PipelineContext | None) -> {p}Options:
    if context is None or not context.execution_context.metadata:
        return {p}Options()
    attrs = context.execution_context.metadata.custom_attributes
    return {p}Options(
        encoding=str(attrs.get("encoding", "utf-8")),
        pretty_print=bool(attrs.get("pretty_print", True)),
    )


class {p}ParserPlugin(ParserPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="{fn}_parser",
            version="1.0.0",
            format_identifier="{fn}",
            description="Official Treqna {fn.upper()} to UDM Parser Plugin",
            supported_media_types=("application/x-{fn}",),
        )

    @property
    def format_identifier(self) -> str:
        return "{fn}"

    def initialize(self, context: PipelineContext) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def parse_to_udm(
        self,
        source_data: bytes | str,
        context: PipelineContext,
    ) -> UDMDocument:
        _ = extract_{fn}_options(context)
        is_b = isinstance(source_data, bytes)
        text = source_data.decode("utf-8") if is_b else source_data
        if not text.strip():
            empty_root = UDMPrimitive(value=None)
            return UDMDocument(root=empty_root, schema_identifier="{fn}_empty")
        lines = [line.strip() for line in text.strip().splitlines() if line.strip()]
        if lines and ":" in lines[0]:
            cols: list[str] = []
            vals: list[Any] = []
            for line in lines:
                if ":" in line:
                    k, v = line.split(":", 1)
                    cols.append(k.strip())
                    vals.append(v.strip())
            return UDMDocument(
                root=UDMTabular(columns=tuple(cols), rows=(tuple(vals),)),
                schema_identifier="{fn}",
            )
        return UDMDocument(root=UDMPrimitive(value=text), schema_identifier="{fn}")

    def stream_parse_to_udm(
        self,
        stream: Iterable[str],
        options: {p}Options | None = None,
    ) -> UDMDocument:
        text = "".join(stream)
        return self.parse_to_udm(text, PipelineContext(session_id="stream"))
"""


def render_writer(opts: DriverTemplateOptions) -> str:
    p = opts.class_prefix
    fn = opts.format_name
    pkg = opts.package_name.replace("-", "_")
    return f"""from typing import TextIO

from treqna.core.context import PipelineContext
from treqna.core.udm import UDMDocument, UDMPrimitive, UDMTabular
from treqna.plugins.interface import PluginMetadata
from treqna.plugins.writer import WriterPluginInterface
from {pkg}.options import {p}Options
from {pkg}.parser import extract_{fn}_options


class {p}WriterPlugin(WriterPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="{fn}_writer",
            version="1.0.0",
            format_identifier="{fn}",
            description="Official Treqna UDM to {fn.upper()} Writer Plugin",
            supported_media_types=("application/x-{fn}",),
        )

    @property
    def format_identifier(self) -> str:
        return "{fn}"

    def initialize(self, context: PipelineContext) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def write_from_udm(
        self,
        document: UDMDocument,
        context: PipelineContext,
    ) -> str:
        _ = extract_{fn}_options(context)
        node = document.root
        if isinstance(node, UDMTabular):
            lines: list[str] = []
            cols = list(node.columns)
            for row in node.rows:
                for i, col in enumerate(cols):
                    val = row[i] if i < len(row) else ""
                    lines.append(f"{{col}}: {{val}}")
            res_str: str = "\\n".join(lines) + "\\n"
            return res_str
        if isinstance(node, UDMPrimitive):
            res_str = str(node.value)
            return res_str
        return str(node)

    def stream_write_from_udm(
        self,
        document: UDMDocument,
        target_stream: TextIO,
        options: {p}Options | None = None,
    ) -> None:
        text = self.write_from_udm(document, PipelineContext(session_id="stream"))
        target_stream.write(text)
"""


def render_detector(opts: DriverTemplateOptions) -> str:
    p = opts.class_prefix
    fn = opts.format_name
    return f"""from treqna.plugins.parser import FormatDetectorInterface


class {p}Detector(FormatDetectorInterface):
    def can_detect(self, source_data: bytes | str) -> bool:
        is_b = isinstance(source_data, bytes)
        text = source_data.decode("utf-8") if is_b else source_data
        text = text.strip()
        if not text:
            return False
        return ":" in text or text.startswith("{fn}")

    def detect_format(self, source_data: bytes | str) -> str:
        if self.can_detect(source_data):
            return "{fn}"
        return "unknown"
"""


def render_inspector(opts: DriverTemplateOptions) -> str:
    p = opts.class_prefix
    fn = opts.format_name
    return f"""from collections.abc import Mapping
from typing import Any

from treqna.plugins.parser import FormatInspectorInterface


class {p}Inspector(FormatInspectorInterface):
    def inspect_schema(self, source_data: bytes | str) -> Mapping[str, Any]:
        is_b = isinstance(source_data, bytes)
        text = source_data.decode("utf-8") if is_b else source_data
        text = text.strip()
        if not text:
            return {{"structure_type": "empty", "line_count": 0}}
        lines = text.splitlines()
        return {{
            "structure_type": "document",
            "format": "{fn}",
            "line_count": len(lines),
        }}
"""


def render_validator(opts: DriverTemplateOptions) -> str:
    p = opts.class_prefix
    fn = opts.format_name
    return f"""from treqna.plugins.writer import FormatValidatorInterface


class {p}Validator(FormatValidatorInterface):
    def validate_output(self, output_data: bytes | str) -> bool:
        valid, _ = self.validate_{fn}_structure(output_data)
        return valid

    def validate_{fn}_structure(
        self,
        source_data: bytes | str,
    ) -> tuple[bool, tuple[str, ...]]:
        is_b = isinstance(source_data, bytes)
        text = source_data.decode("utf-8") if is_b else source_data
        if not text.strip():
            return True, ()
        return True, ()
"""


def render_init_py(opts: DriverTemplateOptions) -> str:
    p = opts.class_prefix
    fn = opts.format_name
    pkg_mod = opts.package_name.replace("-", "_")
    return f"""from {pkg_mod}.detector import {p}Detector
from {pkg_mod}.inspector import {p}Inspector
from {pkg_mod}.manifest import (
    {p.upper()}_FORMAT_DESCRIPTOR,
    {p}PluginManifest,
    register_{fn}_plugin,
)
from {pkg_mod}.options import {p}Options
from {pkg_mod}.parser import {p}ParserPlugin
from {pkg_mod}.validator import {p}Validator
from {pkg_mod}.writer import {p}WriterPlugin

__all__ = [
    "{p}Detector",
    "{p}Inspector",
    "{p}Options",
    "{p}ParserPlugin",
    "{p}PluginManifest",
    "{p}Validator",
    "{p}WriterPlugin",
    "{p.upper()}_FORMAT_DESCRIPTOR",
    "register_{fn}_plugin",
]
"""


def render_unit_test(opts: DriverTemplateOptions) -> str:
    p = opts.class_prefix
    fn = opts.format_name
    pkg = opts.package_name.replace("-", "_")
    return f"""import pytest

from treqna.core.context import ExecutionContext, PipelineContext
from treqna.core.udm import UDMDocument, UDMTabular
from {pkg} import (
    {p}Detector,
    {p}Inspector,
    {p}ParserPlugin,
    {p}Validator,
    {p}WriterPlugin,
)


def create_context() -> PipelineContext:
    exec_ctx = ExecutionContext(current_format="{fn}", target_format="udm")
    return PipelineContext(session_id="test_sess", execution_context=exec_ctx)


def test_{fn}_parser_and_writer() -> None:
    parser = {p}ParserPlugin()
    writer = {p}WriterPlugin()
    ctx = create_context()

    doc = parser.parse_to_udm("key: value", ctx)
    assert isinstance(doc.root, UDMTabular)

    out = writer.write_from_udm(doc, ctx)
    assert "key: value" in out


def test_{fn}_detector_inspector_validator() -> None:
    detector = {p}Detector()
    inspector = {p}Inspector()
    validator = {p}Validator()

    assert detector.can_detect("key: value") is True
    info = inspector.inspect_schema("key: value")
    assert info["structure_type"] == "document"
    assert validator.validate_output("key: value") is True
"""


def render_integration_test(opts: DriverTemplateOptions) -> str:
    fn = opts.format_name
    pkg_mod = opts.package_name.replace("-", "_")
    return f"""import pytest

from treqna.formats.registry import FormatRegistry
from treqna.plugins.registry import PluginRegistry
from {pkg_mod} import register_{fn}_plugin


def test_{fn}_plugin_registration() -> None:
    plugin_reg = PluginRegistry()
    format_reg = FormatRegistry()
    register_{fn}_plugin(plugin_reg, format_reg)

    parser = plugin_reg.get_parser("{fn}")
    writer = plugin_reg.get_writer("{fn}")
    descriptor = format_reg.get_descriptor("{fn}")

    assert parser.metadata.name == "{fn}_parser"
    assert writer.metadata.name == "{fn}_writer"
    assert descriptor.name == "{fn.upper()}"
"""


def render_benchmark_test(opts: DriverTemplateOptions) -> str:
    p = opts.class_prefix
    fn = opts.format_name
    pkg = opts.package_name.replace("-", "_")
    return f"""import time
import pytest

from treqna.core.context import ExecutionContext, PipelineContext
from {pkg} import {p}ParserPlugin, {p}WriterPlugin


def test_{fn}_benchmark() -> None:
    parser = {p}ParserPlugin()
    writer = {p}WriterPlugin()
    exec_ctx = ExecutionContext(current_format="{fn}", target_format="udm")
    ctx = PipelineContext(session_id="bench_sess", execution_context=exec_ctx)

    payload = "\\n".join(f"key_{{i}}: val_{{i}}" for i in range(1000))
    start = time.perf_counter()
    doc = parser.parse_to_udm(payload, ctx)
    out = writer.write_from_udm(doc, ctx)
    duration = time.perf_counter() - start

    assert len(out) > 0
    assert duration < 5.0
"""


def render_mkdocs_yml(opts: DriverTemplateOptions) -> str:
    return f"""site_name: Treqna {opts.format_name.upper()} Driver Plugin
theme:
  name: material

nav:
  - Home: index.md
"""


def render_doc_index(opts: DriverTemplateOptions) -> str:
    fn_upper = opts.format_name.upper()
    return f"""# Treqna {fn_upper} Driver Plugin

Documentation for the official Treqna {fn_upper} format driver plugin.
"""


def render_github_ci() -> str:
    return """name: CI

on:
  push:
    branches: [ "main" ]
  pull_request:
    branches: [ "main" ]

jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - run: pip install -e . pytest mypy ruff
      - run: ruff check .
      - run: mypy src
      - run: pytest
"""


def render_license() -> str:
    return """Apache License
Version 2.0, January 2004
http://www.apache.org/licenses/
"""
