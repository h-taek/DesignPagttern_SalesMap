import statistics
from dataclasses import dataclass
from datetime import datetime, timezone

import structlog
from sqlalchemy.orm import Session

from app import quarter as q
from app.core.config import settings
from app.predictor.base import NotEnoughData
from app.predictor.factory import create_predictor
from app.repositories.prediction import PredictionRepository
from app.repositories.sales import SalesRepository
from app.schemas import IndustryCategory

log = structlog.get_logger("ai.predict")

_INDUSTRIES: list[IndustryCategory] = ["food", "service", "retail"]


@dataclass
class CellPrediction:
    region_id: int
    industry: str
    target_quarter: str
    predicted_sales: int
    previous_sales: int | None
    slope: float | None
    intercept: float | None
    samples_used: int
    from_quarter: str
    to_quarter: str


@dataclass
class CellFailure:
    region_id: int
    industry: str
    reason: str


@dataclass
class BatchResult:
    target_quarter: str
    processed: int
    succeeded: int
    failed: int
    failures: list[CellFailure]


class PredictionGenerateService:
    """셀(region × industry) 단위 선형회귀 예측 생성.

    predictor는 Factory로 생성된 Strategy 객체. 셀마다 새 인스턴스를 만들어
    학습 상태가 섞이지 않게 한다.
    """

    def __init__(self, session: Session, predictor_name: str | None = None) -> None:
        self.session = session
        self.sales_repo = SalesRepository(session)
        self.pred_repo = PredictionRepository(session)
        self.predictor_name = predictor_name or settings.predictor

    def predict_cell(
        self,
        region_id: int,
        industry: str,
        target_quarter: str | None,
        lookback: int,
    ) -> CellPrediction:
        records = self.sales_repo.find_quarters(region_id, industry, lookback)
        if len(records) < 2:
            raise NotEnoughData(f"need >= 2 quarters, got {len(records)}")

        quarters = [r.quarter for r in records]
        sales = [r.total_sales for r in records]
        raw_n = len(records)
        quarters, sales, filled = _forward_fill_quarters(quarters, sales)
        sales, clipped = _clip_outliers_iqr(sales)
        if filled or clipped:
            log.info(
                "preprocess_applied",
                region_id=region_id,
                industry=industry,
                raw_samples=raw_n,
                final_samples=len(sales),
                filled_quarters=filled,
                clipped_values=clipped,
            )

        xs = [q.to_index(qq) for qq in quarters]
        ys = sales

        # target_quarter 미지정 시 최신 분기의 다음 분기
        latest_q = quarters[-1]
        tq = target_quarter or q.next_quarter(latest_q)

        predictor = create_predictor(self.predictor_name)
        predictor.train(xs, ys)
        predicted = predictor.predict(q.to_index(tq))
        params = predictor.params()

        return CellPrediction(
            region_id=region_id,
            industry=industry,
            target_quarter=tq,
            predicted_sales=max(int(round(predicted)), 0),
            previous_sales=records[-1].total_sales,
            slope=params.get("slope"),
            intercept=params.get("intercept"),
            samples_used=len(records),
            from_quarter=records[0].quarter,
            to_quarter=latest_q,
        )

    def run_batch(
        self,
        region_ids: list[int] | None,
        industries: list[str] | None,
        target_quarter: str | None,
        lookback: int,
    ) -> BatchResult:
        regions = region_ids or self.sales_repo.list_region_ids()
        inds = industries or list(_INDUSTRIES)

        processed = succeeded = failed = 0
        failures: list[CellFailure] = []
        resolved_target = target_quarter or ""

        for region_id in regions:
            for industry in inds:
                processed += 1
                try:
                    cell = self.predict_cell(region_id, industry, target_quarter, lookback)
                except NotEnoughData as e:
                    failed += 1
                    failures.append(CellFailure(region_id, industry, f"NO_SALES_DATA:{e}"))
                    continue
                except Exception as e:  # noqa: BLE001 - 셀 단위 격리
                    failed += 1
                    failures.append(CellFailure(region_id, industry, f"ERROR:{e}"))
                    continue

                self.pred_repo.save(
                    region_id=cell.region_id,
                    industry=cell.industry,
                    target_quarter=cell.target_quarter,
                    predicted_sales=cell.predicted_sales,
                    previous_sales=cell.previous_sales,
                    model_slope=cell.slope,
                    model_intercept=cell.intercept,
                    samples_used=cell.samples_used,
                )
                resolved_target = cell.target_quarter
                succeeded += 1

        self.pred_repo.commit()
        return BatchResult(
            target_quarter=resolved_target or (target_quarter or "unknown"),
            processed=processed,
            succeeded=succeeded,
            failed=failed,
            failures=failures,
        )


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _forward_fill_quarters(
    quarters: list[str], sales: list[int]
) -> tuple[list[str], list[int], int]:
    """records 사이에 빠진 분기를 직전 값으로 채워 연속 시계열로 만든다.

    Returns: (quarters, sales, filled_count)
    """
    if len(quarters) < 2:
        return quarters, sales, 0
    start_idx = q.to_index(quarters[0])
    end_idx = q.to_index(quarters[-1])
    known = {q.to_index(qq): v for qq, v in zip(quarters, sales)}
    out_q: list[str] = []
    out_v: list[int] = []
    filled = 0
    last_val = sales[0]
    for i in range(start_idx, end_idx + 1):
        out_q.append(q.from_index(i))
        if i in known:
            last_val = known[i]
        else:
            filled += 1
        out_v.append(last_val)
    return out_q, out_v, filled


def _clip_outliers_iqr(values: list[int], k: float = 1.5) -> tuple[list[int], int]:
    """튜키 IQR 기준 outlier를 [Q1 - k·IQR, Q3 + k·IQR] 경계로 clip.

    표본이 8개 미만이거나 IQR이 0이면 분위수 추정이 불안정해 패스.
    Returns: (clipped_values, clipped_count)
    """
    n = len(values)
    if n < 8:
        return values, 0
    q1, _, q3 = statistics.quantiles(values, n=4)
    iqr = q3 - q1
    if iqr == 0:
        return values, 0
    lo = q1 - k * iqr
    hi = q3 + k * iqr
    clipped = sum(1 for v in values if v < lo or v > hi)
    return [int(round(min(max(v, lo), hi))) for v in values], clipped
