from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.exc import SQLAlchemyError

from app.auth.auth import admin_perm, either_perm
from app.config.database import Pagination, db_dependency, get_pagination
from app.invoices.schemas import CustomerInvoice, InvoiceIn, InvoiceOut, UpdateInvoice
from app.invoices.utils.invoice_data import generate_invoice_pdf
from app.shared.models.base import Customers, Invoices, Orders, Products
from app.shared.schemas.base import PaginationOut
from app.shared.services import email

router = APIRouter(
    prefix="/invoices", tags=["invoices"], responses={404: {"description": "Not found"}}
)


@router.get("/", response_model=PaginationOut)
async def view_invoices(
    pagination: Annotated[Pagination, Depends(get_pagination)],
    db: db_dependency,
    user: either_perm,
    name: str | None = Query(None),
):
    perm = user["scopes"]
    if "admin" in perm:
        query = db.query(Invoices, Customers.company_name).join(
            Customers, Invoices.customer_id == Customers.customer_id
        )
        if name:
            query = query.filter(Customers.company_name.ilike(f"%{name}%"))
        total = query.count()
        invoices = query.offset(pagination.offset).limit(pagination.size).all()

        items = [
            {
                "invoice_id": invoice.invoice_id,
                "customer_id": invoice.customer_id,
                "company_name": company_name,
                "product_ids": invoice.product_ids,
                "status": invoice.status,
                "discount_percent": invoice.discount_percent,
                "date": invoice.date,
            }
            for invoice, company_name in invoices
        ]

        return PaginationOut[InvoiceOut](
            total=total, page=pagination.page, size=pagination.size, items=items
        )

    elif "customer" in perm:
        customer = db.query(Customers).filter(Customers.user_id == user["id"]).first()

        query = (
            db.query(
                Invoices.invoice_id,
                Invoices.date,
                Invoices.status,
                Invoices.discount_percent,
                Invoices.product_ids,
            )
            .filter(Invoices.customer_id == customer.customer_id)
            .filter(Invoices.status != "Draft")
        )
        total = query.count()
        customer_invoices = query.offset(pagination.offset).limit(pagination.size).all()

        if not customer_invoices:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Invoices for customer {customer.company_name} not found",
            )

        return PaginationOut[CustomerInvoice](
            total=total,
            page=pagination.page,
            size=pagination.size,
            items=customer_invoices,
        )


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=CustomerInvoice)
async def add_invoice(invoice: InvoiceIn, db: db_dependency, admin: admin_perm):
    try:
        unpaid_product_ids = (
            db.query(Orders.product_id)
            .filter(Orders.customer_id == invoice.customer_id)
            .filter(Orders.status == "unpaid")
            .distinct()
            .all()
        )
        if not unpaid_product_ids:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Orders for customer {invoice.customer_id} not found",
            )

        product_ids = [pid[0] for pid in unpaid_product_ids]

        new_invoice = Invoices(
            customer_id=invoice.customer_id,
            discount_percent=invoice.discount_percent,
            product_ids=product_ids,
        )

        db.add(new_invoice)
        db.commit()
        db.refresh(new_invoice)

        return new_invoice

    except SQLAlchemyError as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB Error: {str(e)}",
        ) from e


@router.put("/invoice")
async def update_invoice(
    user: either_perm,
    invoice: UpdateInvoice,
    db: db_dependency,
    invoice_id: int = Query(...),
):
    existing_invoice = (
        db.query(Invoices).filter(Invoices.invoice_id == invoice_id).first()
    )
    if not existing_invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found."
        )

    if not any([invoice.discount_percent, invoice.status]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please update at least one value: quantity, status or discount.",
        )

    for field, value in invoice.model_dump(exclude_unset=True).items():
        setattr(existing_invoice, field, value)
    db.commit()
    db.refresh(existing_invoice)
    return {"invoice_id": invoice_id}


@router.delete("/")
async def delete_invoice(
    db: db_dependency, admin: admin_perm, invoice_id: int = Query(...)
):
    invoice = db.query(Invoices).filter(Invoices.invoice_id == invoice_id).first()
    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found."
        )
    db.delete(invoice)
    db.commit()
    return {"message": "Invoice deleted successfully."}


def get_invoice_data(invoice_id: int, db):
    invoice = db.query(Invoices).filter(Invoices.invoice_id == invoice_id).first()
    if not invoice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invoice not found"
        )

    customer = (
        db.query(Customers).filter(Customers.customer_id == invoice.customer_id).first()
    )
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Customer not found"
        )

    product_ids = invoice.product_ids
    if not product_ids:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No product IDs in invoice"
        )

    orders = (
        db.query(Orders)
        .filter(Orders.customer_id == invoice.customer_id)
        .filter(Orders.product_id.in_(product_ids))
        .filter(Orders.status == "unpaid")
        .all()
    )
    if not orders:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No matching orders found"
        )

    products = db.query(Products).filter(Products.product_id.in_(product_ids)).all()
    if not products:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Products not found"
        )

    product_obj = {p.product_id: p for p in products}

    return invoice, customer, orders, product_obj


@router.get(
    "/preview-invoice",
    responses={
        200: {
            "content": {
                "application/pdf": {"schema": {"type": "string", "format": "binary"}}
            }
        }
    },
)
async def preview_invoice(
    db: db_dependency, admin: admin_perm, invoice_id: int = Query(...)
):
    invoice, customer, orders, product_obj = get_invoice_data(invoice_id, db)
    pdf_data = generate_invoice_pdf(invoice, customer, orders, product_obj)

    return StreamingResponse(
        BytesIO(pdf_data),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"inline; filename= invoice_{invoice.invoice_id}_preview.pdf"
        },
    )


@router.get("/download")
async def download_invoice(
    db: db_dependency, admin: admin_perm, invoice_id: int = Query(...)
):
    invoice, customer, orders, product_obj = get_invoice_data(invoice_id, db)
    pdf_data = generate_invoice_pdf(invoice, customer, orders, product_obj)

    return StreamingResponse(
        BytesIO(pdf_data),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename= invoice_{invoice.invoice_id}.pdf"
        },
    )


@router.post("/send-invoice")
async def email_invoice(
    db: db_dependency, admin: admin_perm, invoice_id: int = Query(...)
):
    invoice, customer, orders, product_obj = get_invoice_data(invoice_id, db)
    pdf_data = generate_invoice_pdf(invoice, customer, orders, product_obj)
    customer_email = customer.email

    email_body = f"""
        <h3> Dear {customer.company_name},</h3>
        <p>Please find the attached invoice.<br><br>
        Regards,<br>
        <strong>{customer.store_name}</strong></p>
    """

    await email.send_invoice(
        email_to=customer_email,
        subject=f"Invoice  from {customer.store_name}",
        body=email_body,
        pdf_bytes=pdf_data,
    )

    return {"message": "Invoice sent successfully."}
