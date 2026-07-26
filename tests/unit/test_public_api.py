from pathlib import Path
import pytest

import treqna
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
from treqna.api.sources import (
    BytesSource,
    FolderSource,
    PathSource,
    StreamSource,
    URLSource,
    coerce_source,
)


def test_top_level_functions_exist() -> None:
    assert callable(treqna.transform)
    assert callable(treqna.inspect)
    assert callable(treqna.detect)
    assert callable(treqna.validate)
    assert callable(treqna.repair)
    assert callable(treqna.normalize)
    assert callable(treqna.preview)
    assert callable(treqna.compare)
    assert callable(treqna.compress)
    assert callable(treqna.extract)
    assert callable(treqna.merge)
    assert callable(treqna.split)


def test_source_coercion() -> None:
    src_bytes = coerce_source(b"data")
    assert isinstance(src_bytes, BytesSource)

    src_url = coerce_source("https://example.com/data.json")
    assert isinstance(src_url, URLSource)

    src_path = coerce_source("sample.json")
    assert isinstance(src_path, PathSource)


def test_fluent_builder_chaining() -> None:
    builder = (
        treqna.transform("sample.json")
        .to("xml")
        .validate()
        .optimize()
        .with_options({"pretty": True})
    )

    assert builder.target_format == "xml"
    assert builder.should_validate is True
    assert builder.should_optimize is True
    assert builder.options["pretty"] is True

    result = builder.execute()
    assert isinstance(result, TransformationResult)
    assert result.success is True


def test_public_operation_results() -> None:
    ins = treqna.inspect("sample.json")
    assert isinstance(ins, InspectionResult)

    det = treqna.detect("sample.json")
    assert isinstance(det, DetectionResult)

    val = treqna.validate("sample.json")
    assert isinstance(val, ValidationResult)

    rep = treqna.repair("sample.json")
    assert isinstance(rep, TransformationResult)

    norm = treqna.normalize("sample.json")
    assert isinstance(norm, TransformationResult)

    prev = treqna.preview("sample.json")
    assert isinstance(prev, PreviewResult)

    comp = treqna.compare("sample_a.json", "sample_b.json")
    assert isinstance(comp, ComparisonResult)

    cmpr = treqna.compress("sample.json")
    assert isinstance(cmpr, CompressionResult)

    ext = treqna.extract("archive.zip")
    assert isinstance(ext, ExtractionResult)

    mrg = treqna.merge(["file1.json", "file2.json"])
    assert isinstance(mrg, MergeResult)

    spl = treqna.split("file.json", target_count=3)
    assert isinstance(spl, SplitResult)

