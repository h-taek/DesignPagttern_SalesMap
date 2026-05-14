import httpx
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.api.deps import db_session
from app.core.security import require_internal_token
from app.schemas import IngestRequest, IngestResponse
from app.services.ingest.service import SalesIngestService

router = APIRouter(prefix="/api/ingest", tags=["ingest"])


@router.post(
    "/sales",
    response_model=IngestResponse,
    dependencies=[Depends(require_internal_token)],
)
def ingest_sales(
    body: IngestRequest,
    response: Response,
    session: Session = Depends(db_session),
) -> IngestResponse:
    service = SalesIngestService(session)
    try:
        result = service.run(
            quarters=body.quarters,
            region_ids=body.region_ids,
            industries=body.industries,
            source=body.source,
        )
    except (RuntimeError, httpx.HTTPError) as e:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail={"error": {"code": "UPSTREAM_API_ERROR", "message": str(e)}},
        ) from e
    if result.failed_rows > 0:
        response.status_code = status.HTTP_207_MULTI_STATUS
    return IngestResponse.model_validate(result, from_attributes=True)
