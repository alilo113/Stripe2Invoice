from fastapi import APIRouter

invoice_router = APIRouter()

@invoice_router.post("/")
async def get_invoices():
    return {"message": "Invoices route works"}