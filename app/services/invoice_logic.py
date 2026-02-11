def invoice_input_validation(invoice_data):
    # --- 1. Top-level required fields ---
    required_fields = ["seller_name", "buyer_name", "invoice_number", "invoice_issue_date", "items", "tax_rate", "currency"]
    for field in required_fields:
        if field not in invoice_data:
            return False, f"Missing required field: {field}"

    # --- 2. Items must be non-empty list ---
    items = invoice_data["items"]
    if not isinstance(items, list) or len(items) == 0:
        return False, "Invoice must have at least one item"

    # --- 3. Validate each item ---
    for i, item in enumerate(items):
        if "description" not in item or not item["description"].strip():
            return False, f"Item {i+1} is missing description"
        if "quantity" not in item or item["quantity"] <= 0:
            return False, f"Item {i+1} must have quantity > 0"
        if "unit_price" not in item or item["unit_price"] < 0:
            return False, f"Item {i+1} must have unit_price >= 0"

    # --- 4. Validate tax ---
    tax_rate = invoice_data["tax_rate"]
    if not (0 <= tax_rate <= 1):
        return False, "Tax rate must be between 0 and 1"

    # --- 5. Validate currency ---
    if len(invoice_data["currency"]) != 3:
        return False, "Currency must be a 3-letter ISO code"

    return True, "Validation passed"


def calculate_invoice_totals(invoice_data):
    # Ensure input is valid
    valid, msg = invoice_input_validation(invoice_data)
    if not valid:
        return {"error": msg}

    # Calculate line totals
    for item in invoice_data["items"]:
        item["line_total"] = round(item["quantity"] * item["unit_price"], 2)

    # Calculate subtotal
    subtotal = round(sum(item["line_total"] for item in invoice_data["items"]), 2)

    # Calculate tax
    tax_amount = round(subtotal * invoice_data["tax_rate"], 2)

    # Calculate total
    total = round(subtotal + tax_amount, 2)

    # Return calculated invoice object
    return {
        "invoice_number": invoice_data["invoice_number"],
        "issue_date": invoice_data["invoice_issue_date"],
        "seller_name": invoice_data["seller_name"],
        "buyer_name": invoice_data["buyer_name"],
        "items": invoice_data["items"],
        "subtotal": subtotal,
        "tax_rate": invoice_data["tax_rate"],
        "tax_amount": tax_amount,
        "total": total,
        "currency": invoice_data["currency"]
    }