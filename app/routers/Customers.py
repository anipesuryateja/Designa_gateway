from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from app.auth.jwt_bearer import JWTBearer
from app.Soap import get_customer

router = APIRouter(prefix="/customers", tags=["customers"],dependencies=[Depends(JWTBearer())])

class CustomerRequest(BaseModel):
    user: str
    pwd: str
    personId: int

@router.post("/api/getCustomer")
def get_customer_info(req: CustomerRequest):
    try:
        result = get_customer(req.user, req.pwd, req.personId)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
