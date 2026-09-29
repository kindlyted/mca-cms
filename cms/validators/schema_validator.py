"""
Schema Validator — Validate generated JSON against hardcoded templates.

Can be used standalone to validate existing JSON files.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# Import hardcoded templates
sys.path.insert(0, str(Path(__file__).parent.parent))
from generators.base import TEMPLATES


def validate_json_against_template(data: dict, content_type: str) -> List[str]:
    """
    Validate a JSON dict against the hardcoded template for the given content type.

    Args:
        data: The JSON data to validate
        content_type: "blog", "service", or "provider"

    Returns:
        List of error messages (empty if valid)
    """
    template = TEMPLATES.get(content_type)
    if not template:
        return [f"Unknown content type: {content_type}"]

    errors = []
    _check_keys(template, data, "", errors)
    return errors


def _check_keys(template: dict, data: dict, prefix: str, errors: List[str]):
    """Recursively check that all template keys exist in data."""
    for key, value in template.items():
        path = f"{prefix}.{key}" if prefix else key
        if key not in data:
            errors.append(f"Missing: {path}")
        elif isinstance(value, dict) and isinstance(data.get(key), dict):
            _check_keys(value, data[key], path, errors)


def validate_file(file_path: str) -> Tuple[bool, List[str]]:
    """
    Validate a JSON file against its template.

    Auto-detects content type from _type field.

    Returns:
        (is_valid, errors)
    """
    path = Path(file_path)
    if not path.exists():
        return False, [f"File not found: {file_path}"]

    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)

    content_type = data.get("_type", "")
    if content_type not in TEMPLATES:
        return False, [f"Unknown _type: {content_type}"]

    errors = validate_json_against_template(data, content_type)
    return len(errors) == 0, errors


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python schema_validator.py <file.json> [file2.json ...]")
        sys.exit(1)

    for file_path in sys.argv[1:]:
        is_valid, errors = validate_file(file_path)
        if is_valid:
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} ({len(errors)} issues):")
            for e in errors:
                print(f"   - {e}")
