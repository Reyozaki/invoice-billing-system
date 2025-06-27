import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from .routers import customer, product, auth, invoices
from app.database import engine, Base

app= FastAPI()
app.include_router(customer.router)
app.include_router(product.router)
app.include_router(auth.router)
app.include_router(invoices.router)


Base.metadata.create_all(bind=engine)


