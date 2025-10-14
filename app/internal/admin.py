from decimal import Decimal
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status

from ..auth.auth import admin_perm, bcrypt_context
from ..config.database import Pagination, db_dependency, get_pagination
from ..shared.models import base
from ..shared.schemas.base import Admin, PaginationOut, ProductBase
from .schemas import (
    AdminOut,
    CustomerOut,
    DashboardOut,
    UpdateCustomer,
    UpdateProduct,
)

router = APIRouter(
    prefix="/admin", tags=["admin"], responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=PaginationOut[AdminOut])
async def admin_dashboard(
    pagination: Annotated[Pagination, Depends(get_pagination)],
    db: db_dependency,
    admin: admin_perm,
):
    query = db.query(base.Admin.username, base.Admin.admin_id)
    total = query.count()
    results = query.offset(pagination.offset).limit(pagination.size).all()
    return PaginationOut[AdminOut](
        total=total, page=pagination.page, size=pagination.size, items=results
    )


@router.get("/dashboard", response_model=DashboardOut)
async def dashboard_details(db: db_dependency, admin: admin_perm):
    invoices = db.query(base.Invoices).filter(base.Invoices.status != "Draft")
    total_invoices = invoices.count()

    paid_invoices = db.query(base.Invoices).filter(base.Invoices.status == "Paid")
    total_paid_invoices = paid_invoices.count()

    pending_invoices = db.query(base.Invoices).filter(base.Invoices.status == "Sent")
    total_pending_invoices = pending_invoices.count()

    customers = db.query(base.Customers)
    total_customers = customers.count()

    latest_invoice_query = (
        db.query(base.Invoices)
        .join(base.Customers, base.Invoices.customer_id == base.Customers.customer_id)
        .order_by(base.Invoices.date.desc())
        .first()
    )

    if latest_invoice_query:
        product_ids = latest_invoice_query.product_ids

        subtotal = Decimal("0.0")

        for productid in product_ids:
            product = db.query(base.Products).filter_by(product_id=productid).first()
            order = (
                db.query(base.Orders)
                .filter(
                    base.Orders.customer_id == latest_invoice_query.customer_id,
                    base.Orders.product_id == productid,
                )
                .first()
            )

            if product and order:
                subtotal += product.unit_price * order.quantity

        discount = latest_invoice_query.discount_percent
        total_amount = round(subtotal - (subtotal * discount / 100), 2)

        latest_invoice = {
            "invoice_id": latest_invoice_query.invoice_id,
            "company_name": latest_invoice_query.customer.company_name,
            "date": latest_invoice_query.date,
            "status": latest_invoice_query.status,
            "total_amount": total_amount,
        }
    else:
        latest_invoice = None

    return {
        "total_invoices": total_invoices,
        "paid_invoices": total_paid_invoices,
        "pending_invoices": total_pending_invoices,
        "total_customers": total_customers,
        "latest_invoice": latest_invoice,
    }


@router.post("/")
async def add_admin(admin: Admin, db: db_dependency):
    existing_admin = (
        db.query(base.Admin).filter(base.Admin.username == admin.username).first()
    )
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Admin of that username already exist.",
        )
    hashed_password = bcrypt_context.hash(admin.password)

    new_user = base.Users(
        username=admin.username, password=hashed_password, role="admin"
    )
    db.add(new_user)
    db.flush()

    new_admin = base.Admin(
        user_id=new_user.user_id, username=admin.username, password=hashed_password
    )
    print(new_admin)
    db.add(new_admin)
    db.commit()
    return new_admin


@router.get("/customers", response_model=PaginationOut[CustomerOut])
async def view_customers(
    pagination: Annotated[Pagination, Depends(get_pagination)],
    admin: admin_perm,
    db: db_dependency,
):
    query = db.query(
        base.Customers.customer_id,
        base.Customers.company_name,
        base.Customers.address,
        base.Customers.email,
        base.Customers.tax_id,
        base.Customers.phone,
    )
    total = query.count()
    results = query.offset(pagination.offset).limit(pagination.size).all()
    return PaginationOut[CustomerOut](
        total=total, page=pagination.page, size=pagination.size, items=results
    )


@router.put("/edit-customer")
async def update_customer(
    admin: admin_perm,
    current_customer: UpdateCustomer,
    db: db_dependency,
    customer_id: int = Query(...),
):
    existing_customer = (
        db.query(base.Customers)
        .filter(base.Customers.customer_id == customer_id)
        .first()
    )
    if not existing_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer of that ID does not exist.",
        )

    for field, value in current_customer.model_dump(exclude_unset=True).items():
        setattr(existing_customer, field, value)
    db.commit()
    db.refresh(existing_customer)

    return {
        "message": f"Successfully updated details of Customer{[existing_customer.customer_id, existing_customer.company_name]}"
    }


@router.delete("/delete-customer")
async def delete_customer(
    admin: admin_perm, db: db_dependency, customer_id: int = Query(...)
):
    existing_customer = (
        db.query(base.Customers)
        .filter(base.Customers.customer_id == customer_id)
        .first()
    )
    if not existing_customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer of that ID does not exist.",
        )
    else:
        db.delete(existing_customer)
        db.commit()
        return {
            f"Customer ID: {customer_id}<br> Customer: {existing_customer.company_name}<br> Has been deleted."
        }


@router.get("/view-product", response_model=PaginationOut[ProductBase])
async def view_products(
    pagination: Annotated[Pagination, Depends(get_pagination)],
    db: db_dependency,
    admin: admin_perm,
):
    query = db.query(
        base.Products.product_id,
        base.Products.name,
        base.Products.unit_price,
        base.Products.description,
        base.Products.tax_percent,
    )
    total = query.count()
    results = query.offset(pagination.offset).limit(pagination.size).all()
    return PaginationOut[ProductBase](
        total=total, page=pagination.page, size=pagination.size, items=results
    )


@router.post("/add-product")
async def add_product(admin: admin_perm, product: ProductBase, db: db_dependency):
    existing_product = (
        db.query(base.Products).filter(base.Products.name == product.name).first()
    )
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Product of that name already exist.",
        )
    new_product = base.Products(
        name=product.name,
        unit_price=product.unit_price,
        tax_percent=product.tax_percent,
        description=product.description,
    )
    db.add(new_product)
    db.commit()
    return {"message": f"New product added to {product.name}."}


@router.put("/edit-product")
async def update_product(
    admin: admin_perm,
    current_product: UpdateProduct,
    db: db_dependency,
    product_id: int = Query(...),
):
    existing_product = (
        db.query(base.Products).filter(base.Products.product_id == product_id).first()
    )
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product of that ID does not exist.",
        )

    for field, value in current_product.model_dump(exclude_unset=True).items():
        setattr(existing_product, field, value)
    db.commit()
    db.refresh(existing_product)

    return {
        "product_id": product_id,
        "message": f"Successfully updated details of Product{[existing_product.product_id, existing_product.name]}",
    }


@router.delete("/delete-product")
async def delete_product(
    admin: admin_perm, db: db_dependency, product_id: int = Query(...)
):
    existing_product = (
        db.query(base.Products).filter(base.Products.product_id == product_id).first()
    )
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product of that ID does not exist.",
        )
    else:
        db.delete(existing_product)
        db.commit()
        return {
            f"Product ID: {product_id}<br> Product: {existing_product.name}<br> Has been deleted."
        }
