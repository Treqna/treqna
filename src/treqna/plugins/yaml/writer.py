from typing import TextIO

import yaml  # type: ignore[import-untyped]

from treqna.core.context import PipelineContext
from treqna.core.udm import UDMCollection, UDMDocument
from treqna.plugins.interface import PluginMetadata
from treqna.plugins.json.writer import udm_node_to_json_obj
from treqna.plugins.writer import WriterPluginInterface
from treqna.plugins.yaml.options import YAMLOptions
from treqna.plugins.yaml.parser import extract_yaml_options


class YAMLWriterPlugin(WriterPluginInterface):
    @property
    def metadata(self) -> PluginMetadata:
        return PluginMetadata(
            name="yaml_writer",
            version="1.0.0",
            format_identifier="yaml",
            description="Official Treqna UDM to YAML Writer Plugin",
            supported_media_types=("application/x-yaml", "text/yaml"),
        )

    @property
    def format_identifier(self) -> str:
        return "yaml"

    def initialize(self, context: PipelineContext) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def write_from_udm(
        self,
        document: UDMDocument,
        context: PipelineContext,
    ) -> str:
        options = extract_yaml_options(context)
        if isinstance(document.root, UDMCollection) and options.is_multi_document:
            objects_list = [udm_node_to_json_obj(item) for item in document.root.items]
            res_multi = yaml.safe_dump_all(
                objects_list,
                indent=options.indent,
                explicit_start=options.explicit_start,
                explicit_end=options.explicit_end,
                default_flow_style=options.default_flow_style,
                allow_unicode=options.allow_unicode,
                sort_keys=options.sort_keys,
            )
            return str(res_multi)

        yaml_obj = udm_node_to_json_obj(document.root)
        res_single = yaml.safe_dump(
            yaml_obj,
            indent=options.indent,
            explicit_start=options.explicit_start,
            explicit_end=options.explicit_end,
            default_flow_style=options.default_flow_style,
            allow_unicode=options.allow_unicode,
            sort_keys=options.sort_keys,
        )
        return str(res_single)

    def stream_write_from_udm(
        self,
        document: UDMDocument,
        target_stream: TextIO,
        options: YAMLOptions | None = None,
    ) -> None:
        opts = options if options is not None else YAMLOptions()
        yaml_obj = udm_node_to_json_obj(document.root)
        yaml.safe_dump(
            yaml_obj,
            target_stream,
            indent=opts.indent,
            explicit_start=opts.explicit_start,
            explicit_end=opts.explicit_end,
            default_flow_style=opts.default_flow_style,
            allow_unicode=opts.allow_unicode,
            sort_keys=opts.sort_keys,
        )

