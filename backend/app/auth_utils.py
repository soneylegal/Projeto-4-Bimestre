import uuid
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
from fastapi import Request, Depends, HTTPException, status
from fastapi.security import APIKeyCookie
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .config import settings
from .database import get_db
from .models import User, RefreshToken, AuthAuditLog

# Configuração da segurança para leitura de cookie
cookie_sec = APIKeyCookie(name="access_token", auto_error=False)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt

async def create_refresh_token(db: AsyncSession, user_id: uuid.UUID) -> str:
    token_str = str(uuid.uuid4())
    expires_at = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    
    # Salva o refresh token no banco
    db_token = RefreshToken(
        user_id=user_id,
        token=token_str,
        expires_at=expires_at
    )
    db.add(db_token)
    await db.commit()
    return token_str

async def log_auth_event(
    db: AsyncSession,
    email: str,
    action: str,
    user_id: Optional[uuid.UUID] = None,
    request: Optional[Request] = None,
    metadata_json: Optional[dict] = None
):
    ip_address = None
    user_agent = None
    if request:
        ip_address = request.client.host if request.client else None
        user_agent = request.headers.get("user-agent")

    db_log = AuthAuditLog(
        user_id=user_id,
        email=email,
        action=action,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata_json=metadata_json
    )
    db.add(db_log)
    await db.commit()

async def get_current_user(
    request: Request,
    token: Optional[str] = Depends(cookie_sec),
    db: AsyncSession = Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Sessão expirada ou inválida.",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Se o token não veio no header/cookie, tenta buscar nos cookies do request diretamente
    if not token:
        token = request.cookies.get("access_token")
        
    if not token:
        raise credentials_exception

    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id_str: str = payload.get("sub")
        if user_id_str is None:
            raise credentials_exception
        user_id = uuid.UUID(user_id_str)
    except (JWTError, ValueError):
        raise credentials_exception

    # Busca usuário no banco
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if user is None or not user.is_active:
        raise credentials_exception
        
    return user

def require_role(allowed_roles: list[str]):
    """Garante que o usuário logado possui um dos papéis (roles) permitidos."""
    async def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Acesso negado. Perfil não possui permissão para esta ação."
            )
        return current_user
    return dependency
