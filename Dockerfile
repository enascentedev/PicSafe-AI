# Dockerfile para PicSafe AI
FROM python:3.10-slim

# Configurações de ambiente
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_CACHE_DIR=/tmp/uv-cache

# Instalar sistema de dependências
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    libgtk2.0-dev \
    && rm -rf /var/lib/apt/lists/*

# Instalar uv
RUN pip install uv

# Criar usuário não-root
RUN useradd --create-home --shell /bin/bash picsafe
USER picsafe

# Diretório de trabalho
WORKDIR /app

# Copiar arquivos de dependências
COPY --chown=picsafe:picsafe pyproject.toml ./

# Instalar dependências Python
RUN uv sync --no-install-project --no-dev

# Copiar código fonte
COPY --chown=picsafe:picsafe src/ ./src/
COPY --chown=picsafe:picsafe config.env ./

# Criar diretórios necessários
RUN mkdir -p uploads reports temp

# Expor porta
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando de execução
CMD ["uv", "run", "uvicorn", "src.picsafe_ai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
