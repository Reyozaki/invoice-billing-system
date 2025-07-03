import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from fastapi.staticfiles import StaticFiles

from fastapi import FastAPI
from .internal import admin, invoicedoc
from .routers import customer, product, auth, invoices
from app.database import engine, Base

app= FastAPI()
app.include_router(customer.router)
app.include_router(product.router)
app.include_router(auth.router)
app.include_router(invoices.router)
app.include_router(admin.router)


Base.metadata.create_all(bind=engine)

invoice_dir = os.path.join(os.getcwd(), "invoices")
os.makedirs(invoice_dir, exist_ok=True)

app.mount("/downloads", StaticFiles(directory=invoice_dir), name="downloads")