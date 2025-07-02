from fastapi import APIRouter, HTTPException, Query, status
from datetime import datetime, timedelta
from sqlalchemy.orm import load_only
from typing import Annotated
from pydantic import BaseModel  #type: ignore

from ..database import db_dependency
from ..schemas import UpdateCustomer, Admin, Products, UpdateProduct
import models
from ..routers.auth import bcrypt_context, admin_perm

router= APIRouter(
    prefix= '/admin',    
    tags= ["admin"],
    responses= {404: {"description": "Not found"}}
)

@router.get("/")
async def admin_dashboard(db: db_dependency, admin: admin_perm):
    return db.query(models.Admin).options(load_only(models.Admin.username)).all()
    
@router.post("/")
async def add_admin(admin: Admin, db: db_dependency):
    existing_admin= db.query(models.Admin).filter(models.Admin.username == admin.username).first()
    if existing_admin:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, 
                            detail= "Admin of that username already exist.")
    hashed_password= bcrypt_context.hash(admin.password)
    
    new_user= models.Users(
        username= admin.username,
        password= hashed_password,
        role= "admin"
    )
    db.add(new_user)
    db.flush()
    
    new_admin= models.Admin(
        user_id= new_user.user_id,
        username= admin.username,
        password= hashed_password
    )
    print(new_admin)
    db.add(new_admin)
    db.commit()
    return {"message": "New Admin successfully created."}


@router.delete("/delete-customer")
async def delete_customer(admin: admin_perm, db: db_dependency, 
                          customer_id: int= Query(...)):
    existing_customer= db.query(models.Customers).filter(models.Customers.customer_id == customer_id).first()
    if not existing_customer:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Customer of that ID does not exist.")
    else:
        db.delete(existing_customer)
        db.commit()
        return {f"Customer ID: {customer_id}<br> Customer: {existing_customer.company_name}<br> Has been deleted."}
    

@router.post("/add-product")
async def add_product(admin: admin_perm, product: Products, db: db_dependency):
    existing_product= db.query(models.Products).filter(models.Products.name == product.name).first()
    if existing_product:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, 
                            detail= "Product of that name already exist.")
    new_product= models.Products(
        name= product.name,
        unit_price= product.unit_price,
        tax_percent= product.tax_percent,
        description= product.description
    )
    print(new_product)
    db.add(new_product)
    db.commit()
    return {"message": f"New product added: {product.name}."}

@router.delete("/delete-product")
async def delete_product(admin: admin_perm, db: db_dependency, 
                          product_id: int= Query(...)):
    existing_product= db.query(models.Products).filter(models.Products.product_id == product_id).first()
    if not existing_product:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Product of that ID does not exist.")
    else:
        db.delete(existing_product)
        db.commit()
        return {f"Product ID: {product_id}<br> Product: {existing_product.name}<br> Has been deleted."}