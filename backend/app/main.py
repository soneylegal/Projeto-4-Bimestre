from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import auth, projects, tasks, submissions, reports
from .config import settings

app = FastAPI(
    title="IFAL Projetos API",
    description="Backend para gestão de projetos acadêmicos no IFAL",
    version="1.0.0"
)

# Configuração de CORS parametrizável para desenvolvimento e produção
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registra os roteadores
app.include_router(auth.router)
app.include_router(projects.router)
app.include_router(tasks.router)
app.include_router(submissions.router)
app.include_router(reports.router)

@app.on_event("startup")
async def startup():
    # Cria as tabelas de forma assíncrona no banco de dados na inicialização da app
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "service": "ifal-projetos-api"}
