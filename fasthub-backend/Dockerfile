# Obraz bazowy - Python 3.11 na lekkim systemie Linux
FROM python:3.11-slim

# Ustawienie katalogu roboczego
WORKDIR /app

# Instalacja zależności systemowych (potrzebne dla niektórych bibliotek Python)
RUN apt-get update && apt-get install -y \
    postgresql-client \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Kopiowanie requirements.txt (lista bibliotek Python)
COPY requirements.txt .

# Instalacja bibliotek Python
RUN pip install --no-cache-dir -r requirements.txt

# Kopiowanie całego kodu backendu
COPY . .

# Port na którym działa backend (Railway automatycznie ustawi $PORT)
EXPOSE 8000

# Debug: Check if Railway passes DATABASE_URL
# Skip alembic temporarily to test if backend can start
CMD ["sh", "-c", "echo '=== DEBUG ===' && echo 'DATABASE_URL='$DATABASE_URL && echo 'SECRET_KEY='$SECRET_KEY && echo 'ENVIRONMENT='$ENVIRONMENT && echo 'BACKEND_CORS_ORIGINS='$BACKEND_CORS_ORIGINS && echo '============' && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
