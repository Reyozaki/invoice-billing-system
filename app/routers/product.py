from fastapi import APIRouter, HTTPException, Query, status, Depends
from ..database import db_dependency
from ..schemas import UpdateProduct
from ..models import Orders, Products, Customers
from .auth import admin_perm, customer_perm

router= APIRouter(
    prefix= '/products',
    tags= ["products"],
    responses= {404: {"description": "Not found"}}
    )


@router.get("/")
async def view_products(db: db_dependency):
    return db.query(Products).all()

@router.post("/buy")
async def purchase(db: db_dependency, customer: customer_perm,
                   product_name: str= Query(...)):
    existing_product = db.query(Products).filter(Products.name == product_name).first()
    if not existing_product:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail="Product not found.")
    
    customer_id = db.query(Customers.customer_id).filter(Customers.email == customer.username).first()
    if not customer_id:
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, 
                            detail="Customer ID missing.")

    new_sale = Orders(
        customer_id=customer_id,
        product_id=existing_product.product_id
    )
    try:
        db.add(new_sale)
        db.commit()
        db.refresh(new_sale)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"DB Error: {str(e)}")

    return {"message": f"Product '{product_name}' purchased.", "sale_id": new_sale.sale_id}


@router.put("/edit-product")
async def update_product(admin: admin_perm, current_product: UpdateProduct, db: db_dependency, 
                          product_id: int= Query(...)):
    existing_product= db.query(Products).filter(Products.product_id == product_id).first()
    if not existing_product:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Product of that ID does not exist.")
    
    for field, value in current_product.model_dump(exclude_unset= True).items():
        setattr(existing_product, field, value)
    db.commit()
    db.refresh(existing_product)
    
    return {"message": f"Successfully updated details of Product{[existing_product.product_id, existing_product.name]}"}