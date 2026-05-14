import uuid

import structlog
from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from app.api import predict as predict_api
from app.core.logging import configure_logging, get_logger

configure_logging()
log = get_logger("ai")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-Id") or str(uuid.uuid4())
        structlog.contextvars.clear_contextvars()
        structlog.contextvars.bind_contextvars(
            request_id=request_id,
            n8n_execution_id=request.headers.get("X-N8n-Execution-Id"),
            service="ai",
        )
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


app = FastAPI(title="SalesMap AI", version="0.1.0")
app.add_middleware(RequestIdMiddleware)
app.include_router(predict_api.router)


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "service": "ai"}
