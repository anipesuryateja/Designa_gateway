# app/LogOffService.py
from fastapi import APIRouter, Depends, FastAPI, HTTPException, Header
from pydantic import BaseModel  
from typing import Optional
import logging
import traceback

from app.auth.jwt_bearer import JWTBearer
from app.Soap import logoff  # the SOAP function we defined earlier
from app.config import settings
from app.auth.token_blacklist import blacklist_token
router = APIRouter(prefix="", tags=["LogOff"],dependencies=[Depends(JWTBearer())])
# -----------------------------
# Request/Response Models
# -----------------------------
class LogOffRequest(BaseModel):
    tcc_num: int
   

class LogOffResponse(BaseModel):
    success: bool
    message: str

# -----------------------------
# LogOff Endpoint
# -----------------------------
@router.post("/logoff", response_model=LogOffResponse)
def logoff_rest(req: LogOffRequest, authorization: str = Header(None)):
    """
    Logs off a DESIGNA session for the given TCC number and optional user ID.
    Calls the logOff SOAP method.
    """
    try:
        # ✅ 1. Validate TCC number (optional)
        allowed_tcc = int(settings.DESIGNA_TCC_EXIT)  # or DESIGNA_TCC_EXIT depending on your logic

        if req.tcc_num != allowed_tcc:
            raise HTTPException(
                status_code=400,
                detail=f"TCC {req.tcc_num} is not authorized."
            )

        # ✅ 2. Call SOAP logOff
        result = logoff(
            tcc_num=req.tcc_num
            
        )

        if authorization:
            token = authorization.replace("Bearer ", "")
            blacklist_token(token)

        # ✅ 3. Handle response
        # if result:
        #     message = "LogOff successful"
        # else:
        #     message = "LogOff failed"

        return LogOffResponse(success=result, message="LogOff successful" if result else "LogOff failed")

    except HTTPException:
        raise  # rethrow HTTPException directly
    except Exception as e:
        logging.error(f"Error occurred during logOff: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")
