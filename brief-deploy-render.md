# Brief: Deploy na Render w 5 minut

## Cel
Ktoś wchodzi na GitHub FastHub, klika przycisk "Deploy to Render",
wpisuje kilka zmiennych (klucz Stripe, secret key) i za 5 minut ma
działający system w chmurze.

## Stan obecny
- `render.yaml` ISTNIEJE ale jest niekompletny:
  - Hardcoded credentials (DATABASE_URL z hasłem w pliku!)
  - Brak serwisu PostgreSQL (baza zewnętrzna, ręcznie podłączona)
  - Brak serwisu Redis
  - Frontend używa `npm run preview` (dev server, nie produkcja)
  - Brak health check konfiguracji
  - Brak "Deploy to Render" buttona
- `Procfile` istnieje (alembic + uvicorn)
- `entrypoint.sh` istnieje (migracje + start)
- `.env.example` istnieje
- Dockerfiles istnieją (backend + frontend)
- Health endpoint `/health` istnieje w kodzie

---

## CHECKLIST — co zrobić

### 1. render.yaml — poprawić
- [ ] Dodać serwis PostgreSQL (type: pserv lub databases section)
- [ ] Dodać serwis Redis (type: redis lub pserv)
- [ ] Backend: użyć fromDatabase/fromGroup zamiast hardcoded URL
- [ ] Backend: dodać healthCheckPath: /health
- [ ] Backend: buildCommand z pip install -e . + requirements
- [ ] Backend: startCommand z alembic upgrade head && uvicorn
- [ ] Frontend: zmienić na static site (build + dist/) zamiast npm preview
- [ ] Frontend: auto-rewrite rules dla SPA (React Router)
- [ ] Usunąć hardcoded credentials z pliku
- [ ] Env vars: SECRET_KEY = generateValue (Render auto-generuje)
- [ ] Env vars: DATABASE_URL = fromDatabase (linkowanie)
- [ ] Env vars: REDIS_URL = fromService (linkowanie)
- [ ] Env vars: BACKEND_CORS_ORIGINS = sync:false (user wpisuje)
- [ ] Region: frankfurt (EU, bliżej PL)

### 2. Frontend — produkcyjny build na Render
- [ ] Zmienić z web service (npm preview) na static site
- [ ] Render static site = darmowy CDN + auto-SSL
- [ ] Dodać headers (cache, security) w render.yaml
- [ ] SPA routing: rewrite /* → /index.html
- [ ] VITE_API_URL jako build-time env var

### 3. Backend — dostosowania
- [ ] Sprawdzić czy alembic upgrade head działa z Render DATABASE_URL
- [ ] Render daje DATABASE_URL jako postgresql:// — asyncpg potrzebuje postgresql+asyncpg://
- [ ] Dodać konwersję URL w config.py (replace postgresql:// → postgresql+asyncpg://)
- [ ] Sprawdzić czy health check /health zwraca 200 bez DB connection

### 4. Przycisk "Deploy to Render"
- [ ] Dodać do README.md badge/button z linkiem
- [ ] Format: `[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Piotr-KZ/Fasthub)`
- [ ] Krótka instrukcja: "kliknij → wypełnij zmienne → gotowe"

### 5. Dokumentacja env vars
- [ ] Lista WYMAGANYCH zmiennych (SECRET_KEY, DATABASE_URL)
- [ ] Lista OPCJONALNYCH (STRIPE, SENTRY, SENDGRID, Google OAuth)
- [ ] Opis co każda robi — prostym językiem

---

## WERYFIKACJA — po zakończeniu sprawdzić

### Poprawność render.yaml
- [ ] Brak hardcoded credentials
- [ ] DATABASE_URL linkowany z bazy Render
- [ ] SECRET_KEY auto-generowany
- [ ] Health check skonfigurowany
- [ ] Frontend jako static site z SPA routing
- [ ] Redis skonfigurowany

### Czy działa end-to-end (logiczny test)
- [ ] render.yaml parsuje się poprawnie (valid YAML)
- [ ] Build command zainstaluje fasthub_core + requirements
- [ ] Start command odpali migracje + serwer
- [ ] Frontend zbuilduje się i będzie serwowany jako statyczny
- [ ] CORS pozwoli frontendowi gadać z backendem
- [ ] /health endpoint odpowie 200

### Porównanie z konkurencją
- [ ] Czy jest przycisk "Deploy to Render" w README? → TAK
- [ ] Czy user musi wpisać max 3-5 zmiennych? → TAK
- [ ] Czy reszta jest auto-konfigurowana? → TAK
- [ ] Czy setup trwa < 5 minut? → TAK (po kliknięciu)

---

## CZEGO NIE ROBIMY (out of scope)
- Custom domain setup (to user robi sam w Render dashboard)
- CI/CD pipeline (Render ma auto-deploy z GitHub)
- SSL certyfikaty (Render daje je automatycznie)
- Skalowanie (to konfiguracja w dashboard, nie w yaml)
- Monitoring setup (Sentry DSN to opcjonalny env var)
