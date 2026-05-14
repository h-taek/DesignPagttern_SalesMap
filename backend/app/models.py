from datetime import datetime

from sqlalchemy import BigInteger, DateTime, Float, ForeignKey, Integer, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Region(Base):
    __tablename__ = "region"

    region_id: Mapped[int] = mapped_column(Integer, primary_key=True)
    region_name: Mapped[str] = mapped_column(String(20), nullable=False)
    sgg_code: Mapped[str] = mapped_column(String(5), unique=True, nullable=False)


class RegionDongMap(Base):
    __tablename__ = "region_dong_map"

    dong_code: Mapped[str] = mapped_column(String(10), primary_key=True)
    dong_name: Mapped[str] = mapped_column(String(40), nullable=False)
    region_id: Mapped[int] = mapped_column(Integer, ForeignKey("region.region_id"), nullable=False)


class RegionTrdarMap(Base):
    """상권코드(OA-15560) → 자치구. OA-15572는 자치구 컬럼 없이 TRDAR_CD만 주므로 필요."""

    __tablename__ = "region_trdar_map"

    trdar_code: Mapped[str] = mapped_column(String(7), primary_key=True)
    region_id: Mapped[int] = mapped_column(Integer, ForeignKey("region.region_id"), nullable=False)


class SalesRecord(Base):
    __tablename__ = "sales_record"
    __table_args__ = (
        UniqueConstraint("region_id", "quarter", "industry_category", name="uq_sales_region_quarter_industry"),
    )

    sales_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    region_id: Mapped[int] = mapped_column(Integer, ForeignKey("region.region_id"), nullable=False)
    quarter: Mapped[str] = mapped_column(String(6), nullable=False)
    industry_category: Mapped[str] = mapped_column(String(10), nullable=False)
    total_sales: Mapped[int] = mapped_column(BigInteger, nullable=False)
    total_count: Mapped[int | None] = mapped_column(BigInteger)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class PredictionRecord(Base):
    __tablename__ = "prediction_record"

    prediction_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    region_id: Mapped[int] = mapped_column(Integer, ForeignKey("region.region_id"), nullable=False)
    industry_category: Mapped[str] = mapped_column(String(10), nullable=False)
    target_quarter: Mapped[str] = mapped_column(String(6), nullable=False)
    predicted_sales: Mapped[int] = mapped_column(BigInteger, nullable=False)
    previous_sales: Mapped[int | None] = mapped_column(BigInteger)
    model_slope: Mapped[float | None] = mapped_column(Float)
    model_intercept: Mapped[float | None] = mapped_column(Float)
    samples_used: Mapped[int | None] = mapped_column(Integer)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
