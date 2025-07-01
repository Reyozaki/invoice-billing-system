from sqlalchemy import Column, ForeignKey, DateTime, String, Integer, func, BigInteger, Numeric
from app.database import Base

class Admin(Base):
    __tablename__="admin"
    
    admin_id= Column(BigInteger, primary_key= True)
    username= Column(String, nullable= False, unique= True)
    password= Column(String)
    
class Customers(Base):
    __tablename__= "customers"
    
    customer_id= Column(BigInteger, primary_key= True)
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
    unit_price= Column(Numeric(6, 2), nullable= False)
    tax_percent= Column(Numeric(3, 2), nullable= False)
    description= Column(String(50), nullable= False)
    
class Sale(Base):
    __tablename__= "sales"
    
    sale_id= Column(BigInteger, primary_key= True)
    customer_id= Column(Integer, ForeignKey("customers.customer_id"), index= True, nullable= False)
    product_id= Column(Integer, ForeignKey("products.product_id"), index= True, nullable= False)
    
class Invoices(Base):
    __tablename__ = "invoices"
    
    invoice_id = Column(BigInteger, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("sales.customer_id"), nullable=False)
    date = Column(DateTime(timezone=True), server_default=func.now())
    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(String(20), default="unpaid") 
    quantity = Column(Integer, nullable=True)
    tax = Column(Numeric(5, 2), nullable=True) 
    discount = Column(Numeric(5, 2), nullable=True)  
    