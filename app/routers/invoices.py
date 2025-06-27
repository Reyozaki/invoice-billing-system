from fastapi import APIRouter, HTTPException
from ..database import db_dependency
# from ..schemas import 
import models 

router=APIRouter(    
    prefix= '/invoices',
    tags= ["invoices"],
    responses= {404: {"description": "Not found"}}
    )

@router.get("/")
async def root_invoices():
    return {"message": "This is the root of invoices."}