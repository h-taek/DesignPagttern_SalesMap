from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Region, SalesRecord


class SalesRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_region_ids(self) -> list[int]:
        return list(self.session.scalars(select(Region.region_id).order_by(Region.region_id)).all())

    def find_quarters(self, region_id: int, industry: str, lookback: int) -> list[SalesRecord]:
        """최근 lookback개 분기를 오래된 순으로 반환."""
        stmt = (
            select(SalesRecord)
            .where(SalesRecord.region_id == region_id, SalesRecord.industry_category == industry)
            .order_by(SalesRecord.quarter.desc())
            .limit(lookback)
        )
        rows = list(self.session.scalars(stmt).all())
        rows.reverse()
        return rows
