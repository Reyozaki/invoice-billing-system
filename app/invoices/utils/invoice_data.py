import shutil
import subprocess
from pathlib import Path
from typing import TYPE_CHECKING

from app.invoices.utils.invoicedoc import generate_invoice

if TYPE_CHECKING:
    from docx import Document


def generate_invoice_pdf(invoice, customer, orders, products) -> bytes:
    doc: Document = generate_invoice(invoice, customer, orders, products)

    docx_dir = Path.cwd() / "invoices"
    docx_dir.mkdir(parents=True, exist_ok=True)

    docx_path = docx_dir / f"invoice_{invoice.invoice_id}.docx"
    doc.save(str(docx_path))

    pdf_path = docx_path.with_suffix(".pdf")
    soffice_path = shutil.which("soffice")
    if not soffice_path:
        raise RuntimeError("LibreOffice 'soffice' binary not found")

    subprocess.run(
        [
            str(Path(soffice_path).resolve()),
            "--headless",
            "--convert-to",
            "pdf",
            str(Path(docx_path).resolve()),
            "--outdir",
            str(Path(docx_dir).resolve()),
        ],
        check=True,
    )  # nosec B603

    pdf_data = pdf_path.read_bytes()

    docx_path.unlink(missing_ok=True)
    pdf_path.unlink(missing_ok=True)

    return pdf_data
