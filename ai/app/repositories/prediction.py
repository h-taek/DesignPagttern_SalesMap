from sqlalchemy.orm import Session

from app.models import PredictionRecord


class PredictionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save(
        self,
        *,
        region_id: int,
        industry: str,
        target_quarter: str,
        predicted_sales: int,
        previous_sales: int | None,
        model_slope: float | None,
        model_intercept: float | None,
        samples_used: int,
    ) -> PredictionRecord:
        """예측 결과를 새 row로 누적 저장 (이력 보존).

        사용자 조회는 generated_at DESC LIMIT 1 로 최신 한 건만 본다.
        """
        row = PredictionRecord(
            region_id=region_id,
            industry_category=industry,
            target_quarter=target_quarter,
            predicted_sales=predicted_sales,
            previous_sales=previous_sales,
            model_slope=model_slope,
            model_intercept=model_intercept,
            samples_used=samples_used,
        )
        self.session.add(row)
        self.session.flush()
        return row

    def commit(self) -> None:
        self.session.commit()
