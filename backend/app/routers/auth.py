import os
import httpx
import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from ..config import settings

# URL do frontend para redirecionamento pós-login (produção na Render usa domínio separado)
FRONTEND_URL = os.getenv("FRONTEND_URL", "")
# Detecta se está em produção (HTTPS) para configurar cookies seguros
IS_PRODUCTION = os.getenv("RENDER", "") == "true" or FRONTEND_URL.startswith("https")
from ..database import get_db
from ..models import User, RefreshToken
from ..schemas import UserCreate, UserProfileUpdate, UserResponse, UserUpdate
from ..auth_utils import (
    create_access_token, 
    create_refresh_token, 
    log_auth_event, 
    get_current_user,
    require_role
)

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.get("/authorize")
async def authorize(role: str | None = None):
    """Redireciona o usuário para a página de autorização do SUAP."""
    # Em modo mock (demo/apresentação), pula o SUAP e vai direto pro callback
    if settings.SUAP_CLIENT_ID == "mock_client_id":
        target_role = role if role in ["student", "advisor", "coordinator", "admin"] else "advisor"
        mock_callback_url = f"{settings.SUAP_REDIRECT_URI}?code=mock_code_{target_role}"
        return RedirectResponse(url=mock_callback_url)
    
    authorize_url = (
        f"{settings.SUAP_AUTHORIZE_URL}?"
        f"response_type=code&"
        f"client_id={settings.SUAP_CLIENT_ID}&"
        f"redirect_uri={settings.SUAP_REDIRECT_URI}&"
        f"scope=identificacao email"
    )
    return RedirectResponse(url=authorize_url)

@router.get("/callback")
async def callback(request: Request, response: Response, code: str, db: AsyncSession = Depends(get_db)):
    """Callback do SUAP. Troca o 'code' por token de acesso e sincroniza dados do usuário."""
    if not code:
        await log_auth_event(db, "unknown", "login_failure", metadata_json={"reason": "Missing code"})
        raise HTTPException(status_code=400, detail="Código de autorização ausente.")

    # 1. Simulação para Testes (BFF Mock se client_id for de teste/mock)
    is_mock = settings.SUAP_CLIENT_ID == "mock_client_id" or code.startswith("mock_code_")
    
    suap_user_data = None
    if is_mock:
        # Mock de dados do SUAP para facilitar testes locais e automatizados
        mock_role = "advisor"
        if "student" in code:
            mock_role = "student"
        elif "coordinator" in code:
            mock_role = "coordinator"
        elif "admin" in code:
            mock_role = "admin"

        mock_id = {
            "student": "12345",
            "advisor": "54321",
            "coordinator": "99999",
            "admin": "88888"
        }[mock_role]

        mock_name = {
            "student": "Aluno de Teste",
            "advisor": "Professor Orientador",
            "coordinator": "Coordenador Geral",
            "admin": "Administrador do Sistema"
        }[mock_role]

        mock_email = {
            "student": "aluno.teste@ifal.edu.br",
            "advisor": "orientador.teste@ifal.edu.br",
            "coordinator": "coordenador.teste@ifal.edu.br",
            "admin": "admin.teste@ifal.edu.br"
        }[mock_role]
        
        suap_user_data = {
            "suap_id": mock_id,
            "name": mock_name,
            "email": mock_email,
            "role": mock_role,
            "avatar_url": None
        }
    else:
        # 2. Comunicação real com a API do SUAP
        async with httpx.AsyncClient() as client:
            # Troca o authorization code pelo access token do SUAP
            token_payload = {
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": settings.SUAP_REDIRECT_URI,
                "client_id": settings.SUAP_CLIENT_ID,
                "client_secret": settings.SUAP_CLIENT_SECRET
            }
            try:
                token_resp = await client.post(settings.SUAP_TOKEN_URL, data=token_payload)
                if token_resp.status_code != 200:
                    await log_auth_event(db, "unknown", "login_failure", metadata_json={"reason": "SUAP token exchange failed", "response": token_resp.text})
                    raise HTTPException(status_code=401, detail="Falha ao trocar código pelo token no SUAP.")
                
                suap_tokens = token_resp.json()
                suap_access_token = suap_tokens.get("access_token")
                
                # Obtém as informações do usuário logado usando o token obtido
                headers = {"Authorization": f"Bearer {suap_access_token}"}
                user_data_resp = await client.get(settings.SUAP_USER_DATA_URL, headers=headers)
                if user_data_resp.status_code != 200:
                    await log_auth_event(db, "unknown", "login_failure", metadata_json={"reason": "Failed to get SUAP user data"})
                    raise HTTPException(status_code=401, detail="Falha ao obter dados do usuário do SUAP.")
                
                raw_data = user_data_resp.json()
                
                # Mapeia os dados do SUAP para a estrutura da aplicação
                # Vínculo típico no SUAP pode ajudar a definir o papel (role)
                vinculo = raw_data.get("tipo_vinculo", "aluno").lower()
                role = "student"
                if "docente" in vinculo or "professor" in vinculo:
                    role = "advisor"
                elif "tecnico" in vinculo or "administrador" in vinculo:
                    role = "admin"
                
                suap_user_data = {
                    "suap_id": str(raw_data.get("matricula")),
                    "name": raw_data.get("nome_usual") or raw_data.get("nome"),
                    "email": raw_data.get("email"),
                    "role": role,
                    "avatar_url": raw_data.get("url_foto_150x200")
                }
            except Exception as e:
                await log_auth_event(db, "unknown", "login_failure", metadata_json={"reason": "Exception during SUAP communication", "error": str(e)})
                raise HTTPException(status_code=500, detail="Erro interno na comunicação com o SUAP.")

    if not suap_user_data or not suap_user_data.get("email"):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Dados de usuário SUAP incompletos.")

    # 3. Cria ou atualiza o usuário no banco de dados local
    result = await db.execute(select(User).where(User.suap_id == suap_user_data["suap_id"]))
    db_user = result.scalars().first()

    if not db_user:
        db_user = User(
            suap_id=suap_user_data["suap_id"],
            name=suap_user_data["name"],
            email=suap_user_data["email"],
            role=suap_user_data["role"],
            avatar_url=suap_user_data["avatar_url"],
            is_active=True
        )
        db.add(db_user)
    else:
        # Atualiza informações que podem ter mudado
        db_user.name = suap_user_data["name"]
        db_user.email = suap_user_data["email"]
        db_user.avatar_url = suap_user_data["avatar_url"]
        
    await db.commit()
    await db.refresh(db_user)

    # 4. Gera tokens locais
    access_token = create_access_token(data={"sub": str(db_user.id)})
    refresh_token = await create_refresh_token(db, db_user.id)

    # 5. Registra auditoria
    await log_auth_event(
        db, 
        email=db_user.email, 
        action="login_success", 
        user_id=db_user.id, 
        request=request,
        metadata_json={"suap_id": db_user.suap_id}
    )

    # 6. Cria resposta de redirecionamento para o frontend (BFF Cookie setting)
    # Em produção (Render), redireciona para a URL do frontend (domínio separado)
    # Em dev local, redireciona para "/" (mesmo domínio via proxy do Vite)
    fe_redirect_url = FRONTEND_URL if FRONTEND_URL else "/"
    redirect_response = RedirectResponse(url=fe_redirect_url)
    
    # Em produção (HTTPS/Render), cookies precisam de secure=True e samesite="none"
    # para funcionar cross-origin entre frontend e backend em domínios diferentes
    cookie_secure = IS_PRODUCTION
    cookie_samesite = "none" if IS_PRODUCTION else "lax"
    
    # Define cookies httpOnly com tempo de vida correspondente
    redirect_response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=15 * 60,  # 15 min
        expires=15 * 60,
        samesite=cookie_samesite,
        secure=cookie_secure
    )
    redirect_response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        max_age=30 * 60,  # 30 min
        expires=30 * 60,
        samesite=cookie_samesite,
        secure=cookie_secure
    )

    return redirect_response

@router.post("/logout")
async def logout(request: Request, response: Response, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Finaliza a sessão do usuário limpando os cookies e invalidando o refresh token."""
    # Remove refresh tokens do banco
    rt_cookie = request.cookies.get("refresh_token")
    if rt_cookie:
        result = await db.execute(select(RefreshToken).where(RefreshToken.token == rt_cookie))
        db_rt = result.scalars().first()
        if db_rt:
            await db.delete(db_rt)
            await db.commit()

    # Grava auditoria
    await log_auth_event(
        db,
        email=current_user.email,
        action="logout",
        user_id=current_user.id,
        request=request
    )

    # Limpa os cookies
    res = JSONResponse(content={"message": "Logout efetuado com sucesso."})
    res.delete_cookie(key="access_token", path="/")
    res.delete_cookie(key="refresh_token", path="/")
    return res

@router.get("/me", response_model=UserResponse)
async def me(current_user: User = Depends(get_current_user)):
    """Retorna dados do usuário atualmente logado."""
    return current_user

@router.put("/me", response_model=UserResponse)
async def update_profile(
    profile_in: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Atualiza dados do perfil do usuário logado."""
    if profile_in.name is not None:
        current_user.name = profile_in.name
    if profile_in.email is not None:
        current_user.email = profile_in.email
    if profile_in.avatar_url is not None:
        current_user.avatar_url = profile_in.avatar_url

    await db.commit()
    await db.refresh(current_user)
    return current_user

@router.get("/users", response_model=list[UserResponse])
async def list_users(role: str | None = None, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retorna a lista de usuários ativos, opcionalmente filtrada por papel (role)."""
    query = select(User).where(User.is_active == True)
    if role:
        query = query.where(User.role == role)
    result = await db.execute(query)
    return result.scalars().all()

@router.post("/users", response_model=UserResponse, status_code=201)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Cria um novo usuário. Apenas administradores."""
    existing = await db.execute(
        select(User).where((User.email == user_in.email) | (User.suap_id == user_in.suap_id))
    )
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Já existe um usuário com este email ou SUAP ID.")

    db_user = User(
        suap_id=user_in.suap_id,
        name=user_in.name,
        email=user_in.email,
        role=user_in.role,
        avatar_url=user_in.avatar_url,
        is_active=True
    )
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: uuid.UUID,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Atualiza dados de um usuário. Apenas administradores."""
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    if user_in.name is not None:
        db_user.name = user_in.name
    if user_in.email is not None:
        db_user.email = user_in.email
    if user_in.role is not None:
        db_user.role = user_in.role
    if user_in.is_active is not None:
        db_user.is_active = user_in.is_active

    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.patch("/users/{user_id}/toggle-active", response_model=UserResponse)
async def toggle_user_active(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Ativa/desativa um usuário. Apenas administradores."""
    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")
    if db_user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Você não pode desativar sua própria conta.")

    db_user.is_active = not db_user.is_active
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/users/{user_id}", status_code=204)
async def delete_user(
    user_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_role(["admin"]))
):
    """Remove um usuário do sistema. Apenas administradores."""
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="Você não pode remover sua própria conta.")

    result = await db.execute(select(User).where(User.id == user_id))
    db_user = result.scalars().first()
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado.")

    await db.delete(db_user)
    await db.commit()


@router.post("/refresh")
async def refresh(request: Request, response: Response, db: AsyncSession = Depends(get_db)):
    """Atualiza o access token a partir do refresh token do cookie."""
    refresh_token_str = request.cookies.get("refresh_token")
    if not refresh_token_str:
        raise HTTPException(status_code=401, detail="Refresh token ausente.")

    # Busca o token no banco de dados
    result = await db.execute(
        select(RefreshToken)
        .where(RefreshToken.token == refresh_token_str)
        .where(RefreshToken.expires_at > datetime.utcnow())
    )
    db_rt = result.scalars().first()
    if not db_rt:
        raise HTTPException(status_code=401, detail="Sessão expirada por inatividade.")

    # Recupera o usuário
    result_user = await db.execute(select(User).where(User.id == db_rt.user_id))
    user = result_user.scalars().first()
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="Usuário inativo ou não encontrado.")

    # Gera um novo access_token e rotaciona o refresh token
    new_access_token = create_access_token(data={"sub": str(user.id)})
    new_refresh_token_str = str(uuid.uuid4())
    
    # Atualiza o refresh token existente
    db_rt.token = new_refresh_token_str
    db_rt.expires_at = datetime.utcnow() + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
    await db.commit()

    # Grava log de auditoria
    await log_auth_event(
        db,
        email=user.email,
        action="token_refresh",
        user_id=user.id,
        request=request
    )

    cookie_secure = IS_PRODUCTION
    cookie_samesite = "none" if IS_PRODUCTION else "lax"
    
    res = JSONResponse(content={"message": "Token renovado."})
    res.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        max_age=15 * 60,
        expires=15 * 60,
        samesite=cookie_samesite,
        secure=cookie_secure
    )
    res.set_cookie(
        key="refresh_token",
        value=new_refresh_token_str,
        httponly=True,
        max_age=30 * 60,
        expires=30 * 60,
        samesite=cookie_samesite,
        secure=cookie_secure
    )
    return res
