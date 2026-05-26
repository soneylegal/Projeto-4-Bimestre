import asyncio
import pytest
import pytest_asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from httpx import AsyncClient, ASGITransport

from app.database import Base, get_db
from app.main import app
from app.config import settings

# Garante configurações controladas/seguras para os testes automatizados independente de .env
settings.JWT_SECRET = "test_secret_key_for_jwt_only_in_tests_1234567890"
settings.SUAP_CLIENT_ID = "mock_client_id"
settings.SUAP_CLIENT_SECRET = "mock_client_secret"
settings.SUAP_REDIRECT_URI = "http://test/api/auth/callback"

# Banco de dados SQLite assíncrono para fins de testes
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_engine():
    engine = create_async_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def db_session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    """Cria uma sessão limpa para cada teste."""
    async_session = async_sessionmaker(
        bind=test_engine,
        class_=AsyncSession,
        expire_on_commit=False
    )
    async with async_session() as session:
        yield session
        # Faz rollback automático para garantir isolamento entre testes
        await session.rollback()

@pytest_asyncio.fixture
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Cria um cliente assíncrono HTTPX apontando para o app e com injeção do banco de testes."""
    
    # Sobrescreve a dependência get_db do FastAPI para usar a sessão do banco de teste
    async def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    # Usando ASGITransport para despachar requisições direto na aplicação FastAPI
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
        
    app.dependency_overrides.clear()
