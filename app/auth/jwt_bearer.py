# app/auth/jwt_bearer.py
from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.auth.jwt_handler import decode_access_token
from app.auth.token_blacklist import is_blacklisted
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super(JWTBearer, self).__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super(JWTBearer, self).__call__(request)
        if credentials:
            token = credentials.credentials
            if is_blacklisted(token):
                raise HTTPException(status_code=403, detail="Token has been invalidated")
            payload = decode_access_token(token)
            if payload is None:
                raise HTTPException(status_code=403, detail="Invalid or expired token")
            return payload
        else:
            raise HTTPException(status_code=403, detail="Invalid authorization code")
