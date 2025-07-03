from pydantic import BaseModel, EmailStr, StringConstraints    # type: ignore
from typing import Optional, Literal, List, Annotated
from decimal import Decimal
from datetime import datetime

class Admin(BaseModel):
    username: str
    password: str
    
class CustomerBase(BaseModel):
    company_name: str
    email: EmailStr
    phone: Annotated[str, StringConstraints(pattern= r"^\d{10}$")]
    address: str
    tax_id: int
    password: str
    
class Products(BaseModel):
    name: str
    unit_price: Decimal
    tax_percent: Decimal
    description: str
    
class Orders(BaseModel):
    customer_id: int
    product_id: int
    quantity: int
    status: Literal["unpaid", "paid"]

class UpdateCustomer(BaseModel):
    company_name: Optional[str]= None
    email: Optional[EmailStr]= None
    phone: Optional[Annotated[str, StringConstraints(pattern= r"^\d{10}$")]]= None
    address: Optional[str]= None
    tax_id: Optional[int]= None
    password: Optional[str]= None
    
class UpdateProduct(BaseModel):
    name: Optional[str]= None
    unit_price: Optional[Decimal]= None
    tax_percent: Optional[Decimal]= None
    description: Optional[str]= None

class InvoiceBase(BaseModel):
    invoice_id: Optional[int]= None
    customer_id: int
    total_amount: Decimal
    status: Literal["Draft", "Sent", "Paid"]
    date: Optional[datetime]= None
    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M")
        }
     
class UpdateInvoice(BaseModel):
    quantity: Optional[int] = None
    tax: Optional[Decimal] = None
    discount: Optional[Decimal] = None

    class Config:
        from_attributes = True
    
class CustomerProfile(BaseModel):
    company_name: str
    tax_id: int
    email: EmailStr
    address: str
    phone: Annotated[str, StringConstraints(pattern= r"^\d{10}$")]
    
    class Config:
        from_attributes= True

class CustomerIn(BaseModel):
    company_name:str
    email: EmailStr
    tax_id: int
    phone: Annotated[str, StringConstraints(pattern= r"^\d{10}$")]
    address: str    
    password: str
    
    class Config:
        from_attributes= True
        
class InvoiceIn(BaseModel):
    customer_id: int
    product_ids: List[int]
    status: Literal["Draft", "Sent", "Paid"]
    tax: Decimal
    discount: Decimal
    class Config:
        from_attributes= True
        json_encoders = {
            datetime: lambda v: v.strftime("%Y-%m-%d %H:%M")
        }