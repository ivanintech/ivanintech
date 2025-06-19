from pydantic import BaseModel
from typing import Optional
from .user import User  # Importar el schema de User

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenPayload(BaseModel):
    sub: int

# Schema para la respuesta completa del login
class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User

# Schema for receiving a social auth token
class SocialToken(BaseModel):
    token: str

# Schema for receiving a social auth code (for GitHub flow)
class SocialCode(BaseModel):
    code: str 