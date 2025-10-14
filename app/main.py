import os
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.auth import auth
from app.config.database import Base, engine
from app.customer import customer
from app.internal import admin
from app.invoices import invoices
from app.orders import orders
from app.products import product

app = FastAPI()
app.include_router(customer.router)
app.include_router(product.router)
app.include_router(auth.router)
app.include_router(invoices.router)
app.include_router(orders.router)
app.include_router(admin.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

invoice_dir = os.path.join(os.getcwd(), "invoice")
os.makedirs(invoice_dir, exist_ok=True)

app.mount("/downloads", StaticFiles(directory=invoice_dir), name="downloads")
