from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.jwt_bearer import JWTBearer
from app.Soap import get_Short_Card_Nr

router = APIRouter(
    prefix="/service",
    tags=["service cash point"],
    dependencies=[Depends(JWTBearer())]
)

# Request model
class ShortCardNrRequest(BaseModel):
    shortCardNr: str

@router.post("/api/shortcardnr")
def fetch_shortcard_nr(req: ShortCardNrRequest):
    """
    Fetch short card number from DESIGNA SOAP API.
    """
    try:
        result = get_Short_Card_Nr(req.shortCardNr)
        return {"shortCardNr": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
