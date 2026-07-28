import json
from typing import Any


def deserialize_json(
    value: str | dict[str, Any] | None,
) -> dict[str, Any]:
    """
    Safely convert a stored JSON value into a dictionary.
    """

    if value is None:
        return {}

    if isinstance(value, dict):
        return value

    if not isinstance(value, str):
        return {}

    try:
        parsed = json.loads(value)
    except (json.JSONDecodeError, TypeError):
        return {}

    if not isinstance(parsed, dict):
        return {}

    return parsed


def serialize_json(
    value: dict[str, Any] | None,
) -> str | None:
    """
    Safely serialize a dictionary for SQLite storage.
    """

    if value is None:
        return None

    return json.dumps(
        value,
        ensure_ascii=False,
        default=str,
    )