import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://ifal_user:ifal_password@localhost:5432/ifal_projetos")

# Render fornece DATABASE_URL com prefixo 'postgres://' ou 'postgresql://'.
# SQLAlchemy assíncrono requer o dialeto 'postgresql+asyncpg://'.
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

# Cria o engine assíncrono para PostgreSQL
engine = create_async_engine(DATABASE_URL, echo=True)

# Configura o gerador de sessões assíncronas
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

Base = declarative_base()

# Dependency para injeção da sessão do banco nos endpoints do FastAPI
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
