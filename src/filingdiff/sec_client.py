"""Small official SEC submissions client with raw-response caching."""

from __future__ import annotations

import json
import re
import time
from collections.abc import Callable
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from filingdiff.errors import ConfigurationError, SecRequestError, SecResponseError


SUBMISSIONS_BASE_URL = "https://data.sec.gov/submissions"
_EMAIL_PATTERN = re.compile(r"\b[^\s@]+@[^\s@]+\.[^\s@]+\b")
_ARCHIVE_NAME_PATTERN = re.compile(r"^[A-Za-z0-9._-]+\.json$")

Fetcher = Callable[[Request, float], bytes]


def _default_fetcher(request: Request, timeout: float) -> bytes:
    with urlopen(request, timeout=timeout) as response:  # noqa: S310 - fixed HTTPS host
        return response.read()


class SecClient:
    """Retrieve JSON metadata from the SEC's public submissions service.

    The caller supplies a declared user agent at runtime. A fetcher can be
    injected in tests so the test suite never reaches the network.
    """

    def __init__(
        self,
        user_agent: str,
        *,
        cache_dir: Path | str = Path(".cache/sec"),
        timeout: float = 20.0,
        min_request_interval: float = 0.11,
        fetcher: Fetcher | None = None,
    ) -> None:
        cleaned_user_agent = user_agent.strip()
        if not cleaned_user_agent or not _EMAIL_PATTERN.search(cleaned_user_agent):
            raise ConfigurationError(
                "SEC User-Agent must include an application name and contact "
                "email, for example: 'FilingDiff YourName you@example.com'."
            )
        if timeout <= 0:
            raise ConfigurationError("SEC request timeout must be positive.")
        if min_request_interval < 0:
            raise ConfigurationError("SEC request interval cannot be negative.")

        self.user_agent = cleaned_user_agent
        self.cache_dir = Path(cache_dir)
        self.timeout = timeout
        self.min_request_interval = min_request_interval
        self._fetcher = fetcher or _default_fetcher
        self._last_request_at: float | None = None

    def fetch_company_submissions(self, cik: str) -> dict[str, Any]:
        """Return the main SEC submissions payload for a zero-padded CIK."""

        if not re.fullmatch(r"\d{10}", cik):
            raise ConfigurationError("CIK must contain exactly 10 digits.")
        filename = f"CIK{cik}.json"
        return self._get_json(f"{SUBMISSIONS_BASE_URL}/{filename}", filename)

    def fetch_submission_archive(self, filename: str) -> dict[str, Any]:
        """Return one historical submissions payload named by the SEC."""

        if not _ARCHIVE_NAME_PATTERN.fullmatch(filename):
            raise SecResponseError(
                f"SEC supplied an unsafe historical submissions filename: {filename!r}."
            )
        return self._get_json(f"{SUBMISSIONS_BASE_URL}/{filename}", filename)

    def _get_json(self, url: str, cache_filename: str) -> dict[str, Any]:
        cache_path = self.cache_dir / cache_filename
        if cache_path.is_file():
            try:
                raw = cache_path.read_bytes()
            except OSError as exc:
                raise SecRequestError(f"Could not read SEC cache file {cache_path}.") from exc
        else:
            raw = self._request(url)
            try:
                cache_path.parent.mkdir(parents=True, exist_ok=True)
                temporary_path = cache_path.with_suffix(cache_path.suffix + ".tmp")
                temporary_path.write_bytes(raw)
                temporary_path.replace(cache_path)
            except OSError as exc:
                raise SecRequestError(f"Could not write SEC cache file {cache_path}.") from exc

        try:
            payload = json.loads(raw)
        except (json.JSONDecodeError, UnicodeDecodeError) as exc:
            raise SecResponseError(f"SEC response {cache_filename!r} is not valid JSON.") from exc
        if not isinstance(payload, dict):
            raise SecResponseError(
                f"SEC response {cache_filename!r} must contain a JSON object."
            )
        return payload

    def _request(self, url: str) -> bytes:
        if self._last_request_at is not None:
            elapsed = time.monotonic() - self._last_request_at
            remaining = self.min_request_interval - elapsed
            if remaining > 0:
                time.sleep(remaining)

        request = Request(
            url,
            headers={
                "Accept": "application/json",
                "User-Agent": self.user_agent,
            },
            method="GET",
        )
        try:
            raw = self._fetcher(request, self.timeout)
        except HTTPError as exc:
            raise SecRequestError(
                f"SEC request failed with HTTP {exc.code} for {url}."
            ) from exc
        except (URLError, TimeoutError, OSError) as exc:
            raise SecRequestError(f"Could not retrieve SEC data from {url}: {exc}.") from exc
        finally:
            self._last_request_at = time.monotonic()

        if not isinstance(raw, bytes):
            raise SecResponseError("SEC fetcher returned non-byte response data.")
        return raw

