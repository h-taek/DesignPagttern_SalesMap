from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Region, SalesRecord


class SalesRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_regions(self) -> list[Region]:
        stmt = select(Region).order_by(Region.region_id)
        return list(self.session.scalars(stmt).all())

    def find_region(self, region_id: int) -> Region | None:
        return self.session.get(Region, region_id)

    def find_latest(self, region_id: int, industry: str) -> SalesRecord | None:
        stmt = (
            select(SalesRecord)
            .where(SalesRecord.region_id == region_id, SalesRecord.industry_category == industry)
            .order_by(SalesRecord.quarter.desc())
            .limit(1)
        )
        return self.session.scalars(stmt).first()

    def find_quarters(self, region_id: int, industry: str, n: int) -> list[SalesRecord]:
        stmt = (
            select(SalesRecord)
            .where(SalesRecord.region_id == region_id, SalesRecord.industry_category == industry)
            .order_by(SalesRecord.quarter.desc())
            .limit(n)
        )
        rows = list(self.session.scalars(stmt).all())
        rows.reverse()
        return rows
