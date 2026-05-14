import uuid

import structlog
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import ingest as ingest_api
from app.api import regions as regions_api
from app.api import sales as sales_api
from app.core.config import settings
from app.core.logging import configure_logging

configure_logging()


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            n8n_execution_id=request.headers.get("X-N8n-Execution-Id"),
            service="backend",
        )
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


app = FastAPI(title="SalesMap Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestIdMiddleware)

app.include_router(regions_api.router)
app.include_router(sales_api.router)
app.include_router(ingest_api.router)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "backend"}
