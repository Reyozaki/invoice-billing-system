from app.config import URL_DATABASE
from fastapi import FastAPI, Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, declarative_base # type: ignore
from typing import Annotated

engine= create_engine(URL_DATABASE, pool_size=20, max_overflow=0)

SessionLocal= sessionmaker(autocommit= False, autoflush= False, bind= engine)

Base= declarative_base()

def get_db():
    db= SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
db_dependency= Annotated[Session, Depends(get_db)]