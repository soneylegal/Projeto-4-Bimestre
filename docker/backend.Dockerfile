# Stage 1: Builder
FROM python:3.11-slim AS builder

WORKDIR /build

# Instala ferramentas de compilação necessárias
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Cria ambiente virtual
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copia e instala as dependências definidas no pyproject.toml
COPY pyproject.toml .
RUN pip install --no-cache-dir --upgrade pip && \
    python -c "import tomllib; p = tomllib.load(open('pyproject.toml', 'rb')); print('\n'.join(p.get('project', {}).get('dependencies', []) + p.get('project', {}).get('optional-dependencies', {}).get('test', [])))" > requirements.txt && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim AS runtime

WORKDIR /app

# Copia venv do builder
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Variáveis de ambiente padrão do Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Copia o código-fonte da aplicação
COPY app ./app
COPY tests ./tests
COPY alembic.ini ./alembic.ini
COPY migrations ./migrations

EXPOSE 8000

CMD uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}

