from collections.abc import Iterator

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.core.security import require_internal_token
from app.db import get_session
from app.predictor.base import NotEnoughData
from app.schemas import (
    CellError,
    ModelParamsOut,
    PredictBatchRequest,
    PredictBatchResponse,
    PredictSingleRequest,
    PredictSingleResponse,
    TrainedOnOut,
)
from app.services.predict import PredictionGenerateService, utcnow

router = APIRouter(prefix="/predict", tags=["predict"])


def db_session() -> Iterator[Session]:
    yield from get_session()


@router.post(
    "/batch",
    response_model=PredictBatchResponse,
    dependencies=[Depends(require_internal_token)],
)
def predict_batch(
    body: PredictBatchRequest,
    response: Response,
    session: Session = Depends(db_session),
) -> PredictBatchResponse:
    service = PredictionGenerateService(session)
    result = service.run_batch(
        region_ids=body.region_ids,
        industries=body.industries,
        target_quarter=body.target_quarter,
        lookback=body.lookback_quarters,
    )
    if result.failed > 0:
        response.status_code = status.HTTP_207_MULTI_STATUS
    return PredictBatchResponse(
        target_quarter=result.target_quarter,
        processed_cells=result.processed,
        succeeded_cells=result.succeeded,
        failed_cells=result.failed,
        generated_at=utcnow(),
        errors=[
            CellError(region_id=f.region_id, industry=f.industry, reason=f.reason)
            for f in result.failures
        ],
    )


@router.post(
    "/{region_id}",
    response_model=PredictSingleResponse,
    dependencies=[Depends(require_internal_token)],
)
def predict_single(
    region_id: int,
    body: PredictSingleRequest,
    session: Session = Depends(db_session),
) -> PredictSingleResponse:
    service = PredictionGenerateService(session)
    try:
        cell = service.predict_cell(
            region_id, body.industry, body.target_quarter, body.lookback_quarters
        )
    except NotEnoughData as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "NO_SALES_DATA", "message": str(e)}},
        ) from e

    service.pred_repo.save(
        region_id=cell.region_id,
        industry=cell.industry,
        target_quarter=cell.target_quarter,
        predicted_sales=cell.predicted_sales,
        previous_sales=cell.previous_sales,
        model_slope=cell.slope,
        model_intercept=cell.intercept,
        samples_used=cell.samples_used,
    )
    service.pred_repo.commit()

    return PredictSingleResponse(
        region_id=cell.region_id,
        industry=cell.industry,  # type: ignore[arg-type]
        target_quarter=cell.target_quarter,
        predicted_sales=cell.predicted_sales,
        model=ModelParamsOut(slope=cell.slope, intercept=cell.intercept),
        trained_on=TrainedOnOut(
            from_quarter=cell.from_quarter,
            to_quarter=cell.to_quarter,
            samples=cell.samples_used,
        ),
    )
