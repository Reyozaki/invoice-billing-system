from pydantic import BaseModel, EmailStr, StringConstraints    # type: ignore
from typing import Optional, Literal, List
from decimal import Decimal
from typing import Annotated

class Admin(BaseModel):
    username: str
    password: str
    
class StoreBase(BaseModel):    
    store_name: str
    
class CustomerBase(BaseModel):
    company_name: str
    email: EmailStr
    phone: Annotated[str, StringConstraints(pattern= r"^\d{10}$")]
    address: str
    tax_id: int
    password: str
    
class Products(StoreBase):
    product_id: Optional[int]= None
    name: str
    unit_price: Decimal
    tax_percent: Decimal
    description: str
    
class Sales(CustomerBase, Products):
    pass

class UpdateCustomer(BaseModel):
    company_name: Optional[str]= None
    email: Optional[EmailStr]= None
    phone: Optional[Annotated[str, StringConstraints(pattern= r"^\d{10}$")]]= None
    address: Optional[str]= None
    tax_id: Optional[int]= None
    password: Optional[str]= None
    
class UpdateProduct(BaseModel):
    product_id: Optional[int]= None
    name: Optional[str]= None
    unit_price: Optional[Decimal]= None
    tax_percent: Optional[Decimal]= None
    description: Optional[str]= None