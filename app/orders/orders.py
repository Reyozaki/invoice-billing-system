from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.auth import either_perm
from app.config.database import Pagination, db_dependency, get_pagination
from app.orders.schemas import OrderOut
from app.shared.models.base import Customers, Orders, Products
from app.shared.schemas.base import PaginationOut

router = APIRouter(
    prefix="/orders", tags=["orders"], responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=PaginationOut)
async def view_orders(
    pagination: Annotated[Pagination, Depends(get_pagination)],
    db: db_dependency,
    user: either_perm,
):
    perm = user["scopes"]

    if "admin" in perm:
        query = db.query(
            Orders.order_id,
            Products.name,
            Orders.quantity,
            Products.unit_price,
            Orders.status,
        ).join(Products, Orders.product_id == Products.product_id)
        total = query.count()
        orders = query.offset(pagination.offset).limit(pagination.size).all()

        if not orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoices not found",
            )

        items = [
            {
                "order_id": order.order_id,
                "product_name": order.name,
                "quantity": order.quantity,
                "status": order.status,
                "subtotal": order.quantity * order.unit_price,
            }
            for order in orders
        ]
        return PaginationOut[OrderOut](
            total=total, page=pagination.page, size=pagination.size, items=items
        )

    elif "customer" in perm:
        customer = db.query(Customers).filter(Customers.user_id == user["id"]).first()
        query = (
            db.query(
                Orders.order_id,
                Products.name,
                Orders.quantity,
                Products.unit_price,
                Orders.status,
            )
            .filter(Orders.customer_id == customer.customer_id)
            .join(Products, Orders.product_id == Products.product_id)
        )
        total = query.count()
        customer_orders = query.offset(pagination.offset).limit(pagination.size).all()

        if not customer_orders:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orders for customer {customer.company_name} not found",
            )

        items = [
            {
                "order_id": order.order_id,
                "product_name": order.name,
                "quantity": order.quantity,
                "status": order.status,
                "subtotal": order.quantity * order.unit_price,
            }
            for order in customer_orders
        ]

        return PaginationOut[OrderOut](
            total=total,
            page=pagination.page,
            size=pagination.size,
            items=items,
        )
