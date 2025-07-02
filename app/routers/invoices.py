from fastapi import APIRouter, HTTPException, status
from ..database import db_dependency
from ..schemas import InvoiceBase, UpdateInvoice
from ..schemas import InvoiceBase, UpdateInvoice
from models import Customers, Invoices, Sale
from .auth import customer_perm, admin_perm, either_perm


router=APIRouter(    
    prefix= '/invoices',
    tags= ["invoices"],
    responses= {404: {"description": "Not found"}}
    )

@router.get("/")
async def view_invoices(db: db_dependency, user: either_perm):
    perm = user["scopes"]

    if "admin" in perm:
        invoices = db.query(Invoices).all()
        return invoices

    elif "customer" in perm:
        customer= db.query(Customers).filter(Customers.user_id == user["id"]).first()
        sales= db.query(Sale).filter(Sale.customer_id == customer.customer_id).all()
        sale_ids= [sale.sale_id for sale in sales]
        if not sale_ids:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                                detail= f"No Purchases found for customer {customer.company_name}.")

        customer_invoices = db.query(Invoices).filter(Invoices.sale_id.in_(sale_ids)).all()

        if not customer_invoices:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                                detail= f"Invoices for customer {customer.company_name} not found")

        return customer_invoices
    

@router.post("/", status_code= status.HTTP_201_CREATED)
async def add_invoice(invoice: InvoiceBase, db: db_dependency, admin: admin_perm):
    new_invoice = Invoices(
        customer_id=invoice.customer_id,
        total_amount=invoice.total_amount,
        status=invoice.status
    )
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    return {"message": "New invoice successfully created.", "invoice": new_invoice}

@router.put("/invoice/{invoice_id}")
async def update_invoice(invoice_id: int, invoice: UpdateInvoice, db: db_dependency):
    existing_invoice = db.query(Invoices).filter(Invoices.invoice_id == invoice_id).first()
    if not existing_invoice:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail="Invoice not found.")

    if not any([invoice.quantity, invoice.tax, invoice.discount]):
        raise HTTPException(status_code= status.HTTP_400_BAD_REQUEST, 
                            detail="Please update at least one value: quantity, tax, or discount.")

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
    invoice = db.query(Invoices).filter(Invoices.invoice_id == invoice_id).first()
    if invoice is None:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail="Invoice not found.")
    db.delete(invoice)
    db.commit()
    return {"message": "Invoice deleted successfully."}