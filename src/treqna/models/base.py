import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


def generate_uuid() -> str:
    return str(uuid.uuid4())


def current_utc_time() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, kw_only=True)
class EntityMetadata:
    identifier: str = field(default_factory=generate_uuid)
    name: str
    description: str = ""
    created_at: datetime = field(default_factory=current_utc_time)
    tags: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, kw_only=True)
class ExecutionContext:
    context_id: str = field(default_factory=generate_uuid)
    environment: str = "default"
    metadata: EntityMetadata | None = None
    parameters: dict[str, Any] = field(default_factory=dict)
