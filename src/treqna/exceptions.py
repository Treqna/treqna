class TreqnaError(Exception):
    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message


class ConfigurationError(TreqnaError):
    pass


class PluginError(TreqnaError):
    pass


class PluginNotFoundError(PluginError):
    def __init__(self, plugin_name: str) -> None:
        super().__init__(f"Plugin '{plugin_name}' was not found.")
        self.plugin_name = plugin_name


class PluginRegistrationError(PluginError):
    def __init__(self, plugin_name: str, reason: str) -> None:
        super().__init__(f"Failed to register plugin '{plugin_name}': {reason}")
        self.plugin_name = plugin_name
        self.reason = reason


class RegistryError(TreqnaError):
    pass


class ComponentNotFoundError(RegistryError):
    def __init__(self, component_name: str) -> None:
        super().__init__(f"Component '{component_name}' is not registered.")
        self.component_name = component_name


class ExecutionError(TreqnaError):
    pass


class ValidationError(TreqnaError):
    pass
