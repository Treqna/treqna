from treqna.formats.registry import FormatRegistry
from treqna.plugins.csv.manifest import register_csv_plugin
from treqna.plugins.excel.manifest import register_excel_plugin
from treqna.plugins.json.manifest import register_json_plugin
from treqna.plugins.registry import PluginRegistry
from treqna.plugins.xml.manifest import register_xml_plugin
from treqna.plugins.yaml.manifest import register_yaml_plugin


def discover_and_register_plugins(
    plugin_registry: PluginRegistry,
    format_registry: FormatRegistry | None = None,
) -> None:
    register_csv_plugin(plugin_registry, format_registry)
    register_json_plugin(plugin_registry, format_registry)
    register_yaml_plugin(plugin_registry, format_registry)
    register_xml_plugin(plugin_registry, format_registry)
    register_excel_plugin(plugin_registry, format_registry)
