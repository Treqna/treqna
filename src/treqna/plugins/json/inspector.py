import json
from collections.abc import Mapping
from typing import Any

from treqna.plugins.csv.parser import decode_source_data
from treqna.plugins.parser import FormatInspectorInterface


def calculate_json_depth(obj: Any) -> int:
    if isinstance(obj, dict):
        if not obj:
            return 1
        return 1 + max(calculate_json_depth(v) for v in obj.values())
    if isinstance(obj, list):
        if not obj:
            return 1
        return 1 + max(calculate_json_depth(item) for item in obj)
    return 1


class JSONInspector(FormatInspectorInterface):
    def inspect_schema(self, source_data: bytes | str) -> Mapping[str, Any]:
        text = decode_source_data(source_data).strip()
        if not text:
            return {
                "structure_type": "empty",
                "key_count": 0,
                "item_count": 0,
                "keys": (),
                "depth": 0,
            }
        try:
            parsed = json.loads(text)
            depth = calculate_json_depth(parsed)
            if isinstance(parsed, dict):
                keys = tuple(str(k) for k in parsed)
                return {
                    "structure_type": "object",
                    "key_count": len(keys),
                    "item_count": len(parsed),
                    "keys": keys,
                    "depth": depth,
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
                }
            return {
                "structure_type": "primitive",
                "key_count": 0,
                "item_count": 1,
                "keys": (),
                "depth": depth,
            }
        except json.JSONDecodeError:
            return {
                "structure_type": "malformed",
                "key_count": 0,
                "item_count": 0,
                "keys": (),
                "depth": 0,
            }
