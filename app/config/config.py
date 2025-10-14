import os

from dotenv import load_dotenv

load_dotenv()

POSTGRES_DB = os.getenv("POSTGRES_DB")
if not POSTGRES_DB:
    raise RuntimeError("POSTGRES_DB set in .env file")

HOST = os.getenv("HOST")
if not HOST:
    raise RuntimeError("HOST set in .env file")

DB_DRIVER = os.getenv("DB_DRIVER")
if not DB_DRIVER:
    raise RuntimeError("DB_DRIVER not set in .env file")

POSTGRES_USER = os.getenv("POSTGRES_USER")
if not POSTGRES_USER:
    raise RuntimeError("POSTGRES_USER not set in .env file")

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
if not POSTGRES_PASSWORD:
    raise RuntimeError("POSTGRES_PASSWORD not set in .env file")

URL_DATABASE = (
    f"{DB_DRIVER}://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{HOST}:5432/{POSTGRES_DB}"
)

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set in .env file")

ALGORITHM = os.getenv("ALG")
if not ALGORITHM:
    raise RuntimeError("ALGORITHM not set in .env file")

EMAIL = os.getenv("SENDER_EMAIL")
if not ALGORITHM:
    raise RuntimeError("EMAIL not set in .env file")

PASSWORD = os.getenv("EMAIL_PASSWORD")
if not ALGORITHM:
    raise RuntimeError("ALGORITHM not set in .env file")
