import hashlib
import json
from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import treqna
from treqna.formats.registry import FormatRegistry
from treqna.plugins.discovery import discover_and_register_plugins
from treqna.plugins.excel.options import ExcelOptions
from treqna.plugins.excel.writer import build_xlsx_bytes
from treqna.plugins.registry import PluginRegistry


@dataclass(frozen=True, kw_only=True)
class CompatibilityPairResult:
    source_format: str
    target_format: str
    success: bool
    is_valid: bool
    is_deterministic: bool
    output_hash: str
    duration_seconds: float
    errors: tuple[str, ...] = ()


@dataclass(frozen=True, kw_only=True)
class CompatibilityMatrixReport:
    timestamp: str
    total_pairs: int
    passed_pairs: int
    failed_pairs: int
    pair_results: tuple[CompatibilityPairResult, ...]


def get_default_sample_payloads() -> dict[str, Any]:
    sample_csv = "id,name,role\n101,Alice,Engineer\n102,Bob,Architect\n"
    sample_json = (
        '[{"id": 101, "name": "Alice", "role": "Engineer"}, '
        '{"id": 102, "name": "Bob", "role": "Architect"}]'
    )
    sample_yaml = (
        "- id: 101\n  name: Alice\n  role: Engineer\n"
        "- id: 102\n  name: Bob\n  role: Architect\n"
    )
    sample_xml = (
        "<root>"
        "<item><id>101</id><name>Alice</name><role>Engineer</role></item>"
        "<item><id>102</id><name>Bob</name><role>Architect</role></item>"
        "</root>"
    )
    sample_excel = build_xlsx_bytes(
        ("id", "name", "role"),
        ((101, "Alice", "Engineer"), (102, "Bob", "Architect")),
        ExcelOptions(),
    )

    return {
        "csv": sample_csv,
        "json": sample_json,
        "yaml": sample_yaml,
        "xml": sample_xml,
        "excel": sample_excel,
    }


class CompatibilityMatrixRunner:
    def __init__(
        self,
        plugin_registry: PluginRegistry | None = None,
        format_registry: FormatRegistry | None = None,
    ) -> None:
        self.plugin_registry = (
            plugin_registry if plugin_registry is not None else PluginRegistry()
        )
        self.format_registry = (
            format_registry if format_registry is not None else FormatRegistry()
        )
        if not self.plugin_registry.list_parsers():
            discover_and_register_plugins(self.plugin_registry, self.format_registry)

    def list_supported_formats(self) -> tuple[str, ...]:
        parsers = set(self.plugin_registry.list_parsers())
        writers = set(self.plugin_registry.list_writers())
        return tuple(sorted(parsers.intersection(writers)))

    def run_pair_transformation(
        self,
        source_fmt: str,
        target_fmt: str,
        payload: Any,
    ) -> CompatibilityPairResult:
        supported = self.list_supported_formats()
        if source_fmt not in supported or target_fmt not in supported:
            return CompatibilityPairResult(
                source_format=source_fmt,
                target_format=target_fmt,
                success=False,
                is_valid=False,
                is_deterministic=False,
                output_hash="",
                duration_seconds=0.0,
                errors=(
                    f"Format pair '{source_fmt}' -> '{target_fmt}' is not supported.",
                ),
            )

        builder = treqna.transform(payload).to(target_fmt).validate().optimize()
        res1 = builder.execute()

        if not res1.success or res1.output is None:
            err_msg = res1.errors if res1.errors else ("Transformation failed",)
            return CompatibilityPairResult(
                source_format=source_fmt,
                target_format=target_fmt,
                success=False,
                is_valid=False,
                is_deterministic=False,
                output_hash="",
                duration_seconds=res1.duration,
                errors=err_msg,
            )

        res2 = builder.execute()
        hash1 = hashlib.sha256(str(res1.output).encode("utf-8")).hexdigest()
        hash2 = hashlib.sha256(str(res2.output).encode("utf-8")).hexdigest()
        is_deterministic = hash1 == hash2

        val_res = treqna.validate(res1.output)
        is_valid = val_res.is_valid

        return CompatibilityPairResult(
            source_format=source_fmt,
            target_format=target_fmt,
            success=res1.success and is_valid and is_deterministic,
            is_valid=is_valid,
            is_deterministic=is_deterministic,
            output_hash=hash1,
            duration_seconds=res1.duration,
            errors=res1.errors,
        )

    def run_matrix(
        self,
        sample_payloads: dict[str, Any] | None = None,
    ) -> CompatibilityMatrixReport:
        payloads = get_default_sample_payloads()
        if sample_payloads is not None:
            payloads.update(sample_payloads)
        formats = self.list_supported_formats()

        results: list[CompatibilityPairResult] = []
        passed_count = 0
        failed_count = 0

        for src in formats:
            for tgt in formats:
                payload = payloads.get(src, "")
                res = self.run_pair_transformation(src, tgt, payload)
                results.append(res)
                if res.success:
                    passed_count += 1
                else:
                    failed_count += 1

        now_iso = datetime.now(UTC).isoformat()
        return CompatibilityMatrixReport(
            timestamp=now_iso,
            total_pairs=len(results),
            passed_pairs=passed_count,
            failed_pairs=failed_count,
            pair_results=tuple(results),
        )

    def generate_json_report(
        self,
        report: CompatibilityMatrixReport,
        output_path: str | Path,
    ) -> None:
        data = asdict(report)
        out_p = Path(output_path)
        out_p.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def generate_markdown_report(
        self,
        report: CompatibilityMatrixReport,
        output_path: str | Path,
    ) -> None:
        table_hdr = (
            "| Source Format | Target Format | Success | Valid Output | "
            "Deterministic | Duration (s) | Status |"
        )
        lines: list[str] = [
            "# Treqna Transformation Compatibility Matrix Report",
            "",
            f"**Timestamp**: `{report.timestamp}`",
            f"**Total Pairs Evaluated**: `{report.total_pairs}`",
            f"**Passed Pairs**: `{report.passed_pairs}`",
            f"**Failed Pairs**: `{report.failed_pairs}`",
            "",
            "## Matrix Results",
            "",
            table_hdr,
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]

        for pair in report.pair_results:
            status_str = "PASSED" if pair.success else "FAILED"
            lines.append(
                f"| `{pair.source_format}` | `{pair.target_format}` | "
                f"{pair.success} | {pair.is_valid} | {pair.is_deterministic} | "
                f"{pair.duration_seconds:.6f} | **{status_str}** |"
            )

        out_p = Path(output_path)
        out_p.write_text("\n".join(lines) + "\n", encoding="utf-8")
