from fastapi import APIRouter, FastAPI, HTTPException
from pydantic import BaseModel  
from typing import Optional
import logging
import traceback


from app.Soap import login
from app.auth.jwt_handler import create_access_token
from app.config import settings
router = APIRouter(prefix="", tags=["Login"])
class LoginRequest(BaseModel):
    tcc_num: int
    user_id: Optional[str] = None
    password: Optional[str] = None

class LoginResponse(BaseModel):
    result_code: int
    message: str
    access_token: Optional[str] = None


@router.post("/login", response_model=LoginResponse)
def login_rest(req: LoginRequest):
    """
    Login to DESIGNA system using provided TCC number, user ID, and password.
    Validates TCC number and calls the login SOAP method.
    """
    try:
        # ✅ 1. Validate TCC number (optional: compare with env or database)
        # allowed_tccs = [int(t.strip()) for t in settings.ALLOWED_TCCS.split(",")] if hasattr(settings, "ALLOWED_TCCS") else []
        # if allowed_tccs and req.tcc_num not in allowed_tccs:
        #     raise HTTPException(status_code=400, detail=f"TCC {req.tcc_num} is not recognized or not authorized")

        allowed_tcc = int(settings.DESIGNA_TCC_ENTRY)

        if req.tcc_num != allowed_tcc:
            raise HTTPException(
                status_code=400,
                detail=f"TCC {req.tcc_num} is not authorized."
            )
        # ✅ 2. Call SOAP login
        result_code = login(
            tcc_num=req.tcc_num,
            user_id=req.user_id or settings.DESIGNA_USER,
            password=req.password or settings.DESIGNA_PASSWORD,
        )

        # ✅ 3. Handle response
        if result_code == 0:
            message = "Login successful"
            token_data = {"tcc_num": req.tcc_num, "user_id": req.user_id}
            access_token = create_access_token(token_data)
            return LoginResponse(
                result_code=result_code,
                message=message,
                access_token=access_token,
            )
        else:
            message = f"Login failed (code {result_code})"
            return LoginResponse(result_code=result_code, message=message)

    except HTTPException:
        raise  # rethrow HTTPException directly
    except Exception as e:
        logging.error(f"Error occurred during login: {e}\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")

# @app.post("/login", response_model=LoginResponse)
# def login_rest(req: LoginRequest):
#     """
#     Login to DESIGNA system using provided TCC number, user ID, and password.
#     Calls the login SOAP method.
#     """
#     try:
#         allowed_tccs = [int(t.strip()) for t in settings.ALLOWED_TCCS.split(",")] if hasattr(settings, "ALLOWED_TCCS") else []
#         if allowed_tccs and req.tcc_num not in allowed_tccs:
#             raise HTTPException(status_code=400, detail=f"TCC {req.tcc_num} is not recognized or not authorized")
#         result_code = login(tcc_num = req.tcc_num, user_id = req.user_id, password = req.password)
#         if result_code == 0:
#             message = "Login successful"
#             token_data = {"tcc_num":req.tcc_num, "user_id": req.user_id}
#             access_token = create_access_token(token_data)
#             return LoginResponse(result_code = result_code, message = message, access_token = access_token)
#         else:
#             message = f"Login failed (code {result_code})"
#             return LoginResponse(result_code=result_code, message=message)
#     except HTTPException:
#         raise
#     except Exception as e:
#         logging.error(f"Error occurred during login: {e}\n{traceback.format_exc()}")
#         raise HTTPException(status_code=500, detail=f"Internal error: {e}")

