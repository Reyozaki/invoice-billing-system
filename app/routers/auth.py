from fastapi import APIRouter, HTTPException, Depends
from datetime import datetime, timedelta
from sqlalchemy.orm import Session  #type:ignore
# from jose import jwt, JWTError   #type:ignore
# from passlib.context import CryptContext    #type:ignore
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer    #type:ignore
from starlette import status    #type:ignore
from typing import Annotated
from pydantic import BaseModel  #type: ignore

from ..database import SessionLocal, db_dependency
from ..schemas import Customer
import models

router= APIRouter(
    prefix= '/auth',    
    tags= ["auth"],
    responses= {404: {"description": "Not found"}}
)