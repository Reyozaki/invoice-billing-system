from sqlalchemy import Column, ForeignKey, DateTime, String, Integer, func, BigInteger, Numeric
from sqlalchemy.orm import relationship
from app.database import Base

class Users(Base):
    __tablename__ = "users"
    
    user_id = Column(Integer, primary_key= True)
    username = Column(String, unique= True, nullable= False)
    password = Column(String, nullable= False)
    role = Column(String, nullable= False)
    
class Admin(Base):
    __tablename__="admin"
    
    admin_id= Column(BigInteger, primary_key= True)
    user_id= Column(Integer, ForeignKey("users.user_id"), nullable= False)
    username= Column(String, nullable= False, unique= True)
    password= Column(String)
    
class Customers(Base):
    __tablename__= "customers"
    
    customer_id= Column(BigInteger, primary_key= True)
    user_id= Column(Integer, ForeignKey("users.user_id"), nullable= False)
    store_name= Column(String(20), default="The Store of Stores")
    email= Column(String(25), unique= True, nullable= False)
    phone= Column(String(10), nullable= False)
    address= Column(String(20), nullable= False)
    company_name= Column(String(30), nullable= False)
    tax_id= Column(Integer, unique= True, nullable= False)
    password= Column(String)

class Products(Base):
    __tablename__= "products"
    
    product_id= Column(BigInteger, primary_key= True)
    name= Column(String, unique= True, nullable= False)
    unit_price= Column(Numeric(8, 2), nullable= False)
    tax_percent= Column(Numeric(5, 2), nullable= False)
    description= Column(String(50), nullable= False)
    
class Orders(Base):
    __tablename__= "orders"
    
    order_id= Column(BigInteger, primary_key= True)
    customer_id= Column(Integer, ForeignKey("customers.customer_id"), nullable= False)
    product_id= Column(Integer, ForeignKey("products.product_id"), nullable= False)
    quantity= Column(Integer, nullable= False, default= 1)
    status= Column(String, default= "unpaid", nullable= False)
    
class Invoices(Base):
    __tablename__ = "invoices"
    
    invoice_id = Column(BigInteger, primary_key= True)
    customer_id = Column(Integer, ForeignKey("customers.customer_id"), nullable= False)
    date = Column(DateTime(timezone= True), server_default=func.now())
    status = Column(String(20), default= "Draft")
    tax = Column(Numeric(5, 2), nullable= True)
    discount = Column(Numeric(5, 2), nullable= True)
    