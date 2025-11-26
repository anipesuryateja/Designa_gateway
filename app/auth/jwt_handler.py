# app/auth/jwt_handler.py
from datetime import datetime, timedelta
from jose import JWTError, jwt
from app.config import settings

def create_access_token(data: dict):
    to_encode = data.copy()
    expire_minutes = int(settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None
