from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, StringConstraints


class InvoiceIn(BaseModel):
    customer_id: int
    discount_percent: Decimal

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M")}


class InvoiceOut(BaseModel):
    invoice_id: int
    customer_id: int
    company_name: str
    product_ids: list[int]
    status: str
    discount_percent: Decimal
    date: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M")}


class CustomerInvoice(BaseModel):
    invoice_id: int
    product_ids: list[int]
    status: str
    discount_percent: Decimal
    date: datetime

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M")}


class UpdateInvoice(BaseModel):
    discount_percent: Decimal | None = None
    status: Literal["Draft", "Sent", "Paid"] | None = None

    class Config:
        from_attributes = True


class CustomerProfile(BaseModel):
    company_name: str
    tax_id: int
    email: EmailStr
    address: str
    phone: Annotated[str, StringConstraints(pattern=r"^\d{10}$")]

    class Config:
        from_attributes = True


# class CustomerInvoice(BaseModel):
#     invoice_id: int
#     date: datetime
#     total: Decimal
#     discount_percent: Decimal

#     class Config:
#         from_attributes = True
#         json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M")}
