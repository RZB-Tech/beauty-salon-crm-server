FROM python:3.14-alpine

WORKDIR /app

RUN apk add --no-cache \
    openssl \
    postgresql17-client

COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev

COPY src ./src
COPY alembic.ini .
COPY entrypoint.sh .
COPY migrate_docker.py .
COPY manage_tenants.py .

RUN chmod +x entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]
# CMD ["uv", "run", "--", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
