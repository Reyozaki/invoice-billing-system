from email.message import EmailMessage

import aiosmtplib  # type: ignore
from pydantic import EmailStr

from app.config.config import EMAIL, PASSWORD


async def send_invoice(
    email_to: EmailStr,
    subject: str,
    body: str,
    pdf_bytes: bytes,
    filename: str = "invoice.pdf",
):
    message = EmailMessage()
    message["From"] = EMAIL
    message["To"] = email_to
    message["Subject"] = subject

    message.set_content("HTML is unsupported in your client.")
    message.add_alternative(body, subtype="html")

    message.add_attachment(
        pdf_bytes, maintype="application", subtype="pdf", filename=filename
    )

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username=EMAIL,
        password=PASSWORD,
    )
