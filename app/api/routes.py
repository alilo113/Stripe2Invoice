from urllib import request
from fastapi import APIRouter
from app.services.invoice_logic import invoice_input_validation, calculate_invoice_totals

invoice_router = APIRouter()

@invoice_router.post("/")
async def get_invoices(request):
    # Validate input data
    valid, msg = invoice_input_validation(request.json)
    if not valid:
        return {"error": msg}
    
    # Calculate invoice totals
    result = calculate_invoice_totals(request.json)
    return result