from collections.abc import Iterable
from typing import TypedDict

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.orm import Session

from app.models import Region, RegionDongMap, SalesRecord


class SalesRow(TypedDict):
    region_id: int
    quarter: str
    industry_category: str
    total_sales: int
    total_count: int | None


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

    def upsert_many(self, rows: Iterable[SalesRow]) -> int:
        payload = list(rows)
        if not payload:
            return 0
        stmt = pg_insert(SalesRecord).values(payload)
        stmt = stmt.on_conflict_do_update(
            index_elements=["region_id", "quarter", "industry_category"],
            set_={
                "total_sales": stmt.excluded.total_sales,
                "total_count": stmt.excluded.total_count,
            },
        )
        result = self.session.execute(stmt)
        self.session.commit()
        rowcount = result.rowcount
        return rowcount if rowcount is not None and rowcount >= 0 else len(payload)

    def list_region_sgg(self) -> dict[str, int]:
        rows = self.session.scalars(select(Region)).all()
        return {r.sgg_code: r.region_id for r in rows}

    def list_dong_map(self) -> dict[str, int]:
        rows = self.session.scalars(select(RegionDongMap)).all()
        return {r.dong_code: r.region_id for r in rows}
