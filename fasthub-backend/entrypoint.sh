#!/bin/bash
set -e

# Generate .env file from environment variables
echo "Generating .env file from Railway environment variables..."
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

# Execute the command passed to the script
exec "$@"
