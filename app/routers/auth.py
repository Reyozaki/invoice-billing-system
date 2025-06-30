from fastapi import APIRouter, HTTPException, Depends, status, Security
from datetime import datetime, timedelta
from jose import jwt, JWTError   #type:ignore
from passlib.context import CryptContext    #type:ignore
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer    #type:ignore
from typing import Annotated
from pydantic import BaseModel  #type: ignore

from ..database import db_dependency
from ..schemas import UpdateCustomer, CustomerBase
from app.config import ALGORITHM, SECRET_KEY, ADMIN_KEY
import models

router= APIRouter(
    prefix= '/auth',    
    tags= ["auth"],
    responses= {404: {"description": "Not found"}}
)

bcrypt_context= CryptContext(schemes= ['bcrypt'], deprecated= 'auto')
customer_oauth2_bearer= OAuth2PasswordBearer(tokenUrl= 'auth/token', scheme_name= "CustomerToken")
admin_oauth2_bearer= OAuth2PasswordBearer(tokenUrl= 'auth/atoken', scheme_name= "AdminToken")

class Token(BaseModel):
    access_token: str
    token_type: str


@router.post("/token", response_model= Token)
async def login_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                             db: db_dependency):
    customer= authenticate_customer(form_data.username, form_data.password, db)
    if not customer:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, 
                            detail= "Could not validate Customer.")
    token= create_customer_token(customer.company_name, customer.customer_id, timedelta(minutes= 60))
    return {"access_token": token, "token_type": 'bearer'}

@router.post("/atoken", response_model= Token)
async def adimn_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                             db: db_dependency):
    user= authenticate_admin(form_data.username, form_data.password, db)
    if not user:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, 
                            detail= "Could not validate Admin.")
    token= create_admin_token(user.username, user.admin_id, timedelta(hours= 2))
    return {"access_token": token, "token_type": 'bearer'}


def create_customer_token(company_name: str, customer_id: int, expires_in: timedelta):
    encode= {'sub': company_name, 'id': company_name}
    expires= datetime.now() + expires_in
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm= ALGORITHM)

def create_admin_token(username: str, admin_id: int, expires_in: timedelta):
    encode= {'sub': username, 'id': admin_id}
    expires= datetime.now() + expires_in
    encode.update({'exp': expires})
    return jwt.encode(encode, ADMIN_KEY, algorithm= ALGORITHM)


def authenticate_customer(name: str, password: str, db):
    customer= db.query(models.Customers).filter(models.Customers.company_name== name).first()
    if not customer:
        return False
    if not bcrypt_context.verify(password, customer.password):
        return False
    return customer

def authenticate_admin(username: str, password: str, db):
    admin= db.query(models.Admin).filter(models.Admin.username== username).first()
    if not admin:
        return False
    if not bcrypt_context.verify(password, admin.password):
        return False
    return admin


async def get_current_customer(token: Annotated[str, Security(customer_oauth2_bearer)]):
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        company_name: str= payload.get('sub')
        customer_id: int= payload.get('id')
        if company_name is None or customer_id is None:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, 
                                detail= "Customer could not be validated.")
        return {'company_name': company_name, 'id': customer_id}
    except JWTError:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, 
                            detail= "Customer could not be validated.")

async def get_current_admin(token: Annotated[str, Security(admin_oauth2_bearer)]):
    try:
        payload= jwt.decode(token, ADMIN_KEY, algorithms=[ALGORITHM])
        username: str= payload.get('sub')
        admin_id: int= payload.get('id')
        if username is None or admin_id is None:
            raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, 
                                detail= "Customer could not be validated.")
        return {'company_name': username, 'id': admin_id}
    except JWTError:
        raise HTTPException(status_code= status.HTTP_401_UNAUTHORIZED, 
                            detail= "User could not be validated.")


customer_dependency= Annotated[dict, Security(get_current_customer)]
admin_dependency= Annotated[dict, Security(get_current_admin)]
