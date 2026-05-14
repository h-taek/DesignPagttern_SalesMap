from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

IndustryCategory = Literal["food", "service", "retail"]


def _to_camel(s: str) -> str:
    head, *rest = s.split("_")
    return head + "".join(w.capitalize() for w in rest)


class _Camel(BaseModel):
    model_config = ConfigDict(alias_generator=_to_camel, populate_by_name=True, from_attributes=True)


class PredictBatchRequest(_Camel):
    region_ids: list[int] | None = None
    industries: list[IndustryCategory] | None = None
    target_quarter: str | None = None
    lookback_quarters: int = Field(default=16, ge=2, le=40)


class CellError(_Camel):
    region_id: int
    industry: str
    reason: str


class PredictBatchResponse(_Camel):
    target_quarter: str
    processed_cells: int
    succeeded_cells: int
    failed_cells: int
    generated_at: datetime
    errors: list[CellError] = Field(default_factory=list)


class PredictSingleRequest(_Camel):
    industry: IndustryCategory = "food"
    target_quarter: str | None = None
    lookback_quarters: int = Field(default=16, ge=2, le=40)


class ModelParamsOut(_Camel):
    slope: float | None = None
    intercept: float | None = None


class TrainedOnOut(_Camel):
    from_quarter: str
    to_quarter: str
    samples: int


class PredictSingleResponse(_Camel):
    region_id: int
    industry: IndustryCategory
    target_quarter: str
    predicted_sales: int
    model: ModelParamsOut
    trained_on: TrainedOnOut
