
# app/routers/ops.py
from fastapi import APIRouter, Depends, HTTPException
from app.auth.jwt_bearer import JWTBearer
from app.Soap import get_soap_client
from app.config import settings

router = APIRouter(prefix="/devices", tags=["Operations"],dependencies=[Depends(JWTBearer())])

# -----------------------------
# Ops Endpoints
# -----------------------------
@router.get("/state")
def get_devices_state():
    """
    Calls DESIGNA SOAP getServiceOperationState.
    """
    try:
        client = get_soap_client("DESIGNA_WSDL_SERVICE_OPERATION_URL")
        response = client.service.getServiceOperationState()
        return {"state": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/counters")
def get_counters():
    """
    Calls DESIGNA SOAP getCarParkCounterExt.
    """
    try:
        client = get_soap_client("DESIGNA_WSDL_SERVICE_OPERATION_URL")
        response = client.service.getCarParkCounterExt()
        return {"counters": response}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


