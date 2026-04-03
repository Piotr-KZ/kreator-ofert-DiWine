# Ekosystem Piotr-KZ — Kontekst dla Claude

> **Ten plik jest IDENTYCZNY we wszystkich repozytoriach ekosystemu.**
> Po każdej sesji pracy — zaktualizuj ten plik we WSZYSTKICH projektach.
> Ostatnia aktualizacja: 2026-04-03

## Zasady pracy z Claude

### OBOWIĄZKOWE po każdym znaczącym kroku:
1. **Commituj** automatycznie (nie czekaj na polecenie usera)
2. **Zaktualizuj ten plik** (`CLAUDE.md`) we WSZYSTKICH repo z nowym statusem
3. **Zaktualizuj memory** (`~/.claude/projects/*/memory/MEMORY.md`) — WSZYSTKIE 3 katalogi
4. **Nigdy nie pytaj** — user nie jest programistą, rób co trzeba

### Memory directories (WSZYSTKIE do aktualizacji):
- `~/.claude/projects/C--Users-Lennovo/memory/` — sesje z home
- `~/.claude/projects/C--Projekty-internetowe-autoflow/memory/` — sesje z autoflow
- `~/.claude/projects/C--Projekty-internetowe-Fasthub/memory/` — sesje z fasthub

### Pliki CLAUDE.md (WSZYSTKIE do aktualizacji):
- `C:/Projekty internetowe/autoflow/CLAUDE.md`
- `C:/Projekty internetowe/Fasthub/CLAUDE.md`
- `C:/Projekty internetowe/website-creator/CLAUDE.md`
- `C:/Projekty internetowe/vision-tool/CLAUDE.md`

### Język: Polski (zawsze)

---

## Projekty ekosystemu

### FastHub (SaaS Boilerplate) — COMPLETE
- **Repo**: https://github.com/Piotr-KZ/Fasthub
- **Lokalizacja**: `C:/Projekty internetowe/Fasthub`
- **Branch aktywny**: `feat/brief-29a-billing`
- **Stack**: FastAPI, PostgreSQL, Redis, React 19, TypeScript, Tailwind 4, Vite 7
- **Skala**: ~47k LoC, 376 plików, 645+ testów, 26 modułów w fasthub_core
- **Status**: Development COMPLETE (v5.0), Briefs 0–29b ALL DONE
- **Audyt bezpieczeństwa**: DONE (3 CRITICAL, 10 HIGH, 18 MEDIUM — all fixed)
- **Demo**: https://fasthub-lz4x.onrender.com

### AutoFlow (Automatyzacja procesów) — AKTYWNY
- **Repo**: https://github.com/Piotr-KZ/autoflow
- **Lokalizacja**: `C:/Projekty internetowe/autoflow`
- **Branch aktywny**: `feature/fasthub-core-integration` (+ main)
- **Stack**: Python/FastAPI, React/Vite, SQLAlchemy + Alembic, Redis
- **Status**: Audyt bezpieczeństwa DONE, Plan migracji ZATWIERDZONY
- **Audyt bezpieczeństwa** (2026-04-02): 6 commitów na main — all fixed
- **Kluczowa zależność**: używa fasthub_core (thin wrapper pattern z Brief 12)

### WebCreator (Kreator stron) — Brief 30 DONE
- **Repo**: https://github.com/Piotr-KZ/website-creator
- **Lokalizacja**: `C:/Projekty internetowe/website-creator`
- **Branch**: `main`
- **Status**: Brief 30 (foundation) COMPLETE, CI passing
- **Audyt bezpieczeństwa**: DONE (17 vulnerabilities — all fixed)
- **Brief docs**: `C:/Projekty internetowe/Web kreator/`

### Vision Tool (Testowanie UI) — Security DONE
- **Repo**: https://github.com/Piotr-KZ/vision-tool
- **Lokalizacja**: `C:/Projekty internetowe/vision-tool`
- **Branch**: `main`
- **Status**: V3 complete, security fixes done
- **Plan**: Ewolucja z dev tool → production SaaS (połączony z FastHub)
- **URL**: http://localhost:8500, Token: `vt_dev_webcreator_2026`

---

## Aktywne zadanie: Migracja AutoFlow → modele FastHub

### Plan (plik: `~/.claude/plans/zazzy-gathering-cocoa.md`)

**Problem**: AutoFlow 23 tabel z Integer PK + tenant_id (string). FastHub 29 modeli z UUID PK + org_id (UUID FK). Duplikacja User/Org/Member/Billing/Auth.

**Cel**: AutoFlow używa fasthub_core modeli (auth, users, billing, notifications, audit, RBAC, GDPR, storage). Domain tables (processes, executions, integrations) zostają ale z UUID PK i org FK.

**Pełny plan**: `~/.claude/plans/zazzy-gathering-cocoa.md`

| Faza | Opis | Ryzyko | DB zmiana | Status |
|------|------|--------|-----------|--------|
| 0 | Warstwa abstrakcji (`app/compat/`) | ZERO | NIE | **NOT STARTED** |
| 1 | FastHub auth functions | NISKI | NIE | NOT STARTED |
| 2 | Kolumny UUID obok Integer PK (addytywne) | NISKI | ADD COLUMN | NOT STARTED |
| 3 | Dual-write UUID (API zwraca UUID) | NISKI | NIE | NOT STARTED |
| 4 | Tenant migration (tenant_id → org_uuid) | SREDNI | DATA MIGRATION | NOT STARTED |
| 5 | Swap User/Org/Member → fasthub_core | WYSOKI | RENAME+CREATE | NOT STARTED |
| 6 | Swap billing/notif/audit → fasthub_core | SREDNI | RENAME+CREATE | NOT STARTED |
| 7 | PK swap domain tables + cleanup | NISKI | DROP legacy | NOT STARTED |

**Łącznie**: ~130 zmian w plikach, ~2500 linii, 8 migracji Alembic

### Zasady bezpieczeństwa:
- Każda faza = osobny branch + PR
- Backup bazy PRZED każdą fazą z migracją
- Legacy tables (_legacy) zachowane do Fazy 7
- Nigdy dwie fazy ryzykowne (4-6) w jednej sesji
- CI green PRZED merge

---

## Ukończone zadania (log)

### 2026-04-02: Audyt bezpieczeństwa AutoFlow
- 6 commitów na main
- Rate limiter → Redis primary + in-memory fallback
- Auth, billing isolation, SSRF, WebSocket bridge fixes
- Webhook secret header, WS auth, scheduler engine, encryption guard
- Production guards, payload limits, OAuth hardening
- render.yaml missing env vars
- Thin wrappers restored (Brief 12 separation) — ~2000 lines dedup

### 2026-04-01: Audyt bezpieczeństwa FastHub + Vision Tool + WebCreator
- FastHub: 31 vulnerabilities fixed (3C, 10H, 18M)
- Vision Tool: 6 vulnerabilities fixed
- WebCreator: 17 vulnerabilities fixed (6C, 4H, 7M)

### 2026-03-13: FastHub Briefs 0-29b ALL COMPLETE
### 2026-03-13: WebCreator Brief 30 COMPLETE

---

## Dokumenty referencyjne
- **ANALIZA_POROWNAWCZA.md** — pełne porównanie AutoFlow vs FastHub (moduł po module, 8 sekcji)
- **Plan migracji**: `~/.claude/plans/zazzy-gathering-cocoa.md` (8 faz)
- Oba pliki w KAŻDYM repo ekosystemu

## Środowisko
- **OS**: Windows 10 Pro
- **Docker**: NIE dostępny na tym PC — testy tylko w CI
- **Python**: >=3.11
- **Node**: React 19, Vite 7
- **CI**: GitHub Actions
