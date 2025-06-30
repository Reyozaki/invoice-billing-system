from pydantic import BaseModel, EmailStr, StringConstraints    # type: ignore
from typing import Optional, Literal, List
from decimal import Decimal
from typing import Annotated
from datetime import datetime

class StoreBase(BaseModel):    
    store_name: str
    
class CustomerBase(BaseModel):
    customer_id: Optional[int]= None
    company_name: str
    email: EmailStr
    phone: Annotated[str, StringConstraints(pattern= r"^\d{10}$")]
    address: str
    tax_id: int
    
class Products(StoreBase):
    product_id: Optional[int]= None
    name: str
    unit_price: Decimal
    tax_percent: Decimal
    description: str
    
class Sales(CustomerBase, Products):
    pass

class UpdateCustomer(CustomerBase):
    company_name: Optional[str]= None
    email: Optional[EmailStr]
    phone: Optional[Annotated[str, StringConstraints(pattern= r"^\d{10}$")]]= None
    address: Optional[str]
    tax_id: Optional[int]

class InvoiceBase(BaseModel):
    invoice_id: Optional[int] = None
    customer_id: int
    total_amount: Decimal
    status: Optional[str] = "unpaid"
    date: Optional[datetime] = None

    class Config:
        orm_mode = True
        
class UpdateInvoices(BaseModel):
    customer_id: Optional[int] = None
    total_amount: Optional[Decimal] = None
    status: Optional[str] = None

    class Config:
        orm_mode = True
        
    