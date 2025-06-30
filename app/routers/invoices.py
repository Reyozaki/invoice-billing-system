from fastapi import APIRouter, HTTPException
from ..database import db_dependency
from ..schemas import InvoiceBase,UpdateInvoice
import models 

router=APIRouter(    
    prefix= '/invoices',
    tags= ["invoices"],
    responses= {404: {"description": "Not found"}}
    )

@router.get("/")
async def root_invoices(db: db_dependency):
    return db.query(models.Invoices).all()

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

@router.get("/{invoice_id}", response_model=InvoiceBase)
async def get_invoice(invoice_id: int, db: db_dependency):
    invoice = db.query(models.Invoices).filter(models.Invoices.invoice_id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code=404, detail="Invoice not found.")
    return invoice

@router.put("/invoice/{invoice_id}")
async def update_invoice(invoice_id: int, invoice: UpdateInvoice, db: db_dependency):
    existing_invoice = db.query(models.Invoices).filter(models.Invoices.invoice_id == invoice_id).first()
    if not existing_invoice:
        raise HTTPException(status_code=404, detail="Invoice not found.")

    if not any([invoice.quantity, invoice.tax, invoice.discount]):
        raise HTTPException(status_code=400, detail="Please update at least one value: quantity, tax, or discount.")

    if invoice.quantity is not None:
        existing_invoice.quantity = invoice.quantity
    if invoice.tax is not None:
        existing_invoice.tax = invoice.tax
    if invoice.discount is not None:
        existing_invoice.discount = invoice.discount

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