from fastapi import APIRouter, HTTPException, Query, status
from datetime import datetime, timedelta
from jose import jwt, JWTError   #type:ignore
from passlib.context import CryptContext    #type:ignore
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer    #type:ignore
from typing import Annotated
from pydantic import BaseModel  #type: ignore

from ..database import db_dependency
from ..schemas import UpdateCustomer, Admin, Products, UpdateProduct
import models
from ..routers.auth import bcrypt_context, admin_dependency

router= APIRouter(
    prefix= '/admin',    
    tags= ["admin"],
    responses= {404: {"description": "Not found"}}
)


@router.post("/")
async def add_admin(admin: Admin, db: db_dependency):
    existing_admin= db.query(models.Admin).filter(models.Admin.username == admin.username).first()
    if existing_admin:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Admin of that username already exist.")
    new_admin= models.Admin(
        username= admin.username,
        password= bcrypt_context.hash(admin.password)
    )
    print(new_admin)
    db.add(new_admin)
    db.commit()
    return {"message": "New Admin successfully created."}


@router.put("/edit-customer")
async def update_customer(admin: admin_dependency, current_customer: UpdateCustomer, db: db_dependency, 
                          customerid: int= Query(...)):
    existing_customer= db.query(models.Customers).filter(models.Customers.customer_id == customerid).first()
    if not existing_customer:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Customer of that ID does not exist.")
    
    update_count= 0
    if current_customer.email is not None:
        existing_customer.email= current_customer.email
        update_count += 1
    if current_customer.phone is not None:
        existing_customer.phone= current_customer.phone
        update_count += 1
    if current_customer.address is not None:
        existing_customer.address= current_customer.address
        update_count += 1
    if current_customer.company_name is not None:
        existing_customer.company_name= current_customer.company_name
        update_count += 1 
    if current_customer.tax_id is not None:
        existing_customer.tax_id= current_customer.tax_id
        update_count += 1
    if current_customer.password is not None:
        existing_customer.password= bcrypt_context.hash(current_customer.password)
        update_count += 1             
        
    if update_count== 0:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= "Please update at least one detail.")
    db.commit()
    db.refresh(existing_customer)
    if update_count== 1:
        return {"message": f"Successfully updated {update_count} detail.", "Customer": [existing_customer.customer_id, existing_customer.company_name]}
    return {"message": f"Successfully updated {update_count} details.", "Customer": [existing_customer.customer_id, existing_customer.company_name]}


@router.delete("/delete-customer")
async def delete_customer(admin: admin_dependency, db: db_dependency, 
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
async def add_product(product: Products, db: db_dependency):
    existing_product= db.query(models.Products).filter(models.Products.name == product.name).first()
    if existing_product:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Product of that name already exist.")
    new_product= models.Products(
        product_id= product.product_id,
        name= product.name,
        unit_price= product.unit_price,
        tax_percent= product.tax_percent,
        description= product.description
    )
    print(new_product)
    db.add(new_product)
    db.commit()
    return {"message": f"New product added to {product.name}."}

@router.put("/edit-product")
async def update_product(admin: admin_dependency, current_product: UpdateProduct, db: db_dependency, 
                          productid: int= Query(...)):
    existing_product= db.query(models.Products).filter(models.Products.product_id == productid).first()
    if not existing_product:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Product of that ID does not exist.")
    
    update_count= 0
    if current_product.name is not None:
        existing_product.name= current_product.name
        update_count += 1
    if current_product.unit_price is not None:
        existing_product.unit_price= current_product.unit_price
        update_count += 1
    if current_product.tax_percent is not None:
        existing_product.tax_percent= current_product.tax_percent
        update_count += 1
    if current_product.description is not None:
        existing_product.description= current_product.description
        update_count += 1 
    
    if update_count== 0:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                            detail= "Please update at least one detail.")
    db.commit()
    db.refresh(existing_product)
    if update_count== 1:
        return {"message": f"Successfully updated {update_count} detail.", "Product": [existing_product.product_id, existing_product.name]}
    return {"message": f"Successfully updated {update_count} details.", "Product": [existing_product.product_id, existing_product.name]}

@router.delete("/delete-product")
async def delete_product(admin: admin_dependency, db: db_dependency, 
                          product_id: int= Query(...)):
    existing_product= db.query(models.Products).filter(models.Products.product_id == product_id).first()
    if not existing_product:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Product of that ID does not exist.")
    else:
        db.delete(existing_product)
        db.commit()
        return {f"Product ID: {product_id}<br> Product: {existing_product.name}<br> Has been deleted."}