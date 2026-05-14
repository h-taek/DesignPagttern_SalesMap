from fastapi import APIRouter, Depends

from app.api.deps import sales_service
from app.schemas import RegionOut
from app.services.sales import SalesService

router = APIRouter(prefix="/api/regions", tags=["regions"])


@router.get("", response_model=list[RegionOut])
def list_regions(service: SalesService = Depends(sales_service)) -> list[RegionOut]:
    return [RegionOut.model_validate(r) for r in service.list_regions()]
