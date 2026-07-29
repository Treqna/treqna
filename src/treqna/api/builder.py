from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from treqna.api.client import TreqnaClient
from treqna.api.results import TransformationResult
from treqna.api.sources import DataSource, coerce_source, extract_raw_payload
from treqna.core.enums import ResultStatusEnum
from treqna.plugins.csv.detector import CSVDetector
from treqna.plugins.excel.detector import ExcelDetector
from treqna.plugins.json.detector import JSONDetector
from treqna.plugins.xml.detector import XMLDetector
from treqna.plugins.yaml.detector import YAMLDetector


@dataclass(frozen=True, kw_only=True)
class TransformationBuilder:
    source: DataSource
    target_format: str = ""
    should_validate: bool = False
    should_optimize: bool = False
    options: Mapping[str, Any] = field(default_factory=dict)

    def to(self, format_name: str) -> "TransformationBuilder":
        return TransformationBuilder(
            source=self.source,
            target_format=format_name,
            should_validate=self.should_validate,
            should_optimize=self.should_optimize,
            options=self.options,
        )

    def validate(self) -> "TransformationBuilder":
        return TransformationBuilder(
            source=self.source,
            target_format=self.target_format,
            should_validate=True,
            should_optimize=self.should_optimize,
            options=self.options,
        )

    def optimize(self) -> "TransformationBuilder":
        return TransformationBuilder(
            source=self.source,
            target_format=self.target_format,
            should_validate=self.should_validate,
            should_optimize=True,
            options=self.options,
        )

    def with_options(self, options: Mapping[str, Any]) -> "TransformationBuilder":
        merged = {**self.options, **options}
        return TransformationBuilder(
            source=self.source,
            target_format=self.target_format,
            should_validate=self.should_validate,
            should_optimize=self.should_optimize,
            options=merged,
        )

    def execute(self) -> TransformationResult:
        payload = extract_raw_payload(self.source)
        json_det = JSONDetector()
        csv_det = CSVDetector()
        yaml_det = YAMLDetector()
        xml_det = XMLDetector()
        excel_det = ExcelDetector()
        if excel_det.can_detect(payload):
            source_format = "excel"
        elif json_det.can_detect(payload):
            source_format = "json"
        elif xml_det.can_detect(payload):
            source_format = "xml"
        elif yaml_det.can_detect(payload):
            source_format = "yaml"
        elif csv_det.can_detect(payload):
            source_format = "csv"
        else:
            source_format = "csv"

        target_fmt = self.target_format if self.target_format else "csv"
        client = TreqnaClient()
        engine_result = client.transform(
            source_format=source_format,
            target_format=target_fmt,
            payload=payload,
            options=self.options,
        )
        is_success = engine_result.status == ResultStatusEnum.SUCCESS
        metadata_map = {
            "source_type": self.source.source_type,
            "target_format": target_fmt,
        }
        return TransformationResult(
            success=is_success,
            status=engine_result.status.value,
            output=engine_result.result_data,
            metadata=metadata_map,
            warnings=engine_result.warnings,
            errors=engine_result.errors,
            duration=engine_result.statistics.duration_seconds,
        )


def create_builder(source: Any) -> TransformationBuilder:
    coerced = coerce_source(source)
    return TransformationBuilder(source=coerced)
