from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from app.auth.jwt_bearer import JWTBearer
from app.Soap import get_pm_string

router = APIRouter(
    prefix="/service",
    tags=["service operations"],
    dependencies=[Depends(JWTBearer())]
)

# Request model
class PMStringRequest(BaseModel):
    user: str
    pwd: str
    shortCardNr: str

@router.post("/api/getPMString")
def fetch_pm_string(req: PMStringRequest):
    """
    Fetch PM string from DESIGNA SOAP API.
    """
    try:
        result = get_pm_string(req.user, req.pwd, req.shortCardNr)
        return {"pmString": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
