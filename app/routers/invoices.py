from fastapi import APIRouter, Depends, HTTPException
from ..database import db_dependency
# from ..schemas import 

router = APIRouter(
    prefix="/invoices",
    tags=["Invoices"]
    
    
)

@router.post("/" )
def create_invoice(invoice:str, db:db_dependency):
    pass
#     try:
#         return e(db, invoice)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))

# @router.put("/{invoice_id}/status")
# def update_invoice_status(invoice_id: int, status: schemas.InvoiceStatus, db: Session = Depends(database.SessionLocal)):
#     try:
#         return crud.update_invoice_status(db, invoice_id, status)
#     except ValueError as e:
#         raise HTTPException(status_code=404, detail=str(e))