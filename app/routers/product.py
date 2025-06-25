from fastapi import APIRouter, HTTPException
from ..database import db_dependency
from ..schemas import Products
import models

router= APIRouter(
    prefix= '/product',
    tags= ["product"],
    responses= {404: {"description": "Not found"}}
    )

@router.get("/")
async def root_customer():
    return {"message": "This is the root of products."}

@router.post("/add-product")
async def add_customer(product: Products, db: db_dependency):
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
    return {"message": "New product added to {product.store_name}."}