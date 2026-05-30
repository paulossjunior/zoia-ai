"""HTTP adapter for command completion callback delivery."""

from __future__ import annotations

from typing import Any


class HttpCallbackClient:
    """Deliver callback payloads with an HTTP POST request."""

    def __init__(self, timeout: float = 5.0, client: Any | None = None) -> None:
        self.timeout = timeout
        self.client = client

    def send(self, url: str, payload: dict[str, Any]) -> None:
        """POST a callback payload and raise on connection or non-2xx errors."""
        if self.client is None:
            import httpx

            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(url, json=payload)
        else:
            response = self.client.post(url, json=payload, timeout=self.timeout)
        if response.status_code < 200 or response.status_code >= 300:
            raise RuntimeError(f"Callback delivery failed with HTTP {response.status_code}")
