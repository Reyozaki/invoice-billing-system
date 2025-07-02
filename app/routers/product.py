from fastapi import APIRouter, HTTPException, Query, status
from ..database import db_dependency
from ..schemas import Products, UpdateProduct
import models
from .auth import admin_perm

router= APIRouter(
    prefix= '/products',
    tags= ["products"],
    responses= {404: {"description": "Not found"}}
    )


@router.get("/")
async def view_products(db: db_dependency):
    return db.query(models.Products).all()

@router.put("/edit-product")
async def update_product(admin: admin_perm, current_product: UpdateProduct, db: db_dependency, 
                          product_id: int= Query(...)):
    existing_product= db.query(models.Products).filter(models.Products.product_id == product_id).first()
    if not existing_product:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Product of that ID does not exist.")
    
    for field, value in current_product.model_dump(exclude_unset= True).items():
        setattr(existing_product, field, value)
    db.commit()
    db.refresh(existing_product)
    
    return {"message": f"Successfully updated details of Product{[existing_product.product_id, existing_product.name]}"}