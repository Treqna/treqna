from treqna.core.contracts import TransformationRequest
from treqna.core.engine import TransformationEngine
from treqna.core.enums import PipelineStageEnum, ResultStatusEnum, StageEnum
from treqna.core.pipeline import PipelineBuilder
from treqna.core.udm import UDMDocument, UDMObject, UDMPrimitive, UDMText


def test_udm_structure() -> None:
    primitive = UDMPrimitive(value=42, data_type="integer")
    text_node = UDMText(content="sample text")
    obj_node = UDMObject(properties={"age": primitive, "name": text_node})
    doc = UDMDocument(root=obj_node, schema_identifier="test_schema")

    assert doc.schema_identifier == "test_schema"
    assert isinstance(doc.root, UDMObject)
    assert doc.root.properties["age"].value == 42


def test_pipeline_builder() -> None:
    builder = PipelineBuilder()
    pipeline = builder.with_default_stages().build()

    assert len(pipeline) == 8
    stage_enums = [s.stage for s in pipeline]
    expected_enums = [
        PipelineStageEnum.DETECT,
        PipelineStageEnum.INSPECT,
        PipelineStageEnum.PARSE,
        PipelineStageEnum.GENERATE_UDM,
        PipelineStageEnum.TRANSFORM,
        PipelineStageEnum.VALIDATE,
        PipelineStageEnum.WRITE,
        PipelineStageEnum.FINALIZE,
    ]
    assert stage_enums == expected_enums


def test_stage_enum_aliases() -> None:
    assert StageEnum.DETECT.value == PipelineStageEnum.DETECT.value
    assert StageEnum.FINALIZE.value == PipelineStageEnum.FINALIZE.value


def test_transformation_engine_execution() -> None:
    engine = TransformationEngine()
    request = TransformationRequest(
        source_format="json",
        target_format="xml",
        payload="<data>payload</data>",
    )

    result = engine.transform(request)

    assert result.status == ResultStatusEnum.SUCCESS
    assert result.output_format == "xml"
    assert len(result.stage_results) == 8
    assert result.statistics.duration_seconds >= 0.0
