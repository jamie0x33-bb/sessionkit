"""Connector service client with retry and pagination helpers."""

from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request

from .config import Runtime, load

TIMEOUT = int(os.environ.get("SKILLS_TIMEOUT", "60"))
RETRIES = int(os.environ.get("SKILLS_RETRIES", "3"))
BACKOFF = 0.5


class ConnectorError(RuntimeError):
    def __init__(self, status: int, body: str):
        super().__init__(f"connector service returned {status}")
        self.status = status
        self.body = body


def _once(rt: Runtime, method: str, path: str, payload: dict | None):
    url = f"{rt.base_url.rstrip('/')}{path}"
    data = json.dumps(payload).encode() if payload is not None else None
    req = urllib.request.Request(url, data=data, method=method, headers=rt.headers())
    with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
        return json.loads(resp.read().decode() or "{}")


def request(rt: Runtime, method: str, path: str, payload: dict | None = None):
    """Call the connector service, retrying 429 and 5xx with exponential backoff."""
    last: ConnectorError | None = None
    for attempt in range(1, RETRIES + 1):
        try:
            return _once(rt, method, path, payload)
        except urllib.error.HTTPError as exc:
            err = ConnectorError(exc.code, exc.read().decode(errors="replace"))
            if exc.code != 429 and exc.code < 500:
                raise err from None
            last = err
            if attempt < RETRIES:
                time.sleep(BACKOFF * 2 ** (attempt - 1))
    raise last  # type: ignore[misc]


def list_connectors(rt: Runtime | None = None) -> list[dict]:
    return request(rt or load(), "GET", "/rest/connector-service/connectors").get("connectors", [])


def tool_names(source_id: str, rt: Runtime | None = None) -> list[str]:
    """Tool names for one connector, from the listing rather than a describe call."""
    for c in list_connectors(rt):
        if c.get("source_id") == source_id:
            return [t.get("name") for t in c.get("tools", [])]
    return []


def connected(rt: Runtime | None = None) -> list[dict]:
    return [c for c in list_connectors(rt) if c.get("status") == "CONNECTED"]


def find(query: str, rt: Runtime | None = None) -> list[dict]:
    q = query.lower()
    return [
        c for c in list_connectors(rt)
        if q in (c.get("source_id") or "").lower() or q in (c.get("display_name") or "").lower()
    ]


def describe(source_id: str, rt: Runtime | None = None) -> dict:
    return request(rt or load(), "POST", f"/rest/connector-service/connectors/{source_id}/describe", {})


def call_tool(source_id: str, tool: str, arguments: dict, rt: Runtime | None = None) -> dict:
    path = f"/rest/connector-service/connectors/{source_id}/tools/{tool}/execute"
    return request(rt or load(), "POST", path, {"parameters": arguments})
