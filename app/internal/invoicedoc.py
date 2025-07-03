from docx import Document
from io import BytesIO
from fastapi.responses import StreamingResponse
from ..models import Customers, Invoices, Orders
from typing import List

def generate_invoice(invoice: Invoices, customer: Customers, orders: List[Orders], products: dict):
    doc = Document()
    doc.add_heading(f"{customer.store_name}", 0)
    doc.add_heading("Invoice", 0)

    doc.add_paragraph(f"Customer: {customer.company_name}")
    doc.add_paragraph(f"Email: {customer.email}")
    doc.add_paragraph(f"Date: {invoice.date.strftime('%Y-%m-%d')}")
    doc.add_paragraph(f"Status: {invoice.status}")
    doc.add_paragraph(" ")

    doc.add_heading("Products", level=1)

    table = doc.add_table(rows=1, cols=5)
    table.style = "Light Grid"
    hdr_cells = table.rows[0].cells
    hdr_cells[0].text = "Product Name"
    hdr_cells[1].text = "Unit Price"
    hdr_cells[2].text = "Quantity"
    hdr_cells[3].text = "Tax (%)"
    hdr_cells[4].text = "Total (w/ Tax)"

    total_amount = 0
    quantity = invoice.quantity or 1
    tax = invoice.tax or 0

    for order in orders:
        product = products.get(order.product_id)
        if not product:
            continue

        unit_price = product.unit_price
        subtotal = unit_price * quantity
        taxed_total = subtotal + (subtotal * tax / 100)
        total_amount += taxed_total

        row_cells = table.add_row().cells
        row_cells[0].text = product.name
        row_cells[1].text = f"${unit_price:.2f}"
        row_cells[2].text = str(quantity)
        row_cells[3].text = f"{tax:.2f}%"
        row_cells[4].text = f"${taxed_total:.2f}"

    doc.add_paragraph(" ")
    doc.add_paragraph(f"Total Amount: ${total_amount:.2f}", style="Intense Quote")

    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f"attachment; filename=invoice_{invoice.invoice_id}.docx"}
    )
