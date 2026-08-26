"""Helpers for parsing LLM JSON replies."""

from __future__ import annotations

import json
import re


def _escape_control_chars_in_strings(blob: str) -> str:
    """Escape raw control characters that appear inside JSON string literals."""
    out: list[str] = []
    in_string = False
    escape = False
    for ch in blob:
        if escape:
            out.append(ch)
            escape = False
            continue
        if ch == "\\" and in_string:
            out.append(ch)
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            out.append(ch)
            continue
        if in_string and ord(ch) < 32:
            out.append(f"\\u{ord(ch):04x}")
            continue
        out.append(ch)
    return "".join(out)


def _strip_trailing_commas(blob: str) -> str:
    """Remove trailing commas before } or ] (common LLM JSON mistake)."""
    return re.sub(r",(\s*[}\]])", r"\1", blob)


def extract_json_array(text: str) -> list[dict]:
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text)
        text = re.sub(r"\s*```$", "", text)
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError(f"Could not find JSON array in model output: {text[:300]}")
    blob = text[start : end + 1]
    candidates = [
        blob,
        _escape_control_chars_in_strings(blob),
        _strip_trailing_commas(blob),
        _strip_trailing_commas(_escape_control_chars_in_strings(blob)),
    ]
    last_error: Exception | None = None
    for candidate in candidates:
        try:
            parsed = json.loads(candidate)
            if isinstance(parsed, list):
                return parsed
            raise ValueError(f"Expected JSON array, got {type(parsed).__name__}")
        except (json.JSONDecodeError, ValueError) as exc:
            last_error = exc
            continue
    assert last_error is not None
    raise last_error
