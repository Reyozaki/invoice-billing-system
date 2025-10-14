from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from app.auth.auth import customer_perm
from app.config.database import Pagination, db_dependency, get_pagination
from app.products.schemas import OrderIn, ProductOut
from app.shared.models.base import Customers, Orders, Products
from app.shared.schemas.base import PaginationOut

router = APIRouter(
    prefix="/products", tags=["products"], responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=PaginationOut[ProductOut])
async def view_products(
    pagination: Annotated[Pagination, Depends(get_pagination)], db: db_dependency
):
    query = db.query(
        Products.product_id,
        Products.name,
        Products.unit_price,
        Products.description,
        Products.tax_percent,
    )
    total = query.count()
    results = query.offset(pagination.offset).limit(pagination.size).all()
    return PaginationOut[ProductOut](
        total=total, page=pagination.page, size=pagination.size, items=results
    )


@router.post("/buy")
async def purchase(order: OrderIn, db: db_dependency, customer: customer_perm):
    existing_product = (
        db.query(Products).filter(Products.product_id == order.product_id).first()
    )
    if not existing_product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Product not found."
        )

    customer_id = (
        db.query(Customers.customer_id)
        .filter(Customers.email == customer["username"])
        .scalar()
    )
    if not customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please Login as a Customer.",
        )

    new_order = Orders(
        customer_id=customer_id,
        product_id=existing_product.product_id,
        quantity=order.quantity,
        status=order.status,
    )
    try:
        db.add(new_order)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB Error: {str(e)}",
        ) from e

    return new_order.order_id
