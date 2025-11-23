from __future__ import annotations

from pathlib import Path
from typing import Any


def to_php(value: Any, indent: int = 0) -> str:
    space = "    " * indent
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    if isinstance(value, str):
        escaped = value.replace("\\", "\\\\").replace("'", "\\'")
        return f"'{escaped}'"
    if isinstance(value, dict):
        items = []
        for key, val in value.items():
            items.append(f"{space}    '{key}' => {to_php(val, indent + 1)}")
        inner = ",\n".join(items)
        return f"array(\n{inner}\n{space})"
    if isinstance(value, (list, tuple, set)):
        items = [f"{space}    {to_php(val, indent + 1)}" for val in value]
        inner = ",\n".join(items)
        return f"array(\n{inner}\n{space})"
    return f"'{str(value)}'"


def export_to_php_file(data: Any, output_path: str | Path) -> Path:
    path = Path(output_path)
    php_content = "<?php\nreturn " + to_php(data) + ";\n"
    path.write_text(php_content, encoding="utf-8")
    return path
