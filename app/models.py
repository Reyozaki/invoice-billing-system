from sqlalchemy import Column, ForeignKey, DateTime, String, Integer, func, BigInteger, Numeric
from app.database import Base

class Customers(Base):
    __tablename__= "customers"
    
    customer_id= Column(BigInteger, primary_key= True)
    store_name= Column(String(20), default="The Store of Stores")
    email= Column(String(25), unique= True, nullable= False)
    phone= Column(String(10), nullable= False)
    address= Column(String(20), nullable= False)
    company_name= Column(String(30), nullable= False)
    tax_id= Column(Integer, unique= True, nullable= False)

class Products(Base):
    __tablename__= "products"
    
    product_id= Column(BigInteger, primary_key= True)
    unit_price= Column(Numeric(6, 2), nullable= False)
    tax_percent= Column(Numeric(3, 2), nullable= False)
    description= Column(String(50), nullable= False)
    
class Sale(Base):
    __tablename__= "sales"
    
    customer_id= Column(BigInteger, primary_key= True)
    product_id= Column(Integer, ForeignKey("products.product_id"), index= True, nullable= False)