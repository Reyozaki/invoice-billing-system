from typing import Annotated

from pydantic import BaseModel, EmailStr, StringConstraints


class CustomerIn(BaseModel):
    company_name: str
    email: EmailStr
    tax_id: int
    phone: Annotated[str, StringConstraints(pattern=r"^\d{10}$")]
    address: str
    password: str

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


class UpdateCustomer(BaseModel):
    company_name: str | None = None
    email: EmailStr | None = None
    phone: Annotated[str, StringConstraints(pattern="^\\d{10}$")] | None = None
    address: str | None = None
    tax_id: int | None = None
    password: str | None = None

    class Config:
        from_attributes = True
