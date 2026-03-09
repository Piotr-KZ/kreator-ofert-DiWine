# FastHub — SaaS Boilerplate

Production-ready platforma do budowy aplikacji SaaS. Gotowe "podwozie": auth, organizacje, RBAC, platnosci (5 bramek w tym polskie), RODO, powiadomienia, faktury, multi-tenancy.

**Pierwsza aplikacja na FastHub:** Kreator Stron WWW (WebCreator).

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/Piotr-KZ/Fasthub)

---

## Quick Start (Docker)

```bash
git clone https://github.com/Piotr-KZ/Fasthub.git
cd Fasthub
docker-compose up
```

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## Deploy na Render

1. Kliknij **Deploy to Render** powyzej
2. Po deploy'u ustaw zmienne:

| Serwis | Zmienna | Wartosc |
|--------|---------|---------|
| fasthub-frontend | `VITE_API_URL` | `https://<backend>.onrender.com/api/v1` |
| fasthub-backend | `BACKEND_CORS_ORIGINS` | `["https://<frontend>.onrender.com"]` |

3. **Manual Deploy** na obu serwisach — gotowe.

Opcjonalne zmienne: `STRIPE_SECRET_KEY`, `SENDGRID_API_KEY`, `SENTRY_DSN`, `GOOGLE_CLIENT_ID/SECRET`, `GITHUB_CLIENT_ID/SECRET`.

---

## Tech Stack

| Warstwa | Technologie |
|---------|------------|
| Backend | FastAPI 0.104+, Python 3.11+, fasthub_core (21 modulow) |
| Baza danych | PostgreSQL 15, Redis 7, Alembic (migracje) |
| Frontend | React 19, TypeScript, Tailwind CSS 4, Vite 7, Zustand 5 |
| DevOps | Docker + Docker Compose, GitHub Actions CI/CD |

---

## Struktura projektu

```
Fasthub/
├── fasthub_core/               # Uniwersalny pakiet SaaS (21 modulow)
├── fasthub-backend/            # FastAPI backend
│   ├── app/                    # Kod aplikacji (API, modele, schematy, serwisy)
│   ├── alembic/                # Migracje bazy danych
│   └── tests/                  # Unit + integration testy
├── fasthub-frontend/           # React frontend
│   ├── src/pages/              # Strony (Login, Dashboard, Team, Settings, Billing...)
│   ├── src/components/         # UI components (Btn, Fld, Tile, SectionCard...)
│   ├── src/api/                # API client (Axios + auto-refresh tokenow)
│   └── src/store/              # Zustand stores (auth, org, billing)
├── docker-compose.yml          # Docker orchestration
├── FASTHUB_DOKUMENTACJA_AI.md  # Dokumentacja techniczna (dla AI i programistow)
├── FASTHUB_ARCHITEKTURA.md     # Dokumentacja architektoniczna (biznesowa)
└── docs/TESTING.md             # Testy i CI/CD
```

---

## Development (bez Dockera)

```bash
# Backend
cd fasthub-backend
pip install -r requirements.txt
pip install -e ../  # fasthub_core
alembic upgrade head
uvicorn app.main:app --reload

# Frontend
cd fasthub-frontend
npm install
npm run dev
```

---

## Testy

```bash
# Backend — unit testy
cd fasthub-backend && pytest tests/unit/ -v

# Backend — integration (wymaga PostgreSQL + Redis)
pytest tests/integration/ -v

# Frontend — build check
cd fasthub-frontend && npm run build
```

200 testow (151 unit + 49 integration), 100% PASS. CI: GitHub Actions.

Szczegoly: [docs/TESTING.md](docs/TESTING.md)

---

## Dokumentacja

| Dokument | Zawartosc |
|----------|-----------|
| [FASTHUB_DOKUMENTACJA_AI.md](FASTHUB_DOKUMENTACJA_AI.md) | Pełna dokumentacja techniczna — API, modele, endpointy, konfiguracja |
| [FASTHUB_ARCHITEKTURA.md](FASTHUB_ARCHITEKTURA.md) | Architektura biznesowa — moduly, platnosci, RBAC, RODO |
| [docs/TESTING.md](docs/TESTING.md) | Testy, fixtures, CI/CD, env vars |

---

## License

MIT License

---

*FastHub v3.0 | 2026-03-09 | Built by Piotr-KZ*
