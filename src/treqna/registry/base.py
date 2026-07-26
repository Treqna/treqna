from typing import Generic, TypeVar

from treqna.exceptions import ComponentNotFoundError

T = TypeVar("T")


class ComponentRegistry(Generic[T]):
    def __init__(self) -> None:
        self._components: dict[str, T] = {}

    def register(self, name: str, component: T) -> None:
        self._components[name] = component

    def unregister(self, name: str) -> None:
        if name not in self._components:
            raise ComponentNotFoundError(name)
        del self._components[name]

    def get(self, name: str) -> T:
        if name not in self._components:
            raise ComponentNotFoundError(name)
        return self._components[name]

    def has(self, name: str) -> bool:
        return name in self._components

    def list_all(self) -> list[str]:
        return list(self._components.keys())

    def clear(self) -> None:
        self._components.clear()

    def __len__(self) -> int:
        return len(self._components)
