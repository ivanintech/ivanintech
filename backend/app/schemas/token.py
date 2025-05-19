from pydantic import BaseModel
from typing import Optional
from app.schemas.user import User  # Importar el schema User

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[int | str] = None # Subject (user ID) 

# Nuevo schema para la respuesta del login
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: User  # Incluir la información del usuario 