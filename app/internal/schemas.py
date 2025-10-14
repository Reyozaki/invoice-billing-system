from datetime import datetime
from decimal import Decimal
from typing import Annotated, Literal

from pydantic import BaseModel, EmailStr, StringConstraints


class AdminOut(BaseModel):
    admin_id: int
    username: str

    class Config:
        from_attributes = True


class LatestInvoice(BaseModel):
    invoice_id: int
    company_name: str
    date: datetime
    total_amount: float
    status: str

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M")}


class DashboardOut(BaseModel):
    total_invoices: int
    paid_invoices: int
    pending_invoices: int
    total_customers: int
    latest_invoice: LatestInvoice | None


class CustomerOut(BaseModel):
    customer_id: int
    company_name: str
    tax_id: int
    email: EmailStr
    address: str
    phone: Annotated[str, StringConstraints(pattern=r"^\d{10}$")]

    class Config:
        from_attributes = True


class UpdateInvoice(BaseModel):
    discount_percent: Decimal | None = None
    status: Literal["Draft", "Sent", "Paid"] | None = None

    class Config:
        from_attributes = True


class UpdateProduct(BaseModel):
    name: str | None = None
    unit_price: Decimal | None = None
    tax_percent: Decimal | None = None
    description: str | None = None

    class Config:
        from_attributes = True


class UpdateCustomer(BaseModel):
    company_name: str | None = None
    email: EmailStr | None = None
    phone: Annotated[str, StringConstraints(pattern="^\\d{10}$")] | None = None
    address: str | None = None
    tax_id: int | None = None
    password: str | None = None

    class Config:
        from_attributes = True
