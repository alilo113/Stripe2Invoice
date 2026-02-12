from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import Dict, Optional
from io import BytesIO
import httpx
import datetime

from app.services.invoice_logic import invoice_input_validation, calculate_invoice_totals
from app.services.pdf_generator import generate_invoice_pdf

invoice_router = APIRouter()

@invoice_router.post("/stripe-webhook")
async def stripe_webhook(request: Request):
    """
    Receives Stripe webhook payload, generates PDF invoice,
    and optionally posts it to a callback URL.
    """

    payload = await request.json()

    # --- 1. Map Stripe payload to internal invoice format ---
    try:
        invoice_data = {
            "seller_name": "My SaaS Co.",
            "buyer_name": payload["customer_name"],
            "invoice_number": payload["id"],  # PaymentIntent ID
            "invoice_issue_date": datetime.datetime.fromtimestamp(payload["created"]).strftime("%Y-%m-%d"),
            "items": [
                {
                    "description": item.get("description", "Subscription"),
                    "quantity": item.get("quantity", 1),
                    "unit_price": item.get("unit_price", payload["amount"])
                }
                for item in payload.get("items", [{"description": "Payment", "quantity": 1, "unit_price": payload["amount"]}])
            ],
            "tax_rate": payload.get("tax_percent", 0) / 100,
            "currency": payload.get("currency", "USD").upper()
        }
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing Stripe field: {str(e)}")

    # --- 2. Validate invoice ---
    valid, msg = invoice_input_validation(invoice_data)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)

    # --- 3. Calculate totals ---
    result = calculate_invoice_totals(invoice_data)
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # --- 4. Generate PDF ---
    try:
        pdf_buffer: BytesIO = generate_invoice_pdf(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

    # --- 5. Optional: callback_url ---
    callback_url = payload.get("callback_url")
    if callback_url:
        pdf_bytes = pdf_buffer.getvalue()
        try:
            async with httpx.AsyncClient() as client:
                await client.post(callback_url, files={"invoice.pdf": ("invoice.pdf", pdf_bytes, "application/pdf")})
        except Exception as e:
            # Do not fail the main webhook; just log error
            print(f"Callback failed: {str(e)}")

    # --- 6. Return PDF as response ---
    pdf_buffer.seek(0)
    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=invoice_{result['invoice_number']}.pdf"
        }
    )