from pydantic import BaseModel, EmailStr, HttpUrl
from typing import Optional, Literal
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    name: str
    email: EmailStr
    role: Literal['admin', 'coordinator', 'advisor', 'student']
    avatar_url: Optional[str] = None

class UserCreate(UserBase):
    suap_id: str

class UserResponse(UserBase):
    id: UUID
    suap_id: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class TokenResponse(BaseModel):
    user: UserResponse
    # O access token será enviado por cookie httpOnly, mas opcionalmente retornamos aqui os dados do user
    # Para o front-end saber que está logado. O JSON retornado no callback/me conterá o user.
