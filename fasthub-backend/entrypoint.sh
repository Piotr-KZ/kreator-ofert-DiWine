#!/bin/bash
set -e

# Fallback: load .env if DATABASE_URL not set via environment
if [ -z "$DATABASE_URL" ] && [ -f "/app/.env" ]; then
    echo "=== Loading .env (environment vars not available) ==="
    set -a
    . /app/.env
    set +a
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

# Debug info (only in development, secrets masked)
if [ "$ENVIRONMENT" = "development" ]; then
    echo "=== DEBUG (dev only) ==="
    echo "DATABASE_URL=***masked***"
    echo "SECRET_KEY=***masked***"
    echo "ENVIRONMENT=${ENVIRONMENT}"
    echo "BACKEND_CORS_ORIGINS=${BACKEND_CORS_ORIGINS}"
    echo "========================"
fi

# Run database migrations
echo "Running database migrations..."
alembic upgrade head
echo "Migrations completed!"

# Execute the command passed to the script
exec "$@"
