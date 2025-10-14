from decimal import Decimal
from typing import Literal

from pydantic import BaseModel


class OrderIn(BaseModel):
    quantity: int
    status: Literal["unpaid", "paid"]

    class Config:
        from_attributes = True


class OrderOut(BaseModel):
    order_id: int
    product_name: str
    quantity: int
    status: Literal["unpaid", "paid"]
    subtotal: Decimal
