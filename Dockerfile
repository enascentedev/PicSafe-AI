FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH"

RUN pip install --no-cache-dir uv==0.8.4 \
    && groupadd --system picsafe \
    && useradd --system --gid picsafe --home-dir /app picsafe

WORKDIR /app
COPY pyproject.toml uv.lock README.md ./
RUN uv sync --frozen --no-dev --no-install-project

COPY src ./src
RUN uv sync --frozen --no-dev \
    && mkdir -p /app/reports /app/temp \
    && chown -R picsafe:picsafe /app/reports /app/temp

USER picsafe
EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD ["python", "-c", "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=3)"]

CMD ["uvicorn", "picsafe_ai.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
