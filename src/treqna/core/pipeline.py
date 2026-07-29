import time
from abc import ABC, abstractmethod
from collections.abc import Sequence
from typing import Any

from treqna.core.context import (
    ExecutionStatistics,
    PipelineContext,
    PipelineStageEvent,
)
from treqna.core.contracts import (
    StageResult,
    TransformationRequest,
    TransformationResult,
)
from treqna.core.enums import PipelineStageEnum, ResultStatusEnum
from treqna.core.udm import UDMDocument
from treqna.exceptions import TreqnaError
from treqna.plugins.discovery import discover_and_register_plugins
from treqna.plugins.registry import PluginRegistry


class PipelineStageError(TreqnaError):
    def __init__(self, stage: PipelineStageEnum, message: str) -> None:
        super().__init__(f"Stage '{stage.value}' failed: {message}")
        self.stage = stage


class PipelineStageInterface(ABC):
    @property
    @abstractmethod
    def stage(self) -> PipelineStageEnum: ...

    @abstractmethod
    def execute(self, context: PipelineContext, input_data: Any) -> StageResult: ...


class BasePipelineStage(PipelineStageInterface):
    def __init__(self, stage_enum: PipelineStageEnum) -> None:
        self._stage_enum = stage_enum

    @property
    def stage(self) -> PipelineStageEnum:
        return self._stage_enum

    def execute(self, context: PipelineContext, input_data: Any) -> StageResult:
        start_time = time.perf_counter()
        duration = time.perf_counter() - start_time
        out_data = (
            input_data if isinstance(input_data, (str, bytes, UDMDocument)) else None
        )
        return StageResult(
            stage=self._stage_enum,
            status=ResultStatusEnum.SUCCESS,
            output_data=out_data,
            duration_seconds=duration,
        )


class DetectStage(BasePipelineStage):
    def __init__(self) -> None:
        super().__init__(PipelineStageEnum.DETECT)


class InspectStage(BasePipelineStage):
    def __init__(self) -> None:
        super().__init__(PipelineStageEnum.INSPECT)


class ParseStage(BasePipelineStage):
    def __init__(self, registry: PluginRegistry | None = None) -> None:
        super().__init__(PipelineStageEnum.PARSE)
        self.registry = registry if registry is not None else PluginRegistry()

    def execute(self, context: PipelineContext, input_data: Any) -> StageResult:
        start_time = time.perf_counter()
        fmt = context.execution_context.current_format
        if self.registry.has_parser(fmt):
            parser = self.registry.get_parser(fmt)
            udm_doc = parser.parse_to_udm(input_data, context)
            duration = time.perf_counter() - start_time
            return StageResult(
                stage=self.stage,
                status=ResultStatusEnum.SUCCESS,
                output_data=udm_doc,
                duration_seconds=duration,
            )
        duration = time.perf_counter() - start_time
        return StageResult(
            stage=self.stage,
            status=ResultStatusEnum.SUCCESS,
            output_data=input_data if isinstance(input_data, UDMDocument) else None,
            duration_seconds=duration,
        )


class GenerateUDMStage(BasePipelineStage):
    def __init__(self) -> None:
        super().__init__(PipelineStageEnum.GENERATE_UDM)


class TransformStage(BasePipelineStage):
    def __init__(self) -> None:
        super().__init__(PipelineStageEnum.TRANSFORM)


class ValidateStage(BasePipelineStage):
    def __init__(self) -> None:
        super().__init__(PipelineStageEnum.VALIDATE)


class WriteStage(BasePipelineStage):
    def __init__(self, registry: PluginRegistry | None = None) -> None:
        super().__init__(PipelineStageEnum.WRITE)
        self.registry = registry if registry is not None else PluginRegistry()

    def execute(self, context: PipelineContext, input_data: Any) -> StageResult:
        start_time = time.perf_counter()
        fmt = context.execution_context.target_format
        if self.registry.has_writer(fmt) and isinstance(input_data, UDMDocument):
            writer = self.registry.get_writer(fmt)
            output_str = writer.write_from_udm(input_data, context)
            duration = time.perf_counter() - start_time
            return StageResult(
                stage=self.stage,
                status=ResultStatusEnum.SUCCESS,
                output_data=output_str,
                duration_seconds=duration,
            )
        duration = time.perf_counter() - start_time
        return StageResult(
            stage=self.stage,
            status=ResultStatusEnum.SUCCESS,
            output_data=input_data if isinstance(input_data, (str, bytes)) else None,
            duration_seconds=duration,
        )


class FinalizeStage(BasePipelineStage):
    def __init__(self) -> None:
        super().__init__(PipelineStageEnum.FINALIZE)


class PipelineRegistry:
    def __init__(self) -> None:
        self._stages: dict[PipelineStageEnum, PipelineStageInterface] = {}

    def register_stage(self, stage: PipelineStageInterface) -> None:
        self._stages[stage.stage] = stage

    def get_stage(self, stage_enum: PipelineStageEnum) -> PipelineStageInterface:
        if stage_enum not in self._stages:
            raise KeyError(f"Stage '{stage_enum.value}' is not registered.")
        return self._stages[stage_enum]

    def list_stages(self) -> tuple[PipelineStageEnum, ...]:
        return tuple(self._stages.keys())

    def clear(self) -> None:
        self._stages.clear()


class PipelineBuilder:
    def __init__(self, plugin_registry: PluginRegistry | None = None) -> None:
        self._stages: list[PipelineStageInterface] = []
        self._plugin_registry = plugin_registry

    def add_stage(self, stage: PipelineStageInterface) -> "PipelineBuilder":
        self._stages.append(stage)
        return self

    def with_default_stages(self) -> "PipelineBuilder":
        reg = (
            self._plugin_registry
            if self._plugin_registry is not None
            else PluginRegistry()
        )
        if not reg.list_parsers():
            discover_and_register_plugins(reg)

        self._stages = [
            DetectStage(),
            InspectStage(),
            ParseStage(registry=reg),
            GenerateUDMStage(),
            TransformStage(),
            ValidateStage(),
            WriteStage(registry=reg),
            FinalizeStage(),
        ]
        return self

    def build(self) -> tuple[PipelineStageInterface, ...]:
        return tuple(self._stages)


class PipelineExecutor:
    def execute_pipeline(
        self,
        context: PipelineContext,
        request: TransformationRequest,
        stages: Sequence[PipelineStageInterface],
    ) -> TransformationResult:
        start_time = time.perf_counter()
        stage_results: list[StageResult] = []
        warnings_list: list[str] = []
        errors_list: list[str] = []
        stage_durations: dict[str, float] = {}
        current_data: Any = request.payload

        overall_status = ResultStatusEnum.SUCCESS

        for stage in stages:
            stage_start = time.perf_counter()
            result = stage.execute(context, current_data)
            duration = time.perf_counter() - stage_start

            stage_durations[stage.stage.value] = duration
            stage_results.append(result)
            warnings_list.extend(result.warnings)

            event = PipelineStageEvent(
                stage=stage.stage,
                event_type="stage_completed",
                message=f"Completed stage {stage.stage.value}",
            )
            context.events.append(event)

            if result.status == ResultStatusEnum.FAILURE:
                errors_list.extend(result.errors)
                overall_status = ResultStatusEnum.FAILURE
                break

            if result.output_data is not None:
                current_data = result.output_data

        total_duration = time.perf_counter() - start_time
        stats = ExecutionStatistics(
            duration_seconds=total_duration,
            stage_durations=stage_durations,
        )

        return TransformationResult(
            request_id=request.metadata.request_id if request.metadata else "",
            status=overall_status,
            output_format=request.target_format,
            result_data=current_data,
            stage_results=tuple(stage_results),
            warnings=tuple(warnings_list),
            errors=tuple(errors_list),
            statistics=stats,
        )
