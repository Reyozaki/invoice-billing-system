from datetime import datetime
from decimal import Decimal
from typing import Annotated, Generic, Literal, TypeVar

from pydantic import BaseModel, EmailStr, StringConstraints

T = TypeVar("T")


class Admin(BaseModel):
    username: str
    password: str

    class Config:
        from_attributes = True


class CustomerBase(BaseModel):
    company_name: str
    email: EmailStr
    phone: Annotated[str, StringConstraints(pattern=r"^\d{10}$")]
    address: str
    tax_id: int
    password: str

    class Config:
        from_attributes = True


class ProductBase(BaseModel):
    product_id: int
    name: str
    unit_price: Decimal
    tax_percent: Decimal
    description: str

    class Config:
        from_attributes = True


class Orders(BaseModel):
    customer_id: int
    product_id: int
    quantity: int
    status: Literal["unpaid", "paid"]

    class Config:
        from_attributes = True


class InvoiceBase(BaseModel):
    invoice_id: int | None = None
    customer_id: int
    status: Literal["Draft", "Sent", "Paid"]
    date: datetime | None = None

    class Config:
        from_attributes = True
        json_encoders = {datetime: lambda v: v.strftime("%Y-%m-%d %H:%M")}


class PaginationOut(BaseModel, Generic[T]):
    total: int
    page: int
    size: int
    items: list[T]

    class Config:
        from_attributes = True
