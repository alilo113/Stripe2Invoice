from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from io import BytesIO
import datetime

from app.config import INTERNAL_SECRET
from app.services.invoice_logic import invoice_input_validation, calculate_invoice_totals
from app.services.pdf_generator import generate_invoice_pdf

invoice_router = APIRouter()

@invoice_router.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    payload = await request.json()

    # --- Map Stripe payload ---
    try:
        invoice_data = {
            "seller_name": "My SaaS Co.",
            "buyer_name": payload["customer_name"],
            "invoice_number": payload["id"],
            "invoice_issue_date": datetime.datetime.fromtimestamp(
                payload["created"]
            ).strftime("%Y-%m-%d"),
            "items": [
                {
                    "description": item.get("description", "Payment"),
                    "quantity": item.get("quantity", 1),
                    "unit_price": item.get("unit_price", payload["amount"])
                }
                for item in payload.get(
                    "items",
                    [{"description": "Payment", "quantity": 1, "unit_price": payload["amount"]}]
                )
            ],
            "tax_rate": payload.get("tax_percent", 0) / 100,
            "currency": payload.get("currency", "USD").upper()
        }
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {str(e)}")

    # --- Validate ---
    valid, msg = invoice_input_validation(invoice_data)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    # --- Calculate ---
    result = calculate_invoice_totals(invoice_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # --- Generate PDF ---
    try:
        pdf_buffer: BytesIO = generate_invoice_pdf(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    pdf_buffer.seek(0)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{result['invoice_number']}.pdf"
        }
    )