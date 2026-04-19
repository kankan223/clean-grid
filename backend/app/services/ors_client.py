"""OpenRouteService (ORS) client.

Phase 3: Route Optimization & Real-Time Route Management

Contract:
- Input: ORS Optimization "jobs" + "vehicles" payload parts (as dicts).
- Output: ORS response JSON (dict).
- Errors: Raises typed exceptions so routers/services can handle fallback (e.g. Haversine NN).

Docs:
- Endpoint: POST https://api.openrouteservice.org/optimization
  (older docs sometimes show /v2/optimization; ORS currently serves /optimization)

We intentionally keep this isolated: no DB, no FastAPI router wiring.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx
import structlog

from app.core.config import settings

logger = structlog.get_logger(__name__)


class ORSClientError(Exception):
    """Base error for ORS client failures."""


class ORSClientConfigError(ORSClientError):
    """Missing/invalid client configuration (e.g., no API key)."""


class ORSRateLimitError(ORSClientError):
    """ORS returned 429 Too Many Requests."""


class ORSUpstreamError(ORSClientError):
    """ORS returned a non-2xx response (other than 429)."""


class ORSTransportError(ORSClientError):
    """Network/timeout/transport-level error talking to ORS."""


@dataclass(frozen=True)
class ORSClientOptions:
    base_url: str = "https://api.openrouteservice.org"
    timeout_s: float = 30.0


class ORSClient:
    """Async ORS Optimization API client."""

    def __init__(self, *, options: ORSClientOptions | None = None) -> None:
        self._options = options or ORSClientOptions()
        self._api_key = settings.ORS_API_KEY

        # We don't hard-fail at import time; we fail at call time so the app can still boot
        # and fallback routing can be used.
        if not self._api_key:
            logger.warning("ORS_API_KEY not set; ORS optimization calls will fail and should fallback")

    @property
    def is_configured(self) -> bool:
        return bool(self._api_key)

    async def optimize_route(self, jobs: list[dict[str, Any]], vehicles: list[dict[str, Any]]) -> dict[str, Any]:
        """Call ORS optimization and return the JSON response.

        Args:
            jobs: ORS "jobs" list payload.
            vehicles: ORS "vehicles" list payload.

        Returns:
            Parsed JSON response from ORS.

        Raises:
            ORSClientConfigError: missing ORS_API_KEY.
            ORSRateLimitError: upstream 429.
            ORSUpstreamError: upstream non-2xx.
            ORSTransportError: timeouts/network errors.
        """

        if not self._api_key:
            raise ORSClientConfigError("ORS_API_KEY is not configured")

        if not jobs:
            raise ValueError("jobs must be a non-empty list")

        if not vehicles:
            raise ValueError("vehicles must be a non-empty list")

        url = f"{self._options.base_url}/optimization"

        payload: dict[str, Any] = {
            "jobs": jobs,
            "vehicles": vehicles,
        }

        headers = {
            "Authorization": self._api_key,
            "Content-Type": "application/json",
        }

        try:
            logger.info("ORS optimize_route request", url=url, jobs=len(jobs), vehicles=len(vehicles))

            async with httpx.AsyncClient(timeout=self._options.timeout_s) as client:
                resp = await client.post(url, json=payload, headers=headers)

                if resp.status_code == 429:
                    # ORS may also provide rate-limit headers; log them for observability.
                    logger.warning(
                        "ORS rate limited",
                        retry_after=resp.headers.get("retry-after"),
                        x_ratelimit_limit=resp.headers.get("x-ratelimit-limit"),
                        x_ratelimit_remaining=resp.headers.get("x-ratelimit-remaining"),
                        x_ratelimit_reset=resp.headers.get("x-ratelimit-reset"),
                    )
                    raise ORSRateLimitError("ORS rate limit exceeded (HTTP 429)")

                # Raise for other 4xx/5xx so we can capture response body.
                try:
                    resp.raise_for_status()
                except httpx.HTTPStatusError as e:
                    body = _safe_json(resp)
                    logger.error(
                        "ORS upstream error",
                        status_code=resp.status_code,
                        body=body,
                    )
                    raise ORSUpstreamError(f"ORS error HTTP {resp.status_code}") from e

                data = resp.json()
                logger.info("ORS optimize_route success")
                return data

        except (httpx.TimeoutException, httpx.ConnectError, httpx.NetworkError) as e:
            logger.error("ORS transport error", error=str(e))
            raise ORSTransportError("Transport error calling ORS") from e

        except httpx.HTTPError as e:
            # Catch-all for other httpx issues.
            logger.error("ORS httpx error", error=str(e))
            raise ORSTransportError("HTTP error calling ORS") from e


def _safe_json(resp: httpx.Response) -> Any:
    try:
        return resp.json()
    except Exception:
        return {"text": resp.text}


# Singleton instance (mirrors other services pattern)
ors_client = ORSClient()
