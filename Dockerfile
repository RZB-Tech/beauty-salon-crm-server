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
COPY migrate.py .

RUN mkdir -p /app/secrets && \
    openssl genpkey \
        -algorithm RSA \
        -out /app/secrets/private_key.pem \
        -pkeyopt rsa_keygen_bits:4096 && \
    openssl rsa \
        -pubout \
        -in /app/secrets/private_key.pem \
        -out /app/secrets/public_key.pem

RUN chmod +x entrypoint.sh

EXPOSE 8000
CMD ["./entrypoint.sh"]
# CMD ["uv", "run", "--", "uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
