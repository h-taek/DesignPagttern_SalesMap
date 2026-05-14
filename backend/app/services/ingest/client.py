from collections.abc import Iterator

import httpx

from app.core.config import settings

_PAGE = 1000
_SERVICE_NAME = "VwsmTrdarSelngQq"  # OA-15572


class OpenApiClient:
    """서울 열린데이터 광장 OA-15572 호출 (JSON)."""

    def __init__(self, base: str | None = None, key: str | None = None, timeout: float = 30.0) -> None:
        self._base = (base or settings.open_api_base).rstrip("/")
        self._key = key or settings.open_api_key
        self._timeout = timeout

    def fetch_quarter(self, year_quarter: str | None) -> Iterator[dict]:
        """quarter는 '20244' 형식. None이면 전체 (소량 테스트 권장 안 함)."""
        if not self._key:
            raise RuntimeError("OPEN_API_KEY is empty")

        with httpx.Client(timeout=self._timeout) as client:
            start = 1
            while True:
                end = start + _PAGE - 1
                url = f"{self._base}/{self._key}/json/{_SERVICE_NAME}/{start}/{end}"
                if year_quarter:
                    url += f"/{year_quarter}"
                resp = client.get(url)
                resp.raise_for_status()
                data = resp.json().get(_SERVICE_NAME, {})
                rows: list[dict] = data.get("row", []) or []
                if not rows:
                    return
                yield from rows
                if len(rows) < _PAGE:
                    return
                start += _PAGE
