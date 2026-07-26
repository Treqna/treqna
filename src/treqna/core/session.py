import uuid
from collections.abc import Sequence
from dataclasses import dataclass

from treqna.core.context import (
    ExecutionContext,
    PipelineContext,
    TransformationMetadata,
)
from treqna.core.contracts import TransformationRequest, TransformationResult
from treqna.core.enums import ResultStatusEnum
from treqna.core.pipeline import (
    PipelineBuilder,
    PipelineExecutor,
    PipelineStageInterface,
)
from treqna.exceptions import TreqnaError
from treqna.plugins.registry import PluginRegistry


class SessionError(TreqnaError):
    def __init__(self, session_id: str, message: str) -> None:
        super().__init__(f"Session '{session_id}' error: {message}")
        self.session_id = session_id


def generate_session_id() -> str:
    return str(uuid.uuid4())


@dataclass
class TransformationSession:
    session_id: str
    context: PipelineContext
    pipeline: Sequence[PipelineStageInterface]
    status: ResultStatusEnum = ResultStatusEnum.PENDING

    def execute(
        self,
        request: TransformationRequest,
        executor: PipelineExecutor,
    ) -> TransformationResult:
        self.status = ResultStatusEnum.RUNNING
        result = executor.execute_pipeline(self.context, request, self.pipeline)
        self.status = result.status
        return result

    def cancel(self) -> None:
        self.status = ResultStatusEnum.CANCELLED


class LifecycleManager:
    def __init__(self) -> None:
        self._active_sessions: dict[str, TransformationSession] = {}

    def create_session(
        self,
        request: TransformationRequest,
        pipeline: Sequence[PipelineStageInterface] | None = None,
        plugin_registry: PluginRegistry | None = None,
    ) -> TransformationSession:
        session_id = generate_session_id()
        metadata = (
            request.metadata
            if request.metadata is not None
            else TransformationMetadata(
                request_id=session_id,
                source_identifier=request.source_format,
                target_identifier=request.target_format,
            )
        )
        exec_context = ExecutionContext(
            current_format=request.source_format,
            target_format=request.target_format,
            metadata=metadata,
        )
        pipe_context = PipelineContext(
            session_id=session_id,
            execution_context=exec_context,
        )

        stages = (
            pipeline
            if pipeline is not None
            else PipelineBuilder(plugin_registry=plugin_registry)
            .with_default_stages()
            .build()
        )
        session = TransformationSession(
            session_id=session_id,
            context=pipe_context,
            pipeline=stages,
        )
        self._active_sessions[session_id] = session
        return session

    def get_session(self, session_id: str) -> TransformationSession:
        if session_id not in self._active_sessions:
            raise SessionError(session_id, "Session not found.")
        return self._active_sessions[session_id]

    def terminate_session(self, session_id: str) -> None:
        session = self.get_session(session_id)
        session.cancel()
        del self._active_sessions[session_id]

    def list_active_sessions(self) -> tuple[str, ...]:
        return tuple(self._active_sessions.keys())

    def clear_all(self) -> None:
        self._active_sessions.clear()

