# Obraz bazowy - Python 3.11 na lekkim systemie Linux
FROM python:3.11-slim

# Ustawienie katalogu roboczego
WORKDIR /app

# Instalacja zależności systemowych (potrzebne dla niektórych bibliotek Python )
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

# Port na którym działa backend
EXPOSE 8000

# Komenda uruchamiająca backend (z auto-reload dla development)
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
