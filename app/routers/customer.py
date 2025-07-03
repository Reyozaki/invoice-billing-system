from fastapi import APIRouter, HTTPException, status, Query

from ..database import db_dependency
from ..schemas import UpdateCustomer, CustomerProfile, CustomerIn
from ..models import Customers, Users
from .auth import bcrypt_context, customer_perm, admin_perm

router= APIRouter(
    prefix= '/customer',
    tags= ["customer"],
    responses= {404: {"description": "Not found"}}
    )
    

@router.get("/", response_model= CustomerProfile)
async def view_profile(customer: customer_perm, db: db_dependency):
    customer_s= customer
    print(customer_s)
    customer_profile= db.query(Customers).filter(Customers.user_id == customer["id"]).first()
    return customer_profile

@router.post("/")
async def add_customer(customer: CustomerIn, db: db_dependency):
    existing_customer= db.query(Customers).filter(Customers.company_name == customer.company_name).first()
    if existing_customer:
        raise HTTPException(status_code= status.HTTP_409_CONFLICT, 
                            detail= "Customer of that name already exist.")
    hashed_password= bcrypt_context.hash(customer.password)
    
    new_user= Users(
        username= customer.email,
        password= hashed_password,
        role= "customer"
    )
    db.add(new_user)
    db.flush()
    
    new_customer= Customers(
        user_id= new_user.user_id,
        email= customer.email,
        phone= customer.phone,
        address= customer.address,
        company_name= customer.company_name,
        tax_id= customer.tax_id,
        password= hashed_password
    )
    db.add(new_customer)
    db.commit()
    return {"message": "New Customer account successfully created."}

@router.put("/edit-profile")
async def update_profile(update_customer: UpdateCustomer, db: db_dependency, customer: customer_perm):
    existing_customer= db.query(Customers).filter(Customers.user_id == customer["id"]).first()
    if not existing_customer:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Customer does not exist.")
    
    for field, value in update_customer.model_dump(exclude_unset= True).items():
        setattr(existing_customer, field, value)
    db.commit()
    db.refresh(existing_customer)
    return {"message": f"Details of customer {existing_customer.company_name} successfully updated."}

@router.put("/edit-customer")
async def update_customer(admin: admin_perm, current_customer: UpdateCustomer, db: db_dependency, 
                          customer_id: int= Query(...)):
    existing_customer= db.query(Customers).filter(Customers.customer_id == customer_id).first()
    if not existing_customer:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Customer of that ID does not exist.")
    
    for field, value in current_customer.model_dump(exclude_unset= True).items():
        setattr(existing_customer, field, value)
    db.commit()
    db.refresh(existing_customer)
    
    return {"message": f"Successfully updated details of Customer{[existing_customer.customer_id, existing_customer.company_name]}"}

