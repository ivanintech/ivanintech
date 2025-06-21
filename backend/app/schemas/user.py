from pydantic import BaseModel, EmailStr, computed_field
from typing import Optional

from app.core.config import settings

# Propiedades compartidas
class UserBase(BaseModel):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = True
    is_superuser: bool = False
    full_name: Optional[str] = None
    website_url: Optional[str] = None
    avatar_path: Optional[str] = None
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
    @computed_field
    @property
    def avatar_url(self) -> Optional[str]:
        if self.avatar_path:
            base_url = str(settings.SERVER_HOST).rstrip('/')
            return f"{base_url}{self.avatar_path}"
        return None

    class Config:
        from_attributes = True

# --- Nuevo Schema para cambio de contraseña ---
class NewPassword(BaseModel):
    token: str
    new_password: str

# Schema para la información pública del usuario que se puede anidar.
class UserPublic(BaseModel):
    id: int
    full_name: Optional[str] = None
    avatar_path: Optional[str] = None
    website_url: Optional[str] = None

    @computed_field
    @property
    def avatar_url(self) -> Optional[str]:
        if self.avatar_path:
            base_url = str(settings.SERVER_HOST).rstrip('/')
            avatar_path = self.avatar_path.lstrip('/')
            return f"{base_url}/{avatar_path}"
        return None

    class Config:
        orm_mode = True

# Propiedades adicionales para almacenar en la BD
class UserInDB(UserInDBBase):
    hashed_password: str

class UserWithAvatar(BaseModel):
    avatar_url: str 