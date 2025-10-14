from typing import Annotated

from fastapi import Depends, Query
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from app.config.config import URL_DATABASE

engine = create_engine(URL_DATABASE, pool_size=20, max_overflow=0)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


class Pagination:
    def __init__(
        self,
        page: int = Query(1, ge=1),
        size: int = Query(10, ge=1, le=100),
    ):
        self.page = page
        self.size = size
        self.offset = (page - 1) * size


def get_pagination(pagination: Pagination = Depends()) -> Pagination:
    return pagination
