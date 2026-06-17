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
RUN touch README.md && mkdir app && touch app/__init__.py
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir .[test] && \
    pip uninstall -y ifal-projetos-backend

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
COPY migrations ./migrations
COPY alembic.ini ./alembic.ini

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
