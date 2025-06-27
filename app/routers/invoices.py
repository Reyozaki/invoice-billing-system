from fastapi import APIRouter, HTTPException
from ..database import db_dependency
# from ..schemas import 
import models 

routers=APIRouter(    
    prefix= '/invoices',
    tags= ["invoices"],
    responses= {404: {"description": "Not found"}}
    )