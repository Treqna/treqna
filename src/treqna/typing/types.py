from collections.abc import Callable
from typing import Any, Protocol, TypeVar

T = TypeVar("T")
T_co = TypeVar("T_co", covariant=True)

JsonDict = dict[str, Any]
EventHandler = Callable[[str, JsonDict], None]


class Identifiable(Protocol):
    @property
    def identifier(self) -> str: ...


class Versioned(Protocol):
    @property
    def version(self) -> str: ...


class Initializable(Protocol):
    def initialize(self) -> None: ...

    def shutdown(self) -> None: ...
