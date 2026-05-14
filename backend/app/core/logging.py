import logging
from pathlib import Path
import structlog

_LOG_FILE = Path(__file__).resolve().parents[2] / "app.log"

def configure_logging() -> None:
    # 워크스페이스 내 파일로도 로그 저장 (에이전트가 읽을 수 있도록)
    file_handler = logging.FileHandler(_LOG_FILE)
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    
    logging.basicConfig(
        level=logging.INFO, 
        format="%(message)s",
        handlers=[logging.StreamHandler(), file_handler]
    )
    
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso", utc=True),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str | None = None) -> structlog.stdlib.BoundLogger:
    return structlog.get_logger(name or "backend")
