"""Resilient JSON extraction helpers shared by language model agents."""

from __future__ import annotations

import json
import re
from typing import Any


_FENCE = re.compile(r"```(?:json)?\s*(.+?)\s*```", re.DOTALL | re.IGNORECASE)
_BRACES = re.compile(r"\{.*\}", re.DOTALL)


def extract_json(content: str) -> dict[str, Any]:
    text = content.strip()
    fence = _FENCE.search(text)
    candidate = fence.group(1) if fence else text
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        pass
    match = _BRACES.search(candidate)
    if not match:
        raise ValueError(f"no JSON object found in response: {content[:200]}")
    return json.loads(match.group(0))
