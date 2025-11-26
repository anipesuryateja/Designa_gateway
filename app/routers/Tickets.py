
# app/routers/tickets.py
import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Optional
from app.auth.jwt_bearer import JWTBearer
from app.Soap import get_amount_due, set_rebate, set_card_settlement, set_cleared

router = APIRouter(prefix="/tickets", tags=["Tickets"],dependencies=[Depends(JWTBearer())])

# ----------------------------
# Response Models
# ----------------------------
class AmountDueResponse(BaseModel):
    card_number: str
    amount_due: str

class RebateRequest(BaseModel):
    discount_type: int
    discount_value: int
    discount_account: int

class SettlementRequest(BaseModel):
    amount_paid: float

class GenericResponse(BaseModel):
    result: str
    raw_response: Optional[str] = None
    amount_due_before_payment: Optional[float] = None
    soap_response: Optional[dict] = None

# ----------------------------
# Endpoints
# ----------------------------

# 1️⃣ Home / Lookup
@router.get("/{card_number}", response_model=AmountDueResponse)
async def ticket_lookup(card_number: str, tcc_num: int = int(os.getenv("DESIGNA_TCC_ENTRY", "0"))):
    """
    Lookup ticket by card_number.
    Calls getAmountDue SOAP method.
    """
    try:
        result = get_amount_due(tcc_num, card_number)
        return {"card_number": card_number, "amount_due": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 2️⃣ Plate Search
@router.get("/by-plate/{plate}", response_model=AmountDueResponse)
async def ticket_by_plate(plate: str, tcc_num: int):
    """
    Lookup ticket by license plate.
    Calls getAmountDue or LPR query.
    Currently maps plate → card_number via SOAP (simplified).
    """
    try:
        # Here, ideally you would map plate → card_number
        # For now, we assume plate = card_number
        result = get_amount_due(tcc_num, plate)
        return {"card_number": plate, "amount_due": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 3️⃣ Discounts
@router.post("/{card_number}/rebates", response_model=GenericResponse)
async def ticket_rebate(card_number: str, request: RebateRequest):
    """
    Apply discount rules via setRebate SOAP call.
    """
    try:
        result = set_rebate(
            card_number,
            request.discount_type,
            request.discount_value,
            request.discount_account,
        )
        return {"result": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 4️⃣ Payment
# @router.post("/{card_number}/settlements", response_model=GenericResponse)
# async def ticket_settlement(card_number: str, tcc_num: int, request: SettlementRequest):
#     """
#     Complete payment via setCardSettlement SOAP call.
#     """
#     try:
#         result = set_card_settlement(tcc_num, card_number, request.amount_paid)
#         return {"result": str(result)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))




@router.post("/{card_number}/settlements", response_model=GenericResponse)
async def ticket_settlement(card_number: str, tcc_num: int, request: SettlementRequest):
    """
    Complete payment via setCardSettlement SOAP call with due validation.
    """
    try:
        result = set_card_settlement(tcc_num, card_number, request.amount_paid)
        return result

    except ValueError as ve:
        # Business logic issue (no due / overpayment)
        raise HTTPException(status_code=400, detail=str(ve))

    except RuntimeError as re:
        # SOAP fault or communication failure
        raise HTTPException(status_code=502, detail=str(re))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

# 5️⃣ Clear Ticket
@router.post("/{card_number}/clear", response_model=GenericResponse)
async def ticket_clear(card_number: str, tcc_num: int, user_id: str = None, password: str = None):
    """
    Mark ticket cleared via setCleared SOAP call.
    """
    try:
        result = set_cleared(tcc_num, card_number, user_id, password)
        return {"message": "Ticket cleared successfully","result": str(result)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))