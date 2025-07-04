import os
from dotenv import load_dotenv

load_dotenv()

URL_DATABASE= os.getenv("DATABASE_URL")
if not URL_DATABASE:
    raise RuntimeError("DATABASE_URL not set in .env file")

SECRET_KEY= os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY not set in .env file")

ALGORITHM= os.getenv("ALG")
if not ALGORITHM:
    raise RuntimeError("ALGORITHM not set in .env file")
