from pydantic import BaseModel, EmailStr
from typing import Optional

# Propiedades compartidas
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    website_url: Optional[str] = None
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
    id: Optional[int] = None

    class Config:
        orm_mode = True

# Propiedades adicionales para retornar al cliente (lectura)
class User(UserInDBBase):
    # Excluimos hashed_password por defecto al retornar
    # from_attributes = True ya se hereda de UserInDBBase
    pass

# --- Nuevo Schema para cambio de contraseña ---
class NewPassword(BaseModel):
    token: str
    new_password: str

# Schema para la información pública del usuario que se puede anidar.
class UserPublic(BaseModel):
    id: int
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    website_url: Optional[str] = None

    class Config:
        orm_mode = True

# Propiedades adicionales para almacenar en la BD
class UserInDB(UserInDBBase):
    hashed_password: str

class UserWithAvatar(BaseModel):
    avatar_url: str 