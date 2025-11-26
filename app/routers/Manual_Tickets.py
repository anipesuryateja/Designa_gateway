

# app/routers/manual_tickets.py
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
from app.auth.jwt_bearer import JWTBearer
from app.Soap import calc_tariff, set_card_settlement

router = APIRouter(prefix="/manual-tickets", tags=["Manual Tickets"],dependencies=[Depends(JWTBearer())])

# ----------------------------
# Request Models
# ----------------------------
class ManualTicketRequest(BaseModel):
    carpark_nr: int
    card_type: int
    tariff_id: int
    time_entry: datetime
    time_exit: datetime

class ManualSettlementRequest(BaseModel):
    amount_paid: float

# ----------------------------
# Endpoints
# ----------------------------

# Create surrogate from verified entry
@router.post("", response_model=dict)
async def create_manual_ticket(request: ManualTicketRequest):
    """
    Calls calcTariff SOAP to create manual ticket.
    """
    try:
        result = calc_tariff(
            carpark_nr=request.carpark_nr,
            card_type=request.card_type,
            tariff_id=request.tariff_id,
            time_entry=request.time_entry,
            time_exit=request.time_exit,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Manual ticket payment
# @router.post("/{card_number}/settlements", response_model=dict)
# async def manual_ticket_settlement(card_number: str, tcc_num: int, request: ManualSettlementRequest):
#     """
#     Settle manual ticket via setCardSettlement.
#     """
#     try:
#         result = set_card_settlement(tcc_num, card_number, request.amount_paid)
#         return {"result": str(result)}
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))



@router.post("/{card_number}/settlements", response_model=dict)
async def manual_ticket_settlement(card_number: str, tcc_num: int, request: ManualSettlementRequest):
    """
    Settle manual ticket via setCardSettlement with due check.
    """
    try:
        result = set_card_settlement(tcc_num, card_number, request.amount_paid)
        return result

    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))

    except RuntimeError as re:
        raise HTTPException(status_code=502, detail=str(re))

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")