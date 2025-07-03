from fastapi import APIRouter, HTTPException, status
from sqlalchemy.exc import SQLAlchemyError
import os
import subprocess

from ..database import db_dependency
from ..schemas import InvoiceIn, UpdateInvoice, InvoiceOut
from ..models import Customers, Invoices, Orders, Products
from .auth import admin_perm, either_perm
from ..internal import invoicedoc

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
        
        customer_invoices = (
            db.query(Invoices)
            .filter(Invoices.customer_id == customer.customer_id)
            .filter(Invoices.status != "Draft")
            .all()
        )

        if not customer_invoices:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                                detail= f"Invoices for customer {customer.company_name} not found")

        return customer_invoices
    

@router.post("/", status_code= status.HTTP_201_CREATED, response_model= InvoiceOut)
async def add_invoice(invoice: InvoiceIn, db: db_dependency, admin: admin_perm):
    try:
        unpaid_product_ids= (
            db.query(Orders.product_id)
            .filter(Orders.customer_id == invoice.customer_id)
            .filter(Orders.status == "unpaid")
            .distinct()
            .all()
        )
        product_ids= [pid[0] for pid in unpaid_product_ids]

        new_invoice= Invoices(
            customer_id= invoice.customer_id,
            status= invoice.status,
            tax= invoice.tax,
            discount= invoice.discount,
            product_ids= product_ids
        )
        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)

        return new_invoice

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error: {str(e)}"
        )    

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


@router.get("/{invoice_id}/download")
async def download_invoice(invoice_id: int, db: db_dependency, admin: admin_perm):
    invoice = db.query(Invoices).filter(Invoices.invoice_id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Invoice not found")

    customer = db.query(Customers).filter(Customers.customer_id == invoice.customer_id).first()
    if not customer:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Customer not found")

    product_ids = invoice.product_ids
    if not product_ids:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "No product IDs in invoice")

    orders = (
        db.query(Orders)
        .filter(Orders.customer_id == invoice.customer_id)
        .filter(Orders.product_id.in_(product_ids))
        .filter(Orders.status == "unpaid")
        .all()
    )
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= "No matching orders found")

    products = (
        db.query(Products)
        .filter(Products.product_id.in_(product_ids))
        .all()
    )
    if not products:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= "Products not found")

    product_obj = {p.product_id: p for p in products}

    doc= invoicedoc.generate_invoice(invoice, customer, orders, product_obj)
    
    docx_dir = os.path.join(os.getcwd(), "invoices")
    os.makedirs(docx_dir, exist_ok=True)

    docx_filename = f"invoice_{invoice.invoice_id}.docx"
    docx_path = os.path.join(docx_dir, docx_filename)
    doc.save(docx_path)

    pdf_filename = docx_filename.replace(".docx", ".pdf")
    pdf_path = os.path.join(docx_dir, pdf_filename)

    try:
        subprocess.run([
            "soffice", "--headless", "--convert-to", "pdf", docx_path,
            "--outdir", docx_dir
        ], check=True)
    except subprocess.CalledProcessError as e:
        raise HTTPException(status_code= status.HTTP_500_INTERNAL_SERVER_ERROR, 
                            detail=f"PDF conversion failed: {e}")

    return {
        "docx_download_url": f"http://localhost:8000/downloads/{docx_filename}",
        "pdf_download_url": f"http://localhost:8000/downloads/{pdf_filename}"
    }