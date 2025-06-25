from pydantic import BaseModel, EmailStr, constr    # type: ignore
from typing import Optional, Literal, List
from decimal import Decimal

class StoreBase(BaseModel):
    tax_id: int
    store_name: str
    
class CustomerBase(BaseModel):
    customer_id: Optional[int]= None
    company_name: str
    email: EmailStr
    phone: constr(regex= r"^\d{10}$") #type: ignore
    address: str

class Customer(BaseModel, CustomerBase, Products):
    pass

class Products(BaseModel, StoreBase):
    product_id= Optional[int]= None
    name: str
    unit_price: int
    tax_percent: Decimal
    description: str