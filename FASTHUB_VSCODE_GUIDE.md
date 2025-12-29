# 📘 FastHub - Instrukcja dla Visual Studio Code (dla nie-programistów)

**Ostatnia aktualizacja:** 27 grudnia 2024

---

## 🎯 Co to jest FastHub?

FastHub to **gotowy szablon aplikacji SaaS** (Software as a Service). Zawiera:
- **Backend** (serwer) - obsługuje logikę, bazę danych, API
- **Frontend** (strona WWW) - interfejs użytkownika w przeglądarce

**Lokalizacja na sandboxie:**
- Backend: `/home/ubuntu/fasthub-backend/`
- Frontend: `/home/ubuntu/fasthub-frontend/`

---

## 📥 KROK 1: Zainstaluj rozszerzenia VS Code

### 1.1 Otwórz Visual Studio Code

### 1.2 Kliknij ikonę "Extensions" (kwadraciki po lewej stronie)
Lub naciśnij:
- **Windows:** `Ctrl + Shift + X`
- **Mac:** `Cmd + Shift + X`

### 1.3 Zainstaluj te 5 rozszerzeń:

#### 1. **Python** (by Microsoft)
- Wpisz w wyszukiwarkę: `Python`
- Znajdź rozszerzenie z logo Microsoft
- Kliknij **Install**
- **Do czego służy:** Podświetla składnię kodu Python, sprawdza błędy

#### 2. **Pylance** (by Microsoft)
- Wpisz: `Pylance`
- Znajdź rozszerzenie z logo Microsoft
- Kliknij **Install**
- **Do czego służy:** Inteligentne podpowiedzi kodu Python

#### 3. **ESLint** (by Microsoft)
- Wpisz: `ESLint`
- Znajdź rozszerzenie z logo Microsoft
- Kliknij **Install**
- **Do czego służy:** Sprawdza błędy w kodzie JavaScript/TypeScript

#### 4. **Prettier - Code formatter** (by Prettier)
- Wpisz: `Prettier`
- Znajdź "Prettier - Code formatter"
- Kliknij **Install**
- **Do czego służy:** Automatyczne formatowanie kodu (ładny wygląd)

#### 5. **Thunder Client** (by Thunder Client)
- Wpisz: `Thunder Client`
- Znajdź rozszerzenie z ikoną pioruna ⚡
- Kliknij **Install**
- **Do czego służy:** Testowanie API (wysyłanie requestów do backendu, sprawdzanie odpowiedzi) - alternatywa dla Postman

---

## 🔌 KROK 2: Połącz się z sandboxem (Remote SSH)

### 2.1 Zainstaluj rozszerzenie "Remote - SSH"
- Wpisz w Extensions: `Remote SSH`
- Znajdź "Remote - SSH" by Microsoft
- Kliknij **Install**

### 2.2 Połącz się z sandboxem
1. Naciśnij `F1` (lub `Ctrl+Shift+P` na Windows / `Cmd+Shift+P` na Mac)
2. Wpisz: `Remote-SSH: Connect to Host`
3. Wybierz `+ Add New SSH Host`
4. Wpisz: `ssh ubuntu@<ADRES_SANDBOXA>`
   - Przykład: `ssh ubuntu@sandbox.manus.im`
5. Wybierz plik konfiguracyjny (domyślny: `~/.ssh/config`)
6. Kliknij "Connect"

**Uwaga:** Będziesz potrzebować hasła lub klucza SSH do sandboxa.

---

## 📂 KROK 3: Otwórz projekt FastHub w VS Code

### Opcja A: Otwórz oba projekty w jednym oknie (POLECANE)

1. Kliknij **File → Open Workspace from File...**
2. Przejdź do: `/home/ubuntu/`
3. Stwórz nowy plik: `fasthub.code-workspace`
4. Wklej tę zawartość:

```json
{
  "folders": [
    {
      "path": "/home/ubuntu/fasthub-backend",
      "name": "Backend (FastAPI)"
    },
    {
      "path": "/home/ubuntu/fasthub-frontend",
      "name": "Frontend (React)"
    }
  ],
  "settings": {
    "python.defaultInterpreterPath": "/home/ubuntu/fasthub-backend/venv/bin/python",
    "editor.formatOnSave": true,
    "editor.codeActionsOnSave": {
      "source.fixAll.eslint": true
    },
    "files.exclude": {
      "**/__pycache__": true,
      "**/*.pyc": true,
      "**/node_modules": true,
      "**/.git": false
    }
  }
}
```

5. Zapisz plik
6. Kliknij **File → Open Workspace from File...**
7. Wybierz `fasthub.code-workspace`

**Efekt:** Zobaczysz 2 foldery w panelu Explorer:
- Backend (FastAPI)
- Frontend (React)

### Opcja B: Otwórz tylko backend

1. Kliknij **File → Open Folder...**
2. Przejdź do: `/home/ubuntu/fasthub-backend`
3. Kliknij **OK**

### Opcja C: Otwórz tylko frontend

1. Kliknij **File → Open Folder...**
2. Przejdź do: `/home/ubuntu/fasthub-frontend`
3. Kliknij **OK**

---

## 🚀 KROK 4: Uruchom Backend (FastAPI)

### 4.1 Otwórz Terminal w VS Code
- Naciśnij: **Ctrl + `** (backtick) lub **View → Terminal**

### 4.2 Przejdź do folderu backend
```bash
cd /home/ubuntu/fasthub-backend
```

### 4.3 Aktywuj wirtualne środowisko Python
```bash
source venv/bin/activate
```

**Efekt:** Zobaczysz `(venv)` przed promptem terminala

### 4.4 Uruchom backend
```bash
./start_backend.sh
```

**Lub ręcznie:**
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4.5 Sprawdź czy działa
Otwórz w przeglądarce:
- **API:** `http://localhost:8000/`
- **Dokumentacja API:** `http://localhost:8000/docs`

**Zobaczysz:**
```json
{
  "message": "FastHub API",
  "version": "1.0.0",
  "status": "running"
}
```

---

## 🎨 KROK 5: Uruchom Frontend (React)

### 5.1 Otwórz nowy Terminal
- Kliknij **+** w panelu terminala (prawy górny róg)
- Lub naciśnij: **Ctrl + Shift + `**

### 5.2 Przejdź do folderu frontend
```bash
cd /home/ubuntu/fasthub-frontend
```

### 5.3 Uruchom frontend
```bash
npm run dev
```

### 5.4 Sprawdź czy działa
Otwórz w przeglądarce:
- **Frontend:** `http://localhost:3001/`

**Zobaczysz:** Stronę FastHub z niebieskim gradientem

---

## 🧪 KROK 6: Testowanie API z Thunder Client

### 6.1 Otwórz Thunder Client
- Kliknij ikonę pioruna ⚡ w lewym panelu VS Code

### 6.2 Stwórz nowy Request
1. Kliknij **New Request**
2. Wybierz metodę: **GET**
3. Wpisz URL: `http://localhost:8000/api/v1/health`
4. Kliknij **Send**

**Odpowiedź:**
```json
{
  "status": "healthy",
  "service": "FastHub",
  "version": "1.0.0",
  "timestamp": "2024-12-27T12:00:00"
}
```

### 6.3 Test logowania
1. Stwórz nowy Request
2. Wybierz metodę: **POST**
3. Wpisz URL: `http://localhost:8000/api/v1/auth/login`
4. Kliknij zakładkę **Body**
5. Wybierz **JSON**
6. Wklej:
```json
{
  "email": "test@fasthub.com",
  "password": "Test123!@#"
}
```
7. Kliknij **Send**

**Odpowiedź:** Token JWT (jeśli użytkownik istnieje)

---

## 📁 Struktura projektu w VS Code

### Backend (`fasthub-backend/`)
```
fasthub-backend/
├── app/
│   ├── api/v1/endpoints/     ← API endpoints (auth, users, billing)
│   ├── core/                 ← Konfiguracja, security, dependencies
│   ├── models/               ← Modele bazy danych (SQLAlchemy)
│   ├── schemas/              ← Schematy danych (Pydantic)
│   └── main.py               ← Główny plik aplikacji
├── alembic/                  ← Migracje bazy danych
├── tests/                    ← Testy
├── requirements.txt          ← Zależności Python
└── start_backend.sh          ← Skrypt startowy
```

### Frontend (`fasthub-frontend/`)
```
fasthub-frontend/
├── src/
│   ├── api/                  ← Klienty API (axios)
│   ├── components/           ← Komponenty React
│   ├── pages/                ← Strony aplikacji
│   ├── store/                ← Stan aplikacji (Zustand)
│   ├── types/                ← Typy TypeScript
│   └── App.tsx               ← Główny komponent
├── public/                   ← Pliki statyczne
├── package.json              ← Zależności Node.js
└── vite.config.ts            ← Konfiguracja Vite
```

---

## 🔍 Przydatne skróty klawiszowe VS Code

### Nawigacja
- `Ctrl + P` - Szybkie otwieranie plików
- `Ctrl + Shift + F` - Szukaj w plikach
- `Ctrl + B` - Pokaż/ukryj panel Explorer
- `Ctrl + J` - Pokaż/ukryj panel Terminal

### Edycja
- `Ctrl + /` - Komentarz/odkomentuj linię
- `Ctrl + D` - Zaznacz następne wystąpienie słowa
- `Alt + ↑/↓` - Przenieś linię w górę/dół
- `Shift + Alt + ↓` - Duplikuj linię

### Terminal
- `` Ctrl + ` `` - Pokaż/ukryj terminal
- `Ctrl + Shift + `` ` `` - Nowy terminal
- `Ctrl + C` - Zatrzymaj proces w terminalu

### Debugowanie
- `F5` - Start debugowania
- `F9` - Dodaj/usuń breakpoint
- `F10` - Step over (następna linia)
- `F11` - Step into (wejdź do funkcji)

---

## 🐛 Rozwiązywanie problemów

### Problem: "Python interpreter not found"
**Rozwiązanie:**
1. Naciśnij `Ctrl + Shift + P`
2. Wpisz: `Python: Select Interpreter`
3. Wybierz: `/home/ubuntu/fasthub-backend/venv/bin/python`

### Problem: "Port 8000 already in use"
**Rozwiązanie:**
```bash
# Znajdź proces
lsof -ti:8000

# Zabij proces
kill -9 <PID>

# Lub jedną komendą
lsof -ti:8000 | xargs kill -9
```

### Problem: "npm: command not found"
**Rozwiązanie:** Node.js nie jest zainstalowany. Zainstaluj:
```bash
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs
```

### Problem: "Redis connection refused"
**Rozwiązanie:**
```bash
# Sprawdź status
sudo systemctl status redis

# Uruchom Redis
sudo systemctl start redis
```

### Problem: "Database connection error"
**Rozwiązanie:**
1. Sprawdź czy PostgreSQL działa: `sudo systemctl status postgresql`
2. Sprawdź `DATABASE_URL` w `.env`
3. Upewnij się że baza `fasthub` istnieje: `createdb fasthub`

---

## 📚 Przydatne komendy

### Backend
```bash
# Aktywuj venv
source venv/bin/activate

# Zainstaluj zależności
pip install -r requirements.txt

# Uruchom backend
./start_backend.sh

# Uruchom testy
pytest

# Sprawdź logi
tail -f /tmp/backend.log

# Migracje bazy danych
alembic upgrade head
```

### Frontend
```bash
# Zainstaluj zależności
npm install

# Uruchom frontend
npm run dev

# Build produkcyjny
npm run build

# Lint (sprawdź błędy)
npm run lint

# Preview buildu
npm run preview
```

---

## 🎯 Co dalej?

### 1. Eksploruj kod
- Otwórz `fasthub-backend/app/main.py` - główny plik backendu
- Otwórz `fasthub-frontend/src/App.tsx` - główny komponent frontendu
- Przejrzyj `fasthub-backend/app/api/v1/endpoints/` - endpointy API

### 2. Testuj API
- Użyj Thunder Client do testowania endpointów
- Sprawdź dokumentację API: `http://localhost:8000/docs`
- Przetestuj rejestrację, logowanie, CRUD użytkowników

### 3. Modyfikuj kod
- Zmień kolory w `fasthub-frontend/src/pages/Home.tsx`
- Dodaj nowy endpoint w `fasthub-backend/app/api/v1/endpoints/`
- Stwórz nową stronę w `fasthub-frontend/src/pages/`

### 4. Naucz się więcej
- **FastAPI:** https://fastapi.tiangolo.com/
- **React:** https://react.dev/
- **TypeScript:** https://www.typescriptlang.org/docs/
- **Ant Design:** https://ant.design/components/overview/

---

## ✅ Checklist - Co powinieneś widzieć

- [ ] VS Code połączony z sandboxem przez SSH
- [ ] 5 rozszerzeń zainstalowanych (Python, Pylance, ESLint, Prettier, Thunder Client)
- [ ] Workspace `fasthub.code-workspace` otwarty
- [ ] Backend działa na `http://localhost:8000`
- [ ] Frontend działa na `http://localhost:3001`
- [ ] API docs dostępne na `http://localhost:8000/docs`
- [ ] Thunder Client pokazuje odpowiedzi z API
- [ ] Brak błędów w terminalu

---

## 🆘 Potrzebujesz pomocy?

**Jeśli coś nie działa:**
1. Sprawdź logi w terminalu
2. Sprawdź czy wszystkie serwisy działają (PostgreSQL, Redis)
3. Sprawdź czy porty 8000 i 3001 są wolne
4. Sprawdź pliki `.env` (backend i frontend)

**Kontakt:**
- Email: support@fasthub.com
- Dokumentacja: http://localhost:3001/docs

---

**Powodzenia! 🚀**
