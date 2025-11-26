import os
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

load_dotenv()
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
class Settings(BaseSettings):
    SECRET_KEY: str = Field(..., env="SECRET_KEY")
    ALGORITHM: str = Field("HS256", env="ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(1440, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    DESIGNA_USER: str = Field(..., env="DESIGNA_USER")
    DESIGNA_PASSWORD: str = Field(..., env="DESIGNA_PASSWORD")
    DESIGNA_WSDL_CASHPOINT_URL: str = Field(..., env="DESIGNA_WSDL_CASHPOINT_URL")
    DESIGNA_TCC_ENTRY: int = Field(15, env="DESIGNA_TCC_ENTRY")
    DESIGNA_TCC_EXIT: int = Field(20, env="DESIGNA_TCC_EXIT")
    DESIGNA_SSL_VERIFY: bool = Field(False, env="DESIGNA_SSL_VERIFY")
    # DESIGNA_USER = os.getenv("DESIGNA_USER")
    # DESIGNA_PASSWORD = os.getenv("DESIGNA_PASSWORD")
    # DESIGNA_WSDL_CASHPOINT_URL = os.getenv("DESIGNA_WSDL_CASHPOINT_URL")
    # DESIGNA_TCC_EXIT = int(os.getenv("DESIGNA_TCC_EXIT", "20"))
    # DESIGNA_SSL_VERIFY = os.getenv("DESIGNA_SSL_VERIFY", "False").lower() == "true"
    

class Config:
        env_file = ".env"
        extra = "allow"
settings = Settings()
