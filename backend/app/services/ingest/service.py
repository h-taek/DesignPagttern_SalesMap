from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path

from sqlalchemy.orm import Session

from app.core.config import settings
from app.repositories.sales import SalesRepository, SalesRow
from app.schemas import IndustryCategory
from app.services.ingest.adapter import NormalizedRow, OpenApiRowAdapter
from app.services.ingest.client import OpenApiClient
from app.services.ingest.industry_map import IndustryMap
from app.services.ingest.region_resolver import RegionResolver

_DEFAULT_INDUSTRY_MAP_PATH = Path(__file__).resolve().parents[4] / "infra" / "db" / "industry_map.csv"


@dataclass
class IngestResult:
    source: str
    quarters: list[str]
    industries: list[str]
    processed_rows: int
    accepted_rows: int
    upserted_rows: int
    failed_rows: int
    errors: list[dict] = field(default_factory=list)


class SalesIngestService:
    """Facade — fetch + adapt + aggregate + upsert.

    `rows` 인자를 직접 주면 외부 호출을 건너뛰고 그대로 처리 (CSV 로더 재사용).
    """

    def __init__(
        self,
        session: Session,
        client: OpenApiClient | None = None,
        industry_map_path: Path | None = None,
    ) -> None:
        self.session = session
        self.repo = SalesRepository(session)
        industry_map = IndustryMap.from_csv(industry_map_path or _DEFAULT_INDUSTRY_MAP_PATH)
        region_resolver = RegionResolver(self.repo)
        self.adapter = OpenApiRowAdapter(industry_map, region_resolver)
        self.client = client or OpenApiClient()

    def run(
        self,
        *,
        quarters: list[str] | None = None,
        region_ids: list[int] | None = None,
        industries: list[IndustryCategory] | None = None,
        rows: Iterable[dict] | None = None,
        source: str = "OA-15572",
    ) -> IngestResult:
        # quarters 인자는 'YYYYQn' 또는 외부 API용 'YYYYQ' 둘 다 허용 → 외부 호출에선 'YYYYQ' 변환
        if rows is None:
            quarters_api = [_to_api_quarter(q) for q in quarters] if quarters else [None]
            rows = self._fetch(quarters_api)

        processed = accepted = failed = 0
        errors: list[dict] = []
        normalized: list[NormalizedRow] = []
        for raw in rows:
            processed += 1
            result = self.adapter.adapt(raw)
            if isinstance(result, tuple):
                failed += 1
                if len(errors) < 50:
                    errors.append({"reason": result[1]})
                continue
            if region_ids and result.region_id not in region_ids:
                continue
            if industries and result.industry not in industries:
                continue
            normalized.append(result)
            accepted += 1

        aggregated = self._aggregate(normalized)
        upserted = self.repo.upsert_many(aggregated)

        observed_quarters = sorted({r.quarter for r in normalized})
        observed_industries = sorted({r.industry for r in normalized})

        return IngestResult(
            source=source,
            quarters=observed_quarters or (quarters or []),
            industries=observed_industries or [i for i in (industries or [])],
            processed_rows=processed,
            accepted_rows=accepted,
            upserted_rows=upserted,
            failed_rows=failed,
            errors=errors,
        )

    def _fetch(self, year_quarters_api: list[str | None]):
        for yq in year_quarters_api:
            yield from self.client.fetch_quarter(yq)

    @staticmethod
    def _aggregate(rows: list[NormalizedRow]) -> list[SalesRow]:
        agg: dict[tuple[int, str, str], list[int]] = {}
        for r in rows:
            key = (r.region_id, r.quarter, r.industry)
            slot = agg.setdefault(key, [0, 0])
            slot[0] += r.total_sales
            slot[1] += r.total_count or 0
        out: list[SalesRow] = []
        for (region_id, quarter, industry), (s, c) in agg.items():
            out.append(
                SalesRow(
                    region_id=region_id,
                    quarter=quarter,
                    industry_category=industry,
                    total_sales=s,
                    total_count=c or None,
                )
            )
        return out


def _to_api_quarter(q: str) -> str:
    """ '2024Q4' → '20244', 이미 5자리 숫자면 그대로. """
    if len(q) == 6 and q[4] == "Q":
        return q[:4] + q[5]
    if len(q) == 5 and q.isdigit():
        return q
    raise ValueError(f"unknown quarter format: {q!r}")


__all__ = ["SalesIngestService", "IngestResult"]
