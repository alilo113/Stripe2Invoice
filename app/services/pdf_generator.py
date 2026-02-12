from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch

def generate_invoice_pdf(result):
    # Create document
    doc = SimpleDocTemplate("invoice.pdf")
    
    elements = []
    styles = getSampleStyleSheet()

    # Title
    elements.append(Paragraph("INVOICE", styles["Heading1"]))
    elements.append(Spacer(1, 0.5 * inch))

    # Seller & Buyer Info
    elements.append(Paragraph(f"Seller: {result['seller_name']}", styles["Normal"]))
    elements.append(Paragraph(f"Buyer: {result['buyer_name']}", styles["Normal"]))
    elements.append(Paragraph(f"Invoice #: {result['invoice_number']}", styles["Normal"]))
    elements.append(Spacer(1, 0.5 * inch))

    # Table Data
    table_data = [["Description", "Qty", "Unit Price", "Line Total"]]

    for item in result["items"]:
        table_data.append([
            item["description"],
            str(item["quantity"]),
            f"{item['unit_price']}",
            f"{item['line_total']}"
        ])

    table = Table(table_data)

    # Table Styling
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
        ("GRID", (0, 0), (-1, -1), 1, colors.black),
        ("ALIGN", (1, 1), (-1, -1), "RIGHT"),
    ]))

    elements.append(table)
    elements.append(Spacer(1, 0.5 * inch))

    # Totals
    elements.append(Paragraph(f"Subtotal: {result['subtotal']}", styles["Normal"]))
    elements.append(Paragraph(f"Tax: {result['tax_amount']}", styles["Normal"]))
    elements.append(Paragraph(f"Total: {result['total']}", styles["Heading2"]))

    # Build PDF
    doc.build(elements)