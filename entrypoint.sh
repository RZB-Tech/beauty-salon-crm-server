#!/bin/sh
set -e

mkdir -p /app/secrets

if [ ! -f /app/secrets/private_key.pem ]; then
    echo "Generating RSA key pair..."
    openssl genpkey \
        -algorithm RSA \
        -out /app/secrets/private_key.pem \
        -pkeyopt rsa_keygen_bits:4096

    openssl rsa \
        -pubout \
        -in /app/secrets/private_key.pem \
        -out /app/secrets/public_key.pem
fi

if [ ! -f /app/secrets/admin_private_key.pem ]; then
    echo "Generating admin RSA key pair..."
    openssl genpkey \
        -algorithm RSA \
        -out /app/secrets/admin_private_key.pem \
        -pkeyopt rsa_keygen_bits:4096

    openssl rsa \
        -pubout \
        -in /app/secrets/admin_private_key.pem \
        -out /app/secrets/admin_public_key.pem
fi

echo "Waiting for postgres"
sleep 10

uv run alembic upgrade head

echo "Starting server"
exec uv run uvicorn src.app:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips="*"