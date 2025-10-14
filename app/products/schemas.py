from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class ProductOut(BaseModel):
    product_id: int
    name: str
    unit_price: Decimal
    tax_percent: Decimal
    description: str

    class Config:
        from_attributes = True


class OrderIn(BaseModel):
    product_id: int
    quantity: int
    status: Literal["unpaid", "paid"]

    class Config:
        from_attributes = True
