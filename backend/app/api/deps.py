from collections.abc import Iterator

from fastapi import Depends
from sqlalchemy.orm import Session

from app.db import get_session
from app.services.sales import SalesService


def db_session() -> Iterator[Session]:
    yield from get_session()


def sales_service(session: Session = Depends(db_session)) -> SalesService:
    return SalesService(session)
