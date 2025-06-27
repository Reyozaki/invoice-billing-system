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
from ..schemas import UpdateCustomer, CustomerBase
import models

router= APIRouter(
    prefix= '/auth',    
    tags= ["auth"],
    responses= {404: {"description": "Not found"}}
)

@router.put("/customer/{customer_id}")
async def update_customer(customer: UpdateCustomer, db: db_dependency):
    if customer:
        update_customer= models.Customers(
            email= customer.email,
            phone= customer.phone,
            address= customer.address,
            company_name= customer.company_name,
            tax_id= customer.tax_id
        )
    else:
        return {"message": "Please update at least one value."}
    
    print(update_customer)
    db.add(update_customer)
    db.commit()
    return {"message": "New Customer account successfully created."}

@router.delete("/customer/{customer_id}")
async def delete_customer(customer: CustomerBase, db: db_dependency):
    pass