from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import PredictionRecord


class PredictionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def find_latest(self, region_id: int, industry: str) -> PredictionRecord | None:
        stmt = (
            select(PredictionRecord)
            .where(
                PredictionRecord.region_id == region_id,
                PredictionRecord.industry_category == industry,
            )
            .order_by(
                PredictionRecord.target_quarter.desc(),
                PredictionRecord.generated_at.desc(),
            )
            .limit(1)
        )
        return self.session.scalars(stmt).first()
