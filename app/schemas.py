from pydantic import BaseModel, EmailStr, StringConstraints    # type: ignore
from typing import Optional, Literal, List
from decimal import Decimal
from typing import Annotated

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
    
class Customer(CustomerBase, Products):
    pass
