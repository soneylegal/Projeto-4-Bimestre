import pytest
from sqlalchemy.future import select
from app.models import User, RefreshToken, AuthAuditLog

@pytest.mark.asyncio
async def test_authorize_redirect(client):
    """Testa se a rota authorize redireciona corretamente para o SUAP."""
    response = await client.get("/api/auth/authorize", follow_redirects=False)
    assert response.status_code == 307
    location = response.headers.get("location")
    assert "suap.ifal.edu.br" in location
    assert "response_type=code" in location

@pytest.mark.asyncio
async def test_callback_mock_login_student(client, db_session):
    """Testa o callback com mock code do estudante, verificando a criação de usuário e cookies."""
    response = await client.get("/api/auth/callback?code=mock_code_student", follow_redirects=False)
    assert response.status_code == 307
    
    # Verifica os cookies de sessão definidos pelo BFF
    assert "access_token" in response.cookies
    assert "refresh_token" in response.cookies
    
    # Verifica se o usuário foi criado no banco
    result = await db_session.execute(select(User).where(User.suap_id == "12345"))
    user = result.scalars().first()
    assert user is not None
    assert user.role == "student"
    assert user.email == "aluno.teste@ifal.edu.br"
    
    # Verifica o log de auditoria
    result_audit = await db_session.execute(select(AuthAuditLog).where(AuthAuditLog.user_id == user.id))
    audit = result_audit.scalars().first()
    assert audit is not None
    assert audit.action == "login_success"

@pytest.mark.asyncio
async def test_callback_mock_login_advisor(client, db_session):
    """Testa o callback com mock code do orientador, verificando a criação de usuário com papel correto."""
    response = await client.get("/api/auth/callback?code=mock_code_advisor", follow_redirects=False)
    assert response.status_code == 307
    
    # Verifica se o usuário foi criado no banco
    result = await db_session.execute(select(User).where(User.suap_id == "54321"))
    user = result.scalars().first()
    assert user is not None
    assert user.role == "advisor"
    assert user.email == "orientador.teste@ifal.edu.br"

@pytest.mark.asyncio
async def test_me_endpoint_unauthorized(client):
    """Testa se a rota /me retorna 401 quando não autenticado."""
    response = await client.get("/api/auth/me")
    assert response.status_code == 401

@pytest.mark.asyncio
async def test_me_endpoint_authorized(client):
    """Testa se a rota /me retorna dados corretos após login bem-sucedido."""
    # 1. Faz login
    login_resp = await client.get("/api/auth/callback?code=mock_code_student", follow_redirects=False)
    assert login_resp.status_code == 307
    
    # 2. Faz requisição para o /me mantendo os cookies gerados
    client.cookies.update(login_resp.cookies)
    response = await client.get("/api/auth/me")
    assert response.status_code == 200
    
    data = response.json()
    assert data["email"] == "aluno.teste@ifal.edu.br"
    assert data["role"] == "student"
    assert data["suap_id"] == "12345"

@pytest.mark.asyncio
async def test_logout_endpoint(client, db_session):
    """Testa o logout, garantindo a remoção de cookies e invalidação do refresh token."""
    # 1. Login
    login_resp = await client.get("/api/auth/callback?code=mock_code_student", follow_redirects=False)
    client.cookies.update(login_resp.cookies)
    
    # Confirma que refresh token existe no banco
    rt_cookie = login_resp.cookies.get("refresh_token")
    result_rt_before = await db_session.execute(select(RefreshToken).where(RefreshToken.token == rt_cookie))
    assert result_rt_before.scalars().first() is not None
    
    # 2. Logout
    logout_resp = await client.post("/api/auth/logout")
    assert logout_resp.status_code == 200
    
    # Verifica que cookies foram instruídos a serem limpos
    assert logout_resp.cookies.get("access_token") == "" or "access_token" not in logout_resp.cookies
    
    # Verifica que o refresh token foi deletado do banco
    result_rt_after = await db_session.execute(select(RefreshToken).where(RefreshToken.token == rt_cookie))
    assert result_rt_after.scalars().first() is None

@pytest.mark.asyncio
async def test_token_refresh(client, db_session):
    """Testa o fluxo de renovação de sessão usando refresh token."""
    # 1. Login
    login_resp = await client.get("/api/auth/callback?code=mock_code_student", follow_redirects=False)
    
    # 2. Envia requisição de refresh com o cookie do refresh_token
    client.cookies.clear() # Limpa os cookies do client
    client.cookies.set("refresh_token", login_resp.cookies.get("refresh_token"))
    
    refresh_resp = await client.post("/api/auth/refresh")
    assert refresh_resp.status_code == 200
    assert "access_token" in refresh_resp.cookies
    assert "refresh_token" in refresh_resp.cookies
    
    # Verifica se o refresh token antigo foi substituído
    old_rt = login_resp.cookies.get("refresh_token")
    new_rt = refresh_resp.cookies.get("refresh_token")
    assert old_rt != new_rt
    
    # Confirma que o novo refresh token está no banco
    result_rt = await db_session.execute(select(RefreshToken).where(RefreshToken.token == new_rt))
    assert result_rt.scalars().first() is not None
