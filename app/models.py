from sqlalchemy import Column, ForeignKey, DateTime, String, Integer, func, BigInteger, Numeric
from app.database import Base

class StoreBase(Base):
    __tablename__= "stores"
    
    store_id= Column(Integer, primary_key= True)
    store_name= Column(String(20), unique= True, nullable= False)
    tax_id= Column(Integer, unique= True, nullable= False)

class Customers(Base):
    __tablename__= "customers"
    
    customer_id= Column(BigInteger, primary_key= True)
    email= Column(String(25), unique= True, nullable= False)
    phone= Column(String(10), nullable= False)
    address= Column(String(20), nullable= False)
    company_name= Column(String(30), nullable= False)

class Customer(Base):
    __tablename__= "customer"
    
    customer_id= Column(BigInteger, primary_key= True)
    product_id= Column(Integer, ForeignKey("products.product_id"), index= True, nullable= False)
    
class Products(Base):
    __tablename__= "products"
    
    product_id= Column(BigInteger, primary_key= True)
    unit_price= Column(Integer, nullable= False)
    tax_percent= Column("tax%", Numeric(3, 2), nullable= False)
    description= Column(String(50), nullable= False)
    store_id= Column(Integer, ForeignKey("stores.store_id"), index= True, nullable= False)
    
