from fastapi import APIRouter, HTTPException, status

from app.auth.auth import bcrypt_context, customer_perm
from app.config.database import db_dependency
from app.customer.schemas import CustomerIn, CustomerProfile, UpdateCustomer
from app.shared.models import base

router = APIRouter(
    prefix="/customer", tags=["customer"], responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=CustomerProfile)
async def view_profile(customer: customer_perm, db: db_dependency):
    customer_profile = (
        db.query(base.Customers)
        .filter(base.Customers.user_id == customer["id"])
        .first()
    )
    return customer_profile


@router.post("/")
async def add_customer(customer: CustomerIn, db: db_dependency):
    existing_customer = (
        db.query(base.Customers)
        .filter(base.Customers.company_name == customer.company_name)
        .first()
    )
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Customer of that name already exist.",
        )
    hashed_password = bcrypt_context.hash(customer.password)

    new_user = base.Users(
        username=customer.email, password=hashed_password, role="customer"
    )
    db.add(new_user)
    db.flush()

    new_customer = base.Customers(
        user_id=new_user.user_id,
        email=customer.email,
        phone=customer.phone,
        address=customer.address,
        company_name=customer.company_name,
        tax_id=customer.tax_id,
        password=hashed_password,
    )
    db.add(new_customer)
    db.commit()
    return {"message": "New Customer account successfully created."}


@router.put("/edit-profile")
async def update_profile(
    update_customer: UpdateCustomer, db: db_dependency, customer: customer_perm
):
    existing_customer = (
        db.query(base.Customers)
        .filter(base.Customers.user_id == customer["id"])
        .first()
    )
    if not existing_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer does not exist."
        )

    for field, value in update_customer.model_dump(exclude_unset=True).items():
        setattr(existing_customer, field, value)
    db.commit()
    db.refresh(existing_customer)
    return {
        "message": f"Details of customer {existing_customer.company_name} successfully updated."
    }
