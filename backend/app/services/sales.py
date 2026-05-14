from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models import Region
from app.repositories.prediction import PredictionRepository
from app.repositories.sales import SalesRepository
from app.schemas import (
    IndustryCategory,
    PredictionModelOut,
    PredictionOut,
    RegionOut,
    RegionSalesOut,
    SalesCurrentOut,
    SalesHistoryItem,
    SalesHistoryOut,
)


def _not_found(code: str, message: str, http_status: int = status.HTTP_404_NOT_FOUND) -> HTTPException:
    return HTTPException(
        status_code=http_status,
        detail={"error": {"code": code, "message": message}},
    )


class SalesService:
    def __init__(self, session: Session) -> None:
        self.sales = SalesRepository(session)
        self.predictions = PredictionRepository(session)

    def list_regions(self) -> list[Region]:
        return self.sales.list_regions()

    def get_region_sales(self, region_id: int, industry: IndustryCategory) -> RegionSalesOut:
        region = self.sales.find_region(region_id)
        if region is None:
            raise _not_found("REGION_NOT_FOUND", f"regionId={region_id} not found")

        latest = self.sales.find_latest(region_id, industry)
        if latest is None:
            raise _not_found(
                "NO_SALES_DATA",
                f"no sales for region={region_id} industry={industry}",
                http_status=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )

        prediction_row = self.predictions.find_latest(region_id, industry)
        prediction_out = (
            PredictionOut(
                target_quarter=prediction_row.target_quarter,
                predicted_sales=prediction_row.predicted_sales,
                previous_sales=prediction_row.previous_sales,
                model=PredictionModelOut(
                    slope=prediction_row.model_slope,
                    intercept=prediction_row.model_intercept,
                    samples_used=prediction_row.samples_used,
                ),
                generated_at=prediction_row.generated_at,
            )
            if prediction_row is not None
            else None
        )

        return RegionSalesOut(
            region=RegionOut.model_validate(region),
            industry=industry,
            current=SalesCurrentOut(
                quarter=latest.quarter,
                total_sales=latest.total_sales,
                total_count=latest.total_count,
            ),
            prediction=prediction_out,
        )

    def get_sales_history(
        self, region_id: int, industry: IndustryCategory, quarters: int
    ) -> SalesHistoryOut:
        if self.sales.find_region(region_id) is None:
            raise _not_found("REGION_NOT_FOUND", f"regionId={region_id} not found")
        rows = self.sales.find_quarters(region_id, industry, quarters)
        series = [SalesHistoryItem(quarter=r.quarter, total_sales=r.total_sales) for r in rows]
        return SalesHistoryOut(region_id=region_id, industry=industry, series=series)
