from fastapi import APIRouter, HTTPException
from ..database import db_dependency
from ..schemas import InvoiceBase
import models 

router=APIRouter(    
    prefix= '/invoices',
    tags= ["invoices"],
    responses= {404: {"description": "Not found"}}
    )

@router.get("/")
async def root_invoices():
    return {"message": "This is the root of invoices."}


@router.post("/", status_code=201)
async def add_invoice(invoice: InvoiceBase, db: db_dependency):
    new_invoice = models.Invoices(
        customer_id=invoice.customer_id,
        total_amount=invoice.total_amount,
        status=invoice.status
    )
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return {"message": "New invoice successfully created.", "invoice": new_invoice}

@router.get("/all", response_model=list[InvoiceBase])
async def get_all_invoices(db: db_dependency):
    invoices = db.query(models.Invoices).all()
    return invoices

@router.get("/{invoice_id}", response_model=InvoiceBase)
async def get_invoice(invoice_id: int, db: db_dependency):
    invoice = db.query(models.Invoices).filter(models.Invoices.invoice_id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    return invoice

@router.put("/{invoice_id}")
async def update_invoice(invoice_id: int, updated_invoice: InvoiceBase, db: db_dependency):
    invoice = db.query(models.Invoices).filter(models.Invoices.invoice_id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    invoice.customer_id = updated_invoice.customer_id
    invoice.total_amount = updated_invoice.total_amount
    invoice.status = updated_invoice.status
    db.commit()
    return {"message": "Invoice updated successfully."}

@router.delete("/{invoice_id}")
async def delete_invoice(invoice_id: int, db: db_dependency):
    invoice = db.query(models.Invoices).filter(models.Invoices.invoice_id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    db.delete(invoice)
    db.commit()
    return {"message": "Invoice deleted successfully."}
