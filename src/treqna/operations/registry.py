from treqna.exceptions import TreqnaError
from treqna.operations.enums import OperationCategory
from treqna.operations.models import OperationDescriptor


class OperationNotFoundError(TreqnaError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Operation descriptor '{name}' was not found.")
        self.name = name


class OperationRegistry:
    def __init__(self) -> None:
        self._descriptors_by_name: dict[str, OperationDescriptor] = {}
        self._descriptors_by_category: dict[
            OperationCategory, list[OperationDescriptor]
        ] = {cat: [] for cat in OperationCategory}

    def register(self, descriptor: OperationDescriptor) -> None:
        key = descriptor.name.lower()
        self._descriptors_by_name[key] = descriptor
        self._descriptors_by_category[descriptor.category].append(descriptor)

    def get_by_name(self, name: str) -> OperationDescriptor:
        key = name.lower()
        if key not in self._descriptors_by_name:
            raise OperationNotFoundError(name)
        return self._descriptors_by_name[key]

    def list_by_category(
        self,
        category: OperationCategory,
    ) -> tuple[OperationDescriptor, ...]:
        return tuple(self._descriptors_by_category.get(category, []))

    def list_all(self) -> tuple[OperationDescriptor, ...]:
        return tuple(self._descriptors_by_name.values())

    def clear(self) -> None:
        self._descriptors_by_name.clear()
        for cat in self._descriptors_by_category:
            self._descriptors_by_category[cat].clear()

