import os
from dotenv import load_dotenv

load_dotenv()

URL_DATABASE= os.getenv("DATABASE_URL")
if not URL_DATABASE:
    raise RuntimeError("DATABASE_URL not set in .env file")