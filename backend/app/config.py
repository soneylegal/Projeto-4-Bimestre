import os
from dotenv import load_dotenv

# Carrega as variáveis de ambiente a partir do arquivo .env
load_dotenv()
# Caso seja executado de dentro da subpasta backend/
load_dotenv(os.path.join(os.path.dirname(__file__), "../../.env"))

class Settings:
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")
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

settings = Settings()
