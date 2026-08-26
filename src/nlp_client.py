from __future__ import annotations

import json
import os
from typing import Any

import requests

from .config import DEFAULT_MAX_COMPLETION_TOKENS, DEFAULT_MODEL, DEFAULT_NLP_API_URL


class NLPClientError(RuntimeError):
    pass


def chat(
    user_content: str,
    *,
    system_content: str,
    model: str | None = None,
    max_completion_tokens: int | None = None,
    url: str | None = None,
) -> str:
    endpoint = (url or os.environ.get("NLP_API_URL") or DEFAULT_NLP_API_URL).rstrip("/")
    payload: dict[str, Any] = {
        "history": [
            {"role": "system", "content": system_content},
            {"role": "user", "content": user_content},
        ],
        "model": model or os.environ.get("NLP_MODEL") or DEFAULT_MODEL,
        "max_completion_tokens": max_completion_tokens or DEFAULT_MAX_COMPLETION_TOKENS,
    }
    headers = {"Content-Type": "application/json"}
    api_key = os.environ.get("NLP_API_KEY", "").strip()
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    response = requests.post(endpoint, headers=headers, json=payload, timeout=300)
    if not response.ok:
        raise NLPClientError(f"NLP API error {response.status_code}: {response.text[:500]}")

    data = response.json()
    reply = data.get("reply")
    if isinstance(reply, str) and reply.strip():
        return reply.strip()

    full_response = data.get("full_response") or {}
    choices = full_response.get("choices") or []
    if choices:
        message = choices[0].get("message") or {}
        content = message.get("content")
        if isinstance(content, str) and content.strip():
            return content.strip()

    raise NLPClientError(f"NLP API returned no reply: {json.dumps(data)[:500]}")
