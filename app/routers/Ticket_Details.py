

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.config import settings        # import your settings
from app.Soap import get_card_info   # your SOAP helper
from app.auth.jwt_bearer import JWTBearer

router = APIRouter(
    prefix="/service",
    tags=["service cash point"],
    dependencies=[Depends(JWTBearer())]
)

class CardInfoRequest(BaseModel):
    TccNum: int
    CardNumber: str

@router.post("/api/cardinfo")
def fetch_shortcard_nr(req: CardInfoRequest):
    try:
        result = get_card_info(
            # user_id=settings.DESIGNA_USER,
            # user_pwd=settings.DESIGNA_PASSWORD,
            tcc_num=req.TccNum,
            card_number=req.CardNumber
        )
        return {"cardInfo": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
