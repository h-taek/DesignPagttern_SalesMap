from fastapi import APIRouter, Depends, Query

from app.api.deps import sales_service
from app.schemas import IndustryCategory, RegionSalesOut, SalesHistoryOut
from app.services.sales import SalesService

router = APIRouter(prefix="/api/regions", tags=["sales"])


@router.get("/{region_id}/sales", response_model=RegionSalesOut)
def get_region_sales(
    region_id: int,
    industry: IndustryCategory = Query(default="food"),
    service: SalesService = Depends(sales_service),
) -> RegionSalesOut:
    return service.get_region_sales(region_id, industry)


@router.get("/{region_id}/sales/history", response_model=SalesHistoryOut)
def get_sales_history(
    region_id: int,
    industry: IndustryCategory = Query(default="food"),
    quarters: int = Query(default=8, ge=1, le=20),
    service: SalesService = Depends(sales_service),
) -> SalesHistoryOut:
    return service.get_sales_history(region_id, industry, quarters)
