from treqna.exceptions import TreqnaError
from treqna.formats.enums import FormatCapability
from treqna.formats.models import FormatDescriptor


class FormatNotFoundError(TreqnaError):
    def __init__(self, identifier: str) -> None:
        super().__init__(f"Format descriptor '{identifier}' was not found.")
        self.identifier = identifier


class CapabilityRegistry:
    def __init__(self) -> None:
        self._capability_map: dict[FormatCapability, list[FormatDescriptor]] = {
            cap: [] for cap in FormatCapability
        }

    def index_descriptor(self, descriptor: FormatDescriptor) -> None:
        if descriptor.supports_reading:
            self._capability_map[FormatCapability.READ].append(descriptor)
        if descriptor.supports_writing:
            self._capability_map[FormatCapability.WRITE].append(descriptor)

    def get_descriptors_with_capability(
        self,
        capability: FormatCapability,
    ) -> tuple[FormatDescriptor, ...]:
        return tuple(self._capability_map.get(capability, []))

    def clear(self) -> None:
        for cap in self._capability_map:
            self._capability_map[cap].clear()


class DescriptorRegistry:
    def __init__(self) -> None:
        self._descriptors_by_name: dict[str, FormatDescriptor] = {}
        self._descriptors_by_extension: dict[str, FormatDescriptor] = {}
        self._descriptors_by_mime: dict[str, FormatDescriptor] = {}

    def register(self, descriptor: FormatDescriptor) -> None:
        name_key = descriptor.name.lower()
        self._descriptors_by_name[name_key] = descriptor

        primary_ext = descriptor.extensions.primary.lower().lstrip(".")
        self._descriptors_by_extension[primary_ext] = descriptor
        for ext_alias in descriptor.extensions.aliases:
            self._descriptors_by_extension[ext_alias.lower().lstrip(".")] = descriptor

        primary_mime = descriptor.mime_types.primary.lower()
        self._descriptors_by_mime[primary_mime] = descriptor
        for mime_alias in descriptor.mime_types.aliases:
            self._descriptors_by_mime[mime_alias.lower()] = descriptor

    def get_by_name(self, name: str) -> FormatDescriptor:
        key = name.lower()
        if key not in self._descriptors_by_name:
            raise FormatNotFoundError(name)
        return self._descriptors_by_name[key]

    def get_by_extension(self, extension: str) -> FormatDescriptor:
        key = extension.lower().lstrip(".")
        if key not in self._descriptors_by_extension:
            raise FormatNotFoundError(extension)
        return self._descriptors_by_extension[key]

    def get_by_mime_type(self, mime_type: str) -> FormatDescriptor:
        key = mime_type.lower()
        if key not in self._descriptors_by_mime:
            raise FormatNotFoundError(mime_type)
        return self._descriptors_by_mime[key]

    def list_descriptors(self) -> tuple[FormatDescriptor, ...]:
        return tuple(self._descriptors_by_name.values())

    def clear(self) -> None:
        self._descriptors_by_name.clear()
        self._descriptors_by_extension.clear()
        self._descriptors_by_mime.clear()


class FormatRegistry:
    def __init__(self) -> None:
        self.descriptors = DescriptorRegistry()
        self.capabilities = CapabilityRegistry()

    def register_descriptor(self, descriptor: FormatDescriptor) -> None:
        self.descriptors.register(descriptor)
        self.capabilities.index_descriptor(descriptor)

    def get_descriptor(self, identifier: str) -> FormatDescriptor:
        try:
            return self.descriptors.get_by_name(identifier)
        except FormatNotFoundError:
            pass

        try:
            return self.descriptors.get_by_extension(identifier)
        except FormatNotFoundError:
            pass

        return self.descriptors.get_by_mime_type(identifier)

    def find_best_descriptor(
        self,
        capability: FormatCapability,
        min_score: float = 0.0,
    ) -> FormatDescriptor | None:
        candidates = self.capabilities.get_descriptors_with_capability(capability)
        best_candidate: FormatDescriptor | None = None
        best_score = min_score - 0.0001

        for candidate in candidates:
            score = (
                candidate.quality_metrics.compute_composite_score()
                * candidate.priority.value
            )
            if score > best_score:
                best_score = score
                best_candidate = candidate

        return best_candidate

    def list_all(self) -> tuple[FormatDescriptor, ...]:
        return self.descriptors.list_descriptors()

    def clear(self) -> None:
        self.descriptors.clear()
        self.capabilities.clear()
