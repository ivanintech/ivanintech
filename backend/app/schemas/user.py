from pydantic import BaseModel, EmailStr
from typing import Optional

# Propiedades compartidas
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    # Podrías añadir más campos como full_name aquí

# Propiedades para recibir en creación
class UserCreate(UserBase):
    email: EmailStr
    password: str

# Propiedades para recibir en actualización
class UserUpdate(UserBase):
    password: Optional[str] = None

# Propiedades almacenadas en DB pero no necesariamente retornadas
class UserInDBBase(UserBase):
    id: int | str # Podría ser int si es autoincremental
    hashed_password: str

    class Config:
        # orm_mode = True # Sintaxis antigua para Pydantic V1
        from_attributes = True # Sintaxis nueva para Pydantic V2+

# Propiedades adicionales para retornar al cliente (lectura)
class User(UserInDBBase):
    # Excluimos hashed_password por defecto al retornar
    # from_attributes = True ya se hereda de UserInDBBase
    pass

# --- Nuevo Schema para cambio de contraseña ---
class NewPassword(BaseModel):
    token: str
    new_password: str

# Propiedades adicionales almacenadas en DB (no expuestas)
# class UserInDB(UserInDBBase):
#     pass 