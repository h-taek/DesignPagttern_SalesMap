from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app import quarter as q
from app.core.config import settings
from app.predictor.base import NotEnoughData
from app.predictor.factory import create_predictor
from app.repositories.prediction import PredictionRepository
from app.repositories.sales import SalesRepository
from app.schemas import IndustryCategory

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

        xs = [q.to_index(r.quarter) for r in records]
        ys = [r.total_sales for r in records]

        # target_quarter 미지정 시 최신 분기의 다음 분기
        latest_q = records[-1].quarter
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
