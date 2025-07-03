from fastapi import APIRouter, HTTPException, status
from ..database import db_dependency
from ..schemas import InvoiceIn, UpdateInvoice
from ..models import Customers, Invoices, Orders, Products
from .auth import admin_perm, either_perm
from ..internal import invoicedoc
from typing import List


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
        customer_invoices = db.query(Invoices).filter(Invoices.customer_id == customer.customer_id).all()

        if not customer_invoices:
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND,
                                detail= f"Invoices for customer {customer.company_name} not found")

        return customer_invoices
    

@router.post("/", status_code= status.HTTP_201_CREATED)
async def add_invoice(invoice: InvoiceIn, db: db_dependency, admin: admin_perm):
    new_invoice = Invoices(
        customer_id= invoice.customer_id,
        status= invoice.status,
        tax= invoice.tax,
        discount= invoice.discount
    )
    db.add(new_invoice)
    db.commit()
    db.refresh(new_invoice)
    try:
        for product_id in invoice.product_ids:
            new_order = Orders(
                customer_id= invoice.customer_id,
                product_id= product_id,
                invoice_id= new_invoice.invoice_id  
            )
            db.add(new_order)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database error when adding orders: {e}"
        )

    return {
        "message": "New invoice successfully created.",
        "invoice_id": new_invoice.invoice_id,
        "Purchases": invoice.product_ids
    }

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


@router.get("/invoice/{invoice_id}/download")
async def download_invoice(invoice_id: int, db: db_dependency, admin: admin_perm):
    invoice = db.query(Invoices).filter(Invoices.invoice_id == invoice_id).first()
    if not invoice:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail= "Invoice not found")

    orders = db.query(Orders).filter(Orders.invoice_id == invoice_id).all()
    if not orders:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, 
                            detail= "No orders found for invoice")

    customer = db.query(Customers).filter(Customers.customer_id == invoice.customer_id).first()
    if not customer:
        raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, 
                            detail="Customer not found")

    product_ids = [order.product_id for order in orders]
    product_objs = db.query(Products).filter(Products.product_id.in_(product_ids)).all()
    products = {p.product_id: p for p in product_objs}

    return invoicedoc.generate_invoice(invoice, customer, orders, products)