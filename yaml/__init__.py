"""Small YAML helpers for the profile storage format used in tests.

This module intentionally implements only the subset of YAML required by the
project's profile persistence layer: nested mappings with string keys and
string scalar values.
"""

from __future__ import annotations

from typing import Any, Dict, List


class YAMLError(ValueError):
    """Raised when the lightweight YAML parser cannot decode input."""



def _quote_scalar(value: str) -> str:
    if value == "" or value.strip() != value or any(ch in value for ch in [":", "#", '"', "\n"]):
        escaped = value.replace("\\", "\\\\").replace('"', '\\"')
        return f'"{escaped}"'
    return value



def _parse_scalar(value: str) -> str:
    text = value.strip()
    if len(text) >= 2 and text[0] == text[-1] == '"':
        return bytes(text[1:-1], "utf-8").decode("unicode_escape")
    if len(text) >= 2 and text[0] == text[-1] == "'":
        return text[1:-1]
    return text



def safe_load(text: str) -> Dict[str, Dict[str, str]] | None:
    """Parse a tiny YAML subset into nested dictionaries."""
    if not text.strip():
        return None

    data: Dict[str, Dict[str, str]] = {}
    current_name: str | None = None

    for raw_line in text.splitlines():
        line = raw_line.rstrip()
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        if not line.startswith(" "):
            if not line.endswith(":"):
                raise YAMLError(f"Invalid mapping entry: {raw_line}")
            current_name = _parse_scalar(line[:-1].strip())
            if not current_name:
                raise YAMLError("Mapping keys must be non-empty strings.")
            data[current_name] = {}
            continue

        if current_name is None:
            raise YAMLError("Nested mapping found before a top-level key.")
        if not line.startswith("  ") or ":" not in stripped:
            raise YAMLError(f"Invalid nested mapping entry: {raw_line}")

        key, value = stripped.split(":", 1)
        parsed_key = _parse_scalar(key)
        if not parsed_key:
            raise YAMLError("Nested mapping keys must be non-empty strings.")
        data[current_name][parsed_key] = _parse_scalar(value)

    return data



def _dump_mapping_lines(mapping: Dict[str, Any], indent: int = 0) -> List[str]:
    lines: List[str] = []
    prefix = " " * indent
    for key in sorted(mapping):
        value = mapping[key]
        rendered_key = _quote_scalar(str(key))
        if isinstance(value, dict):
            lines.append(f"{prefix}{rendered_key}:")
            lines.extend(_dump_mapping_lines(value, indent + 2))
        else:
            rendered_value = _quote_scalar(str(value))
            lines.append(f"{prefix}{rendered_key}: {rendered_value}")
    return lines



def safe_dump(data: Dict[str, Any], sort_keys: bool = True, default_flow_style: bool = False) -> str:
    """Serialize nested mappings to a tiny YAML subset."""
    if not isinstance(data, dict):
        raise YAMLError("Only mappings are supported by this lightweight YAML dumper.")
    if not sort_keys:
        data = dict(data)
    if default_flow_style:
        raise YAMLError("Flow style output is not supported.")
    lines = _dump_mapping_lines(data)
    return ("\n".join(lines) + "\n") if lines else "{}\n"
