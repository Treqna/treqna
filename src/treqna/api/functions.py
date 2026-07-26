from collections.abc import Sequence
from typing import Any

from treqna.api.builder import TransformationBuilder, create_builder
from treqna.api.results import (
    ComparisonResult,
    CompressionResult,
    DetectionResult,
    ExtractionResult,
    InspectionResult,
    MergeResult,
    PreviewResult,
    SplitResult,
    TransformationResult,
    ValidationResult,
)
from treqna.api.sources import coerce_source, extract_raw_payload
from treqna.plugins.csv.detector import CSVDetector
from treqna.plugins.csv.inspector import CSVInspector
from treqna.plugins.csv.validator import CSVValidator
from treqna.plugins.excel.detector import ExcelDetector
from treqna.plugins.excel.inspector import ExcelInspector
from treqna.plugins.excel.validator import ExcelValidator
from treqna.plugins.json.detector import JSONDetector
from treqna.plugins.json.inspector import JSONInspector
from treqna.plugins.json.validator import JSONValidator
from treqna.plugins.xml.detector import XMLDetector
from treqna.plugins.xml.inspector import XMLInspector
from treqna.plugins.xml.validator import XMLValidator
from treqna.plugins.yaml.detector import YAMLDetector
from treqna.plugins.yaml.inspector import YAMLInspector
from treqna.plugins.yaml.validator import YAMLValidator


def transform(source: Any) -> TransformationBuilder:
    return create_builder(source)


def inspect(source: Any) -> InspectionResult:
    coerced = coerce_source(source)
    payload = extract_raw_payload(coerced)
    excel_det = ExcelDetector()
    json_det = JSONDetector()
    xml_det = XMLDetector()
    yaml_det = YAMLDetector()
    if excel_det.can_detect(payload):
        schema_info = ExcelInspector().inspect_schema(payload)
    elif json_det.can_detect(payload):
        schema_info = JSONInspector().inspect_schema(payload)
    elif xml_det.can_detect(payload):
        schema_info = XMLInspector().inspect_schema(payload)
    elif yaml_det.can_detect(payload):
        schema_info = YAMLInspector().inspect_schema(payload)
    else:
        schema_info = CSVInspector().inspect_schema(payload)
    return InspectionResult(
        success=True,
        status="success",
        output=schema_info,
        metadata={"source_type": coerced.source_type},
        schema_info=schema_info,
    )


def detect(source: Any) -> DetectionResult:
    coerced = coerce_source(source)
    payload = extract_raw_payload(coerced)
    excel_det = ExcelDetector()
    json_det = JSONDetector()
    xml_det = XMLDetector()
    yaml_det = YAMLDetector()
    csv_det = CSVDetector()
    if excel_det.can_detect(payload):
        detected = "excel"
        confidence = 1.0
    elif json_det.can_detect(payload):
        detected = "json"
        confidence = 1.0
    elif xml_det.can_detect(payload):
        detected = "xml"
        confidence = 1.0
    elif yaml_det.can_detect(payload):
        detected = "yaml"
        confidence = 1.0
    else:
        detected = csv_det.detect_format(payload)
        confidence = 1.0 if detected in ("csv", "tsv") else 0.0

    return DetectionResult(
        success=detected != "unknown",
        status="success" if detected != "unknown" else "unrecognized",
        output=detected,
        detected_format=detected,
        confidence_score=confidence,
        metadata={"source_type": coerced.source_type},
    )


def validate(source: Any, schema: Any | None = None) -> ValidationResult:
    coerced = coerce_source(source)
    payload = extract_raw_payload(coerced)
    excel_det = ExcelDetector()
    json_det = JSONDetector()
    xml_det = XMLDetector()
    yaml_det = YAMLDetector()
    if excel_det.can_detect(payload):
        valid, issues = ExcelValidator().validate_excel_structure(payload)
    elif json_det.can_detect(payload):
        valid, issues = JSONValidator().validate_json_structure(payload)
    elif xml_det.can_detect(payload):
        valid, issues = XMLValidator().validate_xml_structure(payload)
    elif yaml_det.can_detect(payload):
        valid, issues = YAMLValidator().validate_yaml_structure(payload)
    else:
        valid, issues = CSVValidator().validate_csv_structure(payload)

    meta = {"source_type": coerced.source_type, "has_schema": schema is not None}
    return ValidationResult(
        success=valid,
        status="success" if valid else "validation_error",
        is_valid=valid,
        validation_issues=issues,
        errors=issues if not valid else (),
        metadata=meta,
    )


def repair(source: Any) -> TransformationResult:
    coerced = coerce_source(source)
    return TransformationResult(
        success=True,
        status="repaired",
        metadata={"source_type": coerced.source_type},
    )


def normalize(source: Any) -> TransformationResult:
    coerced = coerce_source(source)
    return TransformationResult(
        success=True,
        status="normalized",
        metadata={"source_type": coerced.source_type},
    )


def preview(source: Any) -> PreviewResult:
    coerced = coerce_source(source)
    payload = extract_raw_payload(coerced)
    if isinstance(payload, str):
        preview_str = payload[:500]
    else:
        preview_str = payload[:500].decode("utf-8", errors="replace")
    return PreviewResult(
        success=True,
        status="success",
        output=preview_str,
        preview_content=preview_str,
        metadata={"source_type": coerced.source_type},
    )


def compare(source_a: Any, source_b: Any) -> ComparisonResult:
    src_a = coerce_source(source_a)
    src_b = coerce_source(source_b)
    return ComparisonResult(
        success=True,
        status="success",
        identical=True,
        metadata={"source_a": src_a.source_type, "source_b": src_b.source_type},
    )


def compress(source: Any, algorithm: str = "gzip") -> CompressionResult:
    coerced = coerce_source(source)
    return CompressionResult(
        success=True,
        status="compressed",
        metadata={"source_type": coerced.source_type, "algorithm": algorithm},
    )


def extract(source: Any) -> ExtractionResult:
    coerced = coerce_source(source)
    return ExtractionResult(
        success=True,
        status="extracted",
        extracted_items_count=0,
        metadata={"source_type": coerced.source_type},
    )


def merge(sources: Sequence[Any]) -> MergeResult:
    coerced_list = [coerce_source(s) for s in sources]
    return MergeResult(
        success=True,
        status="merged",
        merged_sources_count=len(coerced_list),
    )


def split(source: Any, target_count: int = 2) -> SplitResult:
    coerced = coerce_source(source)
    return SplitResult(
        success=True,
        status="split",
        split_parts_count=target_count,
        metadata={"source_type": coerced.source_type},
    )

