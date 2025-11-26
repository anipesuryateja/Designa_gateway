
from fastapi import APIRouter, Depends, FastAPI, HTTPException
from pydantic import BaseModel

from app.auth.jwt_bearer import JWTBearer
from app.Soap import get_card_by_carrier

# app = FastAPI(title="DESIGNA REST Wrapper")



router = APIRouter(
    prefix="/plates",
    tags=["Plates"],
    dependencies=[Depends(JWTBearer())]
)
# Request model
class CardCarrierRequest(BaseModel):
    user: str
    pwd: str
    cardCarrierNr: str

@router.post("/api/getCardByCarrier")
def get_card_info(req: CardCarrierRequest):
    try:
        result = get_card_by_carrier(req.user, req.pwd, req.cardCarrierNr)

        # Convert SOAP object to dict for JSON output
        if hasattr(result, "__dict__"):
            result_dict = result.__dict__
        else:
            result_dict = dict(result)

        return result_dict

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
