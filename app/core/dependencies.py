from collections.abc import Generator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from .database import SessionLocal


def get_db() -> Generator[Session, None, None]:
    with SessionLocal() as db:
        yield db


SessionDep = Annotated[Session, Depends(get_db)]
