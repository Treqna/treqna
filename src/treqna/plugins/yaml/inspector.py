from collections.abc import Mapping
from typing import Any

import yaml  # type: ignore[import-untyped]

from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.json.inspector import calculate_json_depth
from treqna.plugins.parser import FormatInspectorInterface


class YAMLInspector(FormatInspectorInterface):
    def inspect_schema(self, source_data: bytes | str) -> Mapping[str, Any]:
        text = decode_source_data(source_data).strip()
        if not text:
            return {
                "structure_type": "empty",
                "key_count": 0,
                "item_count": 0,
                "keys": (),
                "depth": 0,
                "is_multi_document": False,
            }
        try:
            docs = list(yaml.safe_load_all(text))
            is_multi = len(docs) > 1
            parsed = docs[0] if docs else None
            depth = calculate_json_depth(parsed) if parsed is not None else 0

            if isinstance(parsed, dict):
                keys = tuple(str(k) for k in parsed)
                return {
                    "structure_type": "object",
                    "key_count": len(keys),
                    "item_count": len(parsed),
                    "keys": keys,
                    "depth": depth,
                    "is_multi_document": is_multi,
                }
            if isinstance(parsed, list):
                first_keys: tuple[str, ...] = ()
                if parsed and isinstance(parsed[0], dict):
                    first_keys = tuple(str(k) for k in parsed[0])
                return {
                    "structure_type": "array",
                    "key_count": len(first_keys),
                    "item_count": len(parsed),
                    "keys": first_keys,
                    "depth": depth,
                    "is_multi_document": is_multi,
                }
            return {
                "structure_type": "primitive",
                "key_count": 0,
                "item_count": 1,
                "keys": (),
                "depth": depth,
                "is_multi_document": is_multi,
            }
        except (yaml.YAMLError, ValueError):
            return {
                "structure_type": "malformed",
                "key_count": 0,
                "item_count": 0,
                "keys": (),
                "depth": 0,
                "is_multi_document": False,
            }
