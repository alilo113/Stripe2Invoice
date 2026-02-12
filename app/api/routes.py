from fastapi import APIRouter, HTTPException
from typing import Dict
from app.services.invoice_logic import invoice_input_validation, calculate_invoice_totals
from app.services.pdf_generator import generate_invoice_pdf

invoice_router = APIRouter()

@invoice_router.post("/")
async def get_invoices(invoice_data: Dict):
    
    # Validate input data
    valid, msg = invoice_input_validation(invoice_data)
    if not valid:
        raise HTTPException(status_code=400, detail=msg)
    
    # Calculate invoice totals
    result = calculate_invoice_totals(invoice_data)

    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])

    # Generate PDF
    try:
        generate_invoice_pdf(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")
    

    return result