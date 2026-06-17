import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente a partir do arquivo .env
load_dotenv()
# Caso seja executado de dentro da subpasta backend/
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

def _normalize_database_url(url: str) -> str:
    """Converte 'postgres://' ou 'postgresql://' para 'postgresql+asyncpg://'
    necessário pelo SQLAlchemy assíncrono. Render fornece o formato curto."""
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+asyncpg://", 1)
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url

class Settings:
    DATABASE_URL: str = _normalize_database_url(os.getenv("DATABASE_URL", ""))
    SUAP_CLIENT_ID: str = os.getenv("SUAP_CLIENT_ID", "")
    SUAP_CLIENT_SECRET: str = os.getenv("SUAP_CLIENT_SECRET", "")
    SUAP_REDIRECT_URI: str = os.getenv("SUAP_REDIRECT_URI", "")
    
    JWT_SECRET: str = os.getenv("JWT_SECRET", "")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "15"))
    REFRESH_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_MINUTES", "30"))
    
    SUAP_BASE_URL: str = os.getenv("SUAP_BASE_URL", "https://suap.ifal.edu.br")
    SUAP_AUTHORIZE_URL: str = f"{SUAP_BASE_URL}/o/authorize/"
    SUAP_TOKEN_URL: str = f"{SUAP_BASE_URL}/o/token/"
    SUAP_USER_DATA_URL: str = f"{SUAP_BASE_URL}/api/v2/minhas-informacoes/meus-dados/"
    
    CORS_ALLOWED_ORIGINS: list[str] = [
        o.strip() for o in os.getenv(
            "CORS_ALLOWED_ORIGINS",
            "http://localhost:5173,http://localhost:3000,http://localhost"
        ).split(",") if o.strip()
    ]

settings = Settings()

