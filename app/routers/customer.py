from fastapi import APIRouter, HTTPException
from ..database import db_dependency
from ..schemas import CustomerBase, UpdateCustomer
import models

router= APIRouter(
    prefix= '/customer',
    tags= ["customer"],
    responses= {404: {"description": "Not found"}}
    )

@router.get("/")
async def root_customer():
    return {"message": "This is the root of customer."}

@router.post("/")
async def add_customer(customer: CustomerBase, db: db_dependency):
    new_customer= models.Customers(
        email= customer.email,
        phone= customer.phone,
        address= customer.address,
        company_name= customer.company_name,
        tax_id= customer.tax_id
    )
    print(new_customer)
    db.add(new_customer)
    db.commit()
    return {"message": "New Customer account successfully created."}