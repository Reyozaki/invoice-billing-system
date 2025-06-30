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
async def view_products(db: db_dependency):
    return db.query(models.Products).all()

