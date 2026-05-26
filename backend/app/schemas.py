from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

IndustryCategory = Literal["food", "service", "retail"]


def _to_camel(s: str) -> str:
    head, *rest = s.split("_")
    return head + "".join(w.capitalize() for w in rest)


class _Out(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True, from_attributes=True)


class RegionOut(_Out):
    region_id: int
    region_name: str
    sgg_code: str


class SalesCurrentOut(_Out):
    quarter: str
    total_sales: int
    total_count: int | None = None


class PredictionModelOut(_Out):
    slope: float | None = None
    intercept: float | None = None
    samples_used: int | None = None


class PredictionOut(_Out):
    target_quarter: str
    predicted_sales: int
    previous_sales: int | None = None
    model: PredictionModelOut
    generated_at: datetime


class RegionSalesOut(_Out):
    region: RegionOut
    industry: IndustryCategory
    current: SalesCurrentOut | None = None
    prediction: PredictionOut | None = None


class SalesHistoryItem(_Out):
    quarter: str
    total_sales: int


class SalesHistoryOut(_Out):
    region_id: int
    industry: IndustryCategory
    series: list[SalesHistoryItem] = Field(default_factory=list)


class IngestRequest(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True)

    region_ids: list[int] | None = None
    quarters: list[str] | None = None
    industries: list[IndustryCategory] | None = None
    source: str = "OA-15572"


class IngestResponse(_Out):
    source: str
    quarters: list[str]
    industries: list[str]
    processed_rows: int
    accepted_rows: int
    upserted_rows: int
    failed_rows: int
    deduped_rows: int = 0
    negative_rows: int = 0
    errors: list[dict] = Field(default_factory=list)
