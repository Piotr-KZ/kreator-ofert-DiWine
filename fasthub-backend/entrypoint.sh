#!/bin/bash
set -e

# Load .env.production if it exists and DATABASE_URL is empty
if [ -z "$DATABASE_URL" ] && [ -f "/app/.env.production" ]; then
    echo "=== LOADING .env.production (Railway env vars not available) ==="
    export $(cat /app/.env.production | grep -v '^#' | xargs)
fi

# Decode Base64 encoded variables if they exist
if [ -n "$DATABASE_URL_BASE64" ]; then
    DATABASE_URL=$(echo "$DATABASE_URL_BASE64" | base64 -d)
fi

if [ -n "$BACKEND_CORS_ORIGINS_BASE64" ]; then
    BACKEND_CORS_ORIGINS=$(echo "$BACKEND_CORS_ORIGINS_BASE64" | base64 -d)
fi

# Generate .env file from environment variables
echo "Generating .env file from environment variables..."
cat > /app/.env << EOF
DATABASE_URL=${DATABASE_URL}
SECRET_KEY=${SECRET_KEY}
ENVIRONMENT=${ENVIRONMENT}
BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}
EOF

echo "=== DEBUG ==="
echo "DATABASE_URL=${DATABASE_URL}"
echo "SECRET_KEY=${SECRET_KEY}"
echo "ENVIRONMENT=${ENVIRONMENT}"
echo "BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}"
echo "============"

# Run database migrations
echo "Running database migrations..."
alembic upgrade head
echo "Migrations completed!"

# Execute the command passed to the script
exec "$@"
