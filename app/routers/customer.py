from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy.orm import load_only
from pydantic import BaseModel, EmailStr
from typing import Dict

from ..database import db_dependency
from ..schemas import CustomerBase, UpdateCustomer
from models import Customers
from .auth import bcrypt_context, customer_dependency

router= APIRouter(
    prefix= '/customer',
    tags= ["customer"],
    responses= {404: {"description": "Not found"}}
    )


@router.get("/")
async def view_profile(customer: customer_dependency, db: db_dependency, 
                       current_customer: int= Query(...)):
    return db.query(Customers).options(load_only(
        Customers.company_name,
        Customers.address,
        Customers.tax_id,
        Customers.phone,
        Customers.email,
        )).filter(Customers.customer_id == current_customer).first()

@router.post("/")
async def add_customer(customer: CustomerBase, db: db_dependency):
    existing_customer= db.query(Customers).filter(Customers.company_name == customer.company_name).first()
    if existing_customer:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Customer of that name already exist.")
        
    new_customer= Customers(
        email= customer.email,
        phone= customer.phone,
        address= customer.address,
        company_name= customer.company_name,
        tax_id= customer.tax_id,
        password= bcrypt_context.hash(customer.password)
    )
    print(new_customer)
    db.add(new_customer)
    db.commit()
    return {"message": "New Customer account successfully created."}

@router.put("/edit-profile")
async def update_profile(update_customer: UpdateCustomer, db: db_dependency, customer: customer_dependency,
                         current_customer: int= Query(...)):
    existing_customer= db.query(Customers).filter(Customers.customer_id == current_customer).first()
    if not existing_customer:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Customer of that ID does not exist.")
    
    update_count= 0
    if update_customer.email is not None:
        existing_customer.email= update_customer.email
        update_count += 1
    if update_customer.phone is not None:
        existing_customer.phone= update_customer.phone
        update_count += 1
    if update_customer.address is not None:
        existing_customer.address= update_customer.address
        update_count += 1
    if update_customer.company_name is not None:
        existing_customer.company_name= update_customer.company_name
        update_count += 1 
    if update_customer.tax_id is not None:
        existing_customer.tax_id= update_customer.tax_id
        update_count += 1          
    if update_customer.password is not None:
        existing_customer.password= bcrypt_context.hash(update_customer.password)
        update_count += 1   
        
    if update_count== 0:
        raise HTTPException(status_code= 400,detail= "Please update at least one detail.")
    db.commit()
    db.refresh(existing_customer)
    if update_count== 1:
        return {"message": f"{update_count} Customer detail successfully updated."}
    return {"message": f"{update_count} Customer details successfully updated."}